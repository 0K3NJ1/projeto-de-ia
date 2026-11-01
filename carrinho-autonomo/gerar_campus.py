"""Gera os mundos da etapa 2 a partir de campus_config.py; não controla o robô."""

import argparse
import json
import math
from pathlib import Path
import re

import campus_config as cfg

RAIZ = Path(__file__).resolve().parent


def caixas_cenario(config=cfg):
    """Retângulos de colisão das paredes e blocos, também usados na validação."""
    caixas = []
    t, h = config.paredes_padrao["espessura"], config.paredes_padrao["altura"]

    def caixa(ident, centro, tamanho):
        caixas.append({"id": ident, "centro": centro, "tamanho": tamanho})

    def parede(ident, horizontal, fixo, inicio, fim):
        if fim <= inicio:
            raise ValueError(f"Parede {ident}: comprimento deve ser positivo")
        centro = ((inicio + fim) / 2, fixo) if horizontal else (fixo, (inicio + fim) / 2)
        tamanho = (fim - inicio, t, h) if horizontal else (t, fim - inicio, h)
        caixa(ident, centro, tamanho)

    p = config.piso
    xa, xb, ya, yb = (p[k] for k in ("x_min", "x_max", "y_min", "y_max"))
    entrada_x, entrada_l = config.entrada["centro_x"], config.entrada["largura"]
    if not (0 < entrada_l and xa < entrada_x - entrada_l/2 < entrada_x + entrada_l/2 < xb):
        raise ValueError("A entrada deve caber na borda do piso")
    lado_entrada = config.entrada.get("lado", "S")
    if lado_entrada not in ("N", "S"):
        raise ValueError("Lado da entrada deve ser N ou S")
    fechado, aberto = (yb-t/2, ya+t/2) if lado_entrada == "S" else (ya+t/2, yb-t/2)
    parede("LIMITE_"+("N" if lado_entrada == "S" else "S"), True, fechado, xa, xb)
    parede("LIMITE_O", False, xa+t/2, ya, yb)
    parede("LIMITE_L", False, xb-t/2, ya, yb)
    parede(f"LIMITE_{lado_entrada}_O", True, aberto, xa, entrada_x-entrada_l/2)
    parede(f"LIMITE_{lado_entrada}_L", True, aberto, entrada_x+entrada_l/2, xb)
    for s in config.setores:
        x, y = s["centro"]
        w, d = s["tamanho"]
        if s.get("porta") is None:
            # Volume sem interior mapeado: não inventa porta nem acesso transitável.
            caixa(s["id"]+"_VOLUME", (x, y), (w, d, s.get("altura", h)))
            continue
        lado_porta, largura, offset = s["porta"]
        if lado_porta not in ("N", "S", "L", "O") or min(w, d) <= 2*t:
            raise ValueError(f"Setor inválido: {s['id']}")
        comprimento = w if lado_porta in ("N", "S") else d
        if not (0 < largura and abs(offset) + largura/2 < comprimento/2-t):
            raise ValueError(f"Porta não cabe no setor {s['id']}")
        for lado, horizontal, fixo, inicio, fim, meio in [
            ("N", True, y+d/2, x-w/2, x+w/2, x),
            ("S", True, y-d/2, x-w/2, x+w/2, x),
            ("L", False, x+w/2, y-d/2, y+d/2, y),
            ("O", False, x-w/2, y-d/2, y+d/2, y),
        ]:
            ident = f"{s['id']}_{lado}"
            if lado == lado_porta:
                parede(ident+"_1", horizontal, fixo, inicio, meio+offset-largura/2)
                parede(ident+"_2", horizontal, fixo, meio+offset+largura/2, fim)
            else:
                parede(ident, horizontal, fixo, inicio, fim)
    caixas.extend(config.paredes)
    caixas.extend(config.blocos)
    return caixas


