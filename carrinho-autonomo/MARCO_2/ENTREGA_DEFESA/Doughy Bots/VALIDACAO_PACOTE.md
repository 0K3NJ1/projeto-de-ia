# Verificação da pasta Webots de apresentação - 10/11/2026

## Conferências concluídas

- A pasta contém **somente um mundo para abrir**: `worlds/etapa3_buscas.wbt`.
  Ele foi regenerado da configuração atual, sem alterar a geometria. Seu blob
  Git coincide com o mundo gerado já existente no repositório público.
- As **1.531** URLs de textura desse mundo resolvem para arquivos desta pasta.
  A árvore Git das texturas copiadas coincide com a árvore já publicada; os
  arquivos não foram reconstruídos nem reduzidos.
- Os onze módulos Python copiados são byte a byte iguais aos da raiz do projeto
  no momento da preparação. A sintaxe foi analisada sem erro. O PROTO do
  carrinho também foi copiado sem modificação.
- Um teste isolado, executado dentro de `Doughy Bots`, construiu a grade,
  identificou as cinco buscas e confirmou A* de Entrada IESB até Bloco H com
  **29 m de custo da grade** e **137 nós expandidos**. A rota Entrada IESB até
  Biblioteca também retornou um caminho válido.
- `bash -n abrir_webots.sh` passou. Na raiz, `python3 -m unittest discover -s
  tests -v` terminou com **71 testes aprovados**.

## Conferência visual pendente

A tentativa de iniciar a janela do Webots neste ambiente encerrou antes de
abrir o mundo: o Qt informou que não conseguiu conectar ao display `:1` e
não conseguiu carregar o plugin `xcb`. Isso é uma limitação do ambiente de
execução usado nesta verificação. **Não há neste registro um novo ensaio 3D
do pacote isolado**, nem teste novo de motores ou Qwen dentro dele.

No computador da apresentação, execute `./abrir_webots.sh` e siga os cinco
passos do `README.md`. Confira a cena, as cinco buscas, uma rota percorrida
por motores, pausa e parada. Guarde os valores e uma captura se for usar o
Webots como evidência. Os ensaios históricos da raiz em
`test-results/linux-2026-10-27/` pertencem ao projeto anterior à cópia deste
pacote e não devem ser descritos como validação visual desta pasta.
