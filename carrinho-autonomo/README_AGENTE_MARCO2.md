# Marco 2 — agente com ferramentas no Colab

## O que foi construído

O notebook `colab/Carrinho_IESB_Agente_Marco2.ipynb` recebe um pedido em texto.
O Qwen2.5-1.5B-Instruct escolhe `calcular_rota`, `listar_locais` ou nenhuma
ferramenta. O código lê e valida a chamada, executa a função Python autorizada,
devolve o resultado ao modelo e registra a resposta final. A busca A* existente
continua calculando caminho e distância; o Qwen não calcula esses valores.

O mapa é o campus **provisório** de 50 × 30 m, sem o croqui medido de 29/10.
As distâncias são metros no mapa simulado. Não são tempos de percurso.
Este notebook não dirige o robô. O Webots conserva controle manual, cinco
buscas, navegação por motores e localização ideal do Supervisor. Isso não
equivale a sensores de um carrinho físico.

## Onde cada parte está

| Arquivo | Papel |
| --- | --- |
| `colab/agente_marco2.py` | Prompts v1–v9, seleção e validação das ferramentas, ciclo de até três passos e avaliação numérica. |
| `colab/rotas_comentadas.py` | Ponte existente entre nomes de locais, `planejamento.planejar` e resultado do A*. |
| `colab/casos_marco2.py` | Quinze pedidos e expectativas escritos antes de executar o modelo. |
| `colab/preparar_agente_marco2.py` | Gerador do notebook portátil com cópias e hashes dos módulos necessários. |
| `colab/avaliar_agente_local.py` | Reexecuta os 15 pedidos com os pesos locais do Qwen e grava o registro bruto. |
| `tests/test_agente_marco2.py` | Testes do ciclo sem depender de download ou comportamento probabilístico do Qwen. |

O código de cada função nova contém uma docstring sobre seu papel. Comentários
explicam as decisões que afetam a validade do projeto, como a validação dos
argumentos, a origem do custo e a diferença entre resposta bruta e resposta
mostrada. Os fontes são incorporados no notebook sem duplicar manualmente o A*.
Os resultados medidos, incluindo as falhas do Qwen, estão em
`VALIDACAO_AGENTE_MARCO2.md`.

## Como executar

1. Abra `colab/Carrinho_IESB_Agente_Marco2.ipynb` no Google Colab.
2. Configure GPU, se disponível, e execute **Ambiente de execução → Reiniciar
   sessão e executar tudo**. Em CPU, a avaliação demora mais.
3. Confira a saída do exemplo “Entrada IESB → Biblioteca” antes de carregar o
   modelo: o A* deve informar 15 m na grade e cerca de 15,71 m com conectores.
4. Observe uma pergunta de ponta a ponta. A saída mostra a ferramenta escolhida,
   os argumentos, o resultado calculado e a resposta do Qwen.
5. Deixe os 15 pedidos executarem. Registre a taxa de escolha da ferramenta por
   categoria, acertos dos argumentos, custo correto na fala bruta e tempo.
6. Leia todas as respostas, principalmente as recusas fora do domínio e os
   erros. A verificação automática de fidelidade confere somente o número; ela
   não detecta toda afirmação inventada.

Para regenerar o notebook após mudar fontes:

```bash
python3 colab/preparar_agente_marco2.py
```

Para testar o código independente do modelo:

```bash
python3 -m unittest discover -s tests -v
```

Para repetir a medição local com o modelo já baixado neste computador:

```bash
HF_HUB_OFFLINE=1 .venv/bin/python colab/avaliar_agente_local.py \
  --versao v9 --saida test-results/agente-marco2-local.json
```

## Proteções e limites

- O modelo pede uma ferramenta; **somente o código** executa. Nomes de função
  desconhecidos e parâmetros extras viram resposta de erro. Nenhum texto do
  modelo é executado como Python ou comando do sistema.
- A função de rota confere os nomes antes do A*. Um local ausente não é trocado
  silenciosamente por outro. A busca não movimenta o carrinho.
- Na v9, a seleção inicial é um JSON gerado pelo Qwen sem o template de
  ferramentas. O modelo ainda escolhe a ferramenta e os dois argumentos. Antes
  de executar, o código verifica se cada local escolhido aparece no pedido
  pelo nome ou ID cadastrado. Uma troca por um acesso próximo gera erro visível;
  o código não corrige os argumentos nem calcula essa rota. Essa proteção pode
  rejeitar apelidos não cadastrados e não garante que origem e destino estejam
  na ordem certa.
- O registro mantém `resposta_modelo` intacta para medir erros. Se uma rota foi
  calculada mas a fala do modelo omite ou altera o total em metros, `resposta`
  mostra uma referência montada pelo Python e `resposta_ajustada=True` registra
  essa correção. Se o modelo responder a uma pergunta de rota sem chamar o A*,
  o código avisa que não há rota confirmada. Uma lista incompleta é substituída
  pela lista do catálogo, mantendo a fala bruta para avaliação. A presença do
  número correto não garante
  que todo o resto da explicação esteja correto; é preciso revisão humana.
- A chamada pode vir entre `<tool_call>` ou como objeto JSON puro. Os dois
  formatos passam pela mesma lista autorizada de ferramentas.
- Prompts v1–v9 ficam preservados. A versão v4 foi criada após medir
  falhas reais da v3: exemplos copiados, ferramenta ignorada e custo arredondado
  incorretamente. Testes exploratórios de v5 e v6 também estão no código. O
  notebook usa v9; v3 continua como referência da primeira bateria completa.
  Os mesmos 15 pedidos e expectativas foram mantidos. Compare as taxas medidas
  e os erros por categoria em `VALIDACAO_AGENTE_MARCO2.md`.

## Depois desta etapa

O notebook já foi executado em uma sessão nova **na nuvem do Colab** em
10/11/2026; veja `VALIDACAO_COLAB_MARCO2_2026-11-10.md`. O grupo deve
revisar a comparação de versões com os mesmos 15 casos e escrever o relatório de
4 a 8 páginas. A demonstração pode usar este notebook para mostrar a busca,
a tabela e o gráfico de três tamanhos, o ciclo pedido → ferramenta → resposta
e um caso de falha. Os integrantes precisam revisar e saber explicar todas as
partes. O arquivo AUTORES e a declaração de uso de IA são responsabilidades do
grupo, pois dependem da divisão real do trabalho.

Permanece a dúvida acadêmica entre o enunciado geral, que pede custo de tempo
aprendido, e os slides recentes, que direcionam esta turma ao agente com LLM.
Também é necessário confirmar com o professor o recorte do campus em vez de
uma cidade de entregas. Esta implementação não apresenta o modelo de tempo
como pronto.