def restricoes_circulacao(config=cfg):
    """Complemento exato da união de faixas mapeadas; não são paredes físicas.

    Particiona nas bordas dos retângulos e une intervalos adjacentes. As caixas
    resultantes impedem atalhos por gramados/interiores sem acesso documentado.
    A grade e o seguidor expandem estas caixas pelas mesmas margens do robô.
    """
    faixas = getattr(config, "circulacao", None)
    if faixas is None:
        return []  # Compatibilidade com configurações de ensaio anteriores.
    if not faixas:
        raise ValueError("Circulação mapeada não pode ser vazia")
    p = config.piso
    xs, ys = {p["x_min"], p["x_max"]}, {p["y_min"], p["y_max"]}
    limites = []
    for faixa in faixas:
        xa, xb, ya, yb = faixa["limites"]
        if not all(math.isfinite(v) for v in (xa, xb, ya, yb)) or not (
                p["x_min"] <= xa < xb <= p["x_max"] and
                p["y_min"] <= ya < yb <= p["y_max"]):
            raise ValueError("Faixa de circulação inválida: " + faixa["id"])
        xs.update((xa, xb)); ys.update((ya, yb))
        limites.append((xa, xb, ya, yb))
    xs, ys = sorted(xs), sorted(ys)
    retangulos, ativos = [], {}
    for ya, yb in zip(ys, ys[1:]):
        runs, inicio = [], None
        for xa, xb in zip(xs, xs[1:]):
            x, y = (xa+xb)/2, (ya+yb)/2
            livre = any(a < x < b and c < y < d for a,b,c,d in limites)
            if not livre and inicio is None:
                inicio = xa
            if livre and inicio is not None:
                runs.append((inicio, xa)); inicio = None
        if inicio is not None:
            runs.append((inicio, xs[-1]))
        novos = {}
        for xa, xb in runs:
            chave = (xa, xb)
            if chave in ativos:
                rect = ativos[chave]
                rect[3] = yb
            else:
                rect = [xa, xb, ya, yb]
                retangulos.append(rect)
            novos[chave] = rect
        ativos = novos
    return [{"id": f"SEM_ACESSO_MAPEADO_{i:02d}",
             "centro": ((a+b)/2, (c+d)/2), "tamanho": (b-a, d-c, .01)}
            for i, (a,b,c,d) in enumerate(retangulos)]


def validar(config=cfg):
    """Confere dimensões, identificadores e espaço para o robô em cada ponto."""
    p = config.piso
    if not all(math.isfinite(v) for v in p.values()):
        raise ValueError("Piso deve conter números finitos")
    if p["x_min"] >= p["x_max"] or p["y_min"] >= p["y_max"] or p["espessura"] <= 0:
        raise ValueError("Dimensões do piso inválidas")
    if any(not math.isfinite(v) or v <= 0 for v in config.paredes_padrao.values()):
        raise ValueError("Altura e espessura das paredes devem ser positivas")
    if set(config.pontos) != set(config.nomes):
        raise ValueError("pontos e nomes devem ter os mesmos identificadores")
    if config.robo["ponto_inicial"] not in config.pontos or not math.isfinite(config.robo["angulo"]):
        raise ValueError("Posição inicial do robô inválida")
    escala = config.robo["escala"]
    if not math.isfinite(escala) or escala <= 0:
        raise ValueError("Escala do robô deve ser positiva e finita")
    if not math.isfinite(config.folga_robo) or config.folga_robo < 0:
        raise ValueError("Folga do robô deve ser finita e não negativa")
    caixas = caixas_cenario(config)
    ids = [c["id"] for c in caixas]
    if len(ids) != len(set(ids)):
        raise ValueError("Identificadores de paredes/blocos repetidos")
    for c in caixas:
        x, y = c["centro"]
        w, d, h = c["tamanho"]
        if not re.fullmatch(r"[A-Z][A-Z0-9_]*", c["id"]):
            raise ValueError(f"Identificador inválido: {c['id']}")
        if not all(math.isfinite(v) for v in (x,y,w,d,h)) or min(w,d,h) <= 0:
            raise ValueError(f"Dimensões inválidas: {c['id']}")
        if not (p["x_min"]-1e-8 <= x-w/2 and x+w/2 <= p["x_max"]+1e-8
                and p["y_min"]-1e-8 <= y-d/2 and y+d/2 <= p["y_max"]+1e-8):
            raise ValueError(f"Objeto fora do piso: {c['id']}")
    # Raio que engloba o carrinho, acrescido da margem de segurança configurada.
    r = math.hypot(0.12, 0.1125) * escala + config.folga_robo
    for ident, (x,y) in config.pontos.items():
        if not re.fullmatch(r"[A-Z][A-Z0-9_]*", ident) or not all(math.isfinite(v) for v in (x,y)):
            raise ValueError(f"Ponto inválido: {ident}")
        if not (p["x_min"]+r <= x <= p["x_max"]-r and p["y_min"]+r <= y <= p["y_max"]-r):
            raise ValueError(f"Ponto fora do piso ou perto demais da borda: {ident}")
        for c in caixas:
            cx,cy = c["centro"]
            w,d,_ = c["tamanho"]
            if abs(x-cx) <= w/2+r and abs(y-cy) <= d/2+r:
                raise ValueError(f"Ponto {ident} sem folga para o robô junto de {c['id']}")
    return caixas


def vetor(valores):
    """Converte uma sequência de números para o formato do arquivo de mundo."""
    return " ".join(f"{n:.8g}" for n in valores)


def cor(rgb):
    """Define uma aparência fosca com a cor vermelha, verde e azul informada."""
    return f"PBRAppearance {{ baseColor {vetor(rgb)} roughness 1 metalness 0 }}"


