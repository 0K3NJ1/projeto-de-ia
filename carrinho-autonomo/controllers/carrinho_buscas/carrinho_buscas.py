"""Painel de busca e navegação física dentro do Webots, inteiramente em Python.

Supervisor é usado como ferramenta didática: lê a posição, desenha a busca e
permite reposicionar a origem por comando explícito. Não é sensor do carrinho.
"""
import json
import math
from pathlib import Path
import sys

from controller import Keyboard, Supervisor

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "controllers/carrinho_manual"))
from carrinho_manual import Carrinho
import campus_config as cfg
from grade_navegacao import Grade
from planejamento import ALGORITMOS, planejar, resolver_alvo, alvo_do_clique
from navegacao import Seguidor


def marca(ident, ponto, cor, raio=.16, z=.027, transparencia=0):
    """Disco visual horizontal, sem geometria de colisão."""
    x, y = ponto
    return f'''DEF {ident} Pose {{ translation {x} {y} {z} children [ Shape {{
      appearance DEF AP_{ident} PBRAppearance {{ baseColor {cor} roughness 1 metalness 0 transparency {transparencia} }}
      geometry Cylinder {{ radius {raio} height 0.006 subdivision 16 }}
    }} ] }}'''


def trecho(a, b, cor="0.85 0.035 0.12", z=.026):
    """Faixa sobre o piso, orientada entre dois centros ou um conector."""
    distancia = math.dist(a, b)
    if distancia < 1e-8:
        return ""
    angulo = math.atan2(b[1]-a[1], b[0]-a[0])
    return f'''Pose {{ translation {(a[0]+b[0])/2} {(a[1]+b[1])/2} {z}
      rotation 0 0 1 {angulo} children [ Shape {{
      appearance PBRAppearance {{ baseColor {cor} roughness 1 metalness 0 }}
      geometry Box {{ size {distancia} 0.075 0.008 }} }} ] }}'''


