"""Validação do mundo, movimentos e colisão; somente no mundo de teste."""

import math
from pathlib import Path
import sys
import traceback

from controller import Supervisor

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "controllers" / "carrinho_manual"))
import campus_config as cfg
from gerar_campus import validar
from grade_navegacao import Grade
from buscas import a_estrela, custo_do_caminho
from carrinho_manual import Carrinho


def main():
    robot = Supervisor()
    carrinho = Carrinho(robot)
    corpo = robot.getSelf()
    passo = int(robot.getBasicTimeStep())
    escala = cfg.robo["escala"]

    def esperar(segundos):
        """Avança a simulação por um intervalo em segundos."""
        for _ in range(math.ceil(segundos*1000/passo)):
            if robot.step(passo) == -1:
                raise RuntimeError("Simulação interrompida")

    def pose():
        """Lê a posição em metros e a orientação em radianos para os testes."""
        x,y,_ = corpo.getPosition()
        m = corpo.getOrientation()
        return x,y,math.atan2(m[3],m[0])

    def delta(a,b):
        """Calcula a diferença angular sem saltos ao passar de pi para -pi."""
        return math.atan2(math.sin(a-b), math.cos(a-b))

    try:
        caixas = validar()
        # Confere se os marcadores coincidem com as coordenadas da configuração.
        for ident,(x,y) in cfg.pontos.items():
            marcador = robot.getFromDef(ident)
            assert marcador is not None, f"Marcador ausente: {ident}"
            mx,my,_ = marcador.getPosition()
            assert math.hypot(mx-x,my-y) < 1e-6, f"Coordenada divergente: {ident}"
            assert marcador.getField("boundingObject").getSFNode() is None, ident
        for c in caixas:
            # Paredes e blocos devem ter posição, dimensões e colisão corretas.
            node = robot.getFromDef(c["id"])
            assert node is not None, c["id"]
            box = node.getField("boundingObject").getSFNode()
            assert box is not None, f"Sem colisão: {c['id']}"
            assert all(abs(a-b)<1e-6 for a,b in zip(box.getField("size").getSFVec3f(),c["tamanho"]))
            assert all(abs(a-b)<1e-6 for a,b in zip(node.getPosition(),(*c["centro"],c["tamanho"][2]/2)))
        print(f"PASS: {len(cfg.pontos)} marcadores e {len(caixas)} objetos conferidos no Webots",flush=True)
        grade = Grade()
        for celula in grade.celulas.values():
            node = robot.getFromDef(celula.id)
            assert node is not None, f"Célula ausente na árvore: {celula.id}"
            assert all(abs(a-b) < 1e-6 for a,b in zip(node.getPosition()[:2], celula.centro))
            assert node.getField("boundingObject").getSFNode() is None, celula.id
        origem = grade.associacoes["EXT01"]["celula"]
        destino = grade.associacoes["H01"]["celula"]
        caminho, custo, _, _ = a_estrela(grade.grafo, origem, destino, grade.heuristica(destino))
        assert caminho and custo == custo_do_caminho(grade.grafo, caminho)
        print(f"PASS: {len(grade.celulas)} células localizadas por DEF; rota A* calculada ({custo} m), sem condução automática", flush=True)
        esperar(.5)
        x0,y0,a0 = pose()
        xi,yi = cfg.pontos[cfg.robo["ponto_inicial"]]
        assert math.hypot(x0-xi,y0-yi) < .005
        assert abs(delta(a0,cfg.robo["angulo"])) < .02
        esperar(.5)
        x,y,a = pose()
        assert math.hypot(x-x0,y-y0) < .005 and abs(delta(a,a0)) < .02
        resultados = RAIZ / "test-results"
        resultados.mkdir(exist_ok=True)
        robot.exportImage(str(resultados / "etapa2_campus.png"),100)
        print("PASS: robô na entrada, orientação correta e inicialmente parado",flush=True)

        for comando in ("frente","re","esquerda","direita"):
            # Aciona cada movimento e verifica se o carrinho para em seguida.
            x0,y0,a0 = pose()
            carrinho.mover(comando)
            esperar(1)
            carrinho.mover("parar")
            esperar(.25)
            x,y,a = pose()
            desloc = (x-x0)*math.cos(a0)+(y-y0)*math.sin(a0)
            giro = delta(a,a0)
            if comando in ("frente","re"):
                sinal = 1 if comando == "frente" else -1
                assert .1*escala < sinal*desloc < .26*escala and abs(giro) < .1, comando
                assert abs(-(x-x0)*math.sin(a0)+(y-y0)*math.cos(a0)) < .02
            else:
                sinal = 1 if comando == "esquerda" else -1
                assert .8 < sinal*giro < 2.5 and math.hypot(x-x0,y-y0) < .04, comando
            esperar(.5)
            xp,yp,ap = pose()
            assert math.hypot(xp-x,yp-y) < .005 and abs(delta(ap,a)) < .02
            print(f"PASS: {comando} e parar; deslocamento={desloc:.3f} m, giro={giro:.3f} rad",flush=True)

        # Ensaio fixo de colisão, sem sensor ou reconhecimento de obstáculos.
        # Aproximação perpendicular à parede externa direita, pelo corredor sul.
        t = cfg.paredes_padrao["espessura"]
        limite = cfg.piso["x_max"]-t
        y_teste = cfg.piso["y_min"]+1.0
        corpo.getField("translation").setSFVec3f([limite-(.12*escala+.6),y_teste,.06*escala+.001])
        corpo.getField("rotation").setSFRotation([0,0,1,0])
        corpo.resetPhysics()
        esperar(.5)
        carrinho.mover("frente")
        esperar(5)
        carrinho.mover("parar")
        esperar(.3)
        x,y,_ = pose()
        assert abs(x-(limite-.12*escala)) < .04, f"Colisão da parede incorreta: x={x}"
        assert abs(y-y_teste) < .05
        print("PASS: parede bloqueia fisicamente o carrinho",flush=True)
        print("RESULTADO ETAPA 2: TODOS OS TESTES PASSARAM",flush=True)
        robot.simulationQuit(0)
    except Exception:
        carrinho.mover("parar")
        traceback.print_exc()
        robot.simulationQuit(1)
    robot.step(passo)


if __name__ == "__main__":
    main()
