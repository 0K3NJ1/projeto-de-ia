# Navegação automática em Python — 05/10/2026

> **Geometria atualizada em 21/10/2026:** leia `CAMPUS_INTERIORES.md`.
> Os destinos dos setores agora são seus centros internos. Comandos e limites
> de controle abaixo continuam válidos; nomes como Bloco H também são aceitos.

Abra `worlds/etapa3_buscas.wbt` no Webots e inicie a simulação. Clique na cena 3D,
use T para escolher o destino (por exemplo H01), Enter para confirmar e Enter
novamente para calcular. A busca continua podendo ser apenas visualizada.
**G inicia o movimento físico; C pausa/retoma; espaço para e invalida a rota.**
P/N/F continuam controlando somente a animação das expansões. G mostra o resultado
final da busca antes de partir. Q cancela a edição/animação e pausa o movimento.
As teclas Return=4, Enter numérico=5 e Backspace=3 do Webots foram preservadas.

T/O param e invalidam a rota assim que a edição começa, inclusive se ela for
cancelada ou o texto for inválido. Alterar algoritmo também invalida. O e R são
comandos explícitos de montagem do ensaio: reposicionam o robô e zeram a física.
Durante o seguimento nenhum campo de posição/orientação é escrito; o carrinho
se desloca exclusivamente pelas duas rodas motorizadas. Para reiniciar após
parada/falha, calcule novamente com Enter e então use G.

## Separação entre planejamento e controle

- `planejamento.planejar`: mesmas cinco buscas do Laboratório 2, sem mudanças.
- `navegacao.py`: Python puro; transforma o resultado em pontos e, recebendo
  pose/tempo, devolve velocidades dos motores. Executável e testável no Colab.
- `controllers/carrinho_buscas/carrinho_buscas.py`: teclado, visualização,
  leitura da pose e aplicação dos comandos no Webots.
- `controllers/teste_navegacao/teste_navegacao.py`: ensaio físico automatizado,
  no mundo separado `worlds/etapa4_navegacao_teste.wbt`.

A localização desta primeira versão é **ideal, fornecida pelo Supervisor**:
`getPosition()` em metros e rumo `atan2(R[3], R[0])` de `getOrientation()`.
Não é odometria nem sensor real. A matriz e os contatos seguem a
[API oficial do Supervisor](https://github.com/cyberbotics/webots/blob/R2025a/docs/reference/supervisor.md).
Não há detecção de pessoas/obstáculos novos, SLAM ou modelo de bateria.

Escala 3 preservada: chassi 0,72 × 0,48 m, largura total 0,675 m, raio das rodas
0,18 m e distância entre centros das rodas 0,60 m. Frente +X local, esquerda +Y,
Z para cima. Ambos os motores positivos avançam; esquerdo negativo e direito
positivo giram para a esquerda. Para velocidade linear v e angular w:
`esquerdo=(v−w×0,60/2)/0,18`, `direito=(v+w×0,60/2)/0,18`.

## Segurança geométrica e estados

O trajeto inclui posição real → primeiro centro, todos os centros da busca e
último centro → destino real. Nenhuma esquina é simplificada. Cada segmento é
validado por recorte exato contra as caixas e a borda do piso. Além do raio de
0,543464 m já usado na grade (robô + folga de 5 cm), exige-se mais **6 cm** para
aprovar a navegação. Uma busca pode ter solução e ainda ser recusada para condução
por falta dessa reserva; não são alterados o grafo, a geometria ou a margem original.

O controlador gira primeiro, avança quando alinhado, corrige o rumo e desacelera.
Limites: 0,32 m/s, giro de 0,65 rad/s e aceleração linear de 0,40 m/s².
Em cada ponto, entra na tolerância de 1 cm, zera motores e espera pelo menos
0,192 s antes de girar para o próximo segmento. Não faz curvas contínuas cortando
quinas. O pequeno erro restante da esquina é incluído na reserva geométrica.

Estados: parado, girando, avançando, estabilizando, pausado, concluído e falha.
O seguidor para se sair 3,5 cm do segmento ativo, se a ligação atual ao alvo não
preservar mais 2 cm de margem, se ficar 8 s sem progresso, se a pose não for finita
ou se o passo de controle ultrapassar 100 ms. Retomar exige nova verificação da
pose/corredor antes de enviar velocidade. Essas verificações usam o mapa estático;
não substituem sensores de um veículo real.

Origem já a até 1 cm do destino conclui sem movimento (inclui o ruído da física).
Estar apenas na mesma célula, mas longe do ponto final, ainda exige deslocamento.
Destino sem caminho mantém os motores parados e informa falha ao tentar iniciar.
Pose alterada após a busca exige recalcular; o controlador não reaproveita um
conector antigo como se o robô ainda estivesse na origem anterior.

## Métricas e reexecução

O painel separa milissegundos de cálculo da busca de segundos simulados de
deslocamento, incluindo giros e estabilizações e excluindo pausas. O tempo de
deslocamento é conservado ao concluir/parar e reinicia em uma nova navegação.
Pequenos movimentos da física junto a um encontro de células podem mudar a
associação da origem: as buscas usam a posição medida, não uma origem nominal fixa.

Execute `python -m unittest discover -s tests -v` para os testes independentes.
Abra o mundo de ensaio para os testes físicos: ele encerra somente sua própria
instância via `simulationQuit`. Resultados e logs ficam em `test-results`.
Consulte `VALIDACAO_NAVEGACAO.md` para medições e limites efetivamente verificados.

O manual permanece em `worlds/etapa2_campus.wbt`, com seu controlador preservado.
Magenta vivo, vermelho, verde e roxo da visualização também foram preservados.
`python colab/preparar_colab.py` atualiza o ZIP e o notebook locais. O Colab roda
grade, buscas, gráficos e a lógica independente do seguidor; a física e a janela
3D exigem Webots instalado. Nada é enviado automaticamente ao Drive.
