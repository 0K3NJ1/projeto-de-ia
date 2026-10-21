"""Geometria, discretização e conectividade; sem depender do Webots."""
import math
import unittest

import campus_config as cfg
from grade_navegacao import Grade, segmento_intercepta_retangulo


class GradeCampus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grade = Grade()

    def test_conversao_e_limites(self):
        g = self.grade
        self.assertEqual(len(g.celulas), 1500)
        self.assertEqual(g.mundo_para_celula(0, 0), "CEL_C25_L02")
        self.assertEqual(g.celulas["CEL_C25_L02"].centro, (.5, .5))
        for c in g.celulas.values():
            self.assertEqual(g.mundo_para_celula(*c.centro), c.id)
        for xy in ((25, 0), (0, 28), (-25.01, 0)):
            with self.assertRaises(ValueError):
                g.mundo_para_celula(*xy)

    def test_raio_preserva_escala(self):
        self.assertAlmostEqual(self.grade.raio, math.hypot(.36, .3375)+.05)
        self.assertEqual(cfg.robo["escala"], 3)

    def test_centros_livres_nao_bastam(self):
        # Dois centros fora da parede, mas a aresta atravessa seu interior.
        r = (.4, .6, -.1, .1)
        self.assertFalse(segmento_intercepta_retangulo((0, 0), (0, 0), r))
        self.assertFalse(segmento_intercepta_retangulo((1, 0), (1, 0), r))
        self.assertTrue(segmento_intercepta_retangulo((0, 0), (1, 0), r))
        self.assertTrue(segmento_intercepta_retangulo((0, .1), (1, .1), r))
        self.assertFalse(segmento_intercepta_retangulo((0, .2), (1, .2), r))

    def test_arestas_e_folga_amostrada_independente(self):
        g = self.grade
        for n, vizinhos in g.grafo.items():
            a = g.celulas[n]
            for v, custo in vizinhos.items():
                b = g.celulas[v]
                self.assertEqual(g.grafo[v][n], custo)
                self.assertEqual(abs(a.coluna-b.coluna)+abs(a.linha-b.linha), 1)
                self.assertAlmostEqual(custo, math.dist(a.centro, b.centro))
                # Segunda verificação: distância euclidiana ao retângulo original.
                for t in (0, .25, .5, .75, 1):
                    x, y = (a.centro[k]+t*(b.centro[k]-a.centro[k]) for k in (0, 1))
                    for caixa in g.caixas:
                        cx, cy = caixa["centro"]
                        w, d, _ = caixa["tamanho"]
                        distancia = math.hypot(max(abs(x-cx)-w/2, 0), max(abs(y-cy)-d/2, 0))
                        self.assertGreater(distancia, g.raio)

    def test_associacoes(self):
        g = self.grade
        self.assertEqual(len(g.associacoes), 18)
        inicial = g.associacoes["EXT01"]["componente"]
        for ident, a in g.associacoes.items():
            self.assertIsNotNone(a["celula"], ident)
            self.assertLessEqual(a["distancia_m"], cfg.grade["distancia_max_associacao"])
            self.assertTrue(g.segmento_livre(cfg.pontos[ident], g.celulas[a["celula"]].centro))
            self.assertEqual(a["componente"], inicial, ident)

    def test_associacao_impossivel_e_componentes(self):
        self.assertIsNone(self.grade.associar((100, 100))["celula"])
        self.assertEqual(len(set(self.grade.componentes.values())), 1)


if __name__ == "__main__":
    unittest.main()
