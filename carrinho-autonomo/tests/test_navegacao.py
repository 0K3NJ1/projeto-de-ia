"""Regressões independentes do Webots: geometria, estados e falhas do seguidor."""
import math
import unittest
from grade_navegacao import Grade
from planejamento import planejar
from navegacao import Seguidor, pontos_da_rota, segmento_seguro, CORREDOR
from cenarios import isolar_destino


class Navegacao(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grade = Grade()

    def setUp(self):
        self.s = Seguidor(self.grade)
        self.r = planejar(self.grade, (-.5, -.5), 'C25L02')

    def test_conectores_e_centros(self):
        r = planejar(self.grade, (0., 0.), 'H01')
        p = pontos_da_rota(self.grade, r)
        # H01 agora coincide com o último centro; não cria alvo duplicado.
        self.assertEqual(p, [r['posicao_inicial']] + [self.grade.celulas[n].centro for n in r['caminho']])
        self.assertEqual(p[-1], r['ponto_final'])
        self.assertAlmostEqual(sum(math.dist(a, b) for a, b in zip(p, p[1:])), r['percurso_total_m'])

    def test_sem_rota(self):
        with self.assertRaises(ValueError):
            self.s.iniciar(planejar(isolar_destino(self.grade), (0, 0), 'H01'), (0, 0, 0), 0)
        self.assertEqual(self.s.estado, 'falha')
        self.assertEqual(self.s.comando, (0, 0))

    def test_origem_igual_e_mesma_celula_distinta(self):
        r = planejar(self.grade, (0, 0), 'EXT01')
        self.s.iniciar(r, (0, 0, 0), 0)
        self.assertEqual(self.s.estado, 'concluído')
        r = planejar(self.grade, (.0001, .0001), 'EXT01')
        self.s.iniciar(r, (.0001, .0001, 0), 0)
        self.assertEqual(self.s.estado, 'concluído')
        r = planejar(self.grade, (-.4, -.4), 'C24L01')
        self.assertEqual(r['custo_m'], 0)
        self.assertGreater(len(pontos_da_rota(self.grade, r)), 1)

    def test_pose_antiga_recusada(self):
        with self.assertRaises(ValueError):
            self.s.iniciar(self.r, (0, 0, 0), 0)

    def test_giro_sinais_pausa_e_parada(self):
        self.s.iniciar(self.r, (-.5, -.5, -math.pi/2), 0)
        e, d = self.s.atualizar((-.5, -.5, -math.pi/2), .032)
        self.assertLess(e, 0)
        self.assertGreater(d, 0)
        self.s.pausar()
        t = self.s.tempo_s
        self.assertEqual(self.s.atualizar((-.5, -.5, 0), 99), (0, 0))
        self.s.retomar(99)
        self.s.atualizar((-.5, -.5, 0), 99.032)
        self.assertAlmostEqual(self.s.tempo_s, t+.032)
        self.s.parar()
        self.s.retomar(100)
        self.assertEqual(self.s.atualizar((-.5, -.5, 0), 100), (0, 0))

    def test_desvio_e_localizacao_invalida(self):
        for pose in ((-.5, -.5+CORREDOR+.001, 0), (float('nan'), 0, 0)):
            self.s.iniciar(self.r, (-.5, -.5, 0), 0)
            self.assertEqual(self.s.atualizar(pose, .032), (0, 0))
            self.assertEqual(self.s.estado, 'falha')

    def test_sem_progresso_giro_e_avanco(self):
        for rumo in (0, math.pi):
            self.s.iniciar(self.r, (-.5, -.5, rumo), 0)
            for i in range(1, 270):
                self.s.atualizar((-.5, -.5, rumo), i*.032)
            self.assertEqual(self.s.estado, 'falha')
            self.assertIn('progresso', self.s.motivo)

    def test_margem_adicional_nao_reduz_grade(self):
        self.assertFalse(segmento_seguro(self.grade, (0, 0), (0, 28)))
        # Segmento aprovado pela grade, mas sem a reserva adicional junto à parede.
        p = (0, self.grade.piso['y_min']+self.grade.raio+.02)
        self.assertFalse(segmento_seguro(self.grade, p, p))

    def test_modelo_cinematico_curva_sem_cortar(self):
        pose = [-.5, -.5, 0.]
        self.s.iniciar(self.r, pose, 0)
        estados = set()
        for i in range(1, 10000):
            e, d = self.s.atualizar(pose, i*.032)
            estados.add(self.s.estado)
            v, w = (e+d)*self.s.raio_roda/2, (d-e)*self.s.raio_roda/self.s.bitola
            pose[0] += v*math.cos(pose[2])*.032
            pose[1] += v*math.sin(pose[2])*.032
            pose[2] += w*.032
            if self.s.estado not in self.s.ATIVOS:
                break
        self.assertEqual(self.s.estado, 'concluído', self.s.motivo)
        self.assertLess(math.dist(pose[:2], self.r['ponto_final']), .02)
        self.assertTrue({'girando', 'avançando', 'estabilizando'} <= estados)
        self.assertEqual(self.s.comando, (0, 0))


if __name__ == '__main__':
    unittest.main()
