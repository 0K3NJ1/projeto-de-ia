"""Interface Python comum à escolha de destinos no Webots e no notebook."""
import unittest
from grade_navegacao import Grade
from planejamento import planejar, resolver_alvo, planejar_multiparadas
from cenarios import isolar_destino


class Planejamento(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = Grade()

    def test_formatos_mesmo_destino(self):
        for texto in ("C29L25", "CEL_C29_L25", "29,25", " c29 l25 "):
            self.assertEqual(resolver_alvo(self.g, texto), ("CEL_C29_L25", (4.5, 23.5)))
        self.assertEqual(resolver_alvo(self.g, "H01")[0], "CEL_C29_L25")

    def test_rejeita_bloqueada_ausente_e_texto(self):
        for texto in ("C00L00", "C99L99", "qualquer coisa", "-1,2"):
            with self.assertRaises(ValueError):
                resolver_alvo(self.g, texto)

    def test_algoritmos_e_origem_real(self):
        for i in range(5):
            r = planejar(self.g, (0, 0), "H01", i)
            self.assertEqual(r["origem"], "CEL_C24_L01")
            if i in (1, 2, 4):
                self.assertEqual(r["custo_m"], 29)
            else:
                self.assertGreaterEqual(r["custo_m"], 29)
            self.assertEqual(r["expandidos"], len(r["ordem"]))
            self.assertGreater(r["tempo_ms"], 0)
        r = planejar(self.g, (4.5, 22.5), "H01")
        self.assertEqual(r["custo_m"], 1)
        self.assertEqual(r["conectores_m"], 0)

    def test_sem_rota_e_mesmo_estado(self):
        r = planejar(isolar_destino(self.g), (0, 0), "H01")
        self.assertIsNone(r["caminho"])
        self.assertIsNone(r["percurso_total_m"])
        r = planejar(self.g, (4.5, 23.5), "H01")
        self.assertEqual((r["custo_m"], r["expandidos"], r["percurso_total_m"]), (0, 0, 0))

    def test_origem_invalida(self):
        for ponto in ((100, 100), (float("nan"), 0), (-25, -2)):
            with self.assertRaises(ValueError):
                planejar(self.g, ponto, "H01")

    def test_ruido_numerico_do_simulador_nao_muda_desempate(self):
        for ponto in ((1.48e-15, 3.12e-18), (-1e-15, 1e-15)):
            self.assertEqual(planejar(self.g, ponto, "H01")["origem"], "CEL_C24_L01")

    def test_planejar_multiparadas(self):
        # Exemplo do usuario: Cantina -> Bloco H -> Entrada
        r = planejar_multiparadas(self.g, (0, 0), ["CAN01", "H01", "EXT01"])
        self.assertIsNotNone(r["caminho"])
        self.assertGreater(len(r["caminho"]), 10)
        self.assertEqual(len(r["trechos"]), 3)
        self.assertEqual(r["ponto_final"], self.g.config.pontos["EXT01"])
        self.assertGreater(r["custo_m"], 0)


if __name__ == "__main__":
    unittest.main()
