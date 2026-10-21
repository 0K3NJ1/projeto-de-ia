# Etapa 3 — grade e buscas no campus provisório

> **Geometria e medições históricas da primeira etapa de outubro.**
> A planta mudou em 21/10/2026: piso 50 × 30 m, setores ampliados e dez destinos
> internos acessíveis. Leia `CAMPUS_INTERIORES.md` e `VALIDACAO_INTERIORES.md`
> para medidas, IDs e resultados atuais.

**Interface no Webots disponível:** `worlds/etapa3_buscas.wbt` permite selecionar
origem/destino e algoritmo e ver expansões e rota. Leia `GUIA_BUSCAS_WEBOTS.md`.

Implementação de 01/10/2026: planejamento de rotas em Python, com células
identificadas no Webots. **Atualização de 05/10/2026:** seguimento automático por
motores disponível no mesmo mundo: G inicia, C pausa/retoma e espaço para.
Veja `README_NAVEGACAO.md` e `VALIDACAO_NAVEGACAO.md`. O manual foi preservado.
A localização automática usa o Supervisor ideal; não há sensores reais,
bateria medida ou estimativa de autonomia.

## Começar

```text
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python gerar_campus.py
python experimentos_buscas.py
python colab/preparar_colab.py
```

Abra `output/buscas/index.html` para ver a grade, associações, gráficos de custo,
expansões e tempo, e as rotas das cinco buscas. Para mudar a rota do campus inteiro:

```text
python experimentos_buscas.py --origem EXT01 --destino CAN01 --repeticoes 31
```

Os dados são regenerados na mesma pasta. Para preservar uma comparação anterior,
use `--saida output/buscas_cantina`. Os dois mapas menores mantêm seus pares fixos.

## Estados, ações e coordenadas

O estado é o **centro de uma célula**, identificado por `CEL_Cxx_Lyy`.
Índices começam em zero, da esquerda para a direita e de baixo para cima:

- `coluna = floor((x - x_min) / passo)`;
- `linha = floor((y - y_min) / passo)`;
- centro: `(x_min + (coluna + 0,5) × passo, y_min + (linha + 0,5) × passo)`;
- limites superiores do piso são exclusivos na conversão mundo → célula;
- passo atual: 1 m; piso: X de −15 a 15, Y de −2 a 24.

Há 30 colunas × 26 linhas = 780 células. `CEL_C15_L02`, por exemplo, tem
centro `(0,5; 0,5)` e contém a coordenada `(0; 0)`. Uma célula bloqueada existe
no catálogo e na cena, mas **não entra como vértice no grafo navegável**.

As ações levam aos vizinhos +X, +Y, −X, −Y, nessa ordem fixa; a transição troca
o ID atual pelo vizinho. O objetivo é a igualdade com a célula de destino. Cada
aresta custa a distância euclidiana entre centros, atualmente 1 m. Não há diagonais.
A orientação não pertence ao estado desta etapa: supõe-se possibilidade de girar
no centro; o modelo geométrico abaixo reserva espaço para isso.

## Obstáculos e tamanho do carrinho

`grade_navegacao.py` usa as mesmas 57 caixas físicas de `gerar_campus.py`.
O raio conservador é `hypot(0,12; 0,1125) × escala + folga`, hoje **0,543464 m**.
Ele envolve chassi e rodas na escala 3 (largura total 0,675 m), mais 0,05 m.
As caixas são expandidas por esse raio nos dois eixos; isso é mais conservador
nas quinas que a expansão por um disco. Pode excluir trajetos fisicamente possíveis.

Um centro é livre somente se estiver fora dessas caixas e afastado da borda do
piso. Uma aresta só existe quando **todo o segmento** passa livre, por recorte
paramétrico de segmentos contra retângulos. Contato com a borda é bloqueado.
Não se usa apenas a liberdade dos dois extremos, nem amostragem para aprovar arestas.

Resultado atual: **368 vértices livres, 588 arestas não dirigidas, sete componentes**.
A componente da entrada contém 328 vértices; 40 centros livres estão isolados dela.
A cor de ocupação descreve a segurança do centro, não todo o quadrado de 1 m².

## Os 18 locais continuam como referências

