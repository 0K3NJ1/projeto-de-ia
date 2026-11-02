"""Ponte entre o controlador do Webots e o programa separado do Qwen.

Este arquivo NÃO importa torch nem transformers. Ele só:
  1. transforma o resultado do planejar() em dados para explicar;
  2. reaproveita montar_mensagens() de colab/rotas_comentadas.py (mesmo prompt
     do notebook comentado);
  3. inicia o servidor_qwen.py em outro processo e troca mensagens com ele,
     sem nunca esperar a resposta dentro do ciclo de controle.

Lembrete: o Qwen apenas explica. Distâncias e caminho vêm sempre do A*.
"""
import json
import os
import queue
import subprocess
import sys
import threading
from pathlib import Path

from colab.rotas_comentadas import montar_mensagens

RAIZ = Path(__file__).resolve().parent
SERVIDOR = RAIZ / "servidor_qwen.py"
# Avisos e erros do programa do modelo vão para este arquivo, e não para
# o console do Webots, para não esconder as mensagens da navegação.
REGISTRO = RAIZ / ".cache" / "servidor_qwen.log"

# Distância (m) para dizer que o carrinho está "em" um local cadastrado.
# A física do Webots deixa pequenas diferenças de milímetros após parar.
TOLERANCIA_LOCAL_M = 0.05


def nome_do_ponto(grade, ponto, tolerancia=TOLERANCIA_LOCAL_M):
    """Devolve o nome do local cadastrado mais próximo, ou None se estiver longe."""
    for identificador, (x, y) in grade.config.pontos.items():
        # Teorema de Pitágoras: distância entre o ponto e o local cadastrado.
        distancia = ((ponto[0] - x) ** 2 + (ponto[1] - y) ** 2) ** 0.5
        if distancia <= tolerancia:
            return grade.config.nomes[identificador]
    return None


def rota_para_explicar(grade, resultado):
    """Converte o resultado do planejar() do Webots no formato do notebook.

    O formato é o mesmo de calcular_rota() em colab/rotas_comentadas.py,
    para que montar_mensagens() funcione sem nenhuma alteração.
    No simulador, a origem é a POSIÇÃO ATUAL do carrinho, que pode estar
    entre dois locais. Nesse caso, descrevemos a posição em vez de inventar
    um nome. O carrinho nunca é reposicionado por esta função.
    """
    if resultado["caminho"] is None:
        raise ValueError("Não há rota para explicar neste mapa.")

    # Origem: nome cadastrado, se o carrinho estiver em cima dele.
    x, y = resultado["posicao_inicial"]
    nome_origem = nome_do_ponto(grade, (x, y))
    if nome_origem is None:
        origem = f"Posição atual do carrinho (x = {x:.2f} m; y = {y:.2f} m), fora dos locais cadastrados"
    else:
        origem = f"{nome_origem} (posição atual do carrinho)"

    # Destino: nome cadastrado ou, se o usuário digitou uma célula, o ID dela.
    nome_destino = nome_do_ponto(grade, resultado["ponto_final"], tolerancia=1e-6)
    destino = nome_destino or f"Célula {resultado['destino']} (sem nome cadastrado)"

    # Mesmos campos e nomes do notebook. Não arredondamos as distâncias aqui.
    return {
        "status": "ok",
        "mapa": "Campus provisório de 50 x 30 m (mapa antigo)",
        "origem": origem,
        "destino": destino,
        "algoritmo": resultado["algoritmo"],
        "caminho": resultado["caminho"],
        "distancia_grade_m": resultado["custo_m"],
        "conectores_m": resultado["conectores_m"],
        "distancia_total_m": resultado["percurso_total_m"],
    }


def mensagens_da_rota(grade, resultado):
    """Atalho: resultado do Webots -> conversa pronta para o Qwen."""
    return montar_mensagens(rota_para_explicar(grade, resultado))


