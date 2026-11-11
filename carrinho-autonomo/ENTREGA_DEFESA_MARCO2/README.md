# Defesa do Carrinho IESB - Marco 2

Este índice reúne os arquivos **públicos** que o grupo deve estudar para
defender o agente. O pacote local `ENTREGA_DEFESA_MARCO2/` também contém
`AUTORES` e uma minuta de relatório com matrículas; esses arquivos ficam
fora do GitHub público e devem ser entregues pelo canal da disciplina.

## Comece aqui

1. [Notebook do Marco 2](../colab/Carrinho_IESB_Agente_Marco2.ipynb):
   demonstra o pedido em português, a decisão do Qwen, a chamada da
   ferramenta A*, tabela e gráfico das cinco buscas e avaliação dos 15 casos.
   O notebook incorpora os módulos Python usados na execução do Colab.
2. [Guia de defesa](GUIA_DEFESA.md): roteiro de demonstração e conceitos que
   todos os integrantes precisam explicar.
3. [Análise dos 15 casos](ANALISE_15_CASOS.md): acertos, erros de argumento,
   listas incompletas e pedidos fora do domínio. A revisão textual foi feita
   sobre o registro local da v9; as taxas foram observadas também no Colab.
4. [Webots complementar](WEBOTS_COMPLEMENTO.md): como mostrar a simulação sem
   confundir navegação no Webots com a avaliação do agente no Colab.

## Código que sustenta o notebook

| Arquivo | O que faz e por que importa na defesa |
| --- | --- |
| [`colab/agente_marco2.py`](../colab/agente_marco2.py) | Prompts versionados, ferramentas, ciclo do agente, validações e avaliador. |
| [`colab/casos_marco2.py`](../colab/casos_marco2.py) | Quinze pedidos com expectativas escritas antes do teste. |
| [`colab/rotas_comentadas.py`](../colab/rotas_comentadas.py) | Liga nomes dos lugares ao planejamento A*. |
| [`planejamento.py`](../planejamento.py) | Escolhe a busca, resolve origem e destino e mede custo/expansão. |
| [`buscas.py`](../buscas.py) | Implementa profundidade, largura, custo uniforme, gulosa e A*. |
| [`grade_navegacao.py`](../grade_navegacao.py) | Transforma o mapa em grafo de células navegáveis e heurística. |
| [`campus_config.py`](../campus_config.py) | Define geometria, locais e nomes do mapa provisório. |
| [`gerar_campus.py`](../gerar_campus.py) | Fornece validações geométricas usadas pela grade. |
| [`experimentos_buscas.py`](../experimentos_buscas.py) | Calcula as medidas comparativas das cinco buscas. |

As funções centrais têm docstrings; comentários explicam decisões como a
heurística, validação de argumentos, separação entre Qwen e A* e diferença
entre a resposta bruta e a resposta ajustada. O [guia do agente](../README_AGENTE_MARCO2.md)
e a [validação no Colab](../VALIDACAO_COLAB_MARCO2_2026-11-10.md) trazem
instruções e resultados observados.

## Limites para dizer na apresentação

O mapa do campus é provisório, estático e medido em metros. O notebook não
prevê tempo de viagem, não movimenta o carrinho e não comprova sensores
físicos. No teste hospedado, a primeira ferramenta foi correta em 12/15
pedidos, mas isso não é uma taxa de sucesso integral das respostas.

O código e os guias públicos ajudam a estudar. A entrega formal na plataforma
da disciplina exige o link acessível do notebook, o PDF final e o arquivo
`AUTORES` verificado pelo grupo.
