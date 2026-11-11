"""Seguimento diferencial em Python puro; recebe pose ideal, devolve rad/s.

Não importa Webots, não calcula buscas e nunca altera a posição do robô.
Geometria: frente +X, esquerda +Y, Z para cima; motores positivos avançam.
"""
import math

from grade_navegacao import segmento_intercepta_retangulo

MARGEM_TRAJETO = .06  # Além do raio conservador + folga de 5 cm da grade.
CORREDOR = .035      # Desvio máximo do centro em relação ao segmento planejado.
TOLERANCIA = .01


def angulo(a):
    return math.atan2(math.sin(a), math.cos(a))


def distancia_segmento(p, a, b):
    dx, dy = b[0]-a[0], b[1]-a[1]
    d2 = dx*dx+dy*dy
    t = max(0., min(1., ((p[0]-a[0])*dx+(p[1]-a[1])*dy)/d2)) if d2 else 0.
    return math.dist(p, (a[0]+t*dx, a[1]+t*dy))


def segmento_seguro(grade, a, b, margem=MARGEM_TRAJETO):
    """Recorte exato, incluindo borda do piso e reserva para erro de controle."""
    if not all(math.isfinite(v) for p in (a, b) for v in p):
        return False
    r, p = grade.raio+margem, grade.piso
    if any(not (p['x_min']+r < x < p['x_max']-r and
                p['y_min']+r < y < p['y_max']-r) for x, y in (a, b)):
        return False
    return not any(segmento_intercepta_retangulo(a, b, (xa-margem, xb+margem, ya-margem, yb+margem))
                   for _, (xa, xb, ya, yb) in grade.retangulos)


def pontos_da_rota(grade, resultado):
    """Inclui os dois conectores e todos os centros; não simplifica esquinas."""
    if not resultado['caminho']:
        raise ValueError('SEM ROTA: calcule um caminho antes de iniciar.')
    inicio, fim = resultado['posicao_inicial'], resultado['ponto_final']
    # A física produz micromovimentos mesmo após reposicionar e estabilizar.
    # Já estar dentro da tolerância de chegada não exige ir ao centro e voltar.
    if math.dist(inicio, fim) <= TOLERANCIA:
        pontos = [tuple(fim)]
    else:
        pontos = [tuple(inicio)]
        for ponto in [grade.celulas[n].centro for n in resultado['caminho']] + [fim]:
            if math.dist(pontos[-1], ponto) > 1e-8:
                pontos.append(tuple(ponto))
    segmentos = list(zip(pontos, pontos[1:])) or [(pontos[0], pontos[0])]
    if not all(segmento_seguro(grade, a, b) for a, b in segmentos):
        raise ValueError('Rota sem margem adicional de rastreamento; escolha outra origem/destino.')
    return pontos


