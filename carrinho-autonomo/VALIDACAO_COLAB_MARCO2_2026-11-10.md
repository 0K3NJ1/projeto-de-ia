# Marco 2 — execução hospedada no Google Colab em 10/11/2026

## Condições e alcance

O notebook `colab/Carrinho_IESB_Agente_Marco2.ipynb` foi aberto diretamente do
repositório público no Google Colab. Na sessão conectada a uma **GPU T4**, foi
usado **Ambiente de execução → Reiniciar sessão e executar tudo**. As oito células
de código terminaram em ordem, sem exceção na execução limpa. A tabela dos três
mapas e o gráfico inline apareceram. O Qwen2.5-1.5B-Instruct carregou em
`cuda`, e a pergunta de exemplo chamou `calcular_rota` com os argumentos
`EXT01 → E01`, recebendo **23,71 m** do A*.

O Colab exibiu um aviso de que `HF_TOKEN` não estava configurado. Ele não
impediu o download do modelo público. Também avisou que as flags de geração
`temperature`, `top_p` e `top_k` poderiam ser ignoradas. Os resultados abaixo
são da sessão hospedada, não dos ensaios locais de Windows ou Linux.

## Cinco buscas nos três recortes

Cada algoritmo foi medido com **3 repetições** na célula de demonstração. O
tempo é a mediana da busca em milissegundos; ele não mede o deslocamento do
carrinho e não deve ser tratado como limite obrigatório em outra máquina.

| Mapa | Busca | Custo da grade (m) | Nós expandidos | Mediana (ms) |
| --- | --- | ---: | ---: | ---: |
| Pequeno | Profundidade | 64 | 64 | 0,087 |
| Pequeno | Largura | 10 | 66 | 0,084 |
| Pequeno | Custo uniforme | 10 | 66 | 0,139 |
| Pequeno | Gulosa | 10 | 10 | 0,024 |
| Pequeno | A* | 10 | 35 | 0,082 |
| Médio | Profundidade | 266 | 333 | 0,429 |
| Médio | Largura | 24 | 386 | 0,439 |
| Médio | Custo uniforme | 24 | 386 | 0,812 |
| Médio | Gulosa | 24 | 79 | 0,167 |
| Médio | A* | 24 | 130 | 0,300 |
| Campus | Profundidade | 467 | 911 | 1,298 |
| Campus | Largura | 29 | 697 | 0,884 |
| Campus | Custo uniforme | 29 | 697 | 1,704 |
| Campus | Gulosa | 29 | 29 | 0,085 |
| Campus | A* | 29 | 137 | 0,371 |

Custos e expansões coincidiram com a referência atual do projeto em
`validacao_buscas/referencia_linux_2026-11-10.csv`. Não foi feita nesta sessão
uma validação da janela 3D, dos motores ou dos sensores no Webots.
Os 15 valores observados também foram transcritos para
`validacao_buscas/RESPOSTAS_COLAB_2026-11-10.json`, importável no formulário;
os campos de validade do caminho e de Webots continuam vazios.

## Agente Qwen v9: 15 pedidos

| Critério automático | Resultado no Colab | Limite da interpretação |
| --- | ---: | --- |
| Primeira ferramenta correta, incluindo nenhuma | **12/15** | Não mede a resposta final completa. |
| Argumentos corretos em pedidos com ferramenta | **7/11** | Quatro rotas tiveram origem ou destino errado e foram bloqueadas. |
| Custo fiel na fala bruta após rota aceita | **5/5** | Aplica-se somente às cinco rotas com argumentos válidos. |
| Lista completa na fala bruta quando houve listagem | **0/3** | Inclui N02, que chamou a ferramenta sem necessidade; L01/L02 também foram incompletos. |
| Recusa adequada fora do domínio | **0/2** | Paris e aeroporto provocaram chamadas indevidas. |

Os casos F03, F05, D01 e D02 escolheram locais diferentes dos pedidos. O
código registrou a decisão do Qwen e impediu que o A* calculasse uma rota
incorreta. L01 e L02 chamaram `listar_locais`, mas a resposta bruta omitiu
itens; a resposta apresentada veio do catálogo Python. X01 e X02 tentaram
`calcular_rota` para destinos fora do domínio. N02, uma pergunta sobre as
capacidades do agente, também chamou `listar_locais` indevidamente.

A bateria automática separa decisão, argumentos e fidelidade numérica, mas não
julga toda a clareza, adequação ou veracidade do texto. O grupo ainda precisa
ler as **15 respostas**, registrar exemplos de acerto e erro e discutir essas
limitações no relatório. Os números do Colab coincidiram com a reavaliação
local da v9, mas não substituem essa revisão semântica.

## Evidência e próximos passos

Os resultados foram observados na sessão aberta do Colab. A tentativa de
baixar o `.ipynb` executado pelo navegador não produziu um arquivo recuperável
neste ambiente; por isso este registro é uma transcrição das saídas vistas,
não uma cópia executada do notebook. A aba do Colab permanece aberta para o
usuário salvar uma cópia no Drive se quiser preservar todas as saídas.

Ainda faltam a revisão humana das respostas, o relatório final, o arquivo
AUTORES com a participação real e a confirmação do professor sobre o domínio
do campus e a exigência de custo de tempo aprendido.
