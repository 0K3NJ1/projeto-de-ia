"""Interface de planejamento compartilhada pelo Webots e pelo Colab (Python puro)."""
import math
import re
import unicodedata
from time import perf_counter_ns

import buscas

ALGORITMOS = (
    ("Profundidade", buscas.busca_profundidade, False),
    ("Largura", buscas.busca_largura, False),
    ("Custo uniforme", buscas.busca_custo_uniforme, False),
    ("Gulosa", buscas.busca_gulosa, True),
    ("A*", buscas.a_estrela, True),
)


def normalizar_nome(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto.upper()) if c.isalnum())


def alvo_do_clique(grade, x, y, selecionar_setor=True):
    """Destino: clique no interior/nome do bloco escolhe seu centro cadastrado.

    Fora dos setores (ou ao definir origem), preserva a seleção de célula.
    A faixa ocupada pelas paredes não é interpretada como clique no interior.
    """
    if not all(math.isfinite(v) for v in (x, y)):
        raise ValueError('Clique sem posição válida no piso.')
    if selecionar_setor:
        t = grade.config.paredes_padrao['espessura']/2
        destinos = getattr(grade.config, 'destinos_setores', {})
        for setor in grade.config.setores:
            cx, cy = setor['centro']
            w, d = setor['tamanho']
            if abs(x-cx) < w/2-t and abs(y-cy) < d/2-t and setor['id'] in destinos:
                return destinos[setor['id']]
    return grade.mundo_para_celula(x, y)


def resolver_alvo(grade, texto):
    """Aceita H01, Bloco H, H, nome de setor, DEF ou célula; valida sem aproximar parede."""
    valor = texto.strip().upper().replace(" ", "")
    aliases = {normalizar_nome(nome): ident for ident, nome in grade.config.nomes.items()}
    for setor, ident in getattr(grade.config, 'destinos_setores', {}).items():
        aliases[normalizar_nome(setor)] = ident
        if setor.startswith('BLOCO_'):
            aliases[setor[-1]] = ident
    if valor not in grade.config.pontos:
        valor = aliases.get(normalizar_nome(texto), valor)
    if valor in grade.config.pontos:
        ponto = grade.config.pontos[valor]
        ident = grade.associacoes[valor]["celula"]
        if ident is None:
            raise ValueError(f"Local {valor} sem associação segura")
        return ident, ponto
    match = re.fullmatch(r"(?:CEL_)?C(\d+)_?L(\d+)", valor) or re.fullmatch(r"(\d+),(\d+)", valor)
    if not match:
        raise ValueError("Use Bloco H, H01, Biblioteca ou uma célula como C29L25")
    ident = grade.id_celula(*map(int, match.groups()))
    if ident not in grade.celulas:
        raise ValueError("Célula fora da grade")
    if ident not in grade.grafo:
        raise ValueError(f"{ident}: centro bloqueado para o carrinho")
    return ident, grade.celulas[ident].centro


def planejar(grade, posicao_inicial, destino, algoritmo=4):
    """Associa a posição atual e mede somente a busca; não movimenta motores.

    Destino é um texto aceito por resolver_alvo. Célula livre desconectada é um
    resultado válido sem solução; célula bloqueada ou posição insegura gera erro.
    """
    if not 0 <= algoritmo < len(ALGORITMOS):
        raise ValueError("Algoritmo deve ser um índice entre 0 e 4")
    if len(posicao_inicial) != 2 or not all(math.isfinite(v) for v in posicao_inicial):
        raise ValueError("Posição inicial inválida")
    # A associação já verifica o segmento desde a posição contínua do robô.
    origem = grade.associar(posicao_inicial)
    if origem["celula"] is None:
        raise ValueError("Posição atual sem centro acessível; defina outra origem com O")
    z, ponto_final = resolver_alvo(grade, destino)
    nome, funcao, usa_h = ALGORITMOS[algoritmo]
    a = origem["celula"]
    args = (grade.grafo, a, z) + ((grade.heuristica(z),) if usa_h else ())
    inicio = perf_counter_ns()
    caminho, custo, expandidos, ordem = funcao(*args)
    tempo_ms = (perf_counter_ns()-inicio)/1e6
    assert custo == buscas.custo_do_caminho(grade.grafo, caminho)
    conectores = origem["distancia_m"]+math.dist(ponto_final, grade.celulas[z].centro)
    if tuple(posicao_inicial) == tuple(ponto_final):
        conectores = 0.0
    return {"algoritmo": nome, "origem": a, "destino": z,
            "posicao_inicial": tuple(posicao_inicial), "ponto_final": tuple(ponto_final),
            "caminho": caminho, "custo_m": custo, "expandidos": expandidos,
            "ordem": ordem, "tempo_ms": tempo_ms, "conectores_m": conectores,
            "percurso_total_m": None if custo is None else custo+conectores}


def planejar_multiparadas(grade, posicao_inicial, lista_destinos, algoritmo=4):
    """Planeja percurso sequencial passando por múltiplos destinos sucessivos.

    Exemplo: lista_destinos=['CANTINA', 'H01', 'EXT01']
    Devolve resultado unificado compatível com a navegação do carrinho.
    """
    if not lista_destinos:
        raise ValueError("Lista de destinos não pode ser vazia")
    pos_atual = tuple(posicao_inicial)
    caminho_total = []
    ordem_total = []
    custo_total = 0.0
    expandidos_total = 0
    tempo_total_ms = 0.0
    conectores_total = 0.0
    trechos = []

    for dest in lista_destinos:
        r = planejar(grade, pos_atual, dest, algoritmo)
        if r["caminho"] is None:
            return {"algoritmo": r["algoritmo"], "origem": r["origem"], "destino": dest,
                    "posicao_inicial": tuple(posicao_inicial), "ponto_final": r["ponto_final"],
                    "caminho": None, "custo_m": None, "expandidos": expandidos_total + r["expandidos"],
                    "ordem": ordem_total + r["ordem"], "tempo_ms": tempo_total_ms + r["tempo_ms"],
                    "conectores_m": None, "percurso_total_m": None, "trechos": trechos}
        trechos.append(r)
        if not caminho_total:
            caminho_total.extend(r["caminho"])
        else:
            if r["caminho"] and caminho_total[-1] == r["caminho"][0]:
                caminho_total.extend(r["caminho"][1:])
            else:
                caminho_total.extend(r["caminho"])
        ordem_total.extend(r["ordem"])
        custo_total += r["custo_m"]
        expandidos_total += r["expandidos"]
        tempo_total_ms += r["tempo_ms"]
        conectores_total += r["conectores_m"]
        pos_atual = r["ponto_final"]

    ponto_final = trechos[-1]["ponto_final"]
    return {
        "algoritmo": trechos[0]["algoritmo"],
        "origem": trechos[0]["origem"],
        "destino": trechos[-1]["destino"],
        "destinos_intermediarios": list(lista_destinos),
        "posicao_inicial": tuple(posicao_inicial),
        "ponto_final": ponto_final,
        "caminho": caminho_total,
        "custo_m": custo_total,
        "expandidos": expandidos_total,
        "ordem": ordem_total,
        "tempo_ms": tempo_total_ms,
        "conectores_m": conectores_total,
        "percurso_total_m": custo_total + conectores_total,
        "trechos": trechos,
    }
