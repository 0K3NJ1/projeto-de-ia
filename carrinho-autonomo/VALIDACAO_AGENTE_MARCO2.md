# Validação local do agente com ferramenta — 06/11/2026

## Escopo

Esta validação cobre o agente de texto do Marco 2 no mapa provisório do campus.
Não representa execução hospedada no Google Colab, navegação física no Webots,
previsão aprendida de tempo ou teste de sensores reais.

## Código e notebook

- `python3 -m unittest discover -s tests -v`: **67 testes passaram**. Nove
  verificam o novo ciclo de ferramentas sem carregar o Qwen. O teste existente
  do processo separado exibiu avisos `ResourceWarning` de arquivos abertos,
  mas o resultado final foi `OK`.
- `python3 colab/preparar_agente_marco2.py`: notebook portátil gerado.
- `nbformat.validate`: 16 células válidas. A sintaxe das células Python foi
  compilada; a célula `%pip` é um comando do IPython, não sintaxe Python.
- As células que preparam os módulos, calculam a rota e refazem a comparação
  entre cinco buscas e três tamanhos executaram localmente. A janela 3D não é
  parte desse notebook.
- Um ensaio com os pesos locais do `Qwen/Qwen2.5-1.5B-Instruct` produziu uma
  chamada real de `calcular_rota(Entrada IESB, Biblioteca)`. O modelo recebeu
  o resultado do A* e citou **15,71 m** (incluindo conectores) na resposta.

## Bateria de 15 pedidos com o modelo real

O registro completo está em
`test-results/linux-2026-11-06/agente-marco2/avaliacao_v3_final_local.json`.
O resumo computado da resposta **bruta** do modelo está em
`test-results/linux-2026-11-06/agente-marco2/resumo_v3_final_local.json`.
O modelo rodou em **CPU**, offline com os pesos já presentes no cache. Cada
geração usou `do_sample=False` e no máximo 180 tokens novos. Os casos e as
expectativas de `colab/casos_marco2.py` foram escritos antes da execução.

| Critério | Resultado | Como interpretar |
| --- | ---: | --- |
| Primeira ferramenta correta, incluindo nenhuma | **8/15** | Mede a decisão inicial do Qwen. |
| Argumentos corretos | **4/11** | Casos com ferramenta esperada; nomes e IDs do mesmo local contam como equivalentes. |
| Custo exato citado na resposta bruta | **1/3** | Aplicável às três chamadas de rota que retornaram caminho. |
| Lista completa de IDs e nomes na resposta bruta | **0/1** | A resposta omitiu um local cadastrado. |
| Recusa adequada fora do domínio | **0/2** | O modelo repetiu o pedido, sem avisar que o local não está no mapa. |

Acertos da primeira ferramenta por categoria: fácil **1/5**, difícil **2/4**,
outra ferramenta **1/2**, fora do domínio **2/2** e sem ferramenta **2/2**.
Os dois acertos “fora do domínio” significam apenas que o Qwen não chamou uma
ferramenta; as respostas ainda falharam no critério de recusa. Não devem ser
apresentados como acertos completos do agente.

Exemplos observados:

- **F04:** o Qwen pediu `calcular_rota(Entrada IESB, Bloco E)` e citou o total
  **23,71 m** calculado pelo Python. É um exemplo funcional para a demonstração.
- **F01:** diante de “Entrada IESB até Biblioteca”, não chamou o A* e repetiu
  um exemplo do prompt. A camada de apresentação devolveu “Não consegui
  calcular uma rota confirmada”, deixando a fala bruta no registro.
- **D02:** pediu a ferramenta com argumentos corretos, mas começou a listar
  células e não citou os **42,00 m** totais dentro do limite de geração. A
  camada de apresentação mostrou o valor de referência do A*; a avaliação da
  fala bruta continuou marcada como falha.
- **L02:** chamou `listar_locais`, mas a fala final não incluiu todos os
  locais. A proteção atual substitui a lista incompleta pela lista do catálogo.
- **X01/X02:** não houve ferramenta, porém faltou avisar que Paris e aeroporto
  não são destinos cadastrados. A recusa ainda precisa melhorar.

Os erros classificados a partir das expectativas foram: **7 não chamadas**,
**2 explicações numericamente infiéis**, **1 lista incompleta** e **2 recusas
ausentes**. As categorias não esgotam a avaliação semântica; o grupo precisa
ler as 15 respostas antes de usar os números no relatório.

## Versões de prompt e decisão

As versões `v1` a `v6` foram preservadas em `colab/agente_marco2.py`. A bateria
completa acima usa **v3**. Uma rodada exploratória de v4 foi registrada em
`test-results/linux-2026-11-06/agente-marco2/avaliacao_v4_local.json`: houve
6/15 primeiras ferramentas corretas, mas ela usou limite de 140 tokens; não é
uma comparação controlada para concluir que v3 é superior. v5 e v6 tiveram
ensaios curtos e não geraram taxas de 15 casos.

O código foi refinado após inspecionar as respostas: aceita `<tool_call>` ou
JSON puro, oferece custo formatado pela ferramenta, impede apresentar uma rota
sem A*, substitui uma lista incompleta pelo catálogo e preserva a resposta
original para avaliação. As métricas acima foram recalculadas sobre a fala
bruta; os ajustes posteriores de apresentação foram verificados por testes
Python, sem atribuir uma nova taxa ao modelo.

## Verificações que cabem ao grupo

1. Executar o notebook do início ao fim em uma **sessão nova do Google Colab**.
2. Conferir manualmente os 15 resultados e preencher a análise de falhas,
   robustez e IA responsável no relatório de 4 a 8 páginas.
