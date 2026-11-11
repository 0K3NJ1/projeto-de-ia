"""Programa SEPARADO que carrega o Qwen e escreve explicações de rotas.

Por que um programa separado?
    Carregar o modelo leva vários segundos e gerar o texto também demora.
    Se isso acontecesse dentro do controlador do Webots, a simulação ficaria
    congelada nesse tempo e as teclas de parada (espaço, C) não seriam lidas.
    Com dois programas, o controlador continua o ciclo de controle normalmente:
    ele apenas envia um pedido e, mais tarde, lê a resposta quando ela chegar.

Como os dois programas conversam (uma linha de texto JSON por mensagem):
    controlador -> este programa (entrada padrão, stdin):
        {"id": 3, "mensagens": [...]}
    este programa -> controlador (saída padrão, stdout):
        {"tipo": "pronto", "dispositivo": "cuda"}
        {"tipo": "explicacao", "id": 3, "texto": "...", "segundos": 1.2}
        {"tipo": "erro", "id": 3, "erro": "..."}
        {"tipo": "falha_carregamento", "erro": "..."}

O Qwen NÃO calcula rotas aqui. Ele recebe os dados já calculados pelo A*
(preparados por colab/rotas_comentadas.py) e só escreve a explicação.

Comandos úteis, executados na pasta do projeto:
    .venv/bin/python servidor_qwen.py --baixar    # baixa o modelo uma vez (~3 GB)
    .venv/bin/python servidor_qwen.py --exemplo   # explica Entrada IESB -> Biblioteca
"""
import json
import sys
import time
from pathlib import Path

# Mesmo modelo do Laboratório 7 e do notebook comentado.
NOME_MODELO = "Qwen/Qwen2.5-1.5B-Instruct"

# Os pesos ficam dentro do projeto, na pasta .cache (já ignorada pelo Git).
# Assim sabemos exatamente onde estão os ~3 GB e podemos apagá-los depois.
PASTA_MODELOS = Path(__file__).resolve().parent / ".cache" / "huggingface"

# Limite de tokens NOVOS na resposta (tokens são pedaços de palavras).
MAX_TOKENS = 180


def enviar(saida, dados):
    """Escreve uma mensagem JSON em uma única linha e entrega imediatamente."""
    # ensure_ascii=False mantém os acentos; json escapa as quebras de linha,
    # então cada mensagem ocupa sempre exatamente uma linha.
    saida.write(json.dumps(dados, ensure_ascii=False) + "\n")
    # flush envia agora, sem esperar o "buffer" encher.
    saida.flush()


def baixar_modelo():
    """Baixa os arquivos do modelo para PASTA_MODELOS. Exige internet."""
    from huggingface_hub import snapshot_download

    caminho = snapshot_download(NOME_MODELO, cache_dir=PASTA_MODELOS)
    print("Modelo disponível em:", caminho)


def carregar_modelo():
    """Carrega tokenizador e modelo, usando a GPU NVIDIA quando existir."""
    # Importamos aqui dentro: só este programa precisa de torch/transformers.
    # O controlador do Webots continua funcionando mesmo sem essas bibliotecas.
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    # CUDA permite usar a GPU NVIDIA. Sem ela, usamos o processador (CPU).
    if torch.cuda.is_available():
        dispositivo = "cuda"
        tipo_numerico = torch.float16  # Metade da memória: cabe nos 6 GB da RTX 3050.
    else:
        dispositivo = "cpu"
        tipo_numerico = torch.float32  # Opção simples e segura para CPU.

    # local_files_only=True: nunca baixa nada durante a simulação.
    # Se o modelo não estiver baixado, o erro avisa como baixar (--baixar).
    tokenizador = AutoTokenizer.from_pretrained(
        NOME_MODELO, cache_dir=PASTA_MODELOS, local_files_only=True)
    qwen = AutoModelForCausalLM.from_pretrained(
        NOME_MODELO, cache_dir=PASTA_MODELOS, local_files_only=True,
        dtype=tipo_numerico,
    ).to(dispositivo)
    # eval ativa o modo de uso. Aqui NÃO estamos treinando o modelo.
    qwen.eval()
    return tokenizador, qwen, dispositivo