class PainelBusca:
    def __init__(self, robot):
        self.robot = robot
        self.passo = int(robot.getBasicTimeStep())
        self.robo = robot.getSelf()
        self.carrinho = Carrinho(robot)
        self.grade = Grade()
        self.seguidor = Seguidor(self.grade)
        self.ultimo_painel = 0.
        self.teclado = robot.getKeyboard()
        self.teclado.enable(self.passo)
        self.mouse = robot.getMouse()
        self.mouse.enable(self.passo)
        self.mouse.enable3dPosition()
        self.algoritmo = 4
        self.destino_texto = "H01"
        self.edicao = None
        self.texto = ""
        self.resultado = None
        self.indice = 0
        self.reproduzindo = False
        self.relogio = 0.0
        self.intervalo = .06
        self.anterior_teclas = set()
        self.anterior_mouse = False
        self.aparencias = []
        self.mensagem = "Escolha o destino com T; Enter executa a busca."
        self.grupo = robot.getFromDef("VISUAL_BUSCA")
        if self.grupo is None:
            robot.getRoot().getField("children").importMFNodeFromString(-1, "DEF VISUAL_BUSCA Group { children [] }")
            self.grupo = robot.getFromDef("VISUAL_BUSCA")
        self.children = self.grupo.getField("children")
        # O mundo pode ter sido salvo durante uma busca anterior. Os desenhos
        # temporários precisam acompanhar o estado novo do controlador.
        self.limpar()
        self.atualizar_painel()
        print("BUSCAS: T destino | O origem | 1-5 algoritmo | Enter buscar | P/N/F animação | G iniciar | C pausar/retomar movimento | ESPAÇO parar | R entrada", flush=True)

    def limpar(self):
        self.seguidor.parar()
        self.carrinho.mover("parar")
        for i in reversed(range(self.children.getCount())):
            self.children.removeMF(i)
        self.aparencias = []
        self.resultado = None
        self.indice = 0
        self.reproduzindo = False

    def selecionar(self, texto, origem=False):
        self.limpar()
        ident, ponto = resolver_alvo(self.grade, texto)
        if origem:
            # Alterar o estado inicial é uma operação explícita de montagem do ensaio.
            self.carrinho.mover("parar")
            self.robo.getField("translation").setSFVec3f([*ponto, .06*cfg.robo["escala"]+.001])
            self.robo.getField("rotation").setSFRotation([0, 0, 1, cfg.robo["angulo"]])
            self.robo.resetPhysics()
            self.mensagem = f"Origem definida: {ident}. Enter para buscar."
        else:
            self.destino_texto = texto
            self.mensagem = f"Destino definido: {ident}. Enter para buscar."
        self.children.importMFNodeFromString(-1, marca("ALVO_ESCOLHIDO", ponto, "0.85 0.035 0.12", .23))
        self.edicao = None
        self.texto = ""
        self.atualizar_painel()

    def executar_busca(self):
        self.carrinho.mover("parar")
        self.limpar()
        self.resultado = planejar(self.grade, tuple(self.robo.getPosition()[:2]), self.destino_texto, self.algoritmo)
        r = self.resultado
        partes = []
        for i, ident in enumerate(r["ordem"]):
            partes.append(marca(f"EXP_{i}", self.grade.celulas[ident].centro, "1 0 1", transparencia=1))
        partes.extend((marca("INICIO_BUSCA", self.grade.celulas[r["origem"]].centro, "0.02 0.7 0.32", .25, .041),
                       marca("FIM_BUSCA", self.grade.celulas[r["destino"]].centro, "0.85 0.035 0.12", .25, .041)))
        self.children.importMFNodeFromString(-1, "DEF EXPANSOES Group { children ["+"\n".join(partes)+"] }")
        self.aparencias = [self.robot.getFromDef(f"AP_EXP_{i}") for i in range(len(r["ordem"]))]
        self.reproduzindo = True
        self.relogio = self.robot.getTime()
        self.mensagem = "Reproduzindo a ordem real das expansões."
        self.atualizar_painel()
        print(json.dumps({k: r[k] for k in ("algoritmo", "origem", "destino", "custo_m", "expandidos", "tempo_ms")}, ensure_ascii=False), flush=True)

    def avancar(self, quantidade=1):
        if self.resultado is None:
            return
        fim = min(len(self.aparencias), self.indice+quantidade)
        for i in range(self.indice, fim):
            self.aparencias[i].getField("transparency").setSFFloat(0.0)
        self.indice = fim
        if self.indice == len(self.aparencias):
            self.finalizar()
        self.atualizar_painel()

    def finalizar(self):
        self.reproduzindo = False
        r = self.resultado
        if self.robot.getFromDef("ROTA_FINAL") is not None:
            return
        partes = []
        if r["caminho"] is None:
            self.mensagem = "SEM ROTA: destino livre, mas desconectado da origem."
        else:
            pontos = [self.grade.celulas[n].centro for n in r["caminho"]]
            partes = [trecho(a, b) for a, b in zip(pontos, pontos[1:])]
            partes += [trecho(r["posicao_inicial"], pontos[0], "0.5 0.1 0.65"),
                       trecho(pontos[-1], r["ponto_final"], "0.5 0.1 0.65")]
            self.mensagem = "Rota pronta. G inicia o movimento; C pausa/retoma; espaço para."
        self.children.importMFNodeFromString(-1, "DEF ROTA_FINAL Group { children ["+"\n".join(partes)+"] }")

    def atualizar_painel(self):
        origem = self.grade.associar(tuple(self.robo.getPosition()[:2]))["celula"]
        linhas = ["BUSCAS NO CAMPUS | PYTHON", "", f"Algoritmo: {ALGORITMOS[self.algoritmo][0]}",
                  f"Origem: {origem or 'sem associação'}", f"Destino: {self.destino_texto}", "",
                  "T: escolher destino", "O: definir origem do carrinho",
                  "Digite Bloco H ou H01 + Enter", "T + clique no bloco: destino interno", "",
                  "1 Profundidade   2 Largura", "3 Custo uniforme   4 Gulosa   5 A*",
                  "Enter: calcular e mostrar busca", "P: pausar/continuar   N: um passo", "F: ver resultado final   R: entrada", "Q: cancelar seleção / animação", "",
                  "Magenta: nós expandidos", "Vermelho: rota / destino", "Verde: início   Roxo: conector"]
        if self.resultado:
            r = self.resultado
            linhas += ["", f"Expansões: {self.indice}/{r['expandidos']}",
                       f"Custo da grade: {r['custo_m']} m" if r['custo_m'] is not None else "Custo: sem solução",
                       f"Busca: {r['tempo_ms']:.3f} ms", "Tempo acima exclui a animação."]
            if self.indice:
                linhas += [f"Último: {r['ordem'][self.indice-1]}"]
        linhas += ["G: iniciar | C: pausar/retomar", "Espaço: parar e invalidar rota",
                   f"Movimento: {self.seguidor.estado}", f"Deslocamento: {self.seguidor.tempo_s:.1f} s (sem pausas)"]
        if self.edicao:
            linhas += ["", f"Selecionando {self.edicao.upper()}:", self.texto+"_", "Enter confirma | Q cancela"]
        # Um rótulo por linha evita recortes da textura de textos multilinha
        # quando o conteúdo e a quantidade de linhas mudam durante a animação.
        for indice in range(42):
            texto = linhas[indice] if indice < len(linhas) else ""
            self.robot.setLabel(indice, texto, .012, .025+.022*indice, .042, 0x142A3B, 0, "Arial")
        self.robot.setLabel(99, self.mensagem, .012, .95, .044, 0x142A3B, 0, "Arial")

    def tecla(self, tecla):
        tecla &= Keyboard.KEY
        # Webots R2025a transmite teclas Qt mascaradas por 0xffff:
        # Return=4, Enter numérico=5 e Backspace=3 (não ASCII 13/8).
        # Escape é consumido pela janela 3D; Q permite cancelar a edição.
        if tecla == ord(" ") and not self.edicao:
            self.limpar()
            self.mensagem = "Movimento parado e rota invalidada. Enter para recalcular."
        elif tecla in (27, ord("Q")):
            self.seguidor.pausar()
            self.carrinho.mover("parar")
            self.edicao = None
            self.texto = ""
            self.reproduzindo = False
        elif self.edicao:
            if tecla in (4, 5, 10, 13):
                self.selecionar(self.texto, origem=self.edicao == "origem")
            elif tecla in (3, 8, 127):
                self.texto = self.texto[:-1]
            elif 32 <= tecla <= 126 and len(self.texto) < 28:
                self.texto += chr(tecla)
        elif tecla in (ord("T"), ord("O")):
            self.limpar()
            self.edicao = "destino" if tecla == ord("T") else "origem"
            self.texto = ""
            self.reproduzindo = False
        elif ord("1") <= tecla <= ord("5"):
            self.algoritmo = tecla-ord("1")
            self.limpar()
            self.mensagem = "Algoritmo escolhido. Enter para executar."
        elif tecla in (4, 5, 10, 13):
            self.executar_busca()
        elif tecla == ord("G"):
            if self.resultado is None:
                raise ValueError("Enter para calcular uma rota antes de iniciar.")
            if self.seguidor.estado in (*Seguidor.ATIVOS, 'pausado'):
                self.mensagem = "Use C para pausar ou retomar; espaço para parar."
            else:
                self.avancar(len(self.aparencias))
                self.seguidor.iniciar(self.resultado, self.pose(), self.robot.getTime())
                self.mensagem = self.seguidor.motivo
        elif tecla == ord("C"):
            if self.seguidor.estado == 'pausado':
                self.seguidor.retomar(self.robot.getTime())
            else:
                self.seguidor.pausar()
            self.carrinho.mover("parar")
            self.mensagem = self.seguidor.motivo
        elif tecla == ord("F") and self.resultado:
            self.avancar(len(self.aparencias))
        elif tecla == ord("N"):
            self.reproduzindo = False
            self.avancar()
        elif tecla == ord("P") and self.resultado and self.indice < len(self.aparencias):
            self.reproduzindo = not self.reproduzindo
        elif tecla == ord("R"):
            self.selecionar(cfg.robo["ponto_inicial"], origem=True)
        self.atualizar_painel()

    def pose(self):
        # Preferência por leitura dos sensores físicos embarcados (GPS + IMU):
        c = self.carrinho
        if hasattr(c, "gps") and c.gps and hasattr(c, "imu") and c.imu:
            p = c.gps.getValues()
            rpy = c.imu.getRollPitchYaw()
            if all(math.isfinite(v) for v in (*p[:2], rpy[2])):
                return p[0], p[1], rpy[2]
        # Fallback para o Supervisor (oráculo) se executando em mundo sem sensores:
        x, y, _ = self.robo.getPosition()
        m = self.robo.getOrientation()
        return x, y, math.atan2(m[3], m[0])

    def atualizar_movimento(self):
        anterior = self.seguidor.estado
        esquerda, direita = self.seguidor.atualizar(self.pose(), self.robot.getTime())
        self.carrinho.esquerdo.setVelocity(esquerda)
        self.carrinho.direito.setVelocity(direita)
        if self.seguidor.estado != anterior:
            self.mensagem = self.seguidor.motivo
            if self.seguidor.estado in ('concluído', 'falha'):
                print(f"NAVEGAÇÃO: {self.seguidor.estado}; {self.seguidor.motivo}; "
                      f"tempo={self.seguidor.tempo_s:.3f} s; erro={self.seguidor.erro_final} m", flush=True)
        if self.robot.getTime()-self.ultimo_painel >= .25:
            self.ultimo_painel = self.robot.getTime()
            self.atualizar_painel()

    def atualizar(self, ler_entrada=True):
        # Ensaios automáticos não devem receber teclas/cliques da janela.
        if not ler_entrada:
            self.atualizar_movimento()
            return
        teclas = set()
        while (tecla := self.teclado.getKey()) != -1:
            teclas.add(tecla & Keyboard.KEY)
        try:
            # Eventos na pressão, evitando vários Enter enquanto a tecla está segura.
            novas = teclas-self.anterior_teclas
            if ord(' ') in novas and not self.edicao:
                novas = {ord(' ')}  # Parada prevalece sobre comandos simultâneos.
            for tecla in sorted(novas):
                self.tecla(tecla)
            mouse = self.mouse.getState()
            if self.edicao and mouse.left and not self.anterior_mouse and all(math.isfinite(v) for v in (mouse.x, mouse.y)):
                ident = alvo_do_clique(self.grade, mouse.x, mouse.y,
                                      selecionar_setor=self.edicao == 'destino')
                self.selecionar(ident, origem=self.edicao == "origem")
            self.anterior_mouse = mouse.left
        except ValueError as erro:
            self.mensagem = str(erro)
            self.atualizar_painel()
        self.anterior_teclas = teclas
        if self.reproduzindo and self.robot.getTime()-self.relogio >= self.intervalo:
            self.relogio = self.robot.getTime()
            self.avancar()
        self.atualizar_movimento()


def main():
    robot = Supervisor()
    painel = PainelBusca(robot)
    while robot.step(painel.passo) != -1:
        painel.atualizar()


if __name__ == "__main__":
    main()
