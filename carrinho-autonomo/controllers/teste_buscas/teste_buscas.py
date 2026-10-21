"""Ensaio da interface de busca e dos desenhos no Webots; encerra só esta instância."""
import json
import math
from pathlib import Path
import sys
import traceback
from controller import Supervisor

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ/"controllers/carrinho_buscas"))
sys.path.insert(0, str(RAIZ/'tests'))
from carrinho_buscas import PainelBusca
from cenarios import isolar_destino


def main():
    robot = Supervisor()
    try:
        painel = PainelBusca(robot)
        for _ in range(20):
            robot.step(painel.passo)
        inicial = tuple(robot.getSelf().getPosition())
        painel.tecla(ord("T"))
        painel.tecla(ord("C"))
        painel.tecla(ord("Q"))
        assert painel.edicao is None and painel.texto == ""
        for algoritmo in range(5):
            painel.tecla(ord("1")+algoritmo)
            painel.tecla(ord("T"))
            for letra in "C29L24":
                painel.tecla(ord(letra))
            painel.tecla(3)  # Backspace real do Webots
            painel.tecla(ord("5"))
            assert painel.texto == "C29L25"
            painel.tecla(4)  # Return real do Webots: confirma destino
            painel.tecla(5)  # Enter numérico real do Webots: executa
            assert painel.resultado['caminho']
            if algoritmo in (1, 2, 4):
                assert painel.resultado["custo_m"] == 29
            painel.tecla(ord("P"))
            assert not painel.reproduzindo
            painel.tecla(ord("N"))
            assert painel.indice == 1
            assert painel.aparencias[0].getField("transparency").getSFFloat() == 0
            painel.tecla(ord("F"))
            assert painel.indice == painel.resultado["expandidos"]
            assert robot.getFromDef("ROTA_FINAL") is not None
            robot.step(painel.passo)
            assert math.dist(inicial[:2], robot.getSelf().getPosition()[:2]) < .005
            print("PASS: seleção por texto, busca, pausa, passo e rota:", painel.resultado["algoritmo"], flush=True)
        pasta = RAIZ/"test-results"
        pasta.mkdir(exist_ok=True)
        robot.exportImage(str(pasta/"etapa3_buscas_webots.png"), 100)
        (pasta/"etapa3_busca_interativa.json").write_text(json.dumps(painel.resultado, indent=2), encoding="utf-8")
        # Não permite mascarar célula bloqueada por associação a outra célula.
        try:
            painel.selecionar("C00L00")
        except ValueError:
            pass
        else:
            raise AssertionError("Célula bloqueada foi aceita")
        grade_original = painel.grade
        painel.grade = isolar_destino(grade_original)
        painel.selecionar("H01")
        painel.executar_busca()
        painel.avancar(len(painel.aparencias))
        assert painel.resultado["caminho"] is None and "SEM ROTA" in painel.mensagem
        print("PASS: destino bloqueado recusado e grafo de ensaio desconectado sem rota", flush=True)
        painel.grade = grade_original
        painel.selecionar("C29L24", origem=True)
        robot.step(painel.passo)
        painel.selecionar("Bloco H")
        painel.executar_busca()
        assert painel.resultado["custo_m"] == 1
        painel.selecionar("C29L24")
        painel.executar_busca()
        painel.avancar()
        assert painel.resultado["custo_m"] == 0 and painel.resultado["expandidos"] == 0
        painel.tecla(ord("R"))
        robot.step(painel.passo)
        assert math.dist(robot.getSelf().getPosition()[:2], (0, 0)) < .005
        print("PASS: origem editável, origem=destino e retorno à entrada", flush=True)
        print("RESULTADO BUSCAS WEBOTS: TODOS OS TESTES PASSARAM", flush=True)
        robot.simulationQuit(0)
    except Exception:
        traceback.print_exc()
        robot.simulationQuit(1)
    robot.step(int(robot.getBasicTimeStep()))


if __name__ == "__main__":
    main()
