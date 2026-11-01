"""Confere a ponte entre os nomes digitados, o A* existente e os dados do Qwen.

Não carrega um modelo de linguagem. Estes testes validam os dados fornecidos
ao modelo; a qualidade da resposta gerada precisa ser conferida no Colab.
"""
import json
import math
import unittest
from unittest.mock import patch

import buscas
from colab import rotas_comentadas as didatica
from cenarios import isolar_destino
from planejamento import planejar


class RotasComentadas(unittest.TestCase):
    def test_nomes_ids_acentos_e_espacos(self):
        # Variações de escrita precisam identificar o mesmo local cadastrado.
        for texto in ("Biblioteca", " biblioteca ", "BB01", "bb01"):
            self.assertEqual(didatica.encontrar_local(texto), "BB01")
        self.assertEqual(didatica.encontrar_local("Acesso Cantina"), "EXT08")
        self.assertEqual(didatica.encontrar_local("CRUZAMENTO CENTRAL"), "EXT02")

    def test_entradas_invalidas_interrompem_antes_da_busca(self):
        with patch.object(didatica, "planejar") as busca:
            for valor in (None, 42, [], "", "   ", "Local inexistente", "vá à Biblioteca"):
                with self.subTest(valor=valor):
                    with self.assertRaises(ValueError):
                        didatica.calcular_rota(valor, "Biblioteca")
                    with self.assertRaises(ValueError):
                        didatica.calcular_rota("Entrada IESB", valor)
            busca.assert_not_called()

    def test_exemplo_biblioteca_tem_arestas_validas_e_custo_correto(self):
        rota = didatica.calcular_rota("Entrada IESB", "Biblioteca")
        self.assertEqual(rota["status"], "ok")
        self.assertEqual(rota["algoritmo"], "A*")
        self.assertEqual(rota["distancia_grade_m"], 15)
        self.assertAlmostEqual(rota["conectores_m"], math.sqrt(0.5))
        self.assertAlmostEqual(rota["distancia_total_m"], 15 + math.sqrt(0.5))
        # Recalcular pelas arestas detecta tanto custo errado quanto salto na rota.
        custo = buscas.custo_do_caminho(didatica.grade.grafo, rota["caminho"])
        self.assertEqual(custo, rota["distancia_grade_m"])

    def test_todos_os_locais_preservam_planejamento_existente(self):
        for destino in didatica.grade.config.nomes:
            with self.subTest(destino=destino):
                rota = didatica.calcular_rota("EXT01", destino)
                referencia = planejar(didatica.grade, (0, 0), destino, algoritmo=4)
                self.assertEqual(rota["caminho"], referencia["caminho"])
                self.assertEqual(rota["distancia_total_m"], referencia["percurso_total_m"])

    def test_mesmo_local_tem_distancia_zero_inclusive_na_entrada(self):
        for identificador, nome in didatica.grade.config.nomes.items():
            rota = didatica.calcular_rota(identificador, nome)
            self.assertEqual(rota["status"], "ok")
            self.assertEqual(rota["distancia_total_m"], 0)
            self.assertEqual(rota["conectores_m"], 0)

    def test_destino_desconectado_nao_vira_rota_inventada(self):
        # A configuração de ensaio isola o H sem alterar a grade real do projeto.
        with patch.object(didatica, "grade", isolar_destino(didatica.grade)):
            rota = didatica.calcular_rota("Entrada IESB", "Bloco H")
        self.assertEqual(rota["status"], "sem_rota")
        for campo in ("caminho", "distancia_grade_m", "conectores_m", "distancia_total_m"):
            self.assertIsNone(rota[campo])
        with self.assertRaises(ValueError):
            didatica.montar_mensagens(rota)

    def test_modelo_recebe_exatamente_dados_calculados(self):
        rota = didatica.calcular_rota("EXT01", "BB01")
        mensagens = didatica.montar_mensagens(rota)
        self.assertEqual([m["role"] for m in mensagens], ["system", "user"])
        dados = json.loads(mensagens[1]["content"].split("\n", 1)[1])
        self.assertEqual(dados, rota)
        self.assertEqual(dados["origem"], "Entrada IESB")
        self.assertEqual(dados["destino"], "Biblioteca")


if __name__ == "__main__":
    unittest.main()
