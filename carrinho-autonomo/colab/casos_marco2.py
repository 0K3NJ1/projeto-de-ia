"""Quinze pedidos do domínio IESB, definidos antes de executar o Qwen.

Cada caso informa a primeira ferramenta esperada e, quando pertinente, seus
argumentos. A redação final e os pedidos fora do mapa ainda pedem revisão humana.
Estes são casos do AGENTE; as 15 comparações antigas de busca são outro ensaio.
"""

CASOS = [
    # Pedidos claros: servem de referência antes de testar variações de escrita.
    {"id": "F01", "categoria": "facil", "pedido": "Qual a rota da Entrada IESB até a Biblioteca?",
     "ferramenta": "calcular_rota", "argumentos": {"origem": "Entrada IESB", "destino": "Biblioteca"}},
    {"id": "F02", "categoria": "facil", "pedido": "Quero ir da Biblioteca ao Bloco H.",
     "ferramenta": "calcular_rota", "argumentos": {"origem": "Biblioteca", "destino": "Bloco H"}},
    {"id": "F03", "categoria": "facil", "pedido": "Como vou do Bloco C à Cantina?",
     "ferramenta": "calcular_rota", "argumentos": {"origem": "Bloco C", "destino": "Cantina"}},
    {"id": "F04", "categoria": "facil", "pedido": "Calcule a distância da Entrada IESB até o Bloco E.",
     "ferramenta": "calcular_rota", "argumentos": {"origem": "Entrada IESB", "destino": "Bloco E"}},
    {"id": "F05", "categoria": "facil", "pedido": "Rota do Bloco D para a Central de Atendimento, por favor.",
     "ferramenta": "calcular_rota", "argumentos": {"origem": "Bloco D", "destino": "Central de Atendimento"}},

    # Mudam a ordem, caixa ou língua. Os locais esperados são sempre os mesmos
    # do catálogo; o modelo não recebe as respostas esperadas durante a execução.
    {"id": "D01", "categoria": "dificil", "pedido": "tô na biblioteca, bora pro bloco h?",
     "ferramenta": "calcular_rota", "argumentos": {"origem": "Biblioteca", "destino": "Bloco H"}},
    {"id": "D02", "categoria": "dificil", "pedido": "Destino: Cantina. Partida: Bloco B. Qual caminho?",
     "ferramenta": "calcular_rota", "argumentos": {"origem": "Bloco B", "destino": "Cantina"}},
    {"id": "D03", "categoria": "dificil", "pedido": "How do I get from Biblioteca to Bloco J?",
     "ferramenta": "calcular_rota", "argumentos": {"origem": "Biblioteca", "destino": "Bloco J"}},
    {"id": "D04", "categoria": "dificil", "pedido": "Saio de BB01 e preciso chegar em H01.",
     "ferramenta": "calcular_rota", "argumentos": {"origem": "BB01", "destino": "H01"}},

    # A segunda ferramenta tem propósito distinto: apresentar o catálogo.
    {"id": "L01", "categoria": "outra_ferramenta", "pedido": "Quais locais existem no mapa?",
     "ferramenta": "listar_locais", "argumentos": {}},
    {"id": "L02", "categoria": "outra_ferramenta", "pedido": "Liste os destinos cadastrados no campus.",
     "ferramenta": "listar_locais", "argumentos": {}},

    # A resposta apropriada é admitir que o destino não está no domínio.
    # Ferramenta = None expressa que não é preciso calcular uma rota inválida;
    # a honestidade da recusa será inspecionada manualmente no relatório.
    {"id": "X01", "categoria": "fora_do_dominio", "pedido": "Me leve da Entrada IESB para Paris.",
     "ferramenta": None, "argumentos": None},
    {"id": "X02", "categoria": "fora_do_dominio", "pedido": "Qual é a rota da Biblioteca até o aeroporto?",
     "ferramenta": None, "argumentos": None},

    # Conversa sem planejamento não deve consumir a ferramenta de busca.
    {"id": "N01", "categoria": "sem_ferramenta", "pedido": "Bom dia!",
     "ferramenta": None, "argumentos": None},
    {"id": "N02", "categoria": "sem_ferramenta", "pedido": "O que você consegue fazer?",
     "ferramenta": None, "argumentos": None},
]
