"""Percurso físico pelos dez interiores, sem reposicionar entre destinos."""
import json
import math
from pathlib import Path
import sys
import traceback
from controller import Supervisor

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / 'controllers/carrinho_buscas'))
from carrinho_buscas import PainelBusca
from planejamento import alvo_do_clique


def main():
    robot = Supervisor()
    painel = PainelBusca(robot)
    s = painel.seguidor
    pasta = RAIZ / 'test-results/interiores'
    pasta.mkdir(parents=True, exist_ok=True)
    registros = []
    obstaculos = [robot.getFromDef(c['id']) for c in painel.grade.caixas]
    for node in obstaculos:
        assert node is not None
        node.enableContactPointsTracking(painel.passo)

    def passo():
        assert robot.step(painel.passo) != -1
        painel.atualizar(ler_entrada=False)
        for node in obstaculos:
            assert not node.getContactPoints(), f'Contato: {node.getDef()}'

    def ir(destino, nome, setor=None):
        inicio = painel.pose()[:2]
        painel.selecionar(destino)
        painel.tecla(4)
        painel.tecla(ord('G'))
        for _ in range(25000):
            passo()
            if s.estado not in s.ATIVOS:
                break
        assert s.estado == 'concluído', (nome, s.estado, s.motivo, painel.pose())
        for _ in range(16):
            passo()
        final = painel.pose()[:2]
        erro = math.dist(final, painel.resultado['ponto_final'])
        assert erro < .02, (nome, erro)
        assert painel.carrinho.esquerdo.getVelocity() == painel.carrinho.direito.getVelocity() == 0
        if setor:
            x, y = setor['centro']
            assert abs(final[0]-x) < .02 and abs(final[1]-y) < .02
        registro = dict(trecho=nome, destino=destino, inicio=inicio, final=final,
                        erro_final_m=erro, tempo_movimento_s=s.tempo_s,
                        tempo_busca_ms=painel.resultado['tempo_ms'], contatos=0,
                        motores_finais=[0, 0])
        registros.append(registro)
        (pasta / 'resultados.json').write_text(json.dumps(registros, ensure_ascii=False, indent=2), encoding='utf-8')
        print('PASS INTERIOR: ' + json.dumps(registro, ensure_ascii=False), flush=True)

    try:
        for _ in range(16):
            passo()
        robot.exportImage(str(pasta / 'campus_ampliado.png'), 100)
        # Circuito contínuo: chega pelo nome, circula dentro e sai para outro setor.
        setores = {s['id']: s for s in painel.grade.config.setores}
        ordem = ['BLOCO_H', 'BLOCO_F', 'BLOCO_J', 'CANTINA', 'ATENDIMENTO',
                 'BIBLIOTECA', 'BLOCO_E', 'BLOCO_B', 'BLOCO_C', 'BLOCO_D']
        for ident in ordem:
            setor = setores[ident]
            x, y = setor['centro']
            assert alvo_do_clique(painel.grade, x, y+1.8) == painel.grade.config.destinos_setores[ident]
            ir(setor['nome'], ident + ': chegada ao centro', setor)
            if ident == 'BLOCO_H':
                robot.exportImage(str(pasta / 'chegada_bloco_h.png'), 100)
            # Quadrado de 2 x 2 m totalmente interno: quatro posições e giros.
            for i, (dx, dy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1)), 1):
                celula = painel.grade.mundo_para_celula(x+dx, y+dy)
                ir(celula, f'{ident}: circulação {i}')
        ir('EXT01', 'Retorno à entrada')
        print('RESULTADO INTERIORES: TODOS OS 10 SETORES E CIRCULACAO INTERNA APROVADOS', flush=True)
        robot.simulationQuit(0)
    except Exception:
        painel.carrinho.mover('parar')
        traceback.print_exc()
        robot.simulationQuit(1)
    robot.step(painel.passo)


if __name__ == '__main__':
    main()
