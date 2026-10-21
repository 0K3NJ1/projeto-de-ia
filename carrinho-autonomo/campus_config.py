"""Etapa 2 — esquema PROVISÓRIO, não é uma planta oficial do IESB.

Todas as medidas em metros. X: direita no mapa; Y: interior do campus;
Z: altura. Origem (0, 0, 0) na Entrada IESB, sobre o piso.
Após editar: python gerar_campus.py; depois recarregue o mundo no Webots.
"""

import math

# Limites do piso; alterar não redimensiona automaticamente os outros elementos.
piso = {"x_min": -25.0, "x_max": 25.0, "y_min": -2.0, "y_max": 28.0,
        "espessura": 0.10}
paredes_padrao = {"espessura": 0.16, "altura": 0.70}
entrada = {"centro_x": 0.0, "largura": 4.0}  # Abertura na borda y_min.

# Pontos de referência: identificador -> (X, Y), em metros.
# Referências de locais; grade_navegacao.py associa cada uma a uma célula.
pontos = {
    "EXT01": (0.0, 0.0),
    "EXT02": (0.0, 12.5),
    "EXT03": (-4.5, 4.5),
    "EXT04": (4.5, 4.5),
    "EXT05": (-4.5, 12.5),
    "EXT06": (-12.5, 18.0),
    "EXT07": (12.5, 18.0),
    "EXT08": (4.5, 12.5),
    # Destinos internos: o carrinho cruza a porta e chega ao centro do setor.
    "BB01": (-10.5, 4.5),
    "CDA01": (10.5, 4.5),
    "H01": (4.5, 23.5),
    "F01": (12.5, 23.5),
    "J01": (20.5, 23.5),
    "E01": (-10.5, 12.5),
    "D01": (-4.5, 23.5),
    "C01": (-12.5, 23.5),
    "B01": (-20.5, 23.5),
    "CAN01": (10.5, 12.5),
}
# Ao adicionar um ponto, cadastre o mesmo identificador neste dicionário.
nomes = {
    "EXT01": "Entrada IESB",
    "EXT02": "Cruzamento Central",
    "EXT03": "Acesso Biblioteca",
    "EXT04": "Acesso Central de Atendimento",
    "EXT05": "Acesso Bloco E",
    "EXT06": "Acesso Blocos B/C/D",
    "EXT07": "Acesso Blocos H/F/J",
    "EXT08": "Acesso Cantina",
    "BB01": "Biblioteca", "CDA01": "Central de Atendimento",
    "H01": "Bloco H", "F01": "Bloco F", "J01": "Bloco J",
    "E01": "Bloco E", "D01": "Bloco D", "C01": "Bloco C",
    "B01": "Bloco B", "CAN01": "Cantina",
}

# Cada setor é um retângulo aberto em cima, com quatro paredes e uma porta.
# centro = (x, y); tamanho = (largura X, comprimento Y).
# porta: lado N(+Y), S(-Y), L(+X) ou O(-X), largura e deslocamento
# em relação ao meio da parede (positivo em X para N/S, em Y para L/O).
# Ampliação de 21/10/2026: centros e eixos das portas alinhados aos centros da
# grade (coordenadas terminadas em .5). Corredores preservados ao afastar setores.
setores = [
    {"id": "BIBLIOTECA", "nome": "Biblioteca", "centro": pontos["BB01"],
     "tamanho": (8.0, 6.0), "porta": ("L", 2.4, 0.0)},
    {"id": "ATENDIMENTO", "nome": "Central de Atendimento", "centro": pontos["CDA01"],
     "tamanho": (8.0, 6.0), "porta": ("O", 2.4, 0.0)},
    {"id": "BLOCO_E", "nome": "Bloco E", "centro": pontos["E01"],
     "tamanho": (8.0, 6.0), "porta": ("L", 2.4, 0.0)},
    {"id": "CANTINA", "nome": "Cantina", "centro": pontos["CAN01"],
     "tamanho": (8.0, 6.0), "porta": ("O", 2.4, 0.0)},
    {"id": "BLOCO_B", "nome": "Bloco B", "centro": pontos["B01"],
     "tamanho": (6.0, 6.0), "porta": ("S", 2.4, 0.0)},
    {"id": "BLOCO_C", "nome": "Bloco C", "centro": pontos["C01"],
     "tamanho": (6.0, 6.0), "porta": ("S", 2.4, 0.0)},
    {"id": "BLOCO_D", "nome": "Bloco D", "centro": pontos["D01"],
     "tamanho": (6.0, 6.0), "porta": ("S", 2.4, 0.0)},
    {"id": "BLOCO_H", "nome": "Bloco H", "centro": pontos["H01"],
     "tamanho": (6.0, 6.0), "porta": ("S", 2.4, 0.0)},
    {"id": "BLOCO_F", "nome": "Bloco F", "centro": pontos["F01"],
     "tamanho": (6.0, 6.0), "porta": ("S", 2.4, 0.0)},
    {"id": "BLOCO_J", "nome": "Bloco J", "centro": pontos["J01"],
     "tamanho": (6.0, 6.0), "porta": ("S", 2.4, 0.0)},
]
destinos_setores = {"BIBLIOTECA": "BB01", "ATENDIMENTO": "CDA01", "CANTINA": "CAN01",
                    **{f"BLOCO_{letra}": f"{letra}01" for letra in "BCDEHFJ"}}

# Paredes adicionais: centro (x,y), tamanho (X,Y,Z), alinhadas aos eixos.
paredes = []
# Blocos sólidos simples para representar mobiliário, sem reconhecimento.
blocos = [
    {"id": "BANCO_OESTE", "centro": (-18.0, 17.5), "tamanho": (2.0, 0.6, 0.45)},
    {"id": "BANCO_LESTE", "centro": (18.0, 17.5), "tamanho": (2.0, 0.6, 0.45)},
]

# Escala 3: chassi de 0,72 x 0,48 m; largura com rodas de 0,675 m.
robo = {"ponto_inicial": "EXT01", "angulo": math.pi / 2, "escala": 3.0}
marcadores = {"raio": 0.20, "altura": 0.004,
              "tamanho_rotulo": (1.45, 0.42), "deslocamento_rotulo": (0.0, 0.55)}
# Enquadramento da vista superior; não é uma câmera instalada no robô.
vista = {"campo_visual": 0.785398, "proporcao_janela": 2.2, "margem": 1.1}
# Margem além do raio que engloba chassi e rodas. A escala é aplicada pelo gerador.
folga_robo = 0.05

# Células alinhadas às linhas existentes; quatro vizinhos, sem diagonais.
# A associação de um local a um centro exige segmento livre e distância limitada.
grade = {"passo": 1.0, "distancia_max_associacao": 1.5}
