# Carrinho IESB no Colab — grade e buscas

## Novo: A* + Qwen com código comentado (01/11/2026)

Abra `Carrinho_IESB_Rotas_Comentado.ipynb` no Colab. Ele contém a primeira
integração dos Labs 2 e 7: nomes dos locais → A* → explicação pelo Qwen.
Execute em ordem; altere `origem` e `destino` na seção 5. Para o Qwen, selecione
GPU antes de começar. O download do modelo requer internet e alguns GB;
o planejamento pode ser executado sem GPU e sem baixar o modelo.

O código novo está explicado em `rotas_comentadas.py` e aparece inteiro nas
células didáticas. O notebook incorpora apenas os cinco módulos necessários ao
planejamento em uma pasta temporária. Não usa o ZIP antigo nem altera o Webots.
Usa o mapa antigo de 50 × 30 m, não o croqui medido. O resultado do Python fica
visível para conferir possíveis erros no texto produzido pelo Qwen.

Para regenerar após mudar o código: `python3 colab/preparar_rotas_comentadas.py`.
A regeneração captura os módulos atuais, inclusive o mapa; confira a geometria
antes de gerar uma nova cópia. Os hashes das fontes ficam nos metadados do notebook.

Esta etapa ainda não interpreta pedidos livres, não implementa ferramentas dos
Labs 8/9 e não prevê tempo de viagem. Ela também não movimenta o carrinho.
Validação local registrada em `VALIDACAO_ROTAS_COMENTADAS.md`; a geração real com
Qwen e uma sessão nova na nuvem do Colab ainda precisam ser verificadas.

## Pacote anterior: buscas e navegação

**21/10/2026:** pacote ampliado, com dez destinos centrais internos. Bloco H/H01
fica dentro do H. Veja `CAMPUS_INTERIORES.md`; os IDs antigos de células mudaram
de posição com o aumento do piso. As cinco buscas e o carrinho foram preservados.

O pacote inclui `worlds/etapa3_buscas.wbt` para escolher quadrados dentro do Webots.
A seleção do notebook usa `planejamento.py`, a mesma interface Python usada
no simulador. A janela 3D exige Webots local; o planejamento roda no Colab.

Abra `Carrinho_IESB_Base.ipynb` no Google Colab e execute todas as células em sessão
nova. O pacote está incorporado: extrai o projeto, constrói a grade, mostra as
cinco buscas do Laboratório 2, executa testes e produz gráficos e métricas.
Não exige Drive montado ou GPU. Matplotlib é instalado somente se faltar.

A cópia original do Laboratório 2 acompanha o ZIP para auditoria e regressão.
Os controladores que importam `controller` executam somente no Webots.
Reexecutar a extração restaura esta versão: salve suas alterações antes.

Para refazer o pacote: `python colab/preparar_colab.py`. Caminhos locais de Python
(runtime.ini), dependências temporárias, outros projetos e credenciais ficam fora.
O ZIP permite abrir `worlds/etapa2_campus.wbt` para controle manual ou
`worlds/etapa3_buscas.wbt` para buscas e navegação: G inicia, C pausa/retoma,
espaço para. `navegacao.py` e seus testes também executam no Colab; a última
seção demonstra o controle em um modelo cinemático ideal, sem física do Webots.

Veja `README_ETAPA3.md` para geometria, custos, heurística e limitações das portas.
Ainda faltam revisão do trio, relatório final, autoria real e validação em sessão
nova na nuvem do Colab. Atualizar o pacote local não altera os links antigos do Drive.