Os discos e coordenadas originais foram mantidos. `output/buscas/associacoes.csv`
registra a célula que contém cada ponto e a célula associada para navegação.
São conceitos diferentes. A associação escolhe o centro livre mais próximo até
1,5 m, desde que o segmento entre marcador e centro esteja livre. Em empate,
vence o menor ID (coluna, depois linha). Não se escolhe uma componente diferente
apenas para ocultar uma desconexão.

Por esse desempate, EXT01 `(0; 0)` associa-se a `CEL_C14_L01` `(-0,5; -0,5)`,
embora esteja contido em `CEL_C15_L02`. O conector mede aproximadamente 0,707 m.
Todos os 18 locais têm associação segura na componente da entrada.

Os conectores **não são arestas da grade**. O custo comparado entre algoritmos
é a soma das arestas entre centros. A tabela também apresenta, separadamente,
os dois conectores e o percurso total com eles. Origem igual ao destino tem
percurso zero. A optimalidade demonstrada é no grafo discretizado com associações
fixas; não se afirma a menor distância de todo o espaço contínuo.

### Limitação das portas

Os interiores de Biblioteca, Atendimento, Bloco E, Cantina, Bloco B e Bloco J
ficaram inacessíveis desde EXT01 nesta grade. Suas portas têm 1,80 m, mas os centros
das células passam a 0,50 m do eixo da abertura; após a margem, restam cerca de
0,3565 m de cada lado para o centro. Logo, esses segmentos são rejeitados.
Os blocos C/D/H/F têm portas com alinhamentos diferentes e seus interiores conectam.

Os pontos BB01/CDA01/E01/CAN01/B01/J01 representam acessos externos, não os centros
das salas. Não confundir a rota até CAN01 com entrar no interior da Cantina.
Não foram deslocadas paredes, reduzido o carrinho ou diminuída a margem para
forçar conectividade. Uma futura decisão pode realinhar a grade, acrescentar
estados especiais nas portas ou refinar a discretização, explicando a alteração.

## Localizar no Webots

Abra ou recarregue `worlds/etapa2_campus.wbt`. A árvore contém:

```text
GRADE_NAVEGACAO
  LINHA_00
    CEL_C00_L00
    ...
  LINHA_01
    ...
```

Os rótulos no piso mostram `Cxx Lyy`; aproxime a vista para ler.
Verde: centro livre ligado à entrada. Vermelho: bloqueado. Amarelo: livre isolado.
Cada célula possui DEF e `name` com seu estado, sem `boundingObject`.
Paredes podem ocultar rótulos bloqueados; a árvore e o mapa de IDs permitem consultá-los.
As linhas `GRADE_X_*` e `GRADE_Y_*` continuam apenas visuais.

## Relação direta com os laboratórios

O Laboratório 1 fundamenta estados, ações, desempenho e comparação sob as mesmas
condições. Seu custo ilustrativo de movimento não fornece um modelo real de bateria.
O Laboratório 3 trata dados faltantes, codificação, padronização e separação de treino
e teste sem vazamento. É pertinente à fase futura de previsão de tempo; não há
treinamento de modelo ou dados de travessia nesta etapa.

`adaptar_laboratorio2.py` extrai as funções originais e gera `buscas.py`. Preserva
`No`, `pai`, `acao`, `g`, reconstrução, pilha, fila, heap, explorados e ordem.
A mudança de domínio troca o mapa global por parâmetro explícito, cidades por
IDs e quilômetros por metros. Os anexos originais não foram alterados.

| Célula original (índice zero) | Adaptação |
| --- | --- |
| 8 — TODO 1 | Soma `mapa[a][b]` para pares consecutivos. |
| 12 e 14 | Classe `No` e reconstrução pela cadeia de pais. |
| 17 — TODO 2 | `fronteira.append(filho)` na largura. |
| 21 — TODO 3 | Heap com prioridade `filho.g`. |
| 25 | Profundidade com pilha, mantendo a ordem original. |
| 31 | Gulosa com prioridade `h[vizinho]`. |
| 35 — TODO 4 | Heap com prioridade `filho.g + h[vizinho]`. |
| 10, 39 e 40 | Mesma finalidade de mapas e painel; adaptados a células e tempo. |

