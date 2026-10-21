"""Teste físico da etapa 1. O Supervisor serve somente como instrumento de teste."""

import math
from pathlib import Path
import sys
import traceback

from controller import Keyboard, Supervisor

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "carrinho_manual"))
from carrinho_manual import Carrinho, comando_das_teclas


def main():
    robot = Supervisor()
    passo = int(robot.getBasicTimeStep())
    carrinho = Carrinho(robot)
    corpo = robot.getSelf()

    def avancar(segundos):
        """Avança o tempo simulado pela quantidade de segundos solicitada."""
        for _ in range(math.ceil(segundos * 1000 / passo)):
            if robot.step(passo) == -1:
                raise RuntimeError("Simulacao interrompida antes de concluir o teste.")

    def pose():
        """Retorna X e Y em metros e a orientação no plano em radianos."""
        posicao = corpo.getPosition()
        matriz = corpo.getOrientation()
        return posicao[0], posicao[1], math.atan2(matriz[3], matriz[0])

    def diferenca_angular(a, b):
        """Calcula a diferença entre ângulos no intervalo de -pi a pi."""
        return math.atan2(math.sin(a - b), math.cos(a - b))

    try:
        # Testa os comandos de teclado que alimentam o controlador real.
        casos = [([], "parar"), ([ord(" "), ord("W")], "parar"),
                 ([ord("W"), ord("S")], "parar"), ([ord("Q")], "parar"),
                 ([ord("W"), Keyboard.UP], "frente")]
        for letra, seta, esperado in [("W", Keyboard.UP, "frente"),
                                      ("S", Keyboard.DOWN, "re"),
                                      ("A", Keyboard.LEFT, "esquerda"),
                                      ("D", Keyboard.RIGHT, "direita")]:
            casos.extend([([ord(letra)], esperado), ([seta], esperado),
                          ([ord(letra) | Keyboard.SHIFT], esperado)])
        for teclas, esperado in casos:
            assert comando_das_teclas(teclas) == esperado, (teclas, esperado)
        print("PASS: mapeamento de teclado, soltar, espaco e conflitos", flush=True)

        avancar(0.5)
        resultados = Path(__file__).resolve().parents[2] / "test-results"
        resultados.mkdir(exist_ok=True)
        robot.exportImage(str(resultados / "etapa1.png"), 100)
        x0, y0, ang0 = pose()
        avancar(0.5)
        x1, y1, ang1 = pose()
        assert math.hypot(x1 - x0, y1 - y0) < 0.005, "Inicio nao ficou parado"
        print("PASS: inicia parado", flush=True)

        for comando in ("frente", "re", "esquerda", "direita"):
            x0, y0, ang0 = pose()
            carrinho.mover(comando)
            avancar(1.0)
            carrinho.mover("parar")
            avancar(0.25)
            x1, y1, ang1 = pose()
            dx, dy = x1 - x0, y1 - y0
            # Mede o deslocamento em relação à frente inicial do carrinho.
            longitudinal = dx * math.cos(ang0) + dy * math.sin(ang0)
            lateral = -dx * math.sin(ang0) + dy * math.cos(ang0)
            giro = diferenca_angular(ang1, ang0)
            if comando in ("frente", "re"):
                sinal = 1 if comando == "frente" else -1
                assert 0.10 < sinal * longitudinal < 0.26, (comando, longitudinal)
                assert abs(lateral) < 0.02 and abs(giro) < 0.1, (lateral, giro)
            else:
                sinal = 1 if comando == "esquerda" else -1
                assert 0.8 < sinal * giro < 2.5, (comando, giro)
                assert math.hypot(dx, dy) < 0.04, "Giro deslocou demais o centro"
            print(f"PASS: {comando}: deslocamento={longitudinal:.3f} m, giro={giro:.3f} rad", flush=True)

            # Confirma a parada física depois de cada movimento, inclusive giros.
            avancar(0.5)
            x2, y2, ang2 = pose()
            assert math.hypot(x2 - x1, y2 - y1) < 0.005, "Deslocamento apos parar"
            assert abs(diferenca_angular(ang2, ang1)) < 0.02, "Giro apos parar"
            print(f"PASS: parar apos {comando}", flush=True)
        print("RESULTADO: TODOS OS TESTES PASSARAM", flush=True)
        robot.simulationQuit(0)
    except Exception:
        carrinho.mover("parar")
        traceback.print_exc()
        print("RESULTADO: FALHA", flush=True)
        robot.simulationQuit(1)
    robot.step(passo)


if __name__ == "__main__":
    main()
