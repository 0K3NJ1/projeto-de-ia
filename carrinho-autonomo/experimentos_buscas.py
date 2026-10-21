"""Mede as buscas e gera evidências reproduzíveis; não aciona os motores."""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
from html import escape
import json
from pathlib import Path
import platform
import statistics
from time import perf_counter_ns

import buscas as b
import campus_config as cfg
from grade_navegacao import Grade

ALGORITMOS = [
    ("Profundidade", b.busca_profundidade, False, "#9a6700"),
    ("Largura", b.busca_largura, False, "#1e4e79"),
    ("Custo uniforme", b.busca_custo_uniforme, False, "#1b7f5a"),
    ("Gulosa", b.busca_gulosa, True, "#5a6570"),
    ("A*", b.a_estrela, True, "#c8102e"),
]
RAIZ = Path(__file__).resolve().parent


def salvar_csv(caminho, linhas):
    with caminho.open("w", encoding="utf-8-sig", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=list(linhas[0]))
        escritor.writeheader()
        escritor.writerows(linhas)


def medir(g, mapa, origem, destino, repeticoes):
    """Uma passagem de aquecimento; amostras individuais em ordem alternada."""
    b.validar_grafo(mapa)
    a, z = g.associacoes[origem]["celula"], g.associacoes[destino]["celula"]
    if a not in mapa or z not in mapa:
        raise ValueError("Local sem associação livre dentro deste mapa")
    h = g.heuristica(z, mapa)
    resultados, amostras = {}, {nome: [] for nome, *_ in ALGORITMOS}
    for rodada in range(repeticoes+1):
        ordem = ALGORITMOS[rodada % 5:] + ALGORITMOS[:rodada % 5]
        for nome, funcao, usa_h, _ in ordem:
            args = (mapa, a, z) + ((h,) if usa_h else ())
            inicio = perf_counter_ns()
            resultado = funcao(*args)
            tempo = (perf_counter_ns()-inicio)/1e6
            if rodada:
                amostras[nome].append(tempo)
            if nome in resultados and resultado != resultados[nome]:
                raise AssertionError("Busca não determinística")
            resultados[nome] = resultado
    linhas, detalhes = [], {}
    otimo = resultados["Custo uniforme"][1]
    for nome, _, _, _ in ALGORITMOS:
        caminho, custo, expandidos, ordem = resultados[nome]
        assert custo == b.custo_do_caminho(mapa, caminho)
        if nome in ("Largura", "A*"):
            assert custo == otimo
        conectores = (0 if origem == destino else
                      g.associacoes[origem]["distancia_m"]+g.associacoes[destino]["distancia_m"])
        quartis = statistics.quantiles(amostras[nome], n=4, method="inclusive")
        linhas.append({"algoritmo": nome, "origem": origem, "destino": destino,
                       "nos_grafo": len(mapa), "arestas": sum(map(len, mapa.values()))//2,
                       "encontrou": caminho is not None, "custo_grade_m": custo,
                       "conectores_m": conectores,
                       "percurso_com_conectores_m": None if custo is None else custo+conectores,
                       "nos_expandidos": expandidos, "tempo_mediana_ms": statistics.median(amostras[nome]),
                       "tempo_p25_ms": quartis[0], "tempo_p75_ms": quartis[2],
                       "repeticoes": repeticoes})
        detalhes[nome] = {"caminho": caminho, "ordem_expansao": ordem, "tempos_ms": amostras[nome]}
    return linhas, detalhes


