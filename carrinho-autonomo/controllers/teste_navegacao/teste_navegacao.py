"""Ensaio físico isolado: percorre rotas e encerra somente esta simulação."""
import json
import math
from pathlib import Path
import sys
import traceback
from controller import Supervisor

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / 'controllers/carrinho_buscas'))
sys.path.insert(0, str(RAIZ / 'tests'))
from carrinho_buscas import PainelBusca
from navegacao import distancia_segmento
from cenarios import isolar_destino


def main():
    robot = Supervisor()
    painel = PainelBusca(robot)
    corpo, s = robot.getSelf(), painel.seguidor
    saida = RAIZ / 'test-results'
    saida.mkdir(exist_ok=True)
    resultados = []
    # Contatos das 57 caixas: todas estáticas; piso não é obstáculo.
    obstaculos = [robot.getFromDef(c['id']) for c in painel.grade.caixas]
    for node in obstaculos:
        node.enableContactPointsTracking(painel.passo)

    def passo(contatos=True):
        assert robot.step(painel.passo) != -1
        painel.atualizar(ler_entrada=False)
        if contatos:
            for node in obstaculos:
                assert not node.getContactPoints(), f'Contato com {node.getDef()}'

    def esperar(tempo):
        for _ in range(math.ceil(tempo*1000/painel.passo)):
            passo()

    def preparar(origem, destino):
        painel.selecionar(origem, origem=True)
        esperar(.5)
        painel.selecionar(destino)
        painel.tecla(4)  # Return real do Webots R2025a.
        painel.tecla(ord('F'))

    def parado():
        assert painel.carrinho.esquerdo.getVelocity() == 0
        assert painel.carrinho.direito.getVelocity() == 0
        antes = painel.pose()
        esperar(.5)
        assert math.dist(antes[:2], painel.pose()[:2]) < .005

    def percorrer(nome, origem, destino, pausa=False):
        preparar(origem, destino)
        painel.tecla(ord('G'))
        max_desvio, distancia = 0., 0.
        anterior = painel.pose()[:2]
        pausou = False
        for _ in range(30000):
            passo()
            p = painel.pose()[:2]
            distancia += math.dist(p, anterior)
            anterior = p
            max_desvio = max(max_desvio, min(distancia_segmento(p, a, b)
                for a, b in zip(s.pontos, s.pontos[1:])))
            if pausa and not pausou and s.estado == 'avançando' and s.tempo_s > 3:
                painel.tecla(ord('C'))
                t = s.tempo_s
                parado()
                esperar(1)
                assert s.tempo_s == t and s.estado == 'pausado'
                painel.tecla(ord('C'))
                pausou = True
            if s.estado not in s.ATIVOS:
                break
        assert s.estado == 'concluído', (nome, s.estado, s.motivo, painel.pose(), s.indice)
        parado()
        erro = math.dist(painel.pose()[:2], painel.resultado['ponto_final'])
        assert erro < .02
        registro = dict(caso=nome, origem=origem, destino=destino, erro_final_m=erro,
                        celula_inicial=painel.resultado['origem'], pontos=s.pontos,
                        custo_grade_m=painel.resultado['custo_m'],
                        tempo_deslocamento_s=s.tempo_s, tempo_busca_ms=painel.resultado['tempo_ms'],
                        distancia_medida_m=distancia, desvio_maximo_m=max_desvio,
                        contatos_obstaculos=0, motores_finais=[0, 0], pausa_retomada=pausou)
        resultados.append(registro)
        print('PASS NAVEGACAO:', json.dumps(registro, ensure_ascii=False), flush=True)

    try:
        percorrer('reta', 'C24L01', 'C27L01')
        percorrer('curva_90', 'C24L01', 'C25L02', pausa=True)
        percorrer('campus_com_conectores', 'EXT01', 'H01')
        robot.exportImage(str(saida / 'navegacao_chegada.png'), 100)
        grade_original = painel.grade
        painel.grade = isolar_destino(grade_original)
        preparar('EXT01', 'H01')
        try:
            painel.tecla(ord('G'))
        except ValueError:
            pass
        else:
            raise AssertionError('Sem rota iniciou movimento')
        assert s.estado == 'falha'
        parado()
        painel.grade = grade_original
        preparar('C24L01', 'C24L01')
        painel.tecla(ord('G'))
        assert s.estado == 'concluído' and s.tempo_s == 0
        parado()
        preparar('EXT01', 'H01')
        painel.tecla(ord('G'))
        esperar(4)
        painel.tecla(ord(' '))
        assert painel.resultado is None and s.estado == 'parado'
        parado()
        painel.tecla(ord('C'))
        assert s.estado == 'parado'
        for tecla in ('T', 'O'):
            preparar('EXT01', 'H01')
            painel.tecla(ord('G'))
            esperar(3)
            painel.tecla(ord(tecla))
            assert painel.resultado is None and s.estado == 'parado'
            parado()
            painel.tecla(ord('Q'))
        # Falha física de atuação: o ensaio bloqueia os comandos, sem inserir paredes.
        preparar('C24L01', 'C27L01')
        painel.tecla(ord('G'))
        for _ in range(300):
            painel.carrinho.mover('parar')
            passo()
            if s.estado == 'falha':
                break
        assert s.estado == 'falha' and 'progresso' in s.motivo
        parado()
        resultados.append(dict(caso='comandos_e_limites', sem_rota=True, origem_igual=True,
                               parada=True, edicao_invalida_rota=True, sem_progresso=True))
        (saida / 'navegacao_webots.json').write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding='utf-8')
        print('RESULTADO NAVEGACAO WEBOTS: TODOS OS TESTES PASSARAM', flush=True)
        robot.simulationQuit(0)
    except Exception:
        traceback.print_exc()
        robot.simulationQuit(1)
    robot.step(painel.passo)


if __name__ == '__main__':
    main()
