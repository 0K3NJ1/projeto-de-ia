"""Primeira integração didática: nomes dos locais -> A* -> dados para o Qwen.

Este arquivo também aparece, dividido em células, no notebook comentado.
Ele usa somente Python e o planejamento existente. Não carrega o Qwen,
não altera o mapa e não envia comandos aos motores do carrinho.
"""

# %% 1. Preparar o mapa
# import permite usar funções que já estão em outros arquivos do projeto.
# json transforma dicionários Python em texto organizado para o modelo ler.
import json

from grade_navegacao import Grade
from planejamento import normalizar_nome, planejar

# A grade divide o mapa em quadrados e registra as ligações livres entre eles.
# Construímos uma única vez: todas as consultas abaixo usam o mesmo mapa.
# É o campus provisório de 50 x 30 m, chamado aqui de "mapa antigo".
grade = Grade()

# %% 2. Encontrar um local pelo nome
def encontrar_local(texto):
    """Recebe um nome ou ID cadastrado e devolve seu ID, como BB01.

    Exemplos aceitos: 'Biblioteca', 'biblioteca', 'BB01', 'Bloco H'.
    Ainda não interpretamos frases como 'quero ir até a biblioteca'.
    """
    # isinstance verifica o tipo. Precisamos de texto, e não de número ou lista.
    # strip remove espaços nas pontas; texto vazio não identifica um local.
    if not isinstance(texto, str) or not texto.strip():
        raise ValueError("Digite o nome ou o ID de um local do mapa.")

    # A função já existente remove acentos e diferenças de maiúsculas/espaços.
    # Assim, 'entrada iesb' e 'Entrada IESB' podem identificar o mesmo lugar.
    nome_procurado = normalizar_nome(texto)

    # nomes é um dicionário: cada ID está associado a um nome legível.
    # items() permite percorrer os pares, por exemplo ('BB01', 'Biblioteca').
    for identificador, nome in grade.config.nomes.items():
        if nome_procurado in (normalizar_nome(identificador), normalizar_nome(nome)):
            return identificador

    # Não encontramos? Interrompemos a consulta em vez de adivinhar um destino.
    # O notebook mostra a lista de nomes válidos antes do primeiro exemplo.
    raise ValueError(f"Local não cadastrado: {texto!r}. Consulte a lista de locais.")

# %% 3. Calcular a rota com o A*
def calcular_rota(origem, destino):
    """Calcula uma rota entre dois locais cadastrados, sem movimentar o robô.

    Entrada: dois textos, como 'Entrada IESB' e 'Biblioteca'.
    Saída: um dicionário com os nomes, o caminho e as distâncias em metros.
    Local inválido gera ValueError. Local válido sem caminho retorna 'sem_rota'.
    """
    # Primeiro conferimos os DOIS locais. O modelo de linguagem não faz isso.
    id_origem = encontrar_local(origem)
    id_destino = encontrar_local(destino)

    # pontos guarda as coordenadas (x, y) de cada marcador no mapa.
    # O planejador precisa da posição da origem para encontrar a célula inicial.
    posicao_inicial = grade.config.pontos[id_origem]

    # Reaproveitamos a mesma função usada pelo projeto no Webots.
    # A lista de algoritmos começa no índice 0; o A* está no índice 4.
    # A* combina o custo já percorrido com uma estimativa até o destino.
    # A grade fornece as conexões livres e a estimativa de distância Manhattan.
    resultado = planejar(grade, posicao_inicial, id_destino, algoritmo=4)

    # None significa ausência de caminho. É diferente de uma rota de custo zero,
    # que acontece quando a origem e o destino são o mesmo lugar.
    if resultado["caminho"] is None:
        status = "sem_rota"
        conectores = None
    else:
        status = "ok"
        conectores = resultado["conectores_m"]

    # Um dicionário guarda valores com nomes (as "chaves" entre aspas).
    # Usamos nomes oficiais, mesmo quando a pessoa digitou IDs ou minúsculas.
    # O caminho é uma lista de IDs de CÉLULAS, não uma lista de prédios visitados.
    # Não arredondamos aqui: preservamos a precisão do cálculo original.
    return {
        "status": status,
        "mapa": "Campus provisório de 50 x 30 m (mapa antigo)",
        "origem": grade.config.nomes[id_origem],
        "destino": grade.config.nomes[id_destino],
        "algoritmo": resultado["algoritmo"],
        "caminho": resultado["caminho"],
        # Distância percorrida pelas conexões entre centros das células.
        "distancia_grade_m": resultado["custo_m"],
        # Pequenos trechos entre os marcadores dos locais e os centros da grade.
        "conectores_m": conectores,
        # Soma da distância na grade com os conectores: use esta no resumo.
        "distancia_total_m": resultado["percurso_total_m"],
    }

# %% 4. Preparar os dados que o Qwen vai explicar
def montar_mensagens(rota):
    """Transforma a saída de calcular_rota em uma conversa para o Qwen.

    Aqui só preparamos texto. A geração da resposta ocorre depois no notebook.
    Passe o dicionário calculado pelo Python, não um resultado criado pelo modelo.
    """
    # Se não existe caminho, mostramos o aviso diretamente no notebook.
    # Não precisamos pedir para um modelo inventar uma explicação de percurso.
    if rota["status"] != "ok":
        raise ValueError("Não há rota para explicar neste mapa.")

    # system contém as orientações de resposta; user contém os dados calculados.
    # Um prompt orienta o modelo, mas não garante que ele obedeça perfeitamente.
    # Por isso, o notebook também mostra o resultado original para conferência.
    orientacao = (
        "Explique uma rota já calculada por Python. Responda em português, "
        "em até quatro frases. Use somente os dados fornecidos. Informe origem, "
        "destino, algoritmo e distancia_total_m em metros, com duas casas decimais. "
        "Identifique o mapa como provisório. Os itens de caminho são células, "
        "não nomes de prédios. Não invente locais intermediários, direções de "
        "curvas, tempos de viagem, obstáculos, acessibilidade real ou bateria. "
        "Não recalcule nem altere a rota. Não diga que o carrinho já se moveu. "
        "Não confunda distancia_grade_m com distancia_total_m."
    )

    # ensure_ascii=False mantém os acentos legíveis; indent=2 organiza as linhas.
    # JSON é apenas a forma de enviar os dados. Não estamos pedindo saída JSON
    # ao modelo nesta etapa (isso será trabalhado no Laboratório 8).
    dados_em_texto = json.dumps(rota, ensure_ascii=False, indent=2)

    return [
        {"role": "system", "content": orientacao},
        {"role": "user", "content": "Explique este resultado calculado:\n" + dados_em_texto},
    ]