3. Confirmar com o professor o uso do campus como domínio e se a previsão
   aprendida de tempo do enunciado geral continua obrigatória nesta turma.
4. Preparar o arquivo AUTORES com a divisão real do trabalho e a declaração
   de uso de IA. Esses dados dependem do trio e não foram presumidos no código.

## Reavaliação local em 08/11/2026

Os **mesmos 15 pedidos e expectativas** de `colab/casos_marco2.py` foram usados
sem alteração. Qwen2.5-1.5B-Instruct rodou novamente em CPU, com
`do_sample=False`, `max_new_tokens=180` por geração e pesos locais em modo
offline. As versões v7, v8 e v9 preservam os prompts anteriores; seus registros
com decisão, argumentos, resultado da ferramenta, fala bruta, resposta
apresentada, categoria e segundos por caso estão em
`test-results/linux-2026-11-08/agente-marco2/`. O resumo da versão escolhida é
`resumo_v9_local.json`. Os tempos incluem gerações e busca; a quantidade de
gerações e o tamanho dos resultados variam conforme a versão.

| Critério da fala bruta/decisão inicial | v3 (06/11) | v9 (08/11) |
| --- | ---: | ---: |
| Primeira ferramenta correta, inclusive nenhuma | 8/15 | **12/15** |
| Argumentos corretos nos 11 pedidos com ferramenta | 4/11 | **7/11** |
| Custo exato citado após rota válida | 1/3 | **5/5** |
| Lista completa nos pedidos de catálogo com chamada válida | 0/1 | **0/2** |
| Recusa adequada fora do domínio | 0/2 | **0/2** |

Os **5/5** custos da v9 valem somente para as cinco rotas com argumentos
aceitos. Em quatro pedidos de rota o Qwen escolheu locais errados; a v9
registrou a chamada e a bloqueou antes do A*. Portanto, esse número não mede
sucesso ponta a ponta em nove rotas. As duas consultas fora do domínio também
levaram a chamadas inválidas: não houve caminho calculado, mas o modelo falhou
na decisão de recusar antes da ferramenta.

Primeira ferramenta correta por categoria na v9: fácil **5/5**, difícil
**4/4**, outra ferramenta **2/2**, fora do domínio **0/2**, sem ferramenta
**1/2**. A soma dos tempos dos 15 pedidos foi **339,81 s**, com mediana de
**19,19 s** por pedido. Esses são tempos locais de CPU, não latência medida no
Colab nem tempo de movimento do carrinho.

As versões intermediárias deram **8/15** (v7) e **11/15** (v8) primeiras
ferramentas corretas. A v7 removeu o exemplo que a v3 copiava e enviou um
resumo de rota ao modelo, mas perdeu chamadas em frases informais. A v8 usou
uma primeira geração só para escolher a ação em JSON, sem o template de
ferramentas; passou a chamar mais ferramentas, mas calculou rotas para acessos
que a pessoa não pediu. A v9 manteve essa decisão do Qwen e acrescentou uma
checagem genérica: cada local escolhido deve aparecer no pedido pelo nome ou
ID cadastrado. Ela **não** corrige a escolha do modelo e pode rejeitar apelidos
que não estejam no catálogo.

Falhas que o grupo deve discutir no relatório:

- **F03, F05, D01 e D02:** o Qwen selecionou `calcular_rota`, mas trocou a
  origem por um acesso diferente. A v9 registrou `argumento_errado` e não
  executou o A* nesses quatro casos.
- **L01 e L02:** o Qwen chamou `listar_locais` com `{}`, porém a fala bruta
  omitiu pares do catálogo. A resposta apresentada foi substituída pela lista
  completa do Python; a taxa da fala bruta continua **0/2**.
- **X01 e X02:** Paris e aeroporto não são destinos cadastrados; o Qwen tentou
  `calcular_rota`. A validação impediu um caminho falso, mas a primeira
  decisão e a recusa continuam erradas.
- **N02:** a pergunta sobre capacidades provocou `listar_locais`, embora não
  pedisse o catálogo. A resposta bruta acabou sendo uma lista incompleta.

As categorias automáticas medem somente critérios definidos no código. O grupo
deve conferir a clareza e a correção semântica de **todas** as respostas,
inclusive as que têm número correto, antes de atribuir notas no relatório.

## Notebook final em kernel local limpo

O notebook v9 foi regenerado por `python3 colab/preparar_agente_marco2.py` com
hashes das nove fontes incorporadas, e `nbformat.validate` aceitou as 16
células. Depois, um kernel Jupyter **novo e local** executou as oito células de
código em ordem, sem erros. O modelo carregou em **CUDA** nessa execução; a
bateria repetiu **12/15** escolhas, **7/11** argumentos, **5/5** custos após
rotas válidas, **0/2** listas completas e **0/2** recusas. A comparação das
cinco buscas nos três tamanhos foi recalculada e o gráfico inline apareceu.
O notebook executado, com saídas e gráfico, está em
`test-results/linux-2026-11-08/agente-marco2/notebook_v9_local_executado.ipynb`.
Ao concluir, `python3 -m unittest discover -s tests -v` passou com **71 testes**;
o registro completo está em `unittest_final.log` na mesma pasta de resultados.

Esta execução **não foi hospedada no Google Colab**. O grupo ainda precisa abrir
`colab/Carrinho_IESB_Agente_Marco2.ipynb` no Colab, selecionar GPU se houver,
usar **Ambiente de execução → Reiniciar sessão e executar tudo**, conferir o
gráfico e a tabela e guardar as taxas obtidas naquela sessão. Disponibilidade
de GPU, instalação de pacotes, download dos pesos e comportamento do ambiente
hospedado não foram verificados aqui.
