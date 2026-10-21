# Campus ampliado e destinos internos — 21/10/2026

Abra **`worlds/etapa3_buscas.wbt`**, inicie em Real-time e clique na cena 3D.
Os mundos terminados em `_teste.wbt` são ensaios automáticos, não a interface de uso.

## Ir ao centro do Bloco H

1. Aperte **T**, digite **Bloco H** (ou **H01**, ou **H**) e confirme com Enter.
2. Aperte **Enter novamente** para calcular a busca.
3. Aperte **G** para atravessar a porta e chegar ao centro do bloco.
4. **C** pausa/retoma; **espaço** para e invalida a rota.

Alternativa: aperte **T** e clique no piso ou no nome dentro do bloco. O destino
será seu centro cadastrado. Fora dos setores, o clique seleciona a célula.
Para escolher um ponto específico dentro da sala, digite seu ID de célula.
A faixa da parede não é interpretada como clique no interior.

Isso funciona para B/C/D/E/H/F/J, Biblioteca, Cantina e Central de Atendimento.
**O** monta outra origem e reposiciona o ensaio; **R** volta à entrada. O percurso
com G usa somente os motores. T/O ou mudança de algoritmo invalidam a rota.

## Análise de dimensões

| Elemento | Antes | Agora |
| --- | --- | --- |
| Blocos B/C/D/H/F/J | 4 × 4 m | 6 × 6 m |
| Biblioteca, Atendimento, E e Cantina | 6 × 4 m | 8 × 6 m |
| Portas | 1,80 m, algumas desalinhadas | 2,40 m, alinhadas à grade |
| Piso | 30 × 26 m | 50 × 30 m |
| Destinos dos setores | Acessos externos | Centros dos interiores |
| Carrinho | Escala 3 | Escala 3 mantida |

As medidas dos setores são entre eixos das paredes. Com espessura de 16 cm,
os espaços internos livres são 5,84 × 5,84 m e 7,84 × 5,84 m, respectivamente.
Blocos foram afastados e bancos reposicionados para preservar corredores.
O mapa continua provisório, sem representar medidas oficiais do campus.

O carrinho tem chassi de **0,72 × 0,48 m**, largura com rodas de **0,675 m**,
raio das rodas de 0,18 m e bitola de 0,60 m. Não precisava diminuir: o problema
principal era o alinhamento das portas com os centros da grade. Aumentar apenas
as salas não corrigiria a passagem. O tamanho atual cabe nos novos interiores.

Raio conservador do corpo: 0,493464 m. Somando folga da grade de 5 cm e reserva
de seguimento de 6 cm, exige-se raio de **0,603464 m**. Na porta alinhada de
2,40 m sobram aproximadamente **0,5965 m de cada lado** além dessa reserva.
As margens do planejamento e do controle não foram reduzidas.

## Destinos centrais

| Nome digitável | ID | Centro X; Y (m) |
| --- | --- | --- |
| Bloco B | B01 | −20,5; 23,5 |
| Bloco C | C01 | −12,5; 23,5 |
| Bloco D | D01 | −4,5; 23,5 |
| Bloco H | H01 | 4,5; 23,5 |
| Bloco F | F01 | 12,5; 23,5 |
| Bloco J | J01 | 20,5; 23,5 |
| Bloco E | E01 | −10,5; 12,5 |
| Biblioteca | BB01 | −10,5; 4,5 |
| Cantina | CAN01 | 10,5; 12,5 |
| Central de Atendimento (ou Atendimento) | CDA01 | 10,5; 4,5 |

Os 18 IDs de locais foram preservados; EXT02–EXT08 acompanham a nova disposição.
EXT01 continua em (0,0). H01 agora coincide com `CEL_C29_L25`. Como a borda X mudou,
**IDs antigos de células não representam as mesmas posições físicas**. Prefira nomes.

## Validação e reprodução

Grade de 1 m, quatro vizinhos, 1.500 células e 1.090 centros livres em uma única
componente. Os 38 testes Python verificam as cinco buscas até os dez interiores,
os 100 pares de setores, os 324 pares de locais, margens, circulação e seleção.
Ausência de rota continua testada com um grafo de ensaio artificialmente desconectado.

`campus_interiores_teste.wbt` percorre os dez setores sem reposicionar entre
destinos, circula num quadrado interno de 2 × 2 m em cada sala e retorna à entrada.
Monitora contatos das 57 caixas a cada passo, erro final e motores parados.
Veja os resultados efetivos em `VALIDACAO_INTERIORES.md`.
Mapas e 15 comparações atualizados em `output/buscas_interiores/index.html`;
os resultados antigos de `output/buscas` foram preservados.

Ensaios automáticos ignoram teclado/mouse da janela para não interromper a medição.
O mundo interativo recebe as entradas normalmente. `campus_config.py` concentra
geometria/destinos; `gerar_campus.py` regenera os seis mundos de campus.
Manual, PROTO físico e algoritmos de `buscas.py` foram preservados.
A localização de navegação continua ideal por Supervisor.

Snapshot anterior, incluindo mundos salvos pelo usuário:
`backups/antes_ampliacao_20261021_141219.zip`. Guias antigos conservam métricas
históricas; use este documento para a planta atual.

Notebook e ZIP: `python colab/preparar_colab.py`. O Colab executa grade, buscas,
gráficos e controle independente; a física e a janela 3D exigem Webots instalado.
Nenhum envio ao Drive ou a terceiros é feito automaticamente.
