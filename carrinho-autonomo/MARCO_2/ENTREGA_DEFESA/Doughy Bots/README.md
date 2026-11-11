# Doughy Bots (Webots) - pasta de apresentação

**Abra apenas `worlds/etapa3_buscas.wbt`.** Este é o mundo interativo das cinco
buscas e da navegação do carrinho. Ele foi gerado novamente da configuração
atual para começar sem desenhos temporários salvos numa sessão anterior.
O mapa continua provisório, 50 × 30 m; nenhuma alteração de geometria foi
feita nesta preparação.
O que já foi conferido e o ensaio visual que ainda falta estão em
[`VALIDACAO_PACOTE.md`](VALIDACAO_PACOTE.md).

## Como abrir no computador do grupo

Na pasta `Doughy Bots`, execute:

```bash
./abrir_webots.sh
```

O script abre o Webots R2025a no mundo desta pasta, prioriza o ambiente
virtual do projeto e reaproveita os pesos locais do Qwen por um link **ignorado
pelo Git** quando eles existirem. Se o Qwen não carregar, as buscas e os
motores continuam funcionando; a explicação em texto é complementar. Em outro
computador, configure o Webots e o Python conforme o ambiente disponível.

## Ensaio curto para o dia da apresentação

1. Inicie a simulação em **Real-time** e clique na cena 3D para dar foco ao
   teclado. **R** volta à Entrada IESB.
2. Pressione **T**, digite `Bloco H`, **Enter**, selecione **5** (A*) e pressione
   **Enter** novamente para buscar. **F** mostra o caminho completo. Confira
   rota vermelha, início verde e expansões magenta.
3. Sem mudar o destino, repita com **1** profundidade, **2** largura,
   **3** custo uniforme, **4** gulosa e **5** A*. Anote custo da grade,
   expansões e tempo de cálculo. A física pode deslocar levemente o carrinho;
   use **R** antes de comparar as buscas.
4. Com uma rota válida, **G** inicia o movimento pelos motores; **C** pausa ou
   retoma; **espaço** para e invalida a rota. Calcule outra rota antes de
   reiniciar depois de uma parada.
5. Observe no console a explicação do Qwen, se o modelo local estiver
   disponível. Ela não altera o caminho calculado pelo A* e não bloqueia os
   comandos do carrinho.

O controle manual original foi preservado na raiz do projeto. Nesta pasta
entrou apenas o mundo interativo que o grupo abrirá na apresentação. A
localização usada para seguir a rota vem do **Supervisor do Webots**, de forma
ideal; os sensores definidos no PROTO não substituem essa leitura nem validam
um carrinho físico. Milissegundos de busca e segundos simulados de movimento
são medidas diferentes.

## Por que cada arquivo está aqui

| Arquivo ou pasta | Papel |
| --- | --- |
| `worlds/etapa3_buscas.wbt` | Único mundo a abrir no ensaio. Inclui piso, blocos, grade, pontos, carrinho e controlador interativo. |
| `worlds/textures/campus/` | As 1.531 imagens referenciadas pelo mundo. Omitir uma delas deixa rótulos/células sem textura. |
| `protos/Carrinho.proto` | Forma física, rodas, motores e sensores do carrinho usados pelo mundo. |
| `controllers/carrinho_buscas/carrinho_buscas.py` | Teclado, painel, animação das buscas, comandos de navegação e explicação opcional. |
| `controllers/carrinho_manual/carrinho_manual.py` | Classe de motores e dispositivos importada pelo controlador interativo; o mundo manual não está neste pacote. |
| `controllers/*/runtime.ini` | Usa `python3`; o script de abertura prioriza o `.venv` local. Não contém caminho pessoal. |
| `campus_config.py` | Geometria e nomes do mapa. É o ponto de partida para a futura mudança de mapa. |
| `gerar_campus.py` | Gera mundos e texturas a partir da configuração; mantém cena e grade coerentes. |
| `grade_navegacao.py` | Constrói células livres, grafo e heurística. |
| `buscas.py` | Implementa as cinco buscas. |
| `planejamento.py` | Liga posição, destino e algoritmo às métricas da busca. |
| `navegacao.py` | Transforma a rota em velocidades das rodas e aplica condições de parada. |
| `colab/rotas_comentadas.py`, `explicador_qwen.py`, `servidor_qwen.py` | Preparam e geram a explicação opcional do Qwen em processo separado. |
| `abrir_webots.sh` | Abre o mundo certo com ambiente e cache locais, sem incluir pesos do modelo no Git. |
| `VALIDACAO_PACOTE.md` | Registra as conferências estáticas e Python desta cópia e o teste visual ainda pendente. |

## Quando decidirmos alterar o mapa

Edite **esta cópia** de `campus_config.py`, não a da raiz do projeto. A partir
da pasta, `python3 gerar_campus.py --validar` confere a geometria sem escrever
arquivos. `python3 gerar_campus.py` recria texturas e mundos; ele também gera
mundos de teste, mas o único de apresentação é `etapa3_buscas.wbt`. Após a
mudança, compare as cinco buscas, teste o movimento no Webots e atualize o
notebook do Colab para o mesmo mapa antes de dizer que os dois coincidem.

Não altere o `.wbt` gerado à mão: mudanças futuras devem partir da
configuração. Este pacote não contém históricos, backups, capturas, outros
mundos nem pesos do Qwen.
