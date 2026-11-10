"""Gera o notebook portátil do agente com ferramentas para o Colab.

Execute da raiz: ``python3 colab/preparar_agente_marco2.py``.
As fontes são incorporadas ao notebook para que ele rode em uma sessão nova sem
montar o Drive, baixar o repositório ou depender de caminhos deste computador.
"""

import hashlib
import json
from pathlib import Path
from textwrap import dedent

RAIZ = Path(__file__).resolve().parents[1]
DESTINO = RAIZ / "colab" / "Carrinho_IESB_Agente_Marco2.ipynb"
FONTES = [
    "campus_config.py", "gerar_campus.py", "grade_navegacao.py",
    "buscas.py", "planejamento.py", "experimentos_buscas.py",
    "colab/rotas_comentadas.py", "colab/agente_marco2.py",
    "colab/casos_marco2.py",
]


def gerar():
    # Cada código fonte fica legível no projeto e também embutido no notebook.
    # Hashes permitem conferir depois exatamente qual versão foi incorporada.
    arquivos = {nome: (RAIZ / nome).read_text(encoding="utf-8") for nome in FONTES}
    hashes = {nome: hashlib.sha256((RAIZ / nome).read_bytes()).hexdigest()
              for nome in FONTES}
    celulas = []

    def texto(fonte):
        celulas.append({"cell_type": "markdown", "metadata": {},
                        "source": dedent(fonte).strip().splitlines(keepends=True)})

    def codigo(fonte, tags=None, recolher=False):
        celulas.append({"cell_type": "code",
                        "metadata": {"tags": tags or [], "cellView": "form" if recolher else "code"},
                        "execution_count": None, "outputs": [],
                        "source": dedent(fonte).strip().splitlines(keepends=True)})

    texto('''
        # Carrinho IESB — Marco 2: agente com ferramenta A*

        O usuário faz um pedido em português. O **Qwen** decide se chama
        `calcular_rota`, `listar_locais` ou nenhuma ferramenta. O código confere
        os argumentos, executa o **A estrela** existente e devolve o resultado ao
        modelo. A rota e a distância sempre vêm do Python, não do texto gerado.

        Este notebook usa o **mapa provisório de 50 × 30 m**. As distâncias são
        do cenário simulado, em metros; não são tempos de viagem ou medições
        oficiais do campus. Ele planeja rotas, mas não movimenta o Webots.

        Execute as células na ordem. Para o modelo, escolha GPU no Colab antes
        de começar. O download do Qwen exige internet; não há chave no código.
        A avaliação de 15 casos pode demorar bastante em CPU.
    ''')
    texto('''
        ## 1. Preparar os arquivos do projeto

        A célula recolhida contém cópias dos módulos Python do grupo. Ela os
        escreve numa pasta temporária da sessão e os importa. Não modifica o
        Webots, o Drive nem o repositório. Abra a célula se quiser estudar o
        código; as fontes comentadas também acompanham o projeto.
    ''')
    preparacao = '''#@title Preparar fontes do projeto (execute uma vez)
from pathlib import Path
import importlib
import sys
import tempfile

# O gerador coloca aqui as versões verificadas de cada arquivo Python.
arquivos_iesb = ''' + repr(arquivos) + '''

pasta_iesb = Path(tempfile.mkdtemp(prefix="iesb_marco2_"))
for nome, conteudo in arquivos_iesb.items():
    arquivo = pasta_iesb / nome
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(conteudo, encoding="utf-8")
(pasta_iesb / "colab" / "__init__.py").write_text("", encoding="utf-8")
sys.path.insert(0, str(pasta_iesb))
importlib.invalidate_caches()
print("Fontes disponíveis em", pasta_iesb)
'''
    codigo(preparacao, recolher=True)

    texto('''
        ## 2. Conferir o mapa e o A* antes de usar o modelo

        A função `calcular_rota` aproveita o planejamento existente. Este
        exemplo é uma referência objetiva para comparar com a resposta do Qwen.
    ''')
    codigo('''
        from colab.rotas_comentadas import calcular_rota as rota_base, grade
        from colab.agente_marco2 import (FERRAMENTAS, PROMPTS, agente,
            avaliar_caso, resposta_de_referencia)
        from colab.casos_marco2 import CASOS

        exemplo = rota_base("Entrada IESB", "Biblioteca")
        print(resposta_de_referencia(exemplo))
        print("Primeiras células:", exemplo["caminho"][:5])
        print("Ferramentas:", [f.__name__ for f in FERRAMENTAS])
        print("Prompts preservados:", list(PROMPTS))
        assert exemplo["status"] == "ok" and exemplo["distancia_grade_m"] == 15
    ''')

    texto('''
        ## 3. Mostrar o experimento comparativo do Marco 1

        Três recortes do **mesmo campus** com tamanhos diferentes. Recalculamos
        custo, expansões e tempo nesta sessão. O gráfico mostra as cinco buscas,
        mas o agente abaixo usa A*. Tempos de execução são da busca, não do
        deslocamento do carrinho. Três repetições mantêm esta demonstração curta;
        o ensaio salvo no projeto usa 31 repetições.
    ''')
    codigo('''
        import experimentos_buscas as experimento
        import campus_config as cfg
        import matplotlib.pyplot as plt

        piso = cfg.piso
        cenarios = [
            ("pequeno", (-5, 5, -2, 6), "EXT01", "EXT04"),
            ("medio", (-16, 16, -2, 17), "EXT01", "CAN01"),
            ("campus", (piso["x_min"], piso["x_max"],
                        piso["y_min"], piso["y_max"]), "EXT01", "H01"),
        ]
        comparacao = []
        for nome, limites, origem, destino in cenarios:
            mapa = grade.recorte(limites)
            linhas, _ = experimento.medir(grade, mapa, origem, destino, repeticoes=3)
            comparacao.extend({"mapa": nome, **linha} for linha in linhas)

        for linha in comparacao:
            print(f"{linha['mapa']:7} {linha['algoritmo']:14} "
                  f"custo={linha['custo_grade_m']:5.0f} m  "
                  f"expansões={linha['nos_expandidos']:4}  "
                  f"tempo={linha['tempo_mediana_ms']:.3f} ms")

        fig, eixos = plt.subplots(1, 3, figsize=(15, 4), layout="constrained")
        for eixo, campo, titulo in zip(
            eixos, ("custo_grade_m", "nos_expandidos", "tempo_mediana_ms"),
            ("Custo (m)", "Nós expandidos", "Tempo da busca (ms)")):
            for nome, *_ in cenarios:
                linhas = [r for r in comparacao if r["mapa"] == nome]
                eixo.plot([r["algoritmo"] for r in linhas], [r[campo] for r in linhas],
                          marker="o", label=nome)
            eixo.set_title(titulo)
            eixo.tick_params(axis="x", labelrotation=45)
            eixo.legend()
        plt.show()
    ''')

    texto('''
        ## 4. Carregar o Qwen

        `transformers` formata a conversa. Na v9, a primeira geração pede uma
        decisão em JSON; o Python valida o nome e os argumentos antes de chamar
        a ferramenta. A GPU acelera a geração; em CPU o mesmo código funciona
        mais devagar. O modelo público não exige token de API neste notebook.
    ''')
    codigo('''
        # A instalação é feita dentro do ambiente Python do próprio notebook.
        %pip install -q "transformers>=4.45,<5"
    ''', tags=["requer_modelo"])
    codigo('''
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        NOME_MODELO = "Qwen/Qwen2.5-1.5B-Instruct"
        dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
        tipo = torch.float16 if dispositivo == "cuda" else torch.float32
        tokenizador = AutoTokenizer.from_pretrained(NOME_MODELO)
        qwen = AutoModelForCausalLM.from_pretrained(NOME_MODELO, dtype=tipo).to(dispositivo)
        qwen.eval()  # Inferência: não treinamos os pesos do modelo aqui.
        print("Modelo carregado em", dispositivo)

        def conversar(mensagens, ferramentas):
            """Gera uma resposta; versões antigas também usam `tools` no template."""
            entrada = tokenizador.apply_chat_template(
                mensagens, tools=ferramentas, add_generation_prompt=True,
                return_tensors="pt", return_dict=True,
            ).to(dispositivo)
            with torch.no_grad():
                saida = qwen.generate(
                    **entrada, max_new_tokens=180, do_sample=False,
                    pad_token_id=tokenizador.eos_token_id,
                )
            novos = saida[0][entrada["input_ids"].shape[-1]:]
            return tokenizador.decode(novos, skip_special_tokens=True).strip()
    ''', tags=["requer_modelo"])

    texto('''
        ## 5. Acompanhar uma pergunta de ponta a ponta

        O registro mostra a decisão do modelo, os argumentos e o resultado da
        ferramenta. O valor de referência é montado diretamente dos dados do A*.
        Se o modelo não chamar a ferramenta, isso aparece como falha observável.
    ''')
    codigo('''
        # Este pedido chamou o A* no ensaio local. A bateria abaixo também
        # mostra casos em que o mesmo modelo falha ao escolher a ferramenta.
        pergunta = "Calcule a distância da Entrada IESB até o Bloco E."
        # v9 usa seleção em JSON e impede rotas para locais não citados.
        execucao = agente(pergunta, conversar, versao="v9")
        print("Pedido:", pergunta)
        print("Decisão bruta do Qwen:", execucao["decisao_modelo"])
        for chamada in execucao["chamadas"]:
            print("Ferramenta:", chamada["name"], chamada["arguments"])
            print("Referência:", resposta_de_referencia(chamada["resultado"]))
        print("Resposta bruta do Qwen:", execucao["resposta_modelo"])
        print("Resposta apresentada:", execucao["resposta"])
        print("Resposta ajustada pelo código:", execucao.get("resposta_ajustada", False))
        print("Erro do ciclo:", execucao["erro"])
    ''', tags=["requer_modelo"])

    texto('''
        ## 6. Avaliar os 15 pedidos definidos antes da execução

        `CASOS` contém o pedido, a primeira ferramenta esperada e seus
        argumentos. A avaliação automática separa **escolha da ferramenta**,
        **argumentos** e **presença do custo correto** na fala bruta. A última
        checagem é numérica; o grupo ainda deve ler as respostas para identificar
        invenções, recusas inadequadas e erros de linguagem. Uma distância
        correta para argumentos errados não resolve o pedido original.

        Os casos de fora do domínio esperam recusa sem busca. Se o modelo pedir
        `calcular_rota` com um local inexistente, o código devolve erro em vez de
        inventar uma rota; registre essa diferença na análise.
    ''')
    codigo('''
        from collections import defaultdict

        execucoes = {}
        avaliacoes = []
        for caso in CASOS:
            execucoes[caso["id"]] = agente(caso["pedido"], conversar, versao="v9")
            linha = avaliar_caso(caso, execucoes[caso["id"]])
            avaliacoes.append(linha)
            primeira = execucoes[caso["id"]]["chamadas"][:1]
            print(caso["id"], caso["categoria"],
                  "chamada:", [(c["name"], c["arguments"]) for c in primeira],
                  "ferramenta:", linha["ferramenta_ok"],
                  "argumentos:", linha["argumentos_ok"],
                  "fidelidade:", linha["fidelidade"],
                  "lista completa:", linha["lista_fiel"],
                  "recusa:", linha["recusa_ok"],
                  "tipo de erro:", linha["tipo_erro"],
                  "tempo (s):", round(linha["segundos"], 2))

        categorias = defaultdict(list)
        for linha in avaliacoes:
            categorias[linha["categoria"]].append(linha)
        print("\\nAcerto da primeira ferramenta por categoria:")
        for categoria, linhas in categorias.items():
            acertos = sum(linha["ferramenta_ok"] for linha in linhas)
            print(f"{categoria}: {acertos}/{len(linhas)}")
        print("Total:", sum(linha["ferramenta_ok"] for linha in avaliacoes),
              "/", len(avaliacoes))
        for nome in ("argumentos_ok", "fidelidade", "lista_fiel"):
            aplicaveis = [linha[nome] for linha in avaliacoes if linha[nome] is not None]
            print(nome, sum(aplicaveis), "/", len(aplicaveis))
        recusas = [linha["recusa_ok"] for linha in avaliacoes if linha["recusa_ok"] is not None]
        print("Recusas fora do domínio:", sum(recusas), "/", len(recusas))
    ''', tags=["requer_modelo"])
    codigo('''
        # Examine também os erros. A taxa isolada não mostra por que falharam.
        for caso in CASOS:
            execucao = execucoes[caso["id"]]
            linha = next(x for x in avaliacoes if x["id"] == caso["id"])
            if linha["tipo_erro"]:
                print("\\nCASO", caso["id"], caso["pedido"])
                print("Esperado:", caso["ferramenta"], caso["argumentos"])
                print("Decisão bruta:", execucao["decisao_modelo"])
                print("Chamadas:", [(c["name"], c["arguments"]) for c in execucao["chamadas"]])
                print("Resposta bruta do Qwen:", execucao["resposta_modelo"])
                print("Resposta apresentada:", execucao["resposta"])
                print("Ajustada pelo código:", execucao.get("resposta_ajustada", False))
    ''', tags=["requer_modelo"])

    texto('''
        ## 7. Antes de entregar

        1. Execute **Ambiente de execução → Reiniciar sessão e executar tudo**.
        2. Registre as taxas e pelo menos um caso de falha no relatório. Revise
           manualmente as 15 respostas, inclusive fora do domínio.
        3. Compare versões do prompt com os **mesmos** casos antes de concluir
           que uma mudança melhorou o agente.
        4. Inclua a seção de IA responsável e a declaração de uso de IA.

        Este mapa é estático. Não há previsão aprendida de tempo, obstáculos
        dinâmicos, sensores reais nem confirmação de acessibilidade do campus.
        A localização por Supervisor usada no Webots é ideal e não participa
        deste notebook.
    ''')

    notebook = {
        "nbformat": 4, "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"},
            "colab": {"name": DESTINO.name},
            "iesb_fontes_sha256": hashes,
        },
        "cells": celulas,
    }
    for indice, celula in enumerate(celulas):
        celula["id"] = f"marco2-{indice:02d}"
    DESTINO.write_text(json.dumps(notebook, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
    print(f"Notebook gerado: {DESTINO.name} ({DESTINO.stat().st_size:,} bytes)")


if __name__ == "__main__":
    gerar()
