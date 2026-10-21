"""Empacota somente o carrinho e gera um notebook didático de grade e buscas."""
import base64
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "colab"
files = [ROOT / name for name in (
    "campus_config.py", "gerar_campus.py", "grade_navegacao.py", "buscas.py", "planejamento.py", "navegacao.py",
    "adaptar_laboratorio2.py", "experimentos_buscas.py", "README.md", "README_ETAPA2.md",
    "README_ETAPA3.md", "GUIA_BUSCAS_WEBOTS.md", "VALIDACAO_ETAPA3.md", "README_NAVEGACAO.md",
    "VALIDACAO_NAVEGACAO.md", "CAMPUS_INTERIORES.md", "VALIDACAO_INTERIORES.md",
    "requirements-dev.txt", "colab/README.md",
    "referencias_academicas/laboratorio_2_aula03_busca.ipynb",
)]
for pattern in ("controllers/*/*.py", "protos/*.proto", "worlds/*.wbt",
                "worlds/textures/campus/*.png", "tests/*.py"):
    files.extend(sorted(ROOT.glob(pattern)))
archive = OUT / "Carrinho_IESB_Webots.zip"
with ZipFile(archive, "w", ZIP_DEFLATED) as z:
    for file in files:
        z.write(file, file.relative_to(ROOT).as_posix())
payload = base64.b64encode(archive.read_bytes()).decode("ascii")
digest = hashlib.sha256(archive.read_bytes()).hexdigest()
cells = []


def cell(kind, source):
    item = {"cell_type": kind, "metadata": {}, "source": source.splitlines(True),
            "id": f"iesb-{len(cells):02d}"}
    if kind == "code":
        item.update(execution_count=None, outputs=[])
    cells.append(item)