def desenhar_mapa(g, mapa, limites, caminho=None, ordem=None, titulo="Grade navegável", ids=False, locais=None):
    """Mesmo papel de desenhar_mapa do laboratório: rota e ordem de expansão."""
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Patch
    xa, xb, ya, yb = limites
    fig, ax = plt.subplots(figsize=(15, 12), layout="constrained")
    componente = g.associacoes[cfg.robo["ponto_inicial"]]["componente"]
    for celula in g.celulas.values():
        x, y = celula.centro
        if not (xa <= x < xb and ya <= y < yb):
            continue
        cor = "#f0d8d8" if not celula.livre else (
            "#fae5aa" if g.componentes[celula.id] != componente else "#e1f0e8")
        ax.add_patch(Rectangle((x-.5*g.passo, y-.5*g.passo), g.passo, g.passo,
                               facecolor=cor, edgecolor="white", lw=.5, zorder=0))
        if ids:
            ax.text(x, y-.22, f"C{celula.coluna:02d}\nL{celula.linha:02d}",
                    ha="center", va="center", fontsize=5, color="#384149", zorder=3)
    for caixa in g.caixas:
        x, y = caixa["centro"]
        w, d, _ = caixa["tamanho"]
        ax.add_patch(Rectangle((x-w/2, y-d/2), w, d, color="#53616d", zorder=2))
    if ordem:
        xs, ys = zip(*(g.celulas[n].centro for n in ordem))
        pontos = ax.scatter(xs, ys, c=range(1, len(ordem)+1), cmap="Blues", s=38, zorder=4,
                            vmin=0, vmax=max(1,len(ordem)))
        fig.colorbar(pontos, ax=ax, shrink=.6, label="Ordem de expansão (objetivo excluído)")
        if len(ordem) <= 100:
            for i, n in enumerate(ordem, 1):
                ax.text(*g.celulas[n].centro, str(i), fontsize=5, ha="center", va="center",
                        color="white" if i > len(ordem)*.45 else "black", zorder=8)
    if caminho:
        xs, ys = zip(*(g.celulas[n].centro for n in caminho))
        ax.plot(xs, ys, color="#c8102e", lw=2.5, zorder=6)
        ax.scatter([xs[0], xs[-1]], [ys[0], ys[-1]], c=["#107b4f", "#c8102e"], s=75, zorder=7)
        if locais:
            for local, no in zip(locais, (caminho[0], caminho[-1])):
                px, py = cfg.pontos[local]
                nx, ny = g.celulas[no].centro
                ax.plot([px, nx], [py, ny], color="#6d3290", ls="--", lw=1.8, zorder=7)
    for nome, (x, y) in cfg.pontos.items():
        if xa <= x < xb and ya <= y < yb:
            ax.scatter([x], [y], s=12, color="#242c33", zorder=7)
            ax.annotate(nome, (x, y), (4, 5), textcoords="offset points", fontsize=7, zorder=8,
                        bbox={"facecolor": "white", "edgecolor": "none", "alpha": .85, "pad": 1})
    ax.set(xlim=(xa, xb), ylim=(ya, yb), xlabel="X (m)", ylabel="Y (m)", aspect="equal", title=titulo)
    ax.legend(handles=[Patch(color="#e1f0e8", label="Centro livre conectado à entrada"),
                       Patch(color="#f0d8d8", label="Centro bloqueado pela margem"),
                       Patch(color="#fae5aa", label="Centro livre isolado"),
                       Patch(color="#53616d", label="Parede ou banco")],
              loc="upper center", bbox_to_anchor=(.5, -.065), ncol=2, fontsize=8)
    return fig


