"""Extrai a base didática e completa os quatro TODOs sem alterar o anexo original.

Executar novamente regenera buscas.py. As funções mantêm o fluxo do professor;
a mudança de domínio consiste em receber o mapa como argumento explícito.
"""
import ast
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent


def gerar():
    arquivo = RAIZ / "referencias_academicas/laboratorio_2_aula03_busca.ipynb"
    celulas = json.loads(arquivo.read_text(encoding="utf-8"))["cells"]
    fontes = []
    solucoes = {17: "fronteira.append(filho)",
                21: "heapq.heappush(fronteira, (filho.g, next(contador), filho))",
                35: "heapq.heappush(fronteira, (filho.g + h[vizinho], next(contador), filho))"}
    for indice in (12, 14, 8, 25, 17, 21, 31, 35):
        fonte = "".join(celulas[indice]["source"])
        estrutura = ast.parse(fonte)
        bloco = next(n for n in estrutura.body if isinstance(n, (ast.ClassDef, ast.FunctionDef)))
        linhas = fonte.splitlines()[bloco.lineno-1:bloco.end_lineno]
        fonte = "\n".join(linhas)
        if indice not in (12, 14):
            fonte = fonte.replace("(inicio, objetivo", "(mapa, inicio, objetivo")
            fonte = fonte.replace("(caminho):", "(mapa, caminho):").replace("MAPA[", "mapa[")
            fonte = fonte.replace("quilômetros", "unidades do mapa (metros no campus)")
            fonte = fonte.replace("cidade", "estado").replace("cidades", "estados")
        if indice == 8:
            fonte = fonte.replace("# Apague a linha abaixo e escreva sua solução.\n    return None",
                                  "# TODO 1 resolvido: soma de todos os pares consecutivos.\n"
                                  "    if caminho is None:\n        return None\n"
                                  "    return sum(mapa[a][b] for a, b in zip(caminho, caminho[1:]))")
        if indice in solucoes:
            inicio = fonte.index("            # -------------------------------------------------------------")
            fim = fonte.index("            pass", inicio)+len("            pass")
            fonte = fonte[:inicio] + ("            # Lacuna do laboratório resolvida: inserção na fronteira.\n"
                                     "            "+solucoes[indice]) + fonte[fim:]
        if indice not in (12, 14, 8):
            # Insere a checagem depois da docstring, antes do laço didático.
            node = ast.parse(fonte).body[0]
            pos = node.body[0].end_lineno
            linhas = fonte.splitlines()
            linhas.insert(pos, "    conferir_extremos(mapa, inicio, objetivo)")
            fonte = "\n".join(linhas)
        fontes.append(f"# Origem: Laboratório 2, célula {indice} (índice começando em zero).\n"+fonte)
    cabecalho = '''"""Buscas adaptadas do Laboratório 2 do Prof. Rodrigo Gonçalves Pinto.

Gerado por adaptar_laboratorio2.py. O anexo original permanece intacto.
Mapa: dicionário de dicionários, com custos finitos e não negativos.
A* mantém o conjunto fechado didático: requer heurística CONSISTENTE.
Manhattan em grade de quatro vizinhos satisfaz essa condição.
Objetivo testado ao retirar da fronteira; objetivo não conta como expandido.
Retorno: caminho, custo, quantidade de expansões, ordem de expansão.
"""
from collections import deque
import heapq
import itertools
import math


def validar_grafo(mapa):
    """Validação anterior à medição; aceita grafos dirigidos ou não dirigidos."""
    for origem, vizinhos in mapa.items():
        for destino, custo in vizinhos.items():
            if destino not in mapa or not math.isfinite(custo) or custo < 0:
                raise ValueError(f"Aresta inválida: {origem} -> {destino}")


def conferir_extremos(mapa, inicio, objetivo):
    """Distingue estado inválido de estado válido sem caminho até o destino."""
    if inicio not in mapa or objetivo not in mapa:
        raise ValueError("Origem ou destino ausente do grafo navegável")


'''
    (RAIZ / "buscas.py").write_text(cabecalho+"\n\n\n".join(fontes)+"\n", encoding="utf-8")
    print("buscas.py gerado: cinco buscas e quatro TODOs completados.")


if __name__ == "__main__":
    gerar()
