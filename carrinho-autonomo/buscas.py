"""Buscas adaptadas do Laboratório 2 do Prof. Rodrigo Gonçalves Pinto.

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


# Origem: Laboratório 2, célula 12 (índice começando em zero).
class No:
    """Um nó da árvore de busca: estado + memória de como chegamos até ele."""

    __slots__ = ("estado", "pai", "acao", "g")

    def __init__(self, estado, pai=None, acao=None, g=0):
        self.estado = estado    # a cidade
        self.pai = pai          # o nó anterior (None se for a raiz)
        self.acao = acao        # a ação aplicada no pai
        self.g = g              # custo acumulado desde o início

    def __repr__(self):
        # __repr__ define o que aparece quando imprimimos o objeto.
        # Sem ele, o Python mostraria algo como <__main__.No object at 0x7f...>.
        return f"No({self.estado}, g={self.g})"

    def __lt__(self, outro):
        # __lt__ define o operador "<". O heapq (fila de prioridade) precisa
        # dele para desempatar quando duas prioridades forem iguais.
        return self.g < outro.g


# Origem: Laboratório 2, célula 14 (índice começando em zero).
def reconstruir_caminho(no):
    """Devolve a lista de estados da raiz até o nó recebido.

    Parâmetro:
        no (No): o nó final, normalmente o que satisfez o teste de objetivo.

    Devolve:
        list: as cidades em ordem, do início até o nó.
    """
    caminho = []                    # lista vazia para acumular os estados

    while no is not None:           # "is not None" para quando chegar na raiz
        caminho.append(no.estado)   # anota o estado do nó atual
        no = no.pai                 # sobe um nível na cadeia

    # Neste ponto a lista está de TRÁS PARA FRENTE: [Pitesti, ..., Arad].
    # A fatia [::-1] percorre a lista de ré e devolve uma cópia invertida.
    return caminho[::-1]


# Origem: Laboratório 2, célula 8 (índice começando em zero).
def custo_do_caminho(mapa, caminho):
    """Soma os custos de passo ao longo de uma lista de estados.

    Parâmetro:
        caminho (list): lista de estados em ordem, ex. ["Arad", "Sibiu"].

    Devolve:
        int: o custo total do caminho, em unidades do mapa (metros no campus).
    """
    # TODO 1 resolvido: soma de todos os pares consecutivos.
    if caminho is None:
        return None
    return sum(mapa[a][b] for a, b in zip(caminho, caminho[1:]))


# Origem: Laboratório 2, célula 25 (índice começando em zero).
def busca_profundidade(mapa, inicio, objetivo):
    """Busca em profundidade em grafo. Não é ótima — e é esse o ponto."""
    conferir_extremos(mapa, inicio, objetivo)
    pilha = [No(inicio)]
    explorados = set()
    ordem = []

    while pilha:
        no = pilha.pop()                     # retira o mais recente: pilha

        if no.estado == objetivo:
            return reconstruir_caminho(no), no.g, len(ordem), ordem

        if no.estado in explorados:
            continue

        explorados.add(no.estado)
        ordem.append(no.estado)

        for vizinho, custo in mapa[no.estado].items():
            if vizinho not in explorados:
                pilha.append(No(vizinho, pai=no, acao=vizinho, g=no.g + custo))

    return None, None, len(ordem), ordem


# Origem: Laboratório 2, célula 17 (índice começando em zero).
def busca_largura(mapa, inicio, objetivo):
    """Busca em largura em grafo.

    Parâmetros:
        inicio (str): estado de partida.
        objetivo (str): estado de destino.

    Devolve:
        tuple: (caminho, custo, nós expandidos, ordem de expansão).
    """
    conferir_extremos(mapa, inicio, objetivo)
    fronteira = deque([No(inicio)])   # a fronteira começa com o nó inicial
    explorados = set()                # conjunto: consulta imediata
    na_fronteira = {inicio}           # espelho da fronteira, para consulta rápida
    ordem = []                        # registra a ordem das expansões

    while fronteira:                  # enquanto houver nós para examinar
        no = fronteira.popleft()      # retira o mais antigo: regra da fila
        na_fronteira.discard(no.estado)

        # Teste de objetivo NA REMOÇÃO, conforme a convenção da disciplina.
        if no.estado == objetivo:
            return reconstruir_caminho(no), no.g, len(ordem), ordem

        explorados.add(no.estado)     # marca como já expandido
        ordem.append(no.estado)

        for vizinho, custo in mapa[no.estado].items():
            if vizinho in explorados or vizinho in na_fronteira:
                continue              # já visto: ignora e vai para o próximo

            filho = No(vizinho, pai=no, acao=vizinho, g=no.g + custo)

            # Lacuna do laboratório resolvida: inserção na fronteira.
            fronteira.append(filho)

            na_fronteira.add(vizinho)

    return None, None, len(ordem), ordem


# Origem: Laboratório 2, célula 21 (índice começando em zero).
def busca_custo_uniforme(mapa, inicio, objetivo):
    """Expande sempre o nó de menor custo acumulado g(n).

    Parâmetros:
        inicio (str): estado de partida.
        objetivo (str): estado de destino.

    Devolve:
        tuple: (caminho, custo, nós expandidos, ordem de expansão).
    """
    conferir_extremos(mapa, inicio, objetivo)
    contador = itertools.count()      # gera 0, 1, 2, 3... para desempate
    fronteira = []
    heapq.heappush(fronteira, (0, next(contador), No(inicio)))
    explorados = set()
    ordem = []

    while fronteira:
        # heappop devolve a tupla inteira; "_" marca o que não vamos usar.
        _, _, no = heapq.heappop(fronteira)

        if no.estado == objetivo:
            return reconstruir_caminho(no), no.g, len(ordem), ordem

        # Um mesmo estado pode ter entrado várias vezes com custos diferentes.
        # Se já expandimos este estado, esta cópia é obsoleta: descartamos.
        if no.estado in explorados:
            continue

        explorados.add(no.estado)
        ordem.append(no.estado)

        for vizinho, custo in mapa[no.estado].items():
            if vizinho in explorados:
                continue

            filho = No(vizinho, pai=no, acao=vizinho, g=no.g + custo)

            # Lacuna do laboratório resolvida: inserção na fronteira.
            heapq.heappush(fronteira, (filho.g, next(contador), filho))

    return None, None, len(ordem), ordem


# Origem: Laboratório 2, célula 31 (índice começando em zero).
def busca_gulosa(mapa, inicio, objetivo, h):
    """Ordena a fronteira apenas pela estimativa h(n)."""
    conferir_extremos(mapa, inicio, objetivo)
    contador = itertools.count()
    fronteira = []
    heapq.heappush(fronteira, (h[inicio], next(contador), No(inicio)))
    explorados = set()
    ordem = []

    while fronteira:
        _, _, no = heapq.heappop(fronteira)

        if no.estado == objetivo:
            return reconstruir_caminho(no), no.g, len(ordem), ordem

        if no.estado in explorados:
            continue

        explorados.add(no.estado)
        ordem.append(no.estado)

        for vizinho, custo in mapa[no.estado].items():
            if vizinho in explorados:
                continue
            filho = No(vizinho, pai=no, acao=vizinho, g=no.g + custo)
            # A prioridade é SÓ a heurística: o passado é ignorado.
            heapq.heappush(fronteira, (h[vizinho], next(contador), filho))

    return None, None, len(ordem), ordem


# Origem: Laboratório 2, célula 35 (índice começando em zero).
def a_estrela(mapa, inicio, objetivo, h):
    """Ordena a fronteira por f(n) = g(n) + h(n).

    Parâmetros:
        inicio (str): estado de partida.
        objetivo (str): estado de destino.
        h (dict): a função heurística, como dicionário estado -> estimativa.

    Devolve:
        tuple: (caminho, custo, nós expandidos, ordem de expansão).
    """
    conferir_extremos(mapa, inicio, objetivo)
    contador = itertools.count()
    fronteira = []
    heapq.heappush(fronteira, (h[inicio], next(contador), No(inicio)))
    explorados = set()
    ordem = []

    while fronteira:
        _, _, no = heapq.heappop(fronteira)

        if no.estado == objetivo:
            return reconstruir_caminho(no), no.g, len(ordem), ordem

        if no.estado in explorados:
            continue

        explorados.add(no.estado)
        ordem.append(no.estado)

        for vizinho, custo in mapa[no.estado].items():
            if vizinho in explorados:
                continue

            filho = No(vizinho, pai=no, acao=vizinho, g=no.g + custo)

            # Lacuna do laboratório resolvida: inserção na fronteira.
            heapq.heappush(fronteira, (filho.g + h[vizinho], next(contador), filho))

    return None, None, len(ordem), ordem
