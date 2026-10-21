# Validação dos interiores ampliados — 21/10/2026

## Análise e testes Python

Robô mantido na escala 3: chassi 0,72 × 0,48 m e largura com rodas de 0,675 m.
As salas e portas foram ampliadas/alinhadas; margens geométricas preservadas.
Guia e análise dimensional em `CAMPUS_INTERIORES.md`.

38 testes Python aprovados. Além da regressão do laboratório e do seguidor,
verificam cinco buscas até os dez interiores (50 casos), 100 pares de setores,
324 pares dos 18 locais, portas, quatro pontos internos por sala e aliases/cliques.
O campus agora tem 1500 células, 1090 centros livres,
1894 arestas e uma única componente.
Sem rota é testado com um grafo de ensaio desconectado; não há mais interiores isolados.

## Webots R2025a

Três instâncias separadas de teste, sem interromper uma janela do usuário.
Cada controlador encerrou somente sua própria simulação. Nenhum erro/aviso
foi registrado nos três arquivos stderr.

O circuito principal fez **51 trechos consecutivos**, sem reposicionar entre
destinos: dez chegadas ao centro, quatro deslocamentos internos por setor
(quadrado de 2 × 2 m) e retorno à entrada. Isso verificou entrar, girar, circular
e sair de todos os setores. Contatos das 57 caixas monitorados a cada passo:
**zero contatos com obstáculos**. Motores finais zero em todos os 51 trechos.
Erro máximo final medido: **9.901 mm**.

| Destino central | Erro final (mm) | Movimento neste trecho (s simulados) |
| --- | ---: | ---: |
| Bloco H | 9.881 | 169.408 |
| Bloco F | 9.882 | 110.432 |
| Bloco J | 9.881 | 110.400 |
| Cantina | 9.881 | 199.328 |
| Central de Atendimento | 9.882 | 107.680 |
| Biblioteca | 9.881 | 116.960 |
| Bloco E | 9.881 | 124.064 |
| Bloco B | 9.881 | 195.488 |
| Bloco C | 9.881 | 110.304 |
| Bloco D | 9.881 | 110.336 |

Os tempos da tabela são trechos de um circuito: após H, partem do último ponto
de circulação no setor anterior, não todos da entrada. Incluem giros e parada
em cada célula. Tempo de busca é registrado separadamente no JSON. São medições
de uma execução, sem estimativa de bateria ou autonomia.

Também aprovados os ensaios de regressão das cinco buscas e da navegação: códigos
reais Enter 4/5 e Backspace 3; edição, origem igual, sem rota, reta, curva de 90°,
pausa, retomada, parada, invalidação por T/O e detecção de falta de progresso.
Os ensaios automáticos passaram a ignorar teclado/mouse da janela para evitar
interferência humana no percurso do teste; o controlador interativo mantém entrada.

Os testes de clique usam as coordenadas passadas à mesma função da interface.
Não equivalem a uma validação de cliques físicos pelo usuário na janela.
Localização continua ideal por Supervisor; nenhuma comprovação para robô real
ou obstáculos dinâmicos foi realizada.

## Artefatos

- `test-results/interiores/resultados.json`: as 51 medições físicas.
- `test-results/interiores_stdout.log` e `interiores_stderr.log`: circuito principal.
- `test-results/interiores_regressao_buscas_*` e `interiores_regressao_navegacao_*`: regressões.
- `test-results/interiores/campus_ampliado.png` e `chegada_bloco_h.png`: capturas.
- `output/buscas_interiores/index.html`: 15 comparações atualizadas, 31 amostras por caso.
- `colab/Carrinho_IESB_Base.ipynb` e `Carrinho_IESB_Webots.zip`: pacote atualizado.
- `test-results/interiores_notebook.json` e `.log`: registro de execução local das células.

Colab na nuvem não foi testado. Nenhum envio ao Drive ou a terceiros.
Snapshot anterior: `backups/antes_ampliacao_20261021_141219.zip`.

## Integridade

Manual, PROTO e cinco algoritmos mantêm os hashes anteriores. A configuração e
seleção foram alteradas para a nova planta; o seguidor mantém seus limites.

- `controllers/carrinho_manual/carrinho_manual.py`: `2f5375e961f70e22686f511c28aa3a2453e9f52902b1703e47f219c06d3a532e`.
- `protos/Carrinho.proto`: `6e1fba9d60e3ae60887fad5fb80439a7842deed8a7e01fa9f2fbd22a8e59e1d5`.
- `buscas.py`: `a09ac94133f4af0d9b162892a2c866efa1668937cb9849b66fd8dd98d428142e`.
- `campus_config.py`: `6c856e3314eb338a3dd08bd612531a512d0086b5bc6903fe39dcf90f1ae8b7f5`.
- `planejamento.py`: `7b89e9a71b88986252dd340dc6eb43c1e6bf3361aaf35eb88856e75fd671de99`.
- `navegacao.py`: `0aecb87364dd6b9d2c585f2c00b9258dcf7706657078e48d0ffb1c9e81e16364`.