def executar(saida, repeticoes=31, origem="EXT01", destino="H01"):
    if repeticoes < 2:
        raise ValueError("Use pelo menos duas repetições")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    saida = Path(saida)
    saida.mkdir(parents=True, exist_ok=True)
    g = Grade()
    if origem not in g.associacoes or destino not in g.associacoes:
        raise ValueError("Escolha um dos locais cadastrados em campus_config.py")
    p = cfg.piso
    completo = (p["x_min"], p["x_max"], p["y_min"], p["y_max"])
    cenarios = [("pequeno", (-5, 5, -2, 6), "EXT01", "EXT04"),
                ("medio", (-16, 16, -2, 17), "EXT01", "CAN01"),
                ("campus", completo, origem, destino)]
    todas, registros = [], {}
    for nome, limites, a, z in cenarios:
        mapa = g.recorte(limites)
        linhas, detalhes = medir(g, mapa, a, z, repeticoes)
        for linha in linhas:
            todas.append({"mapa": nome, **linha})
        registros[nome] = {"limites": limites, "resultados": detalhes}
        for indice, linha in enumerate(linhas):
            algoritmo = linha["algoritmo"]
            resultado = detalhes[algoritmo]
            titulo = (f"{nome.capitalize()} | {a} → {z} | {algoritmo}\n"
                      f"Custo na grade: {linha['custo_grade_m']} m | {linha['nos_expandidos']} expansões")
            fig = desenhar_mapa(g, mapa, limites, resultado["caminho"], resultado["ordem_expansao"],
                               titulo+"\nTracejado roxo: conectores fora do custo da grade", locais=(a, z))
            fig.savefig(saida / f"rota_{nome}_{indice}.png", dpi=140)
            plt.close(fig)
    fig = desenhar_mapa(g, g.grafo, completo, ids=True,
                       titulo="Campus provisório | células de 1 × 1 m | DEF: CEL_Cxx_Lyy")
    fig.savefig(saida / "grade_identificada.png", dpi=180)
    plt.close(fig)
    fig, eixos = plt.subplots(3, 3, figsize=(16, 12), layout="constrained")
    for i, (nome, *_resto) in enumerate(cenarios):
        linhas = [r for r in todas if r["mapa"] == nome]
        for j, (chave, titulo) in enumerate((("custo_grade_m", "Distância na grade (m)"),
                                             ("nos_expandidos", "Nós expandidos"),
                                             ("tempo_mediana_ms", "Tempo de busca (ms): mediana e IQR"))):
            ax = eixos[i][j]
            valores = [r[chave] if r[chave] is not None else 0 for r in linhas]
            barras = ax.bar(range(5), valores, color=[c for *_, c in ALGORITMOS])
            ax.set_xticks(range(5), ["Prof.", "Larg.", "Uniforme", "Gulosa", "A*"])
            ax.set_title(f"{nome.capitalize()} · {linhas[0]['nos_grafo']} nós\n{titulo}", fontsize=10)
            if j != 2:
                ax.bar_label(barras, labels=["sem rota" if r[chave] is None else f"{r[chave]:.3g}" for r in linhas], padding=4, fontsize=9)
            ax.margins(y=.2)
            if j == 2:
                ax.errorbar(range(5), valores, yerr=([r[chave]-r["tempo_p25_ms"] for r in linhas],
                                                   [r["tempo_p75_ms"]-r[chave] for r in linhas]),
                            fmt="none", ecolor="#202830", capsize=4)
                for indice, r in enumerate(linhas):
                    ax.annotate(f"{r[chave]:.3g}", (indice, r["tempo_p75_ms"]), (0, 5),
                                textcoords="offset points", ha="center", fontsize=9)
            ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle(f"Cinco buscas · três recortes do campus · {repeticoes} repetições por caso\n"
                 "Custo exclui conectores; tempo exclui grade, heurística e gráficos", fontsize=14)
    fig.savefig(saida / "comparacao.png", dpi=150)
    plt.close(fig)
    salvar_csv(saida / "comparacao.csv", todas)
    associacoes = []
    for ident, a in g.associacoes.items():
        associacoes.append({"local": ident, "nome": cfg.nomes[ident],
                            "celula_contem_ponto": g.mundo_para_celula(*cfg.pontos[ident]), **a,
                            "acessivel_desde_entrada": a["componente"] is not None and
                            a["componente"] == g.associacoes["EXT01"]["componente"]})
    salvar_csv(saida / "associacoes.csv", associacoes)
    salvar_csv(saida / "celulas.csv", [{"id": c.id, "coluna": c.coluna, "linha": c.linha,
                "x_m": c.centro[0], "y_m": c.centro[1], "livre": c.livre,
                "componente": g.componentes.get(c.id), "bloqueios": ";".join(c.bloqueios)} for c in g.celulas.values()])
    fontes = ["campus_config.py", "gerar_campus.py", "grade_navegacao.py", "buscas.py", "experimentos_buscas.py",
              "controllers/carrinho_manual/carrinho_manual.py", "referencias_academicas/laboratorio_2_aula03_busca.ipynb"]
    metadados = {"data_utc": datetime.now(timezone.utc).isoformat(), "python": platform.python_version(),
                 "plataforma": platform.platform(), "raio_m": g.raio,
                 "celulas": len(g.celulas), "livres": len(g.grafo), "componentes": len(set(g.componentes.values())),
                 "fontes_sha256": {f: hashlib.sha256((RAIZ/f).read_bytes()).hexdigest() for f in fontes},
                 "medicao": "perf_counter_ns; 1 aquecimento; ordem rotativa; sem grade/heurística/gráfico",
                 "cenarios": registros}
    (saida / "resultados.json").write_text(json.dumps(metadados, ensure_ascii=False, indent=2), encoding="utf-8")
    (saida / "grafo.json").write_text(json.dumps(g.grafo, indent=2), encoding="utf-8")
    partes = ['''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>Buscas no campus</title>
<style>body{font:16px system-ui;max-width:1200px;margin:40px auto;padding:0 24px;color:#24343d;background:#fafbfc}
img{width:100%;height:auto;background:white}table{border-collapse:collapse;font-size:14px}td,th{padding:8px;border-bottom:1px solid #ddd;text-align:left}
summary{cursor:pointer;padding:15px;background:#e1f0e8;margin-top:12px}a{color:#075b78}</style>
<h1>Buscas no campus provisório</h1><p>Grade de 1 × 1 metro. Planejamento de rota; o controlador continua manual.</p>
<p>Verde: centro livre conectado à entrada. Vermelho claro: centro bloqueado pela margem.
Amarelo: livre, mas isolado. As paredes físicas estão em cinza.</p>''']
    partes.append(f"<p>{len(g.celulas)} células · {len(g.grafo)} livres · {sum(map(len,g.grafo.values()))//2} arestas · raio conservador {g.raio:.3f} m.</p>")
    partes.append('<img src="grade_identificada.png" alt="Grade com IDs e ocupação"><h2>Comparação medida</h2><img src="comparacao.png" alt="Custo, expansões e tempo em três mapas">')
    partes.append("<p>As barras de tempo mostram mediana e intervalo interquartil. Tempos pequenos variam com o computador. Largura e custo uniforme têm o mesmo custo porque cada aresta mede 1 m. Os mapas são recortes do mesmo cenário, não três plantas independentes.</p>")
    partes.append("<h2>Referências e centros associados</h2><table><tr><th>Local</th><th>DEF da célula associada</th><th>Conector (m)</th></tr>")
    for a in associacoes:
        distancia = "sem associação" if a["distancia_m"] is None else f"{a['distancia_m']:.3f}"
        partes.append(f"<tr><td>{escape(a['local']+' — '+a['nome'])}</td><td>{a['celula']}</td><td>{distancia}</td></tr>")
    partes.append("</table><p>A célula associada pode ser diferente daquela que contém o marcador. O conector reto foi validado e não integra o custo da grade. O CSV também informa o percurso com os dois conectores.</p>")
    partes.append("<p>Interiores inacessíveis desde a entrada nesta discretização: "+", ".join(s["nome"] for s in cfg.setores if g.associar(s["centro"])["componente"] != g.associacoes["EXT01"]["componente"])+". Os 18 marcadores são referências de acesso e continuam acessíveis.</p>")
    for nome, *_ in cenarios:
        partes.append(f"<h2>Rotas e expansões: {nome}</h2>")
        for i, (algoritmo, *_) in enumerate(ALGORITMOS):
            partes.append(f'<details><summary>{escape(algoritmo)}</summary><img src="rota_{nome}_{i}.png" alt="Rota e expansões de {escape(algoritmo)}"></details>')
    partes.append('<p>Dados: <a href="comparacao.csv">comparação</a> · <a href="associacoes.csv">associações</a> · <a href="celulas.csv">células</a> · <a href="grafo.json">grafo</a> · <a href="resultados.json">rotas, ordens, amostras e ambiente</a>.</p></html>')
    (saida / "index.html").write_text("\n".join(partes), encoding="utf-8")
    for r in todas:
        print(f"{r['mapa']:8} {r['algoritmo']:14} custo={str(r['custo_grade_m']):>6} m; expansões={r['nos_expandidos']:3}; mediana={r['tempo_mediana_ms']:.4f} ms")
    return todas


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saida", type=Path, default=RAIZ/"output/buscas")
    parser.add_argument("--repeticoes", type=int, default=31)
    parser.add_argument("--origem", default="EXT01")
    parser.add_argument("--destino", default="H01")
    args = parser.parse_args()
    executar(args.saida, args.repeticoes, args.origem, args.destino)
