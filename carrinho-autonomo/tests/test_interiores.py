"""Portas, destinos centrais, cliques e reserva geométrica do campus ampliado."""
import math
import unittest
from grade_navegacao import Grade
from planejamento import planejar, resolver_alvo, alvo_do_clique
from navegacao import pontos_da_rota, segmento_seguro


class Interiores(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = Grade()

    def test_destino_no_centro_e_selecao_por_nome(self):
        for s in self.g.config.setores:
            local = self.g.config.destinos_setores[s['id']]
            esperado = resolver_alvo(self.g, local)
            self.assertEqual(esperado[1], s['centro'])
            for alias in (s['nome'], s['id'], s['nome'].lower()):
                self.assertEqual(resolver_alvo(self.g, alias), esperado)
        self.assertEqual(resolver_alvo(self.g, 'H'), resolver_alvo(self.g, 'H01'))
        self.assertEqual(resolver_alvo(self.g, 'atendimento'), resolver_alvo(self.g, 'CDA01'))

    def test_clique_interno_nome_e_paredes(self):
        for s in self.g.config.setores:
            x, y = s['centro']
            w, d = s['tamanho']
            local = self.g.config.destinos_setores[s['id']]
            for p in ((x, y), (x+.5, y+.5), (x, y+d*.30)):
                self.assertEqual(alvo_do_clique(self.g, *p), local)
            self.assertTrue(alvo_do_clique(self.g, x, y+d/2).startswith('CEL_'))
            self.assertTrue(alvo_do_clique(self.g, x, y, False).startswith('CEL_'))
        with self.assertRaises(ValueError):
            alvo_do_clique(self.g, float('nan'), 0)

    def test_entrada_todos_setores_cinco_buscas(self):
        for destino in self.g.config.destinos_setores.values():
            for algoritmo in range(5):
                r = planejar(self.g, (0, 0), destino, algoritmo)
                pts = pontos_da_rota(self.g, r)
                self.assertEqual(pts[-1], self.g.config.pontos[destino])
                self.assertTrue(all(segmento_seguro(self.g, a, b) for a, b in zip(pts, pts[1:])))

    def test_entrada_e_saida_entre_todos_setores(self):
        for inicio in self.g.config.destinos_setores.values():
            for fim in self.g.config.destinos_setores.values():
                r = planejar(self.g, self.g.config.pontos[inicio], fim)
                self.assertTrue(pontos_da_rota(self.g, r))

    def test_espaco_interno_e_portas(self):
        r = self.g.raio+.06
        for s in self.g.config.setores:
            x, y = s['centro']
            w, d = s['tamanho']
            lado, largura, offset = s['porta']
            self.assertGreaterEqual(min(w, d), 6.)
            self.assertGreater(largura, 2*r)
            porta = (x+(w/2 if lado == 'L' else -w/2), y+offset) if lado in ('L', 'O') else (x+offset, y-d/2)
            self.assertTrue(segmento_seguro(self.g, porta, (x, y)))
            # Quatro pontos afastados do centro: há espaço para circular dentro.
            for dx, dy in ((-1., -1.), (1., -1.), (1., 1.), (-1., 1.)):
                p = (x+dx, y+dy)
                local = self.g.mundo_para_celula(*p)
                self.assertTrue(pontos_da_rota(self.g, planejar(self.g, (x, y), local)))
            # Corpos retangulares dos setores não se sobrepõem.
            for outro in self.g.config.setores:
                if outro is s:
                    continue
                ox, oy = outro['centro']
                ow, od = outro['tamanho']
                self.assertTrue(abs(x-ox) > (w+ow)/2 or abs(y-oy) > (d+od)/2)


if __name__ == '__main__':
    unittest.main()