def conversar(tokenizador, qwen, dispositivo, mensagens, max_tokens=MAX_TOKENS):
    """Recebe a conversa e devolve só o texto novo do Qwen (como no Lab 7)."""
    import torch

    # O template organiza os papéis (system/user) no formato que o Qwen aprendeu.
    # add_generation_prompt marca onde começa a resposta do assistente.
    entrada = tokenizador.apply_chat_template(
        mensagens,
        add_generation_prompt=True,
        return_tensors="pt",
        return_dict=True,
    ).to(dispositivo)

    # Sem treinamento, não precisamos guardar os cálculos de gradiente.
    with torch.no_grad():
        saida = qwen.generate(
            **entrada,
            max_new_tokens=max_tokens,
            do_sample=False,  # Sem sorteio: a mesma entrada gera a mesma resposta.
            pad_token_id=tokenizador.eos_token_id,
        )

    # generate devolve a pergunta seguida da resposta; guardamos só a resposta.
    tamanho_da_pergunta = entrada["input_ids"].shape[-1]
    resposta = tokenizador.decode(saida[0][tamanho_da_pergunta:], skip_special_tokens=True)
    return resposta.strip()


def exemplo():
    """Execução direta, sem Webots: A* calcula Entrada IESB -> Biblioteca e o Qwen explica."""
    from colab.rotas_comentadas import calcular_rota, montar_mensagens

    rota = calcular_rota("Entrada IESB", "Biblioteca")
    print("Dados calculados pelo A* (referência):")
    print(f"  {rota['origem']} -> {rota['destino']}, total {rota['distancia_total_m']:.2f} m")
    inicio = time.perf_counter()
    tokenizador, qwen, dispositivo = carregar_modelo()
    print(f"Modelo carregado em {dispositivo} ({time.perf_counter() - inicio:.1f} s)")
    inicio = time.perf_counter()
    texto = conversar(tokenizador, qwen, dispositivo, montar_mensagens(rota))
    print(f"Explicação do Qwen ({time.perf_counter() - inicio:.1f} s):")
    print(texto)


def servir():
    """Modo usado pelo Webots: carrega uma vez e responde pedido por pedido."""
    # Guardamos a saída verdadeira só para as mensagens JSON.
    # Avisos das bibliotecas (print) passam a ir para o registro de erros (stderr),
    # para não misturar texto solto no meio da comunicação.
    saida = sys.stdout
    sys.stdout = sys.stderr

    try:
        tokenizador, qwen, dispositivo = carregar_modelo()
    except Exception as erro:  # Qualquer falha aqui deixa só o Qwen indisponível.
        enviar(saida, {"tipo": "falha_carregamento", "erro": f"{type(erro).__name__}: {erro}"})
        return 1
    enviar(saida, {"tipo": "pronto", "dispositivo": dispositivo})

    # Cada linha recebida é um pedido. Quando o controlador fecha a entrada
    # (por exemplo, ao encerrar a simulação), o laço termina sozinho.
    for linha in sys.stdin:
        if not linha.strip():
            continue
        pedido = {}
        try:
            pedido = json.loads(linha)
            inicio = time.perf_counter()
            texto = conversar(tokenizador, qwen, dispositivo, pedido["mensagens"])
            enviar(saida, {"tipo": "explicacao", "id": pedido["id"], "texto": texto,
                           "segundos": round(time.perf_counter() - inicio, 3)})
        except Exception as erro:  # Um pedido com problema não derruba o programa.
            enviar(saida, {"tipo": "erro", "id": pedido.get("id"),
                           "erro": f"{type(erro).__name__}: {erro}"})
    return 0


if __name__ == "__main__":
    if "--baixar" in sys.argv:
        baixar_modelo()
    elif "--exemplo" in sys.argv:
        exemplo()
    else:
        sys.exit(servir())

