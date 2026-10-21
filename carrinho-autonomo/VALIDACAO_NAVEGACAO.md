# Validação da navegação — 05/10/2026

Implementação em Python, com localização ideal por Supervisor e deslocamento
por motores. Não foi alterada a geometria, a escala, a grade ou as cinco buscas.

## Ensaios físicos no Webots R2025a

Instância separada, modo rápido, mundo `etapa4_navegacao_teste.wbt`.
O controlador termina a própria simulação com `simulationQuit`; não encerra
outras janelas do Webots. Cada ensaio monta explicitamente sua origem antes de
iniciar. Nenhum reposicionamento é usado para percorrer a rota.

| Ensaio | Tempo simulado de movimento | Erro final | Maior desvio da rota |
| --- | ---: | ---: | ---: |
| Reta C14L01 → C17L01 | 19,008 s | 0,00988 m | 0,00085 m |
| Curva de 90° C14L01 → C15L02, com pausa/retomada | 17,280 s | 0,00990 m | 0,00957 m |
| Campus EXT01 → H01, incluindo os dois conectores | 118,272 s | 0,00997 m | 0,00958 m |

Os valores são de uma execução determinística, não médias estatísticas.
Os tempos incluem giros e estabilização em cada centro, excluindo a pausa.
No percurso completo foram medidos aproximadamente 19,810 m de movimento.
A associação da posição efetiva após estabilização foi C15L02, com 19 m de
arestas; a posição nominal exata (0,0) associa a C14L01, com 21 m. Essa diferença
decorre do pequeno deslocamento físico na fronteira entre quatro células.
O planejador não foi alterado para fixar artificialmente uma das associações.

As 57 caixas do campus foram monitoradas a cada passo por contatos do Supervisor:
**zero contatos com obstáculos** nos percursos. O contato normal das rodas com
o piso é permitido. As velocidades comandadas finais foram zero nos dois motores;
a posição permaneceu estável (menos de 5 mm) durante mais 0,5 s após a conclusão.

Também aprovados: pausa e retomada sem incluir a pausa no cronômetro; parada
com invalidação da rota; tentativa de retomar após parada sem mover; T e O
interrompendo a condução; destino livre sem rota; origem igual ao destino.
O ensaio final percorreu o laço completo da interface (`PainelBusca.atualizar`).
Também bloqueou os comandos dos motores para simular falha de atuação:
o seguidor detectou falta de progresso e parou em 8,320 s de navegação.
Foi necessário tratar a igualdade física pela tolerância de 1 cm: a comparação
numérica exata não reconhecia os micromovimentos do corpo em repouso.

Arquivos de evidência local:

- `test-results/navegacao_webots.json`: pontos, métricas e resultados dos casos.
- `test-results/navegacao_stdout.log` e `navegacao_stderr.log`: execução física.
- `test-results/navegacao_chegada.png`: captura inspecionada, com chegada, tempos,
  rota vermelha, expansões magenta, origem verde e conectores roxos.
- `test-results/regressao_buscas_stdout.log`: ensaio original das cinco buscas
  aprovado, mantendo Enter 4/5, Backspace 3, edição e visualização sem movimento.

Único aviso no ensaio final: porta 1234 ocupada pela outra instância de teste;
Webots selecionou 1235 automaticamente. As duas instâncias terminaram sozinhas.

## Testes independentes e pacote

33 testes Python: os 24 existentes e nove novos de seguimento. Cobrem conectores,
preservação dos centros, curva, sinais dos motores, pausa/retomada/parada,
sem caminho, origem igual, mesma célula com pontos diferentes, origem antiga,
localização inválida, desvio do corredor, margem e falta de progresso em giro
e avanço. O teste cinemático é distinto dos ensaios físicos acima.

O notebook inclui demonstração cinemática do seguidor sem importar `controller`.
As oito células foram executadas localmente em processo novo e pasta vazia:
33 testes aprovados, 15 comparações geradas e demonstração cinemática concluída
com erro de 0,00983 m. A biblioteca Matplotlib existente em `tmp/buscas_deps`
exigiu execução fora da sandbox para leitura. Logs em
`test-results/navegacao_notebook.log`; hashes e pasta em `navegacao_notebook.json`.
O ZIP incorpora o módulo novo, os testes, o guia e o mundo de ensaio. Caminhos
locais `runtime.ini` e outros projetos continuam excluídos do pacote.
A execução na nuvem do Colab não foi verificada. Nenhum envio ao Drive ou a terceiros.

## Preservação

SHA-256 do manual antes e depois:
`2f5375e961f70e22686f511c28aa3a2453e9f52902b1703e47f219c06d3a532e`.

PROTO físico preservado:
`6e1fba9d60e3ae60887fad5fb80439a7842deed8a7e01fa9f2fbd22a8e59e1d5`.

Configuração do campus preservada:
`cee764c54fd317575609bf30293616f26f131ab4faf24c069454fde4353f0699`.

Buscas do Laboratório 2 preservadas:
`a09ac94133f4af0d9b162892a2c866efa1668937cb9849b66fd8dd98d428142e`.

Limites: ensaios com o mapa estático e localização ideal, sem comprovação para
obstáculos dinâmicos, robô físico ou sensores reais. Os testes da interface chamam
seus comandos dentro do simulador; não simulam um usuário pressionando teclas
ou clicando com o mouse. A correção 4/5/3 do teclado foi mantida e é usada no ensaio
original de regressão das buscas.
