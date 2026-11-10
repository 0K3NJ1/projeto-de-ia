"""Testes do ciclo de ferramentas sem depender dos pesos do Qwen."""

import json
import unittest
from unittest.mock import patch

from colab import agente_marco2 as agente
from colab.casos_marco2 import CASOS


def chamada(nome, argumentos):
    """Imita o texto de chamada produzido pelo chat template do Qwen."""
    return "<tool_call>\n" + json.dumps({"name": nome, "arguments": argumentos}) + "\n</tool_call>"


class AgenteMarco2(unittest.TestCase):
    def test_ciclo_entrega_resultado_real_ao_modelo(self):
        # A primeira geração pede a ferramenta; a segunda precisa enxergar seu
        # resultado no papel "tool", com o custo do A* já calculado.
        def conversar(mensagens, ferramentas):
            self.assertEqual([f.__name__ for f in ferramentas], ["calcular_rota", "listar_locais"])
            if len(mensagens) == 2:
                return chamada("calcular_rota", {"origem": "Entrada IESB", "destino": "Biblioteca"})
            self.assertEqual([m["role"] for m in mensagens], ["system", "user", "assistant", "tool"])
            resultado = json.loads(mensagens[-1]["content"])
            self.assertEqual(resultado["distancia_grade_m"], 15)
            return f"A distância total é {resultado['distancia_total_m']:.2f} m."

        execucao = agente.agente("Entrada IESB para Biblioteca", conversar)
        self.assertIsNone(execucao["erro"])
        self.assertEqual(len(execucao["chamadas"]), 1)
        self.assertEqual(execucao["chamadas"][0]["resultado"]["status"], "ok")
        self.assertTrue(agente.distancia_aparece(execucao["resposta"],
                                                 execucao["chamadas"][0]["resultado"]["distancia_total_m"]))

    def test_conversa_comum_nao_chama_a_busca(self):
        execucao = agente.agente("Bom dia", lambda _m, _f: "Bom dia! Posso ajudar com rotas.")
        self.assertEqual(execucao["chamadas"], [])
        self.assertEqual(execucao["resposta"], "Bom dia! Posso ajudar com rotas.")

    def test_sem_ferramenta_nao_apresenta_rota_ou_lista_inventada(self):
        rota = agente.agente("Qual a rota da Biblioteca ao Bloco H?",
                            lambda _m, _f: "São 10 m pelo bloco C.")
        self.assertTrue(rota["resposta_ajustada"])
        self.assertIn("Não consegui calcular", rota["resposta"])
        self.assertEqual(rota["resposta_modelo"], "São 10 m pelo bloco C.")
        self.assertTrue(agente.agente("Como vou do Bloco C à Cantina?",
                                    lambda _m, _f: "Siga à direita.")["resposta_ajustada"])
        locais = agente.agente("Quais locais existem no mapa?",
                              lambda _m, _f: "Paris e Brasília")
        self.assertTrue(locais["resposta_ajustada"])
        self.assertIn("Não consegui consultar", locais["resposta"])
        def consultar(mensagens, _ferramentas):
            return (chamada("listar_locais", {}) if len(mensagens) == 2 else
                    "A Biblioteca está entre os locais cadastrados.")
        lista_real = agente.agente("Quais locais existem no mapa?", consultar)
        self.assertTrue(lista_real["resposta_ajustada"])
        self.assertEqual(lista_real["chamadas"][0]["name"], "listar_locais")
        self.assertIn("CAN01: Cantina", lista_real["resposta"])
        catalogo = json.loads(agente.listar_locais())
        quase_completa = agente.lista_de_referencia(catalogo).replace("; CAN01: Cantina", "")
        self.assertIn("EXT08: Acesso Cantina", quase_completa)
        self.assertFalse(agente.lista_fiel(quase_completa, catalogo))

    def test_ferramenta_desconhecida_e_argumentos_invalidos_nao_executam_busca(self):
        with patch.object(agente.rotas_comentadas, "calcular_rota") as busca:
            pedidos = [
                {"name": "apagar_arquivos", "arguments": {}},
                {"name": "calcular_rota", "arguments": {"origem": "Biblioteca"}},
                {"name": "calcular_rota", "arguments": {"origem": "Biblioteca", "destino": 2}},
                {"name": "calcular_rota", "arguments": {"origem": "Biblioteca", "destino": "H01", "extra": 1}},
            ]
            for pedido in pedidos:
                with self.subTest(pedido=pedido):
                    self.assertEqual(json.loads(agente.executar_pedido(pedido))["status"], "erro")
            busca.assert_not_called()

    def test_local_inexistente_vira_erro_e_nao_rota_inventada(self):
        resposta = agente.executar_pedido({"name": "calcular_rota",
                                          "arguments": {"origem": "Biblioteca", "destino": "Paris"}})
        self.assertEqual(json.loads(resposta)["status"], "erro")
        self.assertIn("Paris", resposta)

    def test_chamada_malformada_e_limite_de_passos(self):
        with self.assertRaises(ValueError):
            agente.ler_pedido_de_ferramenta("<tool_call>{texto inválido}</tool_call>")
        self.assertEqual(agente.ler_pedido_de_ferramenta(
            json.dumps({"name": "listar_locais", "arguments": {}}))["name"], "listar_locais")
        self.assertEqual(agente.ler_pedido_de_ferramenta(
            '```json\n{"name":"listar_locais","arguments":{}}\n```')["name"], "listar_locais")
        execucao = agente.agente("Rota", lambda _m, _f: chamada("listar_locais", {}), max_passos=2)
        self.assertEqual(execucao["erro"], "limite_de_passos")
        self.assertEqual(len(execucao["chamadas"]), 2)

    def test_avaliacao_usa_expectativa_anterior_a_execucao(self):
        self.assertEqual(len(CASOS), 15)
        self.assertEqual(len({c["id"] for c in CASOS}), 15)
        caso = CASOS[0]
        resultado = agente.agente(caso["pedido"], lambda mensagens, _f:
            chamada("calcular_rota", caso["argumentos"]) if len(mensagens) == 2 else
            f"Total: {json.loads(mensagens[-1]['content'])['distancia_total_m']:.2f} m")
        avaliacao = agente.avaliar_caso(caso, resultado)
        self.assertTrue(avaliacao["ferramenta_ok"])
        self.assertTrue(avaliacao["argumentos_ok"])
        self.assertTrue(avaliacao["fidelidade"])

    def test_fidelidade_nao_aceita_aproximacao_ou_sufixo_de_outro_numero(self):
        self.assertTrue(agente.distancia_aparece("Total 15,71 m", 15.71))
        self.assertFalse(agente.distancia_aparece("Cerca de 16 m", 15.71))
        self.assertFalse(agente.distancia_aparece("Total 115,71 m", 15.71))

    def test_custo_inventado_e_corrigido_sem_ocultar_erro_original(self):
        def conversar(mensagens, _ferramentas):
            if len(mensagens) == 2:
                return chamada("calcular_rota", {"origem": "Entrada IESB", "destino": "Biblioteca"})
            return "A rota tem cerca de 100 metros."

        execucao = agente.agente("Entrada IESB para Biblioteca", conversar)
        self.assertTrue(execucao["resposta_ajustada"])
        self.assertIn("100 metros", execucao["resposta_modelo"])
        self.assertIn("15.71 m", execucao["resposta"])
        self.assertFalse(agente.avaliar_caso(CASOS[0], execucao)["fidelidade"])

    def test_v7_envia_resumo_ao_modelo_e_guarda_caminho_completo(self):
        def conversar(mensagens, _ferramentas):
            if len(mensagens) == 2:
                return chamada("calcular_rota", {"origem": "Entrada IESB", "destino": "Biblioteca"})
            resumo = json.loads(mensagens[-1]["content"])
            self.assertNotIn("caminho", resumo)
            self.assertEqual(resumo["distancia_total_formatada_m"], "15.71")
            return f"Total {resumo['distancia_total_formatada_m']} m."

        execucao = agente.agente(CASOS[0]["pedido"], conversar, versao="v7")
        self.assertGreater(len(execucao["chamadas"][0]["resultado"]["caminho"]), 1)
        self.assertTrue(agente.avaliar_caso(CASOS[0], execucao)["fidelidade"])

    def test_recusa_reconhece_falta_de_dados_no_mapa(self):
        self.assertTrue(agente.resposta_recusa(
            "Não há informações sobre esse destino neste mapa."))
        self.assertFalse(agente.resposta_recusa(
            "Há informações sobre esse destino neste mapa."))

    def test_v8_seleciona_em_json_sem_template_de_ferramentas(self):
        def conversar(mensagens, ferramentas):
            self.assertEqual(ferramentas, [])
            if len(mensagens) == 2:
                return json.dumps({"name": "calcular_rota", "arguments": {
                    "origem": "Entrada IESB", "destino": "Biblioteca"}})
            self.assertIn("distancia_total_formatada_m", mensagens[-1]["content"])
            self.assertNotIn("caminho", mensagens[-1]["content"])
            return "Entrada IESB até Biblioteca: 15,71 m."

        execucao = agente.agente(CASOS[0]["pedido"], conversar, versao="v8")
        self.assertTrue(agente.avaliar_caso(CASOS[0], execucao)["ferramenta_ok"])
        self.assertTrue(agente.avaliar_caso(CASOS[0], execucao)["fidelidade"])
        self.assertIn("calcular_rota", execucao["decisao_modelo"])

    def test_v9_bloqueia_local_nao_citado_sem_corrigir_o_modelo(self):
        def conversar(mensagens, _ferramentas):
            if len(mensagens) == 2:
                return json.dumps({"name": "calcular_rota", "arguments": {
                    "origem": "Acesso Central de Atendimento", "destino": "Cantina"}})
            return "Não há rota confirmada."

        with patch.object(agente.rotas_comentadas, "calcular_rota") as busca:
            execucao = agente.agente(CASOS[2]["pedido"], conversar, versao="v9")
            busca.assert_not_called()
        self.assertEqual(execucao["chamadas"][0]["resultado"]["status"], "erro")
        self.assertEqual(execucao["chamadas"][0]["arguments"]["origem"],
                         "Acesso Central de Atendimento")
        self.assertFalse(agente.avaliar_caso(CASOS[2], execucao)["argumentos_ok"])
        self.assertTrue(agente.argumentos_citados_no_pedido(
            CASOS[0]["pedido"], {"origem": "EXT01", "destino": "BB01"}))


if __name__ == "__main__":
    unittest.main()
