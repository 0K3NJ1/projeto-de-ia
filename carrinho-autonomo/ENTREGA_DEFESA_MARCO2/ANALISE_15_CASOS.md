# Análise dos 15 pedidos do agente v9

Esta é uma **leitura humana do registro local** registro local completo da avaliação v9 (guardado pelo grupo)
(Qwen2.5-1.5B-Instruct em CPU, 08/11/2026). As taxas automáticas também foram
observadas no Colab em 10/11, mas esta análise textual usa o registro local:
as respostas brutas completas do Colab não foram salvas em um arquivo recuperável.
O avaliador mede itens específicos; esta tabela não substitui a leitura do grupo.

| ID | Esperado | Observação da resposta local | Interpretação |
| --- | --- | --- | --- |
| F01 | Entrada → Biblioteca | Chamou A* com EXT01/BB01; citou 15,71 m e o caráter provisório do mapa. | Exemplo funcional; resposta bruta e apresentada coincidem. |
| F02 | Biblioteca → Bloco H | Chamou A* com BB01/H01; citou 34,00 m. | Acerto de ferramenta, argumentos e número. |
| F03 | Bloco C → Cantina | Escolheu `calcular_rota`, mas tentou EXT04/CAN01. O código rejeitou. | Falha de argumento. A mensagem bruta sugere “verificar informações”, embora o pedido estivesse claro. |
| F04 | Entrada → Bloco E | Chamou A* com EXT01/E01; citou 23,71 m. | Bom exemplo curto para a demonstração. |
| F05 | Bloco D → Atendimento | Escolheu EXT06/BB01, lugares diferentes dos pedidos; chamada rejeitada. | Ferramenta certa, rota não resolvida. |
| D01 | Biblioteca → Bloco H, informal | Escolheu EXT08/BB01; chamada rejeitada. | Texto informal provocou erro de extração dos locais. |
| D02 | Bloco B → Cantina, ordem invertida | Escolheu EXT08/CAN01; chamada rejeitada. | Não preservou a origem indicada; não há rota confirmada. |
| D03 | Biblioteca → Bloco J, inglês | Chamou A* com BB01/J01 e citou 50,00 m. Acrescentou “direto” e “rápida e eficiente”. | Número fiel, mas essas qualificações não foram verificadas pelo resultado da ferramenta. Não apresentar como prova de tempo ou percurso direto. |
| D04 | BB01 → H01, por IDs | Chamou A* com BB01/H01; citou 34,00 m. | Acerto técnico; há pequeno erro gramatical (“do Biblioteca”). |
| L01 | Listar locais | Chamou `listar_locais`, mas a fala bruta omitiu ao menos um item. | Escolha correta; lista final apresentada veio do catálogo Python. Contar a fala bruta como incompleta. |
| L02 | Listar destinos | Mesmo padrão de L01: ferramenta correta, lista bruta incompleta. | A correção de apresentação não melhora retroativamente a taxa do Qwen. |
| X01 | Entrada → Paris | Pediu `calcular_rota` para destino fora do cadastro; a execução falhou. | Deveria recusar claramente, sem ferramenta. A mensagem final genérica não explica que Paris não consta do mapa. |
| X02 | Biblioteca → aeroporto | Pediu rota com EXT08/EXT09, que nem representam o pedido; chamada rejeitada. | Falhou na decisão e nos argumentos. Também não explicou bem o limite do domínio. |
| N01 | Saudação | Respondeu “Olá!” sem ferramenta. | Comportamento esperado. |
| N02 | Pergunta sobre capacidades | Chamou `listar_locais` e gerou lista bruta incompleta; apresentação substituiu pelo catálogo. | Ferramenta desnecessária e resposta que não atende bem à pergunta. |

## Contagem observada

| Critério | Resultado | Denominador correto |
| --- | ---: | --- |
| Primeira ferramenta certa, inclusive nenhuma | 12/15 | Todos os pedidos. |
| Argumentos certos | 7/11 | Pedidos que esperavam uma ferramenta. |
| Custo fiel na fala bruta | 5/5 | Somente rotas com argumentos aceitos e custo calculado. |
| Listas completas na fala bruta | 0/3 | L01, L02 e a chamada indevida em N02. |
| Recusas adequadas fora do domínio | 0/2 | X01 e X02. |

Primeira ferramenta por categoria: pedidos fáceis **5/5**, difíceis **4/4**,
outra ferramenta **2/2**, fora do domínio **0/2**, sem ferramenta **1/2**.
O número de 12/15 não é uma taxa de acerto ponta a ponta. Em F03, F05, D01 e
D02, por exemplo, a primeira ferramenta estava certa, mas os argumentos não.

## Falhas e controles para discutir

- **Alucinação/atribuição indevida:** D03 contém linguagem de rapidez e caminho
  “direto” que não decorre do custo em metros. O modelo não mede tempo de viagem.
- **Extração de entidades:** quatro rotas foram bloqueadas por nomes/IDs
  diferentes dos citados nos pedidos. A proteção prefere expor o erro a
  calcular um caminho para o lugar errado.
- **Resposta incompleta:** listas brutas não cobriram todo o catálogo. O código
  mostra a lista Python completa, mas a avaliação continua usando o texto bruto.
- **Escopo:** X01 e X02 deveriam informar claramente que o destino não existe
  no mapa. A ferramenta rejeitou a tentativa, mas a comunicação ainda é fraca.
- **Robustez:** versões de prompt foram testadas com os mesmos casos; a v9
  elevou a escolha inicial em relação à v3 local (8/15 → 12/15), sem eliminar
  os outros tipos de erro. Não se pode atribuir melhoria geral apenas a essa taxa.

No relatório, distingam dados **locais** do registro bruto e métricas observadas
na sessão **hospedada** do Colab. Não chamem o ajuste feito por Python de acerto
do Qwen e não interpretem milissegundos de busca como tempo de deslocamento.
