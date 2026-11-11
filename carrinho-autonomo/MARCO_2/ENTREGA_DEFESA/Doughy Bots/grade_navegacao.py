"""Grade de estados do campus: geometria conhecida, sem sensores ou motores.

Cada célula descreve uma posição de referência (seu centro). Livre não significa
que todo o quadrado está vazio: significa que o carrinho cabe no centro. Arestas
também são verificadas, usando obstáculos expandidos por uma margem conservadora.
"""

import math
from dataclasses import dataclass

import campus_config as cfg
from gerar_campus import validar, restricoes_circulacao


@dataclass(frozen=True)
class Celula:
    id: str
    coluna: int
    linha: int
    centro: tuple
    bloqueios: tuple

    @property
    def livre(self):
        return not self.bloqueios


def segmento_intercepta_retangulo(a, b, limites):
    """Recorte paramétrico exato: contato com a borda também conta como colisão."""
    entrada, saida = 0.0, 1.0
    for eixo, (menor, maior) in enumerate((limites[:2], limites[2:])):
        delta = b[eixo] - a[eixo]
        if abs(delta) < 1e-12:
            if a[eixo] < menor or a[eixo] > maior:
                return False
        else:
            t1, t2 = sorted(((menor-a[eixo])/delta, (maior-a[eixo])/delta))
            entrada, saida = max(entrada, t1), min(saida, t2)
            if entrada > saida:
                return False
    return True


class Grade:
    def __init__(self, config=cfg):
        self.config = config
        self.caixas_fisicas = validar(config)
        self.caixas = self.caixas_fisicas + restricoes_circulacao(config)
        self.passo = config.grade["passo"]
        if not math.isfinite(self.passo) or self.passo <= 0:
            raise ValueError("Passo da grade deve ser positivo e finito")
        self.raio = math.hypot(.12, .1125)*config.robo["escala"] + config.folga_robo
        self.piso = config.piso
        self.retangulos = []
        for caixa in self.caixas:
            x, y = caixa["centro"]
            w, d, _ = caixa["tamanho"]
            self.retangulos.append((caixa["id"], (x-w/2-self.raio, x+w/2+self.raio,
                                                     y-d/2-self.raio, y+d/2+self.raio)))
        nx = (self.piso["x_max"]-self.piso["x_min"])/self.passo
        ny = (self.piso["y_max"]-self.piso["y_min"])/self.passo
        if not (math.isclose(nx, round(nx)) and math.isclose(ny, round(ny))):
            raise ValueError("O piso deve conter um número inteiro de células")
        self.colunas, self.linhas = round(nx), round(ny)
        self.celulas = {}
        for linha in range(self.linhas):
            for coluna in range(self.colunas):
                centro = (self.piso["x_min"]+(coluna+.5)*self.passo,
                          self.piso["y_min"]+(linha+.5)*self.passo)
                ident = self.id_celula(coluna, linha)
                self.celulas[ident] = Celula(ident, coluna, linha, centro,
                                            tuple(self.bloqueios_segmento(centro, centro)))
        self.grafo = {c.id: {} for c in self.celulas.values() if c.livre}
        # Ordem fixa: +X, +Y, -X, -Y. A pilha da profundidade retira o último.
        for ident in self.grafo:
            c = self.celulas[ident]
            for dc, dl in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                outro = self.id_celula(c.coluna+dc, c.linha+dl)
                if outro in self.grafo:
                    destino = self.celulas[outro].centro
                    if self.segmento_livre(c.centro, destino):
                        self.grafo[ident][outro] = math.dist(c.centro, destino)
        self.componentes = {}
        for ident in self.grafo:
            if ident in self.componentes:
                continue
            numero = len(set(self.componentes.values()))
            pendentes = [ident]
            self.componentes[ident] = numero
            while pendentes:
                for vizinho in self.grafo[pendentes.pop()]:
                    if vizinho not in self.componentes:
                        self.componentes[vizinho] = numero
                        pendentes.append(vizinho)
        self.associacoes = {ident: self.associar(ponto) for ident, ponto in config.pontos.items()}

    @staticmethod
    def id_celula(coluna, linha):
        return f"CEL_C{coluna:02d}_L{linha:02d}"

    def mundo_para_celula(self, x, y):
        """Célula que contém o ponto; limites superiores do piso são exclusivos."""
        p = self.piso
        if not (p["x_min"] <= x < p["x_max"] and p["y_min"] <= y < p["y_max"]):
            raise ValueError("Coordenada fora da grade")
        return self.id_celula(math.floor((x-p["x_min"])/self.passo),
                              math.floor((y-p["y_min"])/self.passo))

    def bloqueios_segmento(self, a, b):
        p, r = self.piso, self.raio
        if any(not (p["x_min"]+r <= x <= p["x_max"]-r and
                    p["y_min"]+r <= y <= p["y_max"]-r) for x, y in (a, b)):
            yield "BORDA_PISO"
        for ident, limites in self.retangulos:
            if segmento_intercepta_retangulo(a, b, limites):
                yield ident

    def segmento_livre(self, a, b):
        return not any(self.bloqueios_segmento(a, b))

    def associar(self, ponto):
        """Centro livre mais próximo com conector seguro; nunca atravessa paredes.

        O conector não é uma aresta da grade. Seu comprimento é informado à parte.
        Empates: coluna e depois linha. Não escolhe componente para ocultar falhas.
        """
        limite = self.config.grade["distancia_max_associacao"]
        if not math.isfinite(limite) or limite < 0:
            raise ValueError("Limite de associação deve ser finito e não negativo")
        # Distâncias iguais a 1 nanômetro usam o ID como desempate. Isso evita
        # trocar de célula por ruído de ponto flutuante do simulador (ex.: 1e-15 m).
        candidatos = sorted(((math.dist(ponto, c.centro), c.id) for c in self.celulas.values()
                             if c.livre and math.dist(ponto, c.centro) <= limite),
                            key=lambda item: (round(item[0], 9), item[1]))
        for distancia, ident in candidatos:
            if self.segmento_livre(ponto, self.celulas[ident].centro):
                return {"celula": ident, "distancia_m": distancia,
                        "componente": self.componentes[ident]}
        return {"celula": None, "distancia_m": None, "componente": None}

    def heuristica(self, destino, grafo=None):
        """Manhattan em metros: admissível e consistente para quatro vizinhos."""
        x, y = self.celulas[destino].centro
        return {ident: abs(c.centro[0]-x)+abs(c.centro[1]-y)
                for ident in (self.grafo if grafo is None else grafo)
                for c in (self.celulas[ident],)}

    def recorte(self, limites):
        """Subgrafo induzido: borda do recorte limita a busca, não cria parede física."""
        xa, xb, ya, yb = limites
        ids = {n for n in self.grafo if xa <= self.celulas[n].centro[0] < xb
               and ya <= self.celulas[n].centro[1] < yb}
        return {n: {v: c for v, c in vs.items() if v in ids}
                for n, vs in self.grafo.items() if n in ids}
