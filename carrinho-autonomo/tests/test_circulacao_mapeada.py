"""União de corredores: impede atalhos em áreas sem acesso mapeado."""
from types import SimpleNamespace
import unittest
from gerar_campus import restricoes_circulacao
from grade_navegacao import segmento_intercepta_retangulo


class CirculacaoMapeada(unittest.TestCase):
    def config(self, faixas):
        return SimpleNamespace(piso=dict(x_min=0, x_max=10, y_min=0, y_max=10),
                               circulacao=[dict(id=str(i), limites=f) for i,f in enumerate(faixas)])

    def test_complemento_da_uniao_sem_criar_parede_na_juncao(self):
        faixas = [(1,4,1,9), (1,9,4,7)]
        caixas = restricoes_circulacao(self.config(faixas))
        for ix in range(40):
            for iy in range(40):
                x, y = (ix+.5)/4, (iy+.5)/4
                dentro = any(a < x < b and c < y < d for a,b,c,d in faixas)
                bloqueado = any(abs(x-r['centro'][0]) < r['tamanho'][0]/2 and
                                abs(y-r['centro'][1]) < r['tamanho'][1]/2 for r in caixas)
                self.assertEqual(bloqueado, not dentro, (x,y))
        for a,b in [((2.5,2),(2.5,5.5)), ((2.5,5.5),(8,5.5))]:
            for r in caixas:
                x,y = r['centro']; w,d,_ = r['tamanho']
                self.assertFalse(segmento_intercepta_retangulo(a,b,(x-w/2,x+w/2,y-d/2,y+d/2)))

    def test_circulacao_invalida(self):
        for faixas in ([],[(1,1,2,3)],[(1,12,2,3)],[(1,float('nan'),2,3)]):
            with self.assertRaises(ValueError):
                restricoes_circulacao(self.config(faixas))

    def test_sem_restricao_em_configuracao_antiga(self):
        self.assertEqual(restricoes_circulacao(SimpleNamespace()), [])
