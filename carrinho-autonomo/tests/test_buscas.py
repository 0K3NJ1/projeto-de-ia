"""Regressão do laboratório, casos de borda e otimalidade na grade do campus."""
import ast
import json
from pathlib import Path
import unittest

import buscas as b
from grade_navegacao import Grade


class Buscas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grade = Grade()

    def test_referencia_romenia(self):
        # Lê somente literais dos dados acadêmicos; não executa o notebook.
        arquivo = Path(__file__).resolve().parents[1] / "referencias_academicas/laboratorio_2_aula03_busca.ipynb"
        cells = json.loads(arquivo.read_text(encoding="utf-8"))["cells"]
        def literal(indice, nome):
            for n in ast.parse("".join(cells[indice]["source"])).body:
                if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == nome for t in n.targets):
                    return ast.literal_eval(n.value)
            self.fail(nome)
        mapa, h = literal(2, "MAPA"), literal(28, "HSLD")
        self.assertEqual(b.custo_do_caminho(mapa, ["Arad", "Sibiu", "Fagaras", "Bucareste"]), 450)
        for funcao, heuristica, custo, exp in (
                (b.busca_largura, False, 450, 8), (b.busca_custo_uniforme, False, 418, 12),
                (b.a_estrela, True, 418, 5), (b.busca_gulosa, True, 450, 3),
                (b.busca_profundidade, False, 733, 7)):
            args = (mapa, "Arad", "Bucareste") + ((h,) if heuristica else ())
            rota, valor, n, ordem = funcao(*args)
            self.assertEqual((valor, n), (custo, exp), funcao.__name__)
            self.assertEqual(valor, b.custo_do_caminho(mapa, rota))
            self.assertEqual(n, len(ordem))

    def test_casos_limite_todas(self):
        mapa = {"A": {"B": 1}, "B": {"A": 1}, "C": {}}
        for f in (b.busca_profundidade, b.busca_largura, b.busca_custo_uniforme, b.busca_gulosa, b.a_estrela):
            def rodar(a, z):
                return f(mapa, a, z, {n: 0 for n in mapa}) if f in (b.busca_gulosa, b.a_estrela) else f(mapa, a, z)
            self.assertEqual(rodar("A", "A"), (["A"], 0, 0, []))
            self.assertEqual(rodar("A", "C"), (None, None, 2, ["A", "B"]))
            with self.assertRaises(ValueError):
                rodar("A", "INEXISTENTE")

    def test_relaxacao_e_teste_ao_remover(self):
        mapa = {"S": {"G": 10, "A": 1, "B": 7}, "A": {"B": 1}, "B": {"G": 1}, "G": {}}
        for f in (b.busca_custo_uniforme, b.a_estrela):
            args = (mapa, "S", "G") + ((dict.fromkeys(mapa, 0),) if f == b.a_estrela else ())
            self.assertEqual(f(*args)[:2], (["S", "A", "B", "G"], 3))
        with self.assertRaises(ValueError):
            b.validar_grafo({"A": {"A": -1}})

    def test_todos_pares_dos_18_locais(self):
        g = self.grade
        b.validar_grafo(g.grafo)
        for origem in g.associacoes.values():
            for destino in g.associacoes.values():
                a, z = origem["celula"], destino["celula"]
                h = g.heuristica(z)
                largura = b.busca_largura(g.grafo, a, z)
                uniforme = b.busca_custo_uniforme(g.grafo, a, z)
                estrela = b.a_estrela(g.grafo, a, z, h)
                self.assertEqual(largura[1], uniforme[1])
                self.assertEqual(estrela[1], uniforme[1])
                self.assertEqual(estrela[1], b.custo_do_caminho(g.grafo, estrela[0]))
                self.assertNotIn(z, estrela[3])
                for n, vs in g.grafo.items():
                    for v, c in vs.items():
                        self.assertLessEqual(h[n], c+h[v]+1e-9)

    def test_todos_interiores_acessiveis(self):
        g = self.grade
        a = g.associacoes["EXT01"]["celula"]
        for setor in g.config.setores:
            z = g.associar(setor['centro'])["celula"]
            self.assertIsNotNone(z, setor['id'])
            self.assertIsNotNone(b.a_estrela(g.grafo, a, z, g.heuristica(z))[0], setor['id'])


if __name__ == "__main__":
    unittest.main()
