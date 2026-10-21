"""Etapa 1: movimento diferencial pelo teclado, sem sensores."""

from controller import Keyboard, Robot


# Velocidade angular dos motores em radianos por segundo.
# Na escala 1, o carrinho anda a cerca de 0,18 m/s; na escala 3, a 0,54 m/s.
VELOCIDADE = 3.0
# Cada comando define as velocidades (motor esquerdo, motor direito).
# Sinais iguais fazem andar; sinais opostos fazem girar no próprio eixo.
MOVIMENTOS = {
    "frente": (VELOCIDADE, VELOCIDADE),
    "re": (-VELOCIDADE, -VELOCIDADE),
    "esquerda": (-VELOCIDADE, VELOCIDADE),
    "direita": (VELOCIDADE, -VELOCIDADE),
    "parar": (0.0, 0.0),
}
# As letras e as setas acionam os mesmos movimentos.
TECLAS = {
    ord("W"): "frente", Keyboard.UP: "frente",
    ord("S"): "re", Keyboard.DOWN: "re",
    ord("A"): "esquerda", Keyboard.LEFT: "esquerda",
    ord("D"): "direita", Keyboard.RIGHT: "direita",
}


def comando_das_teclas(teclas):
    """Para quando não há direção, há espaço ou há direções conflitantes."""
    # Mantém o código da tecla e remove os indicadores de Shift, Ctrl e Alt.
    teclas = {tecla & Keyboard.KEY for tecla in teclas}
    if ord(" ") in teclas:
        return "parar"
    comandos = {TECLAS[tecla] for tecla in teclas if tecla in TECLAS}
    return comandos.pop() if len(comandos) == 1 else "parar"


class Carrinho:
    """Envia comandos aos motores e disponibiliza leitura dos sensores embarcados."""

    def __init__(self, robot):
        self.robot = robot
        self.passo = int(robot.getBasicTimeStep())
        self.esquerdo = robot.getDevice("motor_esquerdo")
        self.direito = robot.getDevice("motor_direito")
        for motor in (self.esquerdo, self.direito):
            # Posição infinita ativa o controle contínuo por velocidade.
            motor.setPosition(float("inf"))
            motor.setVelocity(0.0)

        # Encoders das rodas
        self.encoder_esq = robot.getDevice("encoder_esquerdo")
        self.encoder_dir = robot.getDevice("encoder_direito")
        if self.encoder_esq:
            self.encoder_esq.enable(self.passo)
        if self.encoder_dir:
            self.encoder_dir.enable(self.passo)

        # Sensores de localização e atitude
        self.gps = robot.getDevice("gps")
        if self.gps:
            self.gps.enable(self.passo)
        self.imu = robot.getDevice("imu")
        if self.imu:
            self.imu.enable(self.passo)

        # Sensores de distância (proximidade / obstáculos)
        self.sensores_distancia = {}
        for nome in ("ds_frente", "ds_esquerda", "ds_direita"):
            ds = robot.getDevice(nome)
            if ds:
                ds.enable(self.passo)
                self.sensores_distancia[nome] = ds

    def mover(self, comando):
        """Aplica a velocidade correspondente a cada roda."""
        esquerda, direita = MOVIMENTOS[comando]
        self.esquerdo.setVelocity(esquerda)
        self.direito.setVelocity(direita)


def main():
    """Lê o teclado a cada passo da simulação e atualiza os motores."""
    robot = Robot()
    # O intervalo de atualização é o passo do mundo, em milissegundos.
    passo = int(robot.getBasicTimeStep())
    carrinho = Carrinho(robot)
    teclado = robot.getKeyboard()
    teclado.enable(passo)
    print("Pronto. Clique na cena 3D e segure W/S/A/D ou as setas.", flush=True)
    print("Soltar as teclas ou pressionar ESPACO = parar. Faixa amarela = frente.", flush=True)
    anterior = None
    while robot.step(passo) != -1:
        # Reúne todas as teclas deste passo para detectar comandos conflitantes.
        teclas = []
        tecla = teclado.getKey()
        while tecla != -1:
            teclas.append(tecla)
            tecla = teclado.getKey()
        comando = comando_das_teclas(teclas)
        # Sem tecla de direção pressionada, o comando resultante é parar.
        carrinho.mover(comando)
        # Registra apenas mudanças de comando para não repetir mensagens.
        if comando != anterior:
            print("Comando:", comando, flush=True)
            anterior = comando


if __name__ == "__main__":
    main()
