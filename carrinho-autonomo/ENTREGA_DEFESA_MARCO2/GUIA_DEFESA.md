# Guia de defesa do Marco 2

Todos os integrantes devem conseguir percorrer a cadeia completa. O grupo
informou participação compartilhada em todas as frentes; decidam apenas quem
operará cada parte da demonstração.

## Roteiro de 9 minutos

| Tempo aproximado | Ação na tela | O que explicar |
| --- | --- | --- |
| 0:00-1:00 | Abrir o notebook e mostrar o mapa/locais. | O problema é encontrar uma rota em um campus **simulado e provisório**. O pedido chega em linguagem natural. |
| 1:00-2:30 | Executar o exemplo `Entrada IESB → Biblioteca`. | O Python converte origem e destino em células e executa A*. Distinguir custo da grade (15 m) e percurso total com conectores (aprox. 15,71 m). |
| 2:30-4:00 | Mostrar tabela e gráfico dos três mapas. | Cinco buscas, mesmo problema por mapa, custo, nós expandidos e tempo medidos separadamente. Citar que o tempo é de processamento, não de viagem. |
| 4:00-6:00 | Mostrar F04: `Entrada IESB → Bloco E`. | Qwen escolhe `calcular_rota` e argumentos; Python valida; A* retorna cerca de 23,71 m; Qwen explica. A rota não é calculada pelo modelo. |
| 6:00-7:30 | Mostrar F03 ou D01 como falha. | A ferramenta foi escolhida, mas o Qwen trocou um local. O código bloqueou a rota; portanto a escolha da ferramenta sozinha não significa sucesso. |
| 7:30-9:00 | Mostrar resumo dos 15 casos e limites. | 12/15 na primeira ferramenta, 7/11 nos argumentos, 5/5 no custo **entre rotas aceitas**, 0/3 listas completas na fala bruta, 0/2 recusas corretas. Mencionar revisão semântica e IA responsável. |

O roteiro pressupõe que o notebook já foi executado e a GPU/modelo estão
carregados. Um reinício ao vivo pode demorar; antes da apresentação, comprovem
que uma sessão nova roda do início ao fim e preservem uma sessão pronta para a
demonstração. A Aula 10 requer uma falha explicada, não uma simulação de acerto.

## Fluxo técnico que cada integrante deve saber desenhar

```text
pedido em português
  → Qwen: decisão JSON (v9), nome da ferramenta e argumentos
  → Python: lê a decisão, aceita somente ferramentas previstas e confere os locais
  → calcular_rota: nomes → IDs → grade → planejamento.planejar(..., algoritmo=4)
  → buscas.a_estrela: caminho, custo e nós expandidos
  → Python: devolve resultado ao Qwen e preserva a resposta bruta
  → camada de apresentação: avisa ou usa referência se a resposta não é fiel
  → avaliador: compara decisão, argumentos e resposta com os 15 casos esperados
```

`listar_locais` responde perguntas sobre o catálogo. Uma saudação ou uma
pergunta geral sobre capacidades deveria dispensar ferramenta. Destinos fora do
mapa exigem aviso claro; o resultado observado ainda falha nesse critério.

## Conceitos que devem estar claros na arguição

1. **Formulação da busca:** estado = célula livre; inicial = célula associada à
   origem; ações = ir a vizinho livre; objetivo = célula do destino; custo de
   cada aresta = 1 m na grade. O custo final soma os conectores entre os
   marcadores e os centros das células.
2. **A*:** escolhe a fronteira por `f(n)=g(n)+h(n)`. `g` é custo percorrido;
   `h` é distância Manhattan na grade de quatro vizinhos. Sem diagonais,
   obstáculos só podem aumentar o trajeto; por isso `h` não supera o menor
   custo restante da grade. A implementação está em `buscas.py`.
3. **Cinco buscas:** profundidade e gulosa podem dar caminhos maiores;
   largura, custo uniforme e A* encontraram custo mínimo nos três recortes
   medidos. Menos nós ou menor tempo em um caso não prova superioridade geral.
4. **Separação de responsabilidades:** o Qwen interpreta e explica; o Python
   valida e calcula. Prompt é orientação, não garantia de obediência.
5. **Avaliação:** `12/15` mede só a primeira ferramenta. Quatro rotas tiveram
   argumentos errados; o valor `5/5` de fidelidade numérica se aplica apenas
   às cinco rotas executadas com argumentos aceitos. A fala bruta e a resposta
   ajustada pelo código são coisas diferentes.
6. **Limites:** mapa estático, sem tempo previsto, sem obstáculos dinâmicos,
   sem garantia de acessibilidade real, sem sensores de um robô físico. O
   Webots usa pose ideal do Supervisor, mesmo quando os motores fazem o
   deslocamento simulado.

## Perguntas prováveis e respostas curtas

**O modelo calcula a melhor rota?** Não. Ele escolhe uma ferramenta e organiza
a resposta. `planejamento.py` chama `buscas.a_estrela`, que calcula o caminho.

**Por que usar ferramentas?** Para executar cálculos verificáveis e devolver
ao modelo dados concretos. Ainda precisamos validar a escolha e a explicação.

**Por que 12/15 não significa que 80% das respostas estão certas?** Esse número
mede apenas a primeira ferramenta. Argumentos, rota e texto são avaliados em
separado; uma chamada para o local errado não resolve o pedido.

**Por que a busca gulosa às vezes expande menos nós?** Ela segue só a estimativa
até o destino; pode ser rápida e ainda perder o menor custo. A* combina
estimativa com custo acumulado.

**O que houve em F03/D01?** O modelo pediu `calcular_rota`, mas trocou a
origem/destino. A verificação rejeitou esses argumentos antes do A*. A
resposta não deve ser contada como rota resolvida.

**O que há de responsável nessa implementação?** O código impede executar
ferramentas não autorizadas e deixa falhas visíveis; o relatório expõe
alucinações, recusas inadequadas e limites. O texto do Qwen ainda exige
revisão humana, especialmente em contextos sensíveis.

**Como se encaixa o Webots?** É uma demonstração complementar de navegação no
simulador. O notebook do Marco 2 não envia comandos ao Webots. Para mostrar o
robô, abra o projeto principal e siga `GUIA_BUSCAS_WEBOTS.md`; não confunda
essa prova com sensores de um carrinho físico.

## Checklist de execução antes de apresentar

1. Abrir [`colab/Carrinho_IESB_Agente_Marco2.ipynb`](../colab/Carrinho_IESB_Agente_Marco2.ipynb) no Colab e selecionar GPU
   se disponível.
2. Usar **Ambiente de execução → Reiniciar sessão e executar tudo**. A sessão
   hospedada de 10/11 terminou as oito células; repitam com o link final.
3. Conferir que a tabela, o gráfico, a chamada F04 e os 15 casos aparecem.
4. Ensaiar a explicação de um acerto e de uma falha sem ler frases prontas.
5. Verificar permissão de leitura do link, PDF final de 4 a 8 páginas e
   `AUTORES.txt` antes de enviar pelo Google Sala de Aula.
