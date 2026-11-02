"""Testes da ponte Webots -> Qwen, SEM carregar o modelo de verdade.

Um "servidor falso" (poucas linhas de Python) imita o servidor_qwen.py.
Assim conferimos rapidamente: os dados enviados, o envio sem espera, as
respostas fora de ordem e as falhas. A qualidade do texto do Qwen é
verificada à parte, executando o modelo real (ver VALIDACAO_QWEN_WEBOTS.md).
"""
import json
import math
import sys
import time
import unittest

import explicador_qwen as eq
from colab.rotas_comentadas import calcular_rota
from grade_navegacao import Grade
from planejamento import planejar

# Servidor falso: anuncia "pronto", espera 0,5 s por pedido e responde.
SERVIDOR_FALSO = r'''
import json, sys, time
print(json.dumps({"tipo": "pronto", "dispositivo": "falso"}), flush=True)
for linha in sys.stdin:
    pedido = json.loads(linha)
    time.sleep(0.5)
    print(json.dumps({"tipo": "explicacao", "id": pedido["id"],
                      "texto": "ok " + str(pedido["id"]), "segundos": 0.5}), flush=True)
'''
# Servidor que falha ao carregar, como aconteceria sem torch ou sem o modelo.
SERVIDOR_SEM_MODELO = r'''
import json
print(json.dumps({"tipo": "falha_carregamento", "erro": "OSError: modelo ausente"}), flush=True)
'''


def esperar_respostas(explicador, quantidade, limite_s=10):
    """Junta respostas até ter 'quantidade' ou estourar o tempo limite."""
    recebidas = []
    fim = time.monotonic() + limite_s
    while len(recebidas) < quantidade and time.monotonic() < fim:
        recebidas += explicador.respostas()
        time.sleep(0.02)
    return recebidas


class RotaParaExplicar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grade = Grade()

    def test_origem_cadastrada_igual_ao_notebook(self):
        # Na Entrada IESB, os números devem ser os mesmos do notebook comentado.
        resultado = planejar(self.grade, (0.0, 0.0), "Biblioteca", algoritmo=4)
        rota = eq.rota_para_explicar(self.grade, resultado)
        referencia = calcular_rota("Entrada IESB", "Biblioteca")
        self.assertEqual(rota["origem"], "Entrada IESB (posição atual do carrinho)")
        self.assertEqual(rota["destino"], "Biblioteca")
        for campo in ("algoritmo", "caminho", "distancia_grade_m", "conectores_m", "distancia_total_m"):
            self.assertEqual(rota[campo], referencia[campo])
        self.assertAlmostEqual(rota["distancia_total_m"], 15 + math.sqrt(0.5))

    def test_ruido_da_fisica_ainda_reconhece_o_local(self):
        resultado = planejar(self.grade, (0.004, -0.003), "Bloco H", algoritmo=4)
        rota = eq.rota_para_explicar(self.grade, resultado)
        self.assertTrue(rota["origem"].startswith("Entrada IESB"))
        self.assertEqual(rota["distancia_total_m"], resultado["percurso_total_m"])

    def test_origem_entre_locais_nao_ganha_nome_inventado(self):
        resultado = planejar(self.grade, (2.3, 7.6), "Cantina", algoritmo=4)
        rota = eq.rota_para_explicar(self.grade, resultado)
        self.assertIn("x = 2.30 m; y = 7.60 m", rota["origem"])
        self.assertIn("fora dos locais cadastrados", rota["origem"])
        for nome in self.grade.config.nomes.values():
            self.assertNotIn(nome, rota["origem"])

    def test_destino_celula_e_algoritmo_escolhido(self):
        resultado = planejar(self.grade, (0.0, 0.0), "C29L24", algoritmo=1)
        rota = eq.rota_para_explicar(self.grade, resultado)
        self.assertEqual(rota["destino"], "Célula CEL_C29_L24 (sem nome cadastrado)")
        self.assertEqual(rota["algoritmo"], "Largura")

    def test_sem_rota_nao_gera_mensagens(self):
        resultado = {"caminho": None}
        with self.assertRaises(ValueError):
            eq.mensagens_da_rota(self.grade, resultado)

    def test_mensagens_levam_exatamente_os_dados_calculados(self):
        resultado = planejar(self.grade, (0.0, 0.0), "H01", algoritmo=4)
        mensagens = eq.mensagens_da_rota(self.grade, resultado)
        self.assertEqual([m["role"] for m in mensagens], ["system", "user"])
        dados = json.loads(mensagens[1]["content"].split("\n", 1)[1])
        self.assertEqual(dados, eq.rota_para_explicar(self.grade, resultado))
        self.assertEqual(dados["distancia_total_m"], resultado["percurso_total_m"])


class ProcessoSeparado(unittest.TestCase):
    def test_pedido_nao_espera_e_respostas_chegam_numeradas(self):
        explicador = eq.ExplicadorQwen([sys.executable, "-c", SERVIDOR_FALSO])
        explicador.iniciar()
        try:
            inicio = time.monotonic()
            self.assertTrue(explicador.pedir(1, [{"role": "user", "content": "a"}]))
            self.assertTrue(explicador.pedir(2, [{"role": "user", "content": "b"}]))
            # Enviar dois pedidos não pode esperar a geração (0,5 s cada).
            self.assertLess(time.monotonic() - inicio, 0.2)
            self.assertEqual(explicador.descricao(), "carregando")
            recebidas = esperar_respostas(explicador, 3)
        finally:
            explicador.encerrar()
        self.assertEqual(recebidas[0]["tipo"], "pronto")
        self.assertEqual([m["id"] for m in recebidas[1:]], [1, 2])
        self.assertEqual(explicador.pendentes, set())
        self.assertEqual(explicador.processo.poll(), 0)

    def test_falha_de_carregamento_deixa_indisponivel(self):
        explicador = eq.ExplicadorQwen([sys.executable, "-c", SERVIDOR_SEM_MODELO])
        explicador.iniciar()
        try:
            recebidas = esperar_respostas(explicador, 2, limite_s=2)
            # Só um aviso: o "encerrado" seguinte não repete nem esconde a causa.
            self.assertEqual([m["tipo"] for m in recebidas], ["falha_carregamento"])
            self.assertEqual(explicador.estado, "indisponível")
            self.assertIn("modelo ausente", explicador.erro)
            self.assertFalse(explicador.pedir(1, []))
        finally:
            explicador.encerrar()

    def test_programa_inexistente_nao_quebra(self):
        explicador = eq.ExplicadorQwen(["/caminho/que/nao/existe/python"])
        explicador.iniciar()
        self.assertEqual(explicador.estado, "indisponível")
        self.assertFalse(explicador.pedir(1, []))
        explicador.encerrar()


if __name__ == "__main__":
    unittest.main()