cell("markdown", """# Carrinho IESB — grade e buscas do Laboratório 2

Campus provisório ampliado de 50 × 30 m, células de 1 × 1 m e cinco buscas.
Os dez destinos dos setores ficam dentro dos blocos, nos seus centros.
Blocos de 6 × 6 m, setores laterais de 8 × 6 m e portas alinhadas de 2,40 m.
**Planejamento e seguimento automático implementados em Python no Webots.**
Localização ideal por Supervisor; controle manual preservado em seu mundo.
Execute todas as células em ordem, em sessão nova. O projeto está incorporado;
não exige Drive montado, chave de API ou GPU. Não é a planta oficial do campus.

Base didática: Laboratório 2 do Prof. Rodrigo Gonçalves Pinto. Quatro TODOs foram
completados na adaptação, mantendo `No`, pais, fronteira e explorados.
O anexo original foi preservado. Leia a fonte e explique as decisões com suas
próprias palavras. Declare o apoio de IA no desenvolvimento na entrega do grupo.
""")
cell("markdown", """## 1. Extrair o pacote

Reexecutar esta célula restaura os arquivos da versão incorporada. Salve suas
alterações antes. Não há download do código; as dependências são verificadas depois.
""")
cell("code", f'''import base64
import hashlib
import io
import sys
from pathlib import Path
from zipfile import ZipFile

pacote = base64.b64decode({payload!r})
assert hashlib.sha256(pacote).hexdigest() == {digest!r}
pasta = Path.cwd() / "carrinho_iesb_colab"
pasta.mkdir(exist_ok=True)
with ZipFile(io.BytesIO(pacote)) as arquivo:
    for item in arquivo.infolist():
        if not (pasta / item.filename).resolve().is_relative_to(pasta.resolve()):
            raise ValueError("Caminho fora da pasta do projeto")
    arquivo.extractall(pasta)
(Path.cwd() / "Carrinho_IESB_Webots.zip").write_bytes(pacote)
sys.path.insert(0, str(pasta))
print("Projeto extraído em:", pasta)
''')
cell("markdown", """## 2. Formulação e ocupação

Estado: ID do centro de uma célula livre. Ações: quatro vizinhos (+X, +Y, −X, −Y)
com segmento seguro. Transição: trocar o ID atual pelo vizinho. Objetivo: célula
igual ao destino. Custo: soma das distâncias entre centros (1 m por aresta).
Margem conservadora: raio de aproximadamente 0,543 m, incluindo 0,05 m de folga.
O segmento inteiro deve estar livre; não basta verificar apenas seus extremos.

Os 18 locais associam-se ao centro livre mais próximo com conector seguro até
1,5 m. A célula que contém o marcador pode ser diferente da célula associada.
Os conectores são informados separadamente do custo na grade.
""")
cell("code", '''import importlib
import campus_config, gerar_campus, grade_navegacao, buscas
# Recarrega na ordem das dependências após editar os arquivos.
for modulo in (campus_config, gerar_campus, grade_navegacao, buscas):
    importlib.reload(modulo)
cfg = campus_config
grade = grade_navegacao.Grade()
print(len(grade.celulas), "células;", len(grade.grafo), "centros livres;",
      sum(map(len, grade.grafo.values()))//2, "arestas")
for local, associacao in grade.associacoes.items():
    print(local, cfg.nomes[local], associacao)
print("Interiores desconectados da entrada:")
for setor in cfg.setores:
    if grade.associar(setor["centro"])["componente"] != grade.associacoes["EXT01"]["componente"]:
        print(" -", setor["nome"])
''')
cell("markdown", """## 3. Ler as buscas adaptadas

TODO 1: somar pares consecutivos. TODO 2: `append(filho)` na fila.
TODO 3: heap por `filho.g`. TODO 4: heap por `filho.g + h[vizinho]`.
Profundidade usa pilha; gulosa usa apenas h. O objetivo é testado na remoção
e não é contado como expandido. Empates no heap seguem a ordem de inserção.

A* mantém o conjunto fechado didático, portanto requer heurística **consistente**.
Manhattan `|Δx| + |Δy|` é admissível: sem diagonais, é necessário cobrir as duas
diferenças. É consistente: cada passo de 1 m reduz h em no máximo 1 m.
Obstáculos não diminuem o mínimo. HSLD da Romênia não é reutilizado no campus.
""")
cell("code", '''print((pasta / "buscas.py").read_text(encoding="utf-8"))
''')
cell("markdown", """## 4. Testar antes de comparar

Regressão dos valores da Romênia, origem=destino, ausência de rota, obstáculos,
conectividade, custo somado e A* versus custo uniforme nos 324 pares de locais.
""")
cell("code", '''import unittest
suite = unittest.defaultTestLoader.discover(str(pasta / "tests"))
resultado_testes = unittest.TextTestRunner(verbosity=2).run(suite)
assert resultado_testes.wasSuccessful(), "Corrija os testes antes de comparar"
''')
cell("markdown", """## 5. Planejar uma rota

Altere ORIGEM e DESTINO para referências cadastradas. O custo é entre centros
associados. Planejar o caminho não faz o carrinho percorrê-lo automaticamente.
""")
cell("code", '''ORIGEM, DESTINO = "EXT01", "H01"
a = grade.associacoes[ORIGEM]["celula"]
z = grade.associacoes[DESTINO]["celula"]
rota, custo, expandidos, ordem = buscas.a_estrela(grade.grafo, a, z, grade.heuristica(z))
print("Rota:", rota)
print("Custo na grade (m):", custo, "| Expansões:", expandidos)
assert custo == buscas.custo_do_caminho(grade.grafo, rota)
print("Ordem de expansão:", ordem)
''')
cell("markdown", """## 6. Comparar três mapas e desenhar

Três recortes do campus: 10 × 8, 32 × 19 e 50 × 30 m. Os pares dos dois menores
são fixos; o campus usa a escolha acima. Em cada mapa, os cinco algoritmos têm
as mesmas condições. São recortes de uma geometria, não três plantas independentes.

Medição: `perf_counter_ns`, um aquecimento e 31 amostras com ordem alternada.
Mediana e intervalo interquartil; exclui grade, preparação de h e gráficos.
Não é tempo de viagem, consumo de bateria ou autonomia.
""")
cell("code", '''import importlib.util
import subprocess
# Instala somente se o ambiente não fornecer a biblioteca de gráficos.
if importlib.util.find_spec("matplotlib") is None:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib>=3.8,<4"])
import experimentos_buscas
importlib.reload(experimentos_buscas)
saida = pasta / "output" / "buscas"
tabela = experimentos_buscas.executar(saida, 31, ORIGEM, DESTINO)
try:
    from IPython.display import Image, display
except ImportError:
    print("Fora do Colab/IPython: abra as imagens em", saida)
else:
    for imagem in ("comparacao.png", "rota_campus_4.png", "grade_identificada.png"):
        display(Image(filename=str(saida / imagem)))
''')
cell("markdown", """## 7. Interpretar e continuar

Largura e custo uniforme são ótimos aqui porque todos os passos custam 1 m.
Profundidade e gulosa podem encontrar rotas maiores. Compare custo, expansões e
tempo separadamente: pouca expansão não garante rota curta nem menos milissegundos.

Todos os interiores estão conectados à entrada na planta ampliada de 21/10/2026.
As portas foram alargadas/alinhadas sem reduzir o robô ou suas margens.
Os 18 locais incluem oito referências externas e dez destinos internos.
Veja `CAMPUS_INTERIORES.md`; as métricas dos documentos anteriores são históricas.

Os CSV/JSON e 15 mapas ficam em `carrinho_iesb_colab/output/buscas`. O JSON conserva
amostras e ordens. Baixe o ZIP da primeira célula e abra `worlds/etapa2_campus.wbt`
no Webots R2025a. Células na árvore: `GRADE_NAVEGACAO → LINHA_XX → CEL_CXX_LYY`.
Controle manual: W/S/A/D ou setas; soltar ou espaço para parar. O módulo
`controller` depende do Webots e não deve ser executado diretamente no Colab.

O Laboratório 1 sustenta a formulação e a comparação de desempenho. O Laboratório 3
trata dados faltantes, codificação, padronização e avaliação sem vazamento; será
pertinente a previsões futuras de tempo. Não há dados reais de bateria ou modelo treinado.

Antes de entregar: revisão do trio, análise própria, autoria/divisão reais,
relatório de 2–4 páginas e validação em sessão nova na nuvem do Colab.
Execução local não comprova execução na nuvem. Nada foi enviado ao professor.
""")
cell("markdown", """## 8. Escolher quadrados como no Webots

O mundo `worlds/etapa3_buscas.wbt` permite escolher destino com T, origem com O,
algoritmo com 1–5 e executar com Enter. G inicia a condução física, C pausa/retoma
e espaço para. Sem G, os motores permanecem parados. Digite Bloco H, H ou H01
para seu centro interno; T + clique dentro do setor também seleciona o centro.
O painel e as buscas são Python. O controlador manual também já era Python.
O arquivo físico `.proto` usa a linguagem de cena e um template JavaScript de escala.

A célula abaixo usa **a mesma função** do controlador, sem importar o Webots.
Edite a posição inicial e o ID do quadrado. Algoritmos: 0 profundidade, 1 largura,
2 custo uniforme, 3 gulosa e 4 A*. A janela 3D depende do Webots local; o Colab
executa planejamento e gráficos.
""")
cell("code", '''from planejamento import planejar
resultado_celula = planejar(grade, (0.0, 0.0), "Bloco H", algoritmo=4)
print("Célula inicial:", resultado_celula["origem"])
print("Destino:", resultado_celula["destino"])
print("Caminho:", resultado_celula["caminho"])
print("Custo (m):", resultado_celula["custo_m"], "| Expansões:", resultado_celula["expandidos"])
''')
cell("markdown", """## 9. Seguimento independente: demonstração cinemática

`navegacao.Seguidor` recebe pose (x, y, rumo) e tempo e devolve velocidades das
rodas. Abaixo, um modelo diferencial ideal integra esses comandos: não inclui
contato, atrito, deslizamento nem a física do Webots. Os ensaios físicos reais
do simulador estão documentados em `VALIDACAO_INTERIORES.md`.

No Webots, a pose vem do Supervisor e os comandos são enviados aos motores,
sem teleportes no seguimento. O Colab executa esta lógica e os testes puros;
não abre a janela 3D nem disponibiliza sensores reais.
""")
cell("code", '''import math
from navegacao import Seguidor
resultado_controle = planejar(grade, (-.5, -.5), "C25L02", algoritmo=4)
seguidor = Seguidor(grade)
pose = [-.5, -.5, 0.]
seguidor.iniciar(resultado_controle, pose, 0.)
dt = .032
for passo in range(1, 10000):
    esquerda, direita = seguidor.atualizar(pose, passo*dt)
    v = (esquerda+direita)*seguidor.raio_roda/2
    w = (direita-esquerda)*seguidor.raio_roda/seguidor.bitola
    pose[0] += v*math.cos(pose[2])*dt
    pose[1] += v*math.sin(pose[2])*dt
    pose[2] += w*dt
    if seguidor.estado not in seguidor.ATIVOS:
        break
assert seguidor.estado == "concluído", seguidor.motivo
assert seguidor.comando == (0., 0.)
print("Modelo ideal:", seguidor.estado, "| tempo:", round(seguidor.tempo_s, 3), "s")
print("Erro final:", math.dist(pose[:2], resultado_controle["ponto_final"]), "m")
''')
notebook = {"nbformat": 4, "nbformat_minor": 5, "cells": cells,
            "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                         "language_info": {"name": "python", "version": "3.12"},
                         "colab": {"name": "Carrinho_IESB_Base.ipynb", "provenance": []}}}
target = OUT / "Carrinho_IESB_Base.ipynb"
target.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"Criados: {target.name} e {archive.name}; {len(files)} arquivos no pacote.")