class Seguidor:
    ATIVOS = ('girando', 'avançando', 'estabilizando')

    def __init__(self, grade):
        self.grade = grade
        self.raio_roda = .06*grade.config.robo['escala']
        self.bitola = .20*grade.config.robo['escala']
        self.pontos = []
        self.estado = 'parado'
        self.motivo = ''
        self.tempo_s = 0.
        self.comando = (0., 0.)
        self.indice = 0
        self.erro_final = None
        self._velocidade = 0.

    def parar(self, motivo='Parado. Enter para recalcular.'):
        self.estado, self.motivo = 'parado', motivo
        self.pontos = []
        return self._zero()

    def _zero(self):
        self.comando = (0., 0.)
        self._velocidade = 0.
        return self.comando

    def falhar(self, motivo):
        self.estado, self.motivo = 'falha', motivo
        return self._zero()

    def iniciar(self, resultado, pose, agora):
        self.parar()
        try:
            pontos = pontos_da_rota(self.grade, resultado)
            if math.dist(pose[:2], pontos[0]) > TOLERANCIA:
                raise ValueError('Posição mudou desde a busca. Enter para recalcular.')
            if not segmento_seguro(self.grade, pose[:2], pontos[min(1, len(pontos)-1)], .02):
                raise ValueError('Conector atual inseguro. Recalcule a busca.')
        except ValueError as erro:
            self.falhar(str(erro))
            raise
        self.pontos, self.indice = pontos, min(1, len(pontos)-1)
        self.tempo_s, self.erro_final = 0., None
        self._ultimo_tempo = agora
        self._reiniciar_progresso(agora)
        self.estado = 'girando' if len(pontos) > 1 else 'concluído'
        self.motivo = 'Navegação iniciada.' if len(pontos) > 1 else 'Chegou: origem igual ao destino.'
        if len(pontos) == 1:
            self.erro_final = math.dist(pose[:2], pontos[-1])
        return self._zero()

    def pausar(self):
        if self.estado in self.ATIVOS:
            self.estado, self.motivo = 'pausado', 'Pausado. C retoma; espaço para.'
        return self._zero()

    def retomar(self, agora):
        if self.estado == 'pausado':
            self.estado, self.motivo = 'girando', 'Navegação retomada.'
            self._ultimo_tempo = agora
            self._reiniciar_progresso(agora)

    def _reiniciar_progresso(self, agora):
        self._melhor = float('inf')
        self._progresso = agora
        self._modo_progresso = None

    def atualizar(self, pose, agora):
        if self.estado not in self.ATIVOS:
            return self._zero()
        if not all(math.isfinite(v) for v in (*pose, agora)):
            return self.falhar('Localização inválida.')
        dt = agora-self._ultimo_tempo
        self._ultimo_tempo = agora
        if not 0 <= dt <= .1:
            return self.falhar('Intervalo de controle inválido (> 100 ms).')
        self.tempo_s += dt
        p, alvo = pose[:2], self.pontos[self.indice]
        distancia = math.dist(p, alvo)
        self.erro_final = math.dist(p, self.pontos[-1])
        if distancia_segmento(p, self.pontos[self.indice-1], alvo) > CORREDOR:
            return self.falhar('Desvio do corredor seguro.')
        # Confere também a ligação real ao alvo após a tolerância de uma esquina.
        if not segmento_seguro(self.grade, p, alvo, .02):
            return self.falhar('Posição ou segmento atual sem margem segura.')
        if self.estado == 'estabilizando':
            if agora-self._parada >= .192:
                if distancia > .02:
                    return self.falhar('Deriva durante a parada no alvo.')
                if self.indice == len(self.pontos)-1:
                    self.estado, self.motivo = 'concluído', 'Chegou ao destino. Motores parados.'
                else:
                    self.indice += 1
                    self.estado = 'girando'
                    self._reiniciar_progresso(agora)
            return self._zero()
        if distancia <= TOLERANCIA:
            self.estado, self._parada = 'estabilizando', agora
            return self._zero()
        erro = angulo(math.atan2(alvo[1]-p[1], alvo[0]-p[0])-pose[2])
        if self.estado == 'girando' and abs(erro) < .025:
            self.estado = 'avançando'
        elif self.estado == 'avançando' and abs(erro) > .18:
            self.estado = 'girando'
        medida = abs(erro) if self.estado == 'girando' else distancia
        if self._modo_progresso != self.estado:
            self._reiniciar_progresso(agora)
            self._modo_progresso = self.estado
        if medida < self._melhor-.002:
            self._melhor, self._progresso = medida, agora
        if agora-self._progresso > 8.:
            return self.falhar('Sem progresso por 8 segundos; verifique o percurso.')
        if self.estado == 'girando':
            v = 0.
            w = max(-.65, min(.65, 2.5*erro))
        else:
            v = min(.32, 1.4*distancia, self._velocidade+.4*dt)
            w = max(-.5, min(.5, 3.*erro))
        self._velocidade = v
        self.comando = ((v-w*self.bitola/2)/self.raio_roda,
                        (v+w*self.bitola/2)/self.raio_roda)
        return self.comando
