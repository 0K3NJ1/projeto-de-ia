# Carrinho IESB no Colab — grade e buscas

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