As buscas testam o objetivo quando retirado da fronteira. **O objetivo não conta
como expandido**. Duplicatas descartadas também não contam. Empates no heap usam
contador de inserção. A pilha visita primeiro o último vizinho inserido.
Resultado sem solução: caminho/custo `None`, preservando as expansões realizadas.
Estado ausente ou bloqueado: erro explícito, diferente de destino livre desconectado.

### Heurística

`h(n) = |x_n − x_destino| + |y_n − y_destino|`, em metros (Manhattan).
Sem diagonais, qualquer rota precisa cobrir pelo menos essas duas diferenças.
Obstáculos só aumentam esse mínimo: portanto h é **admissível**.
Para cada aresta de comprimento 1, h muda no máximo 1: `h(n) ≤ 1 + h(v)`;
é também **consistente**, com h(objetivo)=0. Isso justifica manter o conjunto fechado
do A* didático sem reabertura. Outra heurística requer nova validação dessa condição.

Largura e custo uniforme podem coincidir em rota, custo e expansões porque todos
os passos custam 1 m. O heap pode ter sobrecusto de execução. A* não é necessariamente
mais rápido em todo problema pequeno; gulosa e profundidade não garantem menor custo.

## Experimentos e evidências

Três mapas são subgrafos induzidos do campus, mantendo obstáculos e escala:

| Mapa | Limites X; Y (m) | Par |
| --- | --- | --- |
| Pequeno (10 × 8 m) | [−5,5); [−2,6) | EXT01 → EXT04 |
| Médio (20 × 16 m) | [−10,10); [−2,14) | EXT01 → CAN01 |
| Campus (30 × 26 m) | [−15,15); [−2,24) | EXT01 → H01 por padrão |

Cada comparação usa o mesmo grafo, par e ordem de vizinhos para os cinco algoritmos.
São mapas de tamanhos diferentes derivados da mesma geometria, e não evidência
de desempenho em plantas independentes. A borda de um recorte limita a busca,
mas não cria paredes no Webots. Esses recortes são fixos ao cenário provisório;
revise-os quando trocar a planta em `campus_config.py`.

Medição: `perf_counter_ns`, uma execução de aquecimento e 31 amostras por algoritmo,
alternando a ordem dos algoritmos. Relatam-se mediana, quartis e amostras brutas.
Inclui busca e reconstrução; exclui construção/validação do grafo, cálculo prévio
da heurística, gráficos e arquivos. **Tempo computacional não é tempo de viagem**.

Resultados: `comparacao.csv`, `resultados.json` (rotas, ordens, tempos e hashes),
`grafo.json`, `celulas.csv`, `associacoes.csv`, `comparacao.png`, mapa completo
de IDs e 15 mapas de rotas/expansões. Cores azuis indicam ordem de expansão;
quando há até 100 expansões, também são numeradas. A ordem completa está no JSON.

## Validação e limites da entrega acadêmica

Os testes cobrem regressão da Romênia (largura 450/8; uniforme 418/12; A* 418/5),
origem=destino, destino inexistente, destino desconectado, caminho mais barato
descoberto depois, simetria, conexões através de obstáculos, custos recalculados,
heurística consistente e comparação A*/uniforme/largura nos 324 pares de locais.
O controlador de ensaio também verifica os 780 DEFs no mundo e calcula uma rota,
além dos testes físicos existentes. Esse cálculo não aciona os motores pela rota.

O PDF acadêmico pede no Marco 1 uma busca não informada e A*, três mapas, custo,
expansões, tempo, notebook Colab, relatório de 2–4 páginas e AUTORES com divisão
do trio. O cenário de campus segue a orientação atual relatada pelo usuário;
o PDF originalmente descreve entregas numa cidade. Não presumimos prazo atualizado
a partir de 16/09. Ainda faltam o relatório final com autoria real, validação em
uma sessão nova **na nuvem do Colab** e a revisão do grupo antes da submissão.
Nenhum material foi enviado ao professor ou ao Classroom.

O notebook e o ZIP locais são atualizados por `colab/preparar_colab.py`.
Os links históricos no Drive não se atualizam automaticamente com os arquivos locais.
Consulte `VALIDACAO_ETAPA3.md` para o registro do que foi efetivamente executado.
