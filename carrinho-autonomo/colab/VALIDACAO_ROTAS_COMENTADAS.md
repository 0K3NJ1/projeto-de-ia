# Validação local — A* e preparação da explicação (01/11/2026)

## Entrega

- `Carrinho_IESB_Rotas_Comentado.ipynb`: notebook de aproximadamente 75 KB,
  com instruções, exemplos e código comentado para estudo em grupo.
- `rotas_comentadas.py`: código didático que aparece nas células do notebook.
- `preparar_rotas_comentadas.py`: gerador; incorpora os cinco módulos de
  planejamento sem extrair arquivos ZIP, backups ou documentos acadêmicos.
- `tests/test_rotas_comentadas.py`: sete testes novos para a integração.

O mapa usado é o campus provisório de 50 × 30 m: 1.500 células, 1.090 livres.
Não foram modificados os módulos de planejamento, as cinco buscas, os mundos
ou os controladores. A configuração do croqui medido não foi ativada.

## O que foi executado

`python3 -m unittest discover -s tests -v`: **49 testes passaram**, incluindo
os 42 testes anteriores e os sete novos. A integração verifica nomes e IDs,
entradas inválidas, arestas e custos, os 18 destinos, origem igual ao destino,
destino desconectado em um cenário de teste e os dados enviados ao modelo.

O notebook foi validado com `nbformat` e todas as células tiveram a sintaxe
compilada, incluindo a conversão da instrução `%pip` pelo IPython.
As nove células que não exigem modelo foram executadas em um processo isolado,
com diretório de trabalho temporário. Os cinco módulos foram importados da
cópia incorporada no notebook; seus hashes coincidem com as fontes atuais.

Exemplo Entrada IESB → Biblioteca: A*, 15 m na grade, aproximadamente
0,7071 m de conectores, total **15,71 m** após arredondamento de exibição.
Esse total é uma distância no mapa provisório, não uma medição do campus real.

Registros locais em `test-results/linux-2026-11-01/rotas-comentadas/`:
`resumo.json` e `execucao_notebook_sem_modelo.txt`.

## O que ainda precisa ser verificado

As quatro células marcadas `requer_modelo` não foram executadas: instalação,
carregamento, definição da conversa e geração de texto. `torch`, `transformers`
e os pesos Qwen não estão instalados no ambiente local. A compilação da sintaxe
não comprova compatibilidade de execução nem qualidade das respostas do modelo.
Não houve execução na nuvem do Colab ou novo ensaio físico no Webots.

Para validar a parte restante:

1. Abra `Carrinho_IESB_Rotas_Comentado.ipynb` no Colab, selecione GPU e execute
   as células em ordem. A parte do modelo requer internet e alguns GB de download.
2. Confira a explicação da seção 9 contra os dados da seção 5: mesmos locais,
   A*, total de 15,71 m e nenhuma informação inventada sobre o trajeto.
3. Troque os locais na seção 5 e execute as seções 5–7 e 9 novamente. Não é
   necessário recarregar o modelo da seção 8 enquanto a sessão continuar ativa.
4. Experimente Entrada IESB → Cantina, Biblioteca → Bloco H e
   Biblioteca → Biblioteca. Registre também explicações incorretas, se ocorrerem.

O prompt orienta a resposta, mas não garante ausência de invenções. O cálculo
Python continua sendo a referência. Esta entrega cobre a primeira integração
dos Labs 2 e 7; interpretação de pedidos, ferramentas dos Labs 8/9 e previsão
de tempo de viagem ainda não foram implementadas.
