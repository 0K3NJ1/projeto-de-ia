# Escolher uma célula e executar buscas no Webots

Abra **File → Open World** e selecione `worlds/etapa3_buscas.wbt`.
**Não use `_teste.wbt` para uso interativo:** são ensaios automáticos.
**21/10/2026:** blocos ampliados, com destinos no centro dos interiores.
Novas medidas e destinos em `CAMPUS_INTERIORES.md`.
É o campus completo com os quadrados, IDs e um painel de busca na própria cena.
Inicie a simulação em **Real-time** e clique na área 3D para ela receber o teclado.
O mundo `etapa2_campus.wbt` continua disponível para dirigir manualmente.

## Primeira busca, sem alterar a origem

1. O carrinho começa em EXT01. A origem da busca é associada à posição atual dele.
2. Aperte **T** para selecionar o destino.
3. Digite **Bloco H** e pressione **Enter** para confirmar. Também pode digitar
   `H01`, `H`, `C29L25` ou `29,25`. As letras podem ser digitadas normalmente.
4. Aperte **5** para escolher A* (já é a seleção inicial).
5. Aperte **Enter novamente** para executar a busca.
6. Os nós expandidos aparecem em magenta vivo, na ordem registrada pelo algoritmo.
   Ao terminar, a rota aparece em vermelho.
7. Para percorrer a rota, aperte **G**. **C** pausa/retoma o movimento;
   **espaço** para e invalida a rota. Sem G, é possível apenas visualizar a busca.
8. Ao calcular a rota com Enter, o modelo **Qwen2.5-1.5B-Instruct** é acionado em
   segundo plano e imprime no console a explicação em português dos dados calculados,
   sem travar a simulação nem bloquear o comando G.

Alternativa ao passo 3: depois de **T**, clique no piso dentro do quadrado desejado.
Dentro de um bloco, o clique escolhe seu centro; fora, escolhe a célula.
Para um ponto específico dentro do bloco, digite o ID da célula.
Um clique em parede ou banco pode resultar em célula bloqueada e ser recusado.
Use digitação de ID para selecionar sem ambiguidade ou sem mudar a câmera.

## Controles

| Tecla | Ação |
| --- | --- |
| T | Selecionar destino por texto ou clique no piso. |
| O | Definir outra origem por texto ou clique; reposiciona o carrinho para montar o ensaio. |
| 1 | Profundidade. |
| 2 | Largura. |
| 3 | Custo uniforme. |
| 4 | Gulosa. |
| 5 | A*. |
| Enter | Confirmar a seleção; fora da edição, executar a busca. |
| P | Pausar/continuar a reprodução das expansões. |
| N | Pausar e mostrar exatamente mais uma expansão. |
| F | Mostrar todas as expansões e a rota final imediatamente. |
| G | Mostrar a rota final e iniciar a navegação pelos motores. |
| C | Pausar ou retomar o movimento físico. |
| Espaço | Parar o movimento e invalidar a rota; Enter calcula outra. |
| R | Reposicionar o carrinho na entrada EXT01 e limpar a busca anterior. |
| Q | Cancelar a edição, pausar a animação e o movimento. |
| Backspace | Apagar um caractere durante a digitação. |

As teclas são lidas enquanto a simulação está rodando e a cena 3D tem foco.
Mantenha cada tecla por um instante (cerca de 0,1 s) e solte entre dois
acionamentos: o Webots lê teclas pressionadas a cada passo da simulação.
Se o editor ou o console tiver foco,
clique primeiro na cena. Digitar enquanto T/O está ativo insere o texto;
os números só escolhem algoritmo fora desse modo de edição.

## O que aparece

- **Magenta vivo (rosa):** centros já expandidos, com contador e último ID no painel.
- **Verde:** centro inicial associado à posição do carrinho.
- **Vermelho:** centro de destino e caminho encontrado.
- **Roxo:** ligação do ponto de referência ao centro da célula, fora do custo da grade.
- **Tempo de busca:** cálculo em Python, sem incluir o tempo da animação.
- **Sem rota:** a célula é livre, mas não está conectada à origem na grade.
- **Centro bloqueado:** a seleção é recusada; não é substituída silenciosamente por outro quadrado.

O algoritmo calcula primeiro e devolve a ordem de expansão. A interface reproduz
essa ordem em ritmo visível (aproximadamente uma expansão a cada 0,06 s simulados).
Não se trata de atraso computacional da busca nem de movimento do carrinho.
**Os motores ficam parados até o comando G.** P/N/F afetam só a animação;
C controla a pausa do movimento. O painel informa estado e tempo de deslocamento
em segundos simulados, separado do tempo de cálculo e sem contar pausas.
T/O interrompem o movimento e invalidam a rota anterior assim que a edição começa.
Sem caminho, sem margem adicional ou em falha de rastreamento, o carrinho para.
Leia `README_NAVEGACAO.md` para localização ideal por Supervisor e limites.
O comando O altera explicitamente a montagem do estado inicial por Supervisor;
não representa deslocamento físico nem navegação autônoma.

As portas foram ampliadas e alinhadas: todos os interiores agora conectam à entrada.
Os dez locais dos setores estão dentro das salas, não nos acessos externos.

## Linguagens e compatibilidade com Colab

- `buscas.py`: cinco algoritmos adaptados do Laboratório 2, em Python.
- `grade_navegacao.py`: ocupação e grafo, em Python.
- `planejamento.py`: escolha de estados e execução, em Python puro; funciona no Colab.
- `navegacao.py`: seguimento da rota e estados em Python puro; recebe pose e devolve velocidades.
- `controllers/carrinho_buscas/carrinho_buscas.py`: interface e desenho no Webots, em Python.
- `controllers/carrinho_manual/carrinho_manual.py`: motores e teclado manuais, já em Python e preservado.
- `protos/Carrinho.proto`: descrição física na linguagem de cena do Webots, com
  template JavaScript para aplicar a escala; não é código C nem implementa IA.
- `.wbt`: arquivos de cena gerados por `gerar_campus.py`, também em Python.

O Colab executa grade, busca, métricas e gráficos. A janela 3D, o teclado e o
Supervisor dependem do Webots instalado; não executam como células Python comuns
no Colab. Ambos usam as mesmas funções de planejamento, sem duplicar os algoritmos.

Para selecionar células também no notebook:

```python
from grade_navegacao import Grade
from planejamento import planejar

grade = Grade()
resultado = planejar(grade, (0.0, 0.0), "Bloco H", algoritmo=4)  # 4 = A*
print(resultado["caminho"], resultado["custo_m"], resultado["expandidos"])
```

Os seis mundos de campus são regenerados por `python gerar_campus.py`. O pacote portátil
é atualizado por `python colab/preparar_colab.py`. Configure o Python do Webots
nas preferências se estiver usando outro computador; caminhos locais não vão no ZIP.
