"""Mapas de falha explícitos: o campus ampliado já não tem interiores isolados."""
import copy
from planejamento import resolver_alvo


def isolar_destino(grade, destino='H01'):
    g = copy.copy(grade)
    z, _ = resolver_alvo(g, destino)
    g.grafo = {n: {v: custo for v, custo in vs.items() if v != z}
               for n, vs in grade.grafo.items()}
    g.grafo[z] = {}
    return g
