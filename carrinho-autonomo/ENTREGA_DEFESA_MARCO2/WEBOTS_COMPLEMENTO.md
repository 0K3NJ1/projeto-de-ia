# Webots como demonstração complementar

O notebook do Marco 2 calcula rotas e avalia o agente de texto. Ele **não**
envia comandos ao Webots. Se o grupo tiver tempo na apresentação e o professor
aceitar a demonstração adicional, mostrem o carrinho no simulador depois dos
quatro itens obrigatórios descritos em `GUIA_DEFESA.md`.

O projeto Webots completo está **na pasta principal**, fora deste pacote:
`worlds/`, `controllers/`, `protos/`, texturas e `navegacao.py` precisam ficar
juntos. Copiar só um `.wbt` para esta pasta quebraria dependências. Para abrir
no computador do grupo, vá à raiz do projeto e execute `./iniciar_webots.sh`.
O mundo interativo é `worlds/etapa3_buscas.wbt`; o guia detalhado da raiz é
[`GUIA_BUSCAS_WEBOTS.md`](../GUIA_BUSCAS_WEBOTS.md).

Uma sequência curta: **R** volta à entrada; **T**, `Bloco H`, **Enter** define
o destino; escolha **1–5** para uma das cinco buscas; **Enter** calcula;
**F** mostra o resultado; **G** inicia o movimento simulado. **C** pausa ou
retoma e **espaço** para. Ensaiem antes porque teclas exigem foco na janela 3D.

Na defesa, descrevam corretamente a separação:

- Busca/A*: calcula a rota na grade.
- Controlador de navegação: transforma a rota em velocidades dos motores.
- Supervisor do Webots: fornece posição e orientação ideais ao ensaio.

Isso é uma simulação com motores, não prova de sensores físicos, desvio de
obstáculos dinâmicos ou localização autônoma em um carrinho real. O mapa é
provisório. Os resultados do Colab não validam automaticamente o movimento no
Webots. O formulário `validacao_buscas/FORMULARIO_BUSCAS.html`, na raiz do
projeto, tem campos separados para a conferência visual do simulador.
