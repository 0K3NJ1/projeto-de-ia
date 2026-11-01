"""Gera o notebook leve de A* + Qwen, sem abrir ou extrair nenhum ZIP antigo.

Execute da raiz: python3 colab/preparar_rotas_comentadas.py
O conteúdo didático vem de rotas_comentadas.py, para não manter duas versões.
"""
import hashlib
import json
from pathlib import Path
from textwrap import dedent

RAIZ = Path(__file__).resolve().parents[1]
PASTA = RAIZ / "colab"

# São os cinco módulos necessários para planejar, sem Webots, imagens ou backups.
NOMES = ["campus_config.py", "gerar_campus.py", "grade_navegacao.py",
         "buscas.py", "planejamento.py"]


def gerar():
    # Incorporar o código permite abrir só o notebook no Colab.
    # Não baixamos a branch main: uma alteração futura no GitHub não troca o mapa.
    arquivos = {}
    hashes = {}
    for nome in NOMES:
        conteudo = (RAIZ / nome).read_bytes()
        arquivos[nome] = conteudo.decode("utf-8")
        hashes[nome] = hashlib.sha256(conteudo).hexdigest()

    celulas = []

    def texto(conteudo):
        celulas.append({"cell_type": "markdown", "metadata": {},
                        "source": dedent(conteudo).strip().splitlines(keepends=True)})

    def codigo(conteudo, tags=None, recolher=False):
        metadata = {"tags": tags or []}
        if recolher:
            metadata["cellView"] = "form"
        celulas.append({"cell_type": "code", "metadata": metadata,
                        "execution_count": None, "outputs": [],
                        "source": dedent(conteudo).strip().splitlines(keepends=True)})

    texto('''
        # Carrinho IESB — A* e explicação pelo Qwen, passo a passo

        **Primeira etapa da integração dos Laboratórios 2 e 7.**
        Fluxo: nomes cadastrados → A* → dados calculados → explicação em português.
        Usamos o **mapa antigo**, campus provisório de 50 × 30 m. O croqui medido
        ainda não foi aplicado. As distâncias deste cenário não são medições reais.

        Abra este arquivo no Colab e execute as células de cima para baixo.
        Para a parte do Qwen, selecione uma GPU em **Ambiente de execução →
        Alterar tipo de ambiente de execução**, antes de começar. Em CPU é mais lento.
        O modelo é baixado da Hugging Face e ocupa alguns GB; essa parte usa internet.
        A parte de A* funciona sem GPU, sem baixar modelos e sem abrir o Webots.

        Cada bloco apresenta a ideia antes do código. Para mudar o exemplo,
        altere apenas `origem` e `destino` na seção 5 e execute as células seguintes.
        Reiniciar o ambiente apaga as variáveis: nesse caso, comece novamente do topo.
    ''')
    texto('''
        ## 0. Disponibilizar a base que já existe

        A célula abaixo contém uma cópia dos cinco arquivos Python necessários.
        Ela os escreve em uma pasta temporária e permite importá-los. Não extrai
        backups nem modifica os arquivos do projeto. O código do A* continua em
        `buscas.py`; a geometria continua em `campus_config.py`.
        Esta preparação está recolhida no Colab por ser longa; o conteúdo de estudo
        começa na seção 1. É possível expandi-la para consultar as cópias dos arquivos.
    ''')
    preparacao = '''#@title Preparar os cinco arquivos do mapa antigo (execute uma vez)
# pathlib trabalha com caminhos; tempfile cria uma pasta temporária nova.
# sys.path é a lista de pastas em que o Python procura módulos para importar.
from pathlib import Path
import tempfile
import sys

# Este dicionário contém o texto dos cinco arquivos, incorporado pelo gerador.
arquivos_do_mapa = ''' + repr(arquivos) + '''

pasta_do_mapa = Path(tempfile.mkdtemp(prefix="iesb_mapa_antigo_"))
for nome, conteudo in arquivos_do_mapa.items():
    (pasta_do_mapa / nome).write_text(conteudo, encoding="utf-8")
    # Se a célula for repetida, a próxima importação usará esta mesma cópia.
    sys.modules.pop(Path(nome).stem, None)

sys.path.insert(0, str(pasta_do_mapa))
print("Mapa antigo disponível. Continue para a seção 1.")
'''
    codigo(preparacao, recolher=True)

    # Cada marcador # %% delimita uma célula do arquivo didático.
    fonte = (PASTA / "rotas_comentadas.py").read_text(encoding="utf-8")
    partes = fonte.split("# %% ")[1:]
    for parte in partes:
        titulo, corpo = parte.split("\n", 1)
        texto("## " + titulo)
        codigo(corpo)
        if titulo.startswith("1."):
            codigo('''
                # Veja quais nomes e IDs podem ser usados nas consultas.
                # O f antes das aspas permite colocar variáveis dentro de {chaves}.
                for identificador, nome in grade.config.nomes.items():
                    print(f"{identificador}: {nome}")
            ''')

    texto('''
        ## 5. Experimentar uma rota sem usar o modelo

        Primeiro conferimos o cálculo sozinho. As células são os estados da busca;
        não representam prédios. A distância total inclui os pequenos conectores
        entre os marcadores e os centros das células. **Metros não são segundos.**
        O tempo de execução do algoritmo também não seria o tempo de viagem.
    ''')
    codigo('''
        # Troque estes dois textos para experimentar outros locais cadastrados.
        origem = "Entrada IESB"
        destino = "Biblioteca"

        # Começar com None evita reutilizar uma rota antiga se a nova consulta falhar.
        rota = None
        try:
            rota = calcular_rota(origem, destino)
        except ValueError as erro:
            # try/except permite mostrar uma mensagem compreensível em caso de erro.
            print("Não foi possível calcular:", erro)

        if rota is not None:
            if rota["status"] == "sem_rota":
                print("Não existe caminho entre esses locais neste mapa.")
            else:
                print("Resultado calculado pelo Python (referência para conferir o Qwen):")
                print("Origem:", rota["origem"])
                print("Destino:", rota["destino"])
                print("Algoritmo:", rota["algoritmo"])
                # :.2f mostra duas casas decimais sem alterar o valor guardado.
                print(f"Na grade: {rota['distancia_grade_m']:.2f} m")
                print(f"Conectores: {rota['conectores_m']:.2f} m")
                print(f"Total: {rota['distancia_total_m']:.2f} m")
                # join une os IDs com uma seta, mostrando a ordem do caminho.
                print("Células:", " → ".join(rota["caminho"]))
    ''')
    texto('''
        ## 6. Entender os casos especiais

        Origem igual ao destino tem distância zero. Um nome inexistente gera erro:
        isso não significa que o caminho está bloqueado. São situações diferentes.
        A ausência de caminho entre locais válidos também é tratada pela função,
        mas todos os locais cadastrados estão conectados no mapa antigo atual.
    ''')
    codigo('''
        # Este exemplo não muda a variável rota usada na consulta principal.
        mesma_origem = calcular_rota("Biblioteca", "BB01")
        print("Mesmo lugar:", mesma_origem["distancia_total_m"], "m")

        try:
            calcular_rota("Entrada IESB", "Local que não existe")
        except ValueError as erro:
            print("Erro esperado:", erro)
    ''')
    texto('''
        ## 7. Ver exatamente o que será enviado ao Qwen

        Uma conversa é uma lista de mensagens. Cada mensagem tem `role` (quem fala)
        e `content` (o texto). A mensagem `system` orienta a resposta; a mensagem
        `user` leva os dados calculados. O modelo vai explicar esses dados.
    ''')
    codigo('''
        mensagens = None
        if rota is not None and rota["status"] == "ok":
            mensagens = montar_mensagens(rota)
            for mensagem in mensagens:
                print("\\nPapel:", mensagem["role"])
                print(mensagem["content"])
        else:
            print("Corrija a consulta na seção 5 antes de pedir uma explicação.")
    ''')
    texto('''
        ## 8. Instalar e carregar o Qwen

        Usamos `Qwen/Qwen2.5-1.5B-Instruct`, o modelo do Laboratório 7.
        `transformers` fornece o carregamento e a geração; `torch` executa as
        operações numéricas e já vem no Colab. Não é necessário colocar token
        pessoal no notebook para este modelo público.
    ''')
    codigo('''
        # %pip instala no mesmo ambiente Python que executa este notebook.
        # A faixa mantém a API da série 4 usada nesta implementação.
        %pip install -q "transformers>=4.45,<5"
    ''', tags=["requer_modelo"])
    codigo('''
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM

        nome_modelo = "Qwen/Qwen2.5-1.5B-Instruct"

        # CUDA permite usar uma GPU compatível. Sem ela, usamos o processador (CPU).
        if torch.cuda.is_available():
            dispositivo = "cuda"
            tipo_numerico = torch.float16  # Menor consumo de memória na GPU.
        else:
            dispositivo = "cpu"
            tipo_numerico = torch.float32  # Opção simples para executar na CPU.

        print("Dispositivo escolhido:", dispositivo)

        # O tokenizador transforma texto em tokens (números que representam texto).
        tokenizador = AutoTokenizer.from_pretrained(nome_modelo)

        # O modelo contém os pesos já treinados. Aqui NÃO estamos treinando uma IA.
        # .to coloca os pesos no dispositivo escolhido; eval ativa o modo de uso.
        qwen = AutoModelForCausalLM.from_pretrained(
            nome_modelo,
            torch_dtype=tipo_numerico,
        ).to(dispositivo)
        qwen.eval()
        print("Qwen carregado. Agora podemos gerar a explicação.")
    ''', tags=["requer_modelo"])
    texto('''
        ## 9. Gerar somente a resposta nova

        A estrutura abaixo acompanha o Laboratório 7: preparar a conversa,
        gerar tokens e converter a resposta de volta em texto. Não há chamada
        automática de ferramentas nesta etapa; nós chamamos o A* na seção 5.
    ''')
    codigo('''
        def conversar(mensagens, max_tokens=180):
            """Recebe a conversa e devolve o texto novo produzido pelo Qwen."""
            # O template organiza os papéis no formato que este modelo aprendeu.
            # add_generation_prompt marca onde começa a resposta do assistente.
            # return_tensors="pt" cria os tensores do PyTorch.
            entrada = tokenizador.apply_chat_template(
                mensagens,
                tokenize=True,
                add_generation_prompt=True,
                return_tensors="pt",
                return_dict=True,
            ).to(dispositivo)

            # Sem treinamento, não precisamos guardar cálculos de gradientes.
            with torch.no_grad():
                saida = qwen.generate(
                    **entrada,  # Entrega ao modelo os campos preparados acima.
                    max_new_tokens=max_tokens,  # Limite de tokens novos, não de palavras.
                    do_sample=False,  # Não sorteia o próximo token.
                    pad_token_id=tokenizador.eos_token_id,
                )

            # generate devolve a entrada seguida da resposta. Removemos a entrada
            # para não imprimir outra vez todas as instruções e os dados da rota.
            tamanho_entrada = entrada["input_ids"].shape[-1]
            tokens_novos = saida[0][tamanho_entrada:]

            # decode converte números em texto; skip_special_tokens remove marcadores.
            resposta = tokenizador.decode(tokens_novos, skip_special_tokens=True)
            return resposta.strip()
    ''', tags=["requer_modelo"])
    codigo('''
        # Só geramos texto quando o cálculo anterior encontrou uma rota válida.
        if mensagens is not None:
            explicacao = conversar(mensagens)
            print("Explicação produzida pelo Qwen (confira com a seção 5):")
            print(explicacao)
        else:
            print("Não há rota válida para explicar. Volte à seção 5.")
    ''', tags=["requer_modelo"])
    texto('''
        ## 10. Conferir e explicar ao grupo

        Compare a resposta com a seção 5: os locais estão corretos? O total em metros
        confere? Apareceu algum prédio intermediário, tempo ou direção não informado?
        Se houver informação inventada, registre o caso e revise o prompt; não a
        considere resultado do planejamento. O prompt não garante ausência de erros.

        Para praticar, experimente Entrada IESB → Cantina, Biblioteca → Bloco H e
        Biblioteca → Biblioteca. Execute novamente desde a seção 5; o modelo já
        carregado pode ser reutilizado, sem repetir as instalações ou a seção 8.

        **O que esta etapa faz:** reutiliza a busca e fornece seus dados ao modelo.
        **Próximas etapas:** interpretar pedidos em linguagem natural com validação
        (Lab 8) e permitir chamadas controladas de ferramentas (Lab 9). Prever tempo
        de viagem por aprendizado de máquina também continua pendente.

        O notebook não aciona o carrinho. A grade usa a geometria conhecida do mapa;
        esta demonstração não valida localização por sensores de um carrinho físico.

        Referências de API: [modelo Qwen](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct)
        e [conversas no Transformers](https://huggingface.co/docs/transformers/chat_templating).
    ''')
    notebook = {
        "nbformat": 4, "nbformat_minor": 5,
        "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                     "language_info": {"name": "python"},
                     "colab": {"name": "Carrinho_IESB_Rotas_Comentado.ipynb"},
                     "iesb_fontes_sha256": hashes},
        "cells": celulas,
    }
    for indice, celula in enumerate(celulas):
        celula["id"] = f"iesb-{indice:02d}"
    destino = PASTA / "Carrinho_IESB_Rotas_Comentado.ipynb"
    destino.write_text(json.dumps(notebook, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Notebook gerado: {destino.name} ({destino.stat().st_size:,} bytes)")


if __name__ == "__main__":
    gerar()