def caixa_wbt(ident, centro, tamanho, rgb, colide=True):
    """Cria o texto de um bloco, com colisão física opcional."""
    x,y,z = centro
    return f'''DEF {ident} Solid {{
  translation {vetor((x,y,z))}
  name "{ident}"
  children [ Shape {{ appearance {cor(rgb)} geometry Box {{ size {vetor(tamanho)} }} }} ]
  {f'boundingObject Box {{ size {vetor(tamanho)} }}' if colide else ''}
}}
'''


def textura(ident, texto, fundo):
    """Salva uma imagem com o nome do setor ou identificador do ponto."""
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGB", (1024,256), fundo)
    draw = ImageDraw.Draw(img)
    tamanho = 220
    while True:
        fonte = ImageFont.load_default(size=tamanho)
        if draw.textbbox((0,0), texto, font=fonte)[2] < 970 or tamanho <= 20:
            break
        tamanho -= 2
    draw.text((512,128), texto, font=fonte, fill="white", anchor="mm")
    destino = RAIZ / "worlds" / "textures" / "campus"
    destino.mkdir(parents=True, exist_ok=True)
    img.save(destino / f"{ident}.png")


def rotulo(ident, x, y, z, tamanho):
    """Posiciona a imagem de um rótulo sobre o piso, sem colisão."""
    return f'''Pose {{
  translation {vetor((x,y,z))}
  children [ Shape {{
    appearance PBRAppearance {{
      baseColorMap ImageTexture {{ url ["textures/campus/{ident}.png"] }}
      roughness 1 metalness 0
    }}
    geometry Plane {{ size {vetor(tamanho)} }}
  }} ]
}}
'''


