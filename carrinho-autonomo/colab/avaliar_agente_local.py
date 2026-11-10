"""Reexecuta os 15 casos com os pesos locais do Qwen, fora do Colab.

Da raiz do projeto:
    HF_HUB_OFFLINE=1 .venv/bin/python colab/avaliar_agente_local.py

Esta medição usa o modelo real e pode demorar vários minutos em CPU. Os testes
unitários não a executam, porque verificam o código sem baixar pesos do modelo.
"""

import argparse
import json
import os
from pathlib import Path
import sys

# O modelo já deve estar no cache local. Definir antes de carregar Transformers
# evita uma consulta à rede em ambientes onde o modelo foi baixado previamente.
os.environ.setdefault("HF_HUB_OFFLINE", "1")
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))  # Permite importar colab e servidor_qwen ao rodar como arquivo.

from colab.agente_marco2 import PROMPTS, agente, avaliar_caso  # noqa: E402
from colab.casos_marco2 import CASOS  # noqa: E402
from servidor_qwen import carregar_modelo  # noqa: E402


def executar(versao, saida):
    import torch

    tokenizador, qwen, dispositivo = carregar_modelo()

    def conversar(mensagens, ferramentas):
        # Esta é a mesma geração usada no notebook portátil. A ficha das
        # funções entra pelo chat template; somente o Python as executa.
        entrada = tokenizador.apply_chat_template(
            mensagens, tools=ferramentas, add_generation_prompt=True,
            return_tensors="pt", return_dict=True,
        ).to(dispositivo)
        with torch.no_grad():
            saida_modelo = qwen.generate(
                **entrada, max_new_tokens=180, do_sample=False,
                pad_token_id=tokenizador.eos_token_id,
            )
        novos = saida_modelo[0][entrada["input_ids"].shape[-1]:]
        return tokenizador.decode(novos, skip_special_tokens=True).strip()

    linhas = []
    for caso in CASOS:
        execucao = agente(caso["pedido"], conversar, versao=versao)
        avaliacao = avaliar_caso(caso, execucao)
        linhas.append({"caso": caso, "execucao": execucao, "avaliacao": avaliacao})
        print(caso["id"], "ferramenta:", avaliacao["ferramenta_ok"],
              "argumentos:", avaliacao["argumentos_ok"],
              "fidelidade:", avaliacao["fidelidade"],
              "recusa:", avaliacao["recusa_ok"], flush=True)

    # O arquivo preserva perguntas, expectativas e respostas brutas. Assim o
    # trio pode revisar cada classificação e não depende só de uma taxa geral.
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(json.dumps({
        "modelo": "Qwen/Qwen2.5-1.5B-Instruct", "dispositivo": dispositivo,
        "versao": versao, "max_new_tokens": 180, "casos": linhas,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Registro:", saida)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--versao", choices=PROMPTS, default="v9")
    parser.add_argument("--saida", type=Path,
                        default=Path("test-results/agente-marco2-local.json"))
    argumentos = parser.parse_args()
    executar(argumentos.versao, argumentos.saida)
