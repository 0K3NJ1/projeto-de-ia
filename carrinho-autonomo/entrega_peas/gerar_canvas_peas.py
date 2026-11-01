"""Canvas PEAS de uma página, com versão HTML editável e PDF para apresentação."""
from pathlib import Path
from html import escape
import json

from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "pdf"
OUT.mkdir(parents=True, exist_ok=True)
PDF = OUT / "Canvas_PEAS_Carrinho_IESB.pdf"
HTML = ROOT / "entrega_peas" / "Canvas_PEAS_Carrinho_IESB.html"
RED = "#C8102E"
INK = "#20252B"
MUTED = "#59616A"
FONT_CANDIDATES = (
    (Path("C:/Windows/Fonts/arial.ttf"), Path("C:/Windows/Fonts/arialbd.ttf")),
    (Path("/usr/share/fonts/truetype/croscore/Arimo-Regular.ttf"),
     Path("/usr/share/fonts/truetype/croscore/Arimo-Bold.ttf")),
    (Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
     Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")),
)
FONT_REGULAR, FONT_BOLD = next(
    ((regular, bold) for regular, bold in FONT_CANDIDATES
     if regular.is_file() and bold.is_file()),
    (None, None),
)
if FONT_REGULAR is None:
    raise FileNotFoundError("Nenhuma fonte compatível encontrada para gerar o PDF PEAS")
pdfmetrics.registerFont(TTFont("Arial", str(FONT_REGULAR)))
pdfmetrics.registerFont(TTFont("Arial-Bold", str(FONT_BOLD)))
pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-Bold")

TITLE = "PEAS"
SUBTITLE = "Navegação de um carrinho no Campus Edson Machado | Webots + Python"
OBJECTIVE = "<b>Objetivo do agente proposto:</b> navegar entre uma origem e um destino escolhido pelo usuário no térreo do campus, buscando o menor caminho válido e parando no destino sem colisões."
CARDS = [
    ("P", "Desempenho", "Performance", [
        "<b>Sucesso:</b> alcançar o destino solicitado e parar.",
        "<b>Qualidade:</b> minimizar a distância total da rota, em metros.",
        "<b>Execução:</b> utilizar passagens válidas e evitar colisões.",
        "<b>Avaliação futura:</b> custo da rota, nós expandidos e tempo de busca.",
    ], "Critérios propostos; ainda sem avaliação de navegação autônoma."),
    ("E", "Ambiente", "Environment", [
        "<b>Domínio:</b> térreo do campus, com corredores e acessos aos setores.",
        "<b>Cenário:</b> piso, paredes, portas e blocos simples no Webots.",
        "<b>Referências:</b> 18 pontos com coordenadas em metros.",
        "<b>Modelo inicial:</b> mapa conhecido e estático, sem obstáculos móveis.",
    ], "Planta oficial pendente; dimensões e posições provisórias."),
    ("A", "Atuadores", "Actuators", [
        "<b>Estrutura:</b> duas rodas com motores independentes.",
        "<b>Comandos atuais:</b> frente, ré, esquerda, direita e parar.",
        "<b>Planejamento futuro:</b> deslocar-se para um ponto vizinho permitido.",
        "<b>Integração futura:</b> converter a rota em comandos dos motores.",
    ], "Os movimentos já funcionam por controle manual."),
    ("S", "Percepções", "Sensors", [
        "<b>Entradas previstas:</b> mapa cadastrado, origem e destino.",
        "<b>Estado previsto:</b> ponto atual conhecido no modelo discreto.",
        "<b>Protótipo atual:</b> recebe comandos do teclado.",
        "<b>Sensoriamento:</b> sem sensores de localização ou obstáculos implementados.",
    ], "Dados do modelo não são medições de sensores físicos."),
]
AUTHORS = [
    ("Integrante 1", "PREENCHER"),
    ("Integrante 2", "PREENCHER"),
    ("Integrante 3", "PREENCHER"),
]
NOW = "Carrinho manual, cenário provisório e 18 pontos de referência."
NEXT = "Grafo, busca de rotas e integração com os motores."

w, h = landscape(A4)
c = canvas.Canvas(str(PDF), pagesize=(w,h))
c.setTitle("PEAS - Navegação no Campus Edson Machado")
c.setAuthor("; ".join(a[0] for a in AUTHORS))
measurements = []

def text(x, top, value, size=10, bold=False, color=INK):
    c.setFillColor(HexColor(color))
    c.setFont("Arial-Bold" if bold else "Arial", size)
    c.drawString(x, h-top-size, value)

def para(value, x, top, width, size=10.3, leading=14.2, color=INK):
    style = ParagraphStyle("p", fontName="Arial", fontSize=size, leading=leading,
                           textColor=HexColor(color))
    p = Paragraph(value, style)
    pw, ph = p.wrap(width, h)
    p.drawOn(c, x, h-top-ph)
    measurements.append({"top":top,"bottom":top+ph,"text":value})
    return ph

def rect(x, top, width, height, fill, stroke=None):
    c.setFillColor(HexColor(fill))
    if stroke:
        c.setStrokeColor(HexColor(stroke))
    c.rect(x,h-top-height,width,height,fill=1,stroke=int(stroke is not None))

margin=30
usable=w-2*margin
text(margin, 21, "IESB | INTELIGÊNCIA ARTIFICIAL", 9, True, RED)
text(w-193, 21, "2026/2 | Especificação do agente", 8.5, color=MUTED)
text(margin, 43, TITLE, 27, True, RED)
text(margin, 80, SUBTITLE, 11, color=MUTED)
c.setStrokeColor(HexColor("#D0D4D8"))
c.line(margin,h-100,w-margin,h-100)
rect(margin,111,usable,45,"#FCEFF2")
rect(margin,111,3,45,RED)
para(OBJECTIVE,margin+13,121,usable-26,10.5,14.2)

gap=12
cardw=(usable-3*gap)/4
cardtop=170
cardheight=280
for index,(letter,title,english,bullets,note) in enumerate(CARDS):
    x=margin+index*(cardw+gap)
    rect(x,cardtop,cardw,cardheight,"#FFFFFF","#D6DADF")
    rect(x,cardtop,cardw,4,RED)
    text(x+12,cardtop+12,letter,30,True,RED)
    text(x+46,cardtop+15,title,13,True)
    text(x+46,cardtop+34,english,9,color=MUTED)
    y=cardtop+66
    for bullet in bullets:
        height=para(bullet,x+12,y,cardw-24)
        y+=height+9
    notetop=cardtop+232
    assert y-9 <= notetop-5, (letter,y,notetop)
    rect(x+1,notetop,cardw-2,cardheight-232-1,"#F4F6F8")
    nh=para(note,x+12,notetop+9,cardw-24,8.3,11)
    assert nh <= 32, (letter,nh)

text(margin,463,"JÁ IMPLEMENTADO",8.5,True,RED)
para(NOW,margin,478,usable/2-18,9.5,12)
text(margin+usable/2+10,463,"PLANEJADO",8.5,True,RED)
para(NEXT,margin+usable/2+10,478,usable/2-10,9.5,12)
c.setStrokeColor(HexColor("#D0D4D8"))
c.line(margin,h-512,w-margin,h-512)
for i,(name,ra) in enumerate(AUTHORS):
    x=margin+i*usable/3
    text(x,523,name,9,True)
    text(x,537,"Matrícula: "+ra,8.5,color=MUTED)
text(margin,562,"Prof. Rodrigo Gonçalves Pinto | Projeto do grupo",8,color=MUTED)
text(w-178,562,"PEAS | Escopo inicial: navegação",8,color=MUTED)
c.save()

# O mesmo conteúdo em HTML editável; alterações podem ser salvas pelo navegador.
cards_html="".join(f'''<section class="card"><header><span>{letter}</span><div><h2>{title}</h2><small>{english}</small></div></header><div class="body">{''.join('<p>'+b+'</p>' for b in bullets)}</div><aside>{note}</aside></section>''' for letter,title,english,bullets,note in CARDS)
html = '''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>PEAS - IESB</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#e9edf1;color:#20252b;font-family:Arial,sans-serif}.tools{padding:16px;text-align:center;font-size:14px}.tools button{cursor:pointer;padding:9px 16px;margin:0 6px;border:1px solid #c8102e;border-radius:4px;background:white;color:#c8102e}.sheet{width:1123px;margin:0 auto 32px;padding:32px 40px;background:white}.meta{display:flex;justify-content:space-between;font-size:12px;color:#59616a}.meta b{color:#c8102e}h1{font-size:36px;color:#c8102e;margin:18px 0 8px}.subtitle{font-size:15px;color:#59616a;margin-bottom:18px;padding-bottom:14px;border-bottom:1px solid #d0d4d8}.objective{padding:14px 16px;background:#fceff2;border-left:4px solid #c8102e;font-size:14px;line-height:1.5}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-top:18px}.card{border:1px solid #d6dadf;border-top:5px solid #c8102e;display:flex;flex-direction:column}header{display:flex;align-items:center;gap:16px;padding:14px 16px}header span{font-size:40px;font-weight:bold;color:#c8102e}h2{font-size:18px;margin:0 0 5px}small{color:#59616a}.body{padding:0 16px;flex:1}.body p{font-size:14px;line-height:1.45;margin:10px 0 14px}aside{background:#f4f6f8;padding:12px 16px;font-size:12px;line-height:1.45;color:#59616a}.status{display:grid;grid-template-columns:1fr 1fr;gap:26px;margin:20px 0;font-size:13px;line-height:1.5}.status b{color:#c8102e;font-size:12px}.authors{border-top:1px solid #d0d4d8;padding-top:14px;display:grid;grid-template-columns:repeat(3,1fr);font-size:12px;line-height:1.7}footer{margin-top:20px;color:#59616a;font-size:11px;display:flex;justify-content:space-between}[contenteditable]:focus{outline:2px dashed #c8102e;outline-offset:8px}
@page{size:A4 landscape;margin:8mm}@media print{.tools{display:none}body{background:white}.sheet{width:100%;padding:0;margin:0}h1{font-size:28px}.body p{font-size:11px}.objective{font-size:12px}.card header{padding:10px}header span{font-size:32px}h2{font-size:14px}aside{font-size:10px}.grid{gap:10px}.authors{font-size:10px}.status{font-size:11px}*{print-color-adjust:exact;-webkit-print-color-adjust:exact}}
</style><div class="tools">Clique no texto para editar. <button onclick="window.print()">Imprimir / salvar PDF</button><button onclick="salvar()">Baixar HTML editado</button></div><main class="sheet" contenteditable="true">
'''
html += f'<div class="meta"><b>IESB | INTELIGÊNCIA ARTIFICIAL</b><span>2026/2 | Especificação do agente</span></div><h1>{TITLE}</h1><div class="subtitle">{SUBTITLE}</div><div class="objective">{OBJECTIVE}</div><div class="grid">{cards_html}</div>'
html += f'<div class="status"><div><b>JÁ IMPLEMENTADO</b><br>{NOW}</div><div><b>PLANEJADO</b><br>{NEXT}</div></div><div class="authors">'
html += ''.join(f'<div><b>{escape(name)}</b><br>Matrícula: {ra}</div>' for name,ra in AUTHORS)
html += '</div><footer><span>Prof. Rodrigo Gonçalves Pinto | Projeto do grupo</span><span>PEAS | Escopo inicial: navegação</span></footer></main>'
html += '''<script>function salvar(){const blob=new Blob(['<!doctype html>\n'+document.documentElement.outerHTML],{type:'text/html;charset=utf-8'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='Canvas_PEAS_Carrinho_IESB.html';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}</script></html>'''
HTML.write_text(html,encoding="utf-8")
print(json.dumps({"pdf":str(PDF),"html":str(HTML),"pages":1},ensure_ascii=False))
