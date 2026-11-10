# Formulário de validação das cinco buscas

Depois de clonar o repositório ou baixar **Code → Download ZIP** no GitHub, abra
[FORMULARIO_BUSCAS.html](FORMULARIO_BUSCAS.html) como arquivo local no navegador.
A visualização do código HTML na página do GitHub não é o formulário interativo.
O arquivo funciona sem instalação e sem servidor. Cada integrante pode preencher uma cópia, baixar
`respostas_validacao_buscas.json` e enviar o JSON nesta conversa. O botão
**Importar respostas** permite continuar o preenchimento de outro integrante.
Imagens não entram no JSON: anexe as capturas separadamente e escreva seus nomes
nas observações do formulário.

O arquivo [RESPOSTAS_COLAB_2026-11-10.json](RESPOSTAS_COLAB_2026-11-10.json)
contém os 15 custos, expansões e tempos observados em uma sessão hospedada do
Colab. É possível importá-lo no formulário para continuar o trabalho. Ele é
**parcial**: a conferência humana dos caminhos e os cinco ensaios visuais no
Webots permanecem vazios.

## O que registrar

1. Execute a comparação dos mapas pequeno, médio e campus no notebook ou com
   `.venv/bin/python experimentos_buscas.py --saida /tmp/minha_validacao --repeticoes 31`
   no Linux (ou o Python do ambiente virtual no Windows).
   Em cada mapa, registre as cinco buscas: profundidade, largura, custo uniforme,
   gulosa e A*. Preencha se houve rota, custo **da grade**, nós expandidos,
   tempo medido (se disponível) e se o caminho parece válido. Copie os IDs do
   caminho para o campo de detalhes quando houver dúvida.
2. No Webots, abra `worlds/etapa3_buscas.wbt`, ative Real-time e clique na cena.
   Para cada algoritmo, use **R**, depois **T → Bloco H → Enter**, escolha a tecla
   **1–5**, pressione **Enter** para buscar e **F** para mostrar o resultado.
   Registre as expansões magenta, a rota vermelha e se o carrinho permaneceu
   parado. **G** inicia navegação por motores e é uma validação separada.
   O formulário registra custo e expansões vistos no Webots, mas não os usa
   para aprovar a conferência visual: um pequeno deslocamento da física pode
   mudar a célula inicial associada à posição do carrinho.
3. Exporte o JSON e envie-o aqui. O resumo de texto também pode ser colado no
   chat, mas o JSON preserva todos os campos e facilita a análise caso a caso.

## Interpretação dos valores esperados

O arquivo [referencia_linux_2026-11-10.csv](referencia_linux_2026-11-10.csv)
foi recalculado nesta cópia em Linux com o código atual, usando 3 repetições
para obter custo e expansões dos 15 casos. Ele é uma **referência de regressão**
da implementação, não uma prova independente de correção. Os pares são
`EXT01 → EXT04` no mapa pequeno, `EXT01 → CAN01` no médio e `EXT01 → H01` no
campus completo. O cenário é o mapa provisório de 50 × 30 m; o croqui medido
ainda não o substituiu.

O formulário compara custo e expansões com essa referência. Uma diferença de
tempo entre máquinas é normal e **não** gera reprovação automática. Se o número
de nós/arestas ou o mapa for diferente, registre isso antes de interpretar os
demais valores. Custos da grade não incluem os conectores entre o ponto de
referência e as células. A resposta “caminho válido” depende de conferência
humana: verificar se começa e termina nos locais pedidos e não atravessa áreas
bloqueadas. Um status “Confere” no formulário significa concordância com os
campos de referência; ainda cabe revisão do grupo.

No grafo de grade usado aqui, cada aresta mede 1 m. Largura, custo uniforme e
A* devem encontrar o menor custo. Profundidade e gulosa podem produzir caminhos
maiores. A ordem de expansão e o caminho exato podem depender do algoritmo e
dos critérios de desempate; caminhos de mesmo custo podem ser igualmente bons.

Consulte [GUIA_BUSCAS_WEBOTS.md](../GUIA_BUSCAS_WEBOTS.md) para os controles e
[CAMPUS_INTERIORES.md](../CAMPUS_INTERIORES.md) para a geometria atual. O
Webots usa localização ideal do Supervisor; este formulário não valida sensores
de um carrinho físico.
