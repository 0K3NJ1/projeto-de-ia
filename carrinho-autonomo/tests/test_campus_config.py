"""Verifica erros de edição antes de abrir o Webots (sem simulação ou busca)."""

import copy
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import campus_config as cfg
from gerar_campus import validar


def copia():
    return SimpleNamespace(**{k: copy.deepcopy(getattr(cfg,k)) for k in
        ("piso","paredes_padrao","entrada","pontos","nomes","robo","setores","paredes","blocos","folga_robo")})


class ConfiguracaoCampus(unittest.TestCase):
    def test_configuracao_atual(self):
        esperados = {f"EXT{i:02d}" for i in range(1,9)} | {
            "BB01","CDA01","H01","F01","J01","E01","D01","C01","B01","CAN01"}
        self.assertTrue(esperados.issubset(cfg.pontos))
        self.assertGreater(len(validar()),0)

    def test_novo_ponto_em_area_livre(self):
        c = copia()
        c.pontos["NOVO01"] = (0.,7.)
        c.nomes["NOVO01"] = "Novo acesso"
        validar(c)

    def test_ponto_sem_nome(self):
        c = copia()
        c.pontos["NOVO01"] = (0.,7.)
        with self.assertRaisesRegex(ValueError,"mesmos identificadores"):
            validar(c)

    def test_ponto_em_parede(self):
        c = copia()
        x, y = c.setores[0]['centro']
        c.pontos["EXT02"] = (x, y+c.setores[0]['tamanho'][1]/2)
        with self.assertRaisesRegex(ValueError,"sem folga"):
            validar(c)

    def test_ponto_fora_do_piso(self):
        c = copia()
        c.pontos["EXT02"] = (100.,100.)
        with self.assertRaisesRegex(ValueError,"fora do piso"):
            validar(c)

    def test_porta_larga_demais(self):
        c = copia()
        c.setores[0]["porta"] = ("L",10.,0.)
        with self.assertRaisesRegex(ValueError,"Porta não cabe"):
            validar(c)

    def test_dimensao_negativa(self):
        c = copia()
        c.blocos[0]["tamanho"] = (-1.,1.,1.)
        with self.assertRaisesRegex(ValueError,"Dimensões inválidas"):
            validar(c)


if __name__ == "__main__":
    unittest.main()