def gerar():
    """Gera as texturas e os mundos de controle manual e de teste do campus."""
    caixas = validar()  # Não sobrescreve os mundos se a configuração for inválida.
    # Importação local evita ciclo: a grade reutiliza a geometria deste gerador.
    from grade_navegacao import Grade
    grade = Grade()
    p = cfg.piso
    w,d = p["x_max"]-p["x_min"], p["y_max"]-p["y_min"]
    cx,cy = (p["x_max"]+p["x_min"])/2, (p["y_max"]+p["y_min"])/2
    altura_vista = (max(w, d*cfg.vista["proporcao_janela"])
                    / (2*math.tan(cfg.vista["campo_visual"]/2)) * cfg.vista["margem"])
    partes = ['''#VRML_SIM R2025a utf8
# GERADO por gerar_campus.py. Edite campus_config.py, não este arquivo.
# Esquema provisório: NÃO é a planta oficial do campus.
EXTERNPROTO "../protos/Carrinho.proto"
WorldInfo {
  title "IESB - campus ampliado - destinos internos"
  coordinateSystem "ENU"
  basicTimeStep 32
  contactProperties [ ContactProperties { material1 "apoio" coulombFriction [ 0.001 ] } ]
}
''', f'''DEF VISTA Viewpoint {{
  orientation -0.577350269 0.577350269 0.577350269 2.094395102
  position {vetor((cx,cy,altura_vista))}
  fieldOfView {cfg.vista['campo_visual']}
}}
Background {{ skyColor [ 0.75 0.81 0.86 ] }}
DirectionalLight {{ direction -0.3 0.4 -1 intensity 1 }}
''', caixa_wbt("PISO_CAMPUS", (cx,cy,-p["espessura"]/2), (w,d,p["espessura"]), (.79,.81,.80))]
    # Grade de 1 m puramente visual, sem boundingObject.
    for x in range(math.ceil(p["x_min"]), math.floor(p["x_max"])+1):
        partes.append(caixa_wbt(f"GRADE_X_{x-p['x_min']:.0f}", (x,cy,.001), (.012,d,.001), (.67,.70,.70), False))
    for y in range(math.ceil(p["y_min"]), math.floor(p["y_max"])+1):
        partes.append(caixa_wbt(f"GRADE_Y_{y-p['y_min']:.0f}", (cx,y,.001), (w,.012,.001), (.67,.70,.70), False))
    for s in cfg.setores:
        x,y = s["centro"]
        sw,sd = s["tamanho"]
        partes.append(caixa_wbt("AREA_"+s["id"], (x,y,.003), (sw,sd,.002), (.62,.71,.78), False))
        textura(s["id"], s["nome"], (48,68,89))
        # O nome fica dentro do bloco, acima do ponto central de chegada.
        partes.append(rotulo(s["id"],x,y+sd*.30,.008,(sw*.82,.65)))
    for c in caixas:
        rgb = (.40,.47,.52) if c in cfg.blocos else (.89,.85,.73)
        partes.append(caixa_wbt(c["id"], (*c["centro"],c["tamanho"][2]/2), c["tamanho"], rgb))
    # Células reais de navegação: agrupadas por linha para facilitar a árvore.
    # Sem boundingObject: a ocupação é uma decisão do planejador, não um objeto físico.
    componente_entrada = grade.associacoes[cfg.robo["ponto_inicial"]]["componente"]
    partes.append("DEF GRADE_NAVEGACAO Group { children [")
    for linha in range(grade.linhas):
        partes.append(f"DEF LINHA_{linha:02d} Group {{ children [")
        for celula in (c for c in grade.celulas.values() if c.linha == linha):
            estado = "LIVRE" if celula.livre else "BLOQUEADA"
            if celula.livre and grade.componentes[celula.id] != componente_entrada:
                estado = "ISOLADA"
            fundo = {"LIVRE": (44, 104, 78), "BLOQUEADA": (132, 58, 60), "ISOLADA": (150, 107, 29)}[estado]
            curto = f"C{celula.coluna:02d} L{linha:02d}"
            textura(celula.id, curto, fundo)
            x, y = celula.centro
            partes.append(f'''DEF {celula.id} Solid {{
  translation {vetor((x,y,.014))}
  name "{celula.id} - {estado}"
  children [ {rotulo(celula.id,0,0,0,(.76,.20))} ]
}}''')
        partes.append("] }")
    partes.append("] }")
    for ident,(x,y) in cfg.pontos.items():
        rgb = (.03,.48,.61) if ident.startswith("EXT") else (.80,.31,.08)
        textura(ident, ident, tuple(round(v*255) for v in rgb))
        m = cfg.marcadores
        partes.append(f'''DEF {ident} Solid {{
  translation {vetor((x,y,.008))}
  name {json.dumps(ident+' - '+cfg.nomes[ident], ensure_ascii=False)}
  children [ Shape {{ appearance {cor(rgb)}
    geometry Cylinder {{ radius {m['raio']} height {m['altura']} }} }} ]
}}
''')
        ox,oy = m["deslocamento_rotulo"]
        partes.append(rotulo(ident,x+ox,y+oy,.018,m["tamanho_rotulo"]))
    for ident,centro,tamanho,rgb in [
        ("EIXO_X",(1.5,0,.006),(3,.045,.002),(.85,.12,.12)),
        ("EIXO_Y",(0,1.5,.006),(.045,3,.002),(.08,.55,.20)),
    ]:
        partes.append(caixa_wbt(ident,centro,tamanho,rgb,False))
    for ident,texto,x,y,tamanho in [
        ("LEGENDA_X","+X (m)",3.3,-.5,(1.5,.42)),
        ("LEGENDA_Y","+Y (m)",.9,2.8,(1.5,.42)),
        ("AVISO","PROVISORIO | grade: 1 m",cx,p["y_max"]-1,(10,.65)),
    ]:
        textura(ident,texto,(41,55,65))
        partes.append(rotulo(ident,x,y,.012,tamanho))
    ambiente = "\n".join(partes)
    x,y = cfg.pontos[cfg.robo["ponto_inicial"]]
    mundos = (("etapa2_campus.wbt", "carrinho_manual", False),
              ("etapa2_campus_teste.wbt", "teste_campus", True),
              ("etapa3_buscas.wbt", "carrinho_buscas", True),
              ("etapa3_buscas_teste.wbt", "teste_buscas", True),
              ("etapa4_navegacao_teste.wbt", "teste_navegacao", True),
              ("campus_interiores_teste.wbt", "teste_interiores", True))
    for nome, controlador, supervisor in mundos:
        # Supervisor: interface didática e localização ideal da navegação.
        robo = f'''DEF ROBO Carrinho {{
  translation {vetor((x,y,.06*cfg.robo['escala']+.001))}
  escala {cfg.robo['escala']}
  rotation 0 0 1 {cfg.robo['angulo']:.10g}
  controller "{controlador}"
  supervisor {'TRUE' if supervisor else 'FALSE'}
}}
'''
        titulo = ('IESB - TESTE AUTOMATICO: ' + controlador if controlador.startswith('teste_')
                  else 'IESB - campus ampliado - ' + ('INTERATIVO: buscas e navegacao' if supervisor else 'controle manual'))
        cena = ambiente.replace('title "IESB - campus ampliado - destinos internos"', f'title "{titulo}"')
        (RAIZ/"worlds"/nome).write_text(cena+robo,encoding="utf-8")
    print(f"Gerados {len(mundos)} mundos, {len(cfg.pontos)} pontos e {len(caixas)} paredes/blocos.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validar", action="store_true", help="Valida sem gerar arquivos")
    args = parser.parse_args()
    if args.validar:
        validar()
        print("Configuração válida.")
    else:
        gerar()