class ExplicadorQwen:
    """Controla o programa separado do Qwen sem travar a simulação.

    Ideia principal: o controlador ENVIA um pedido e segue em frente.
    Uma "thread" (linha de execução auxiliar) fica esperando as respostas
    e as coloca em uma fila. A cada passo, o controlador olha a fila
    rapidamente com respostas(); se estiver vazia, continua normalmente.
    """

    def __init__(self, comando=None):
        # comando permite trocar o programa nos testes automáticos.
        self.comando = comando or [sys.executable, str(SERVIDOR)]
        self.processo = None
        self.fila = queue.Queue()
        self.estado = "desligado"  # desligado, carregando, pronto, indisponível
        self.pendentes = set()     # números dos pedidos ainda sem resposta
        self.erro = ""

    def iniciar(self):
        """Abre o programa do modelo. Não espera o carregamento terminar."""
        try:
            REGISTRO.parent.mkdir(parents=True, exist_ok=True)
            # Garante que nada será baixado da internet durante a simulação.
            ambiente = dict(os.environ, HF_HUB_OFFLINE="1", TOKENIZERS_PARALLELISM="false")
            # "with" fecha o arquivo aqui; o processo filho fica com a sua cópia.
            with open(REGISTRO, "w", encoding="utf-8") as registro:
                # stdin/stdout viram "canos" (pipes) para trocar as linhas JSON.
                self.processo = subprocess.Popen(
                    self.comando, cwd=RAIZ, env=ambiente, text=True, encoding="utf-8",
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=registro,
                )
        except OSError as erro:
            self.estado, self.erro = "indisponível", str(erro)
            return
        self.estado = "carregando"
        # daemon=True: a thread não impede o controlador de encerrar.
        threading.Thread(target=self._ler_respostas, daemon=True).start()

    def _ler_respostas(self):
        """Roda na thread auxiliar: espera linhas do Qwen e as põe na fila."""
        for linha in self.processo.stdout:
            try:
                self.fila.put(json.loads(linha))
            except json.JSONDecodeError:
                continue  # Linha estranha: ignoramos em vez de quebrar o controle.
        # O laço acaba quando o programa do modelo fecha (fim ou falha).
        self.fila.put({"tipo": "encerrado"})

    def pedir(self, numero, mensagens):
        """Envia um pedido numerado. Devolve False se o Qwen não puder receber."""
        if self.estado not in ("carregando", "pronto"):
            return False
        try:
            self.processo.stdin.write(json.dumps({"id": numero, "mensagens": mensagens},
                                                 ensure_ascii=False) + "\n")
            self.processo.stdin.flush()
        except (BrokenPipeError, OSError, ValueError) as erro:
            self.estado, self.erro = "indisponível", str(erro)
            return False
        self.pendentes.add(numero)
        return True

    def respostas(self):
        """Devolve, sem esperar, todas as mensagens que já chegaram."""
        chegadas = []
        while True:
            try:
                mensagem = self.fila.get_nowait()
            except queue.Empty:
                break
            tipo = mensagem.get("tipo")
            if tipo == "pronto":
                self.estado = "pronto"
            elif tipo in ("falha_carregamento", "encerrado"):
                # Guardamos a PRIMEIRA causa: o aviso de "encerrado" que vem
                # depois de uma falha não deve esconder o motivo verdadeiro
                # nem repetir o mesmo aviso no console.
                if self.estado == "indisponível":
                    continue
                self.erro = mensagem.get("erro", "programa do Qwen encerrado")
                self.estado = "indisponível"
                self.pendentes.clear()
            else:
                self.pendentes.discard(mensagem.get("id"))
            chegadas.append(mensagem)
        return chegadas

    def descricao(self):
        """Texto curto para o painel da cena."""
        if self.estado == "pronto" and self.pendentes:
            return "gerando explicação"
        return self.estado

    def encerrar(self):
        """Fecha o programa do modelo ao sair da simulação."""
        if self.processo is None or self.processo.poll() is not None:
            return
        try:
            self.processo.stdin.close()  # O servidor termina ao ver a entrada fechada.
            self.processo.wait(timeout=3)
        except Exception:
            self.processo.kill()
