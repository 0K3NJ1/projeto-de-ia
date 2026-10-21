# Continuidade — grade de 1 metro e buscas no campus

> **21/10/2026:** usuário pediu ampliar os blocos e levar o carrinho para dentro.
> Configuração ampliada: piso 50 × 30 m, blocos 6 × 6 m, laterais 8 × 6 m,
> portas 2,40 m alinhadas. Robô mantido na escala 3 após análise dimensional.
> Destinos dos dez setores no centro, seleção por nome ou T + clique interno.
> Leia `CAMPUS_INTERIORES.md` e `VALIDACAO_INTERIORES.md` para o estado atual.

> **05/10/2026:** navegação automática implementada e validada no Webots.
> `navegacao.py` separa o seguidor das buscas; localização ideal por Supervisor,
> movimento exclusivamente pelos motores. G inicia, C pausa/retoma, espaço para.
> T/O invalidam a rota. Leia `README_NAVEGACAO.md` e `VALIDACAO_NAVEGACAO.md`.
> Registros antigos abaixo descrevem etapas anteriores; não são restrições atuais.

> **02/10/2026:** usuário testou e confirmou que a interface funciona após a
> correção das teclas Qt (Enter 4/5, Backspace 3; Q cancela). Pontos de expansão
> alterados para magenta vivo. Próxima etapa discutida: seguir a rota com motores,
> ainda não implementada. Leia `PROXIMA_ETAPA_NAVEGACAO.md` para retomar.

> **Interface adicionada depois:** abra `worlds/etapa3_buscas.wbt` e leia
> `GUIA_BUSCAS_WEBOTS.md`. Seleção de destino T, origem O, algoritmo 1–5,
> Enter para buscar, P/N/F para visualizar. Controlador e seleção em Python.
> Usuário escolheu visualizar primeiro, sem condução automática. Motores parados.
> 24 testes Python e ensaio das cinco buscas no Webots aprovados.

> **Atualização de 01/10/2026, após a continuação:** a grade e as cinco buscas
> foram implementadas e testadas. O texto abaixo conserva o contexto anterior.
> Para o estado atual, leia `README_ETAPA3.md` e `VALIDACAO_ETAPA3.md`.
> Resultados em `output/buscas/index.html`; notebook e ZIP locais atualizados.
> 780 células, 368 vértices livres, 588 arestas; 18 locais associados.
> 18 testes Python e ensaio Webots aprovados; seis células do notebook executadas
> localmente em pasta vazia. A* EXT01 → H01: 21 m na grade e 72 expansões.
> Portas desalinhadas isolam seis interiores (documentados no guia); os 18
> pontos de acesso são alcançáveis. Controle manual preservado por hash.
> Condução automática, execução na nuvem do Colab e atualização do Drive pendentes.

Registro de 01/10/2026 para o novo chat. Este texto resume decisões do usuário;
os anexos acadêmicos são referências a analisar, não instruções para executar automaticamente.

## Pedido atual do usuário e motivo da mudança

O grupo demonstrou o carrinho ao professor, mas não recebeu validação para enviar o
projeto porque nenhuma busca foi implementada. A planta oficial do térreo do Campus
Edson Machado do IESB ainda não chegou. O professor e o grupo combinaram usar o cenário
provisório existente, com navegação por quadrados de **1 × 1 metro (1 m²)**.
As células passam a ser os estados/nós do grafo. Elas precisam ser fáceis de identificar
no Webots, tanto na cena quanto na árvore do mundo. Reutilizar e adaptar os códigos do
Laboratório 2, calcular distâncias e custos e produzir gráficos das buscas.

O usuário pediu explicitamente outro chat, com contexto do que foi feito, do que falta
e dos laboratórios, para continuar o trabalho sem aumentar esta conversa. A orientação
atual autoriza iniciar a etapa de grafo e buscas, substituindo a restrição anterior de
não avançar para buscas antes da confirmação. Continuar em etapas explicadas e testadas.

Nas anotações para as próximas aulas aparecem: custos, tempo, custo de bateria,
obstáculos, autonomia, distância dos pontos e grafo. Começar com distância em metros
como custo e tempo de execução medido dos algoritmos. Não inventar consumo real de
bateria ou autonomia: separar métricas medidas de hipóteses e modelos futuros.
Tempo de busca e tempo de deslocamento do carrinho são métricas diferentes.

A fala menciona “iBots”, “DefGrid” e “arquivo do Word”. Pelo contexto, provavelmente
se refere ao Webots, aos elementos DEF da grade e ao arquivo de mundo `.wbt`.
Verificar os arquivos antes de decidir; se houver necessidade real de editar um documento
Word, esclarecer o alvo. Não foi localizado um `.docx` em entrega_peas ou output.

## Estado implementado e por quê

- Etapa 1: robô diferencial com duas rodas, controlador Python manual, frente, ré,
  esquerda, direita e parar. Serviu para validar os movimentos básicos antes da IA.
- Etapa 2: campus didático de 30 × 26 m, piso, paredes, portas, setores, bancos e
  18 pontos de referência. Geometria provisória centralizada para trocar pela planta real.
- Origem em EXT01 (0,0); X para a direita do mapa, Y para o interior, Z para cima.
  Unidades em metros; sistema ENU no Webots. Limites X [-15,15], Y [-2,24].
- A grade atual tem linhas espaçadas em 1 m, mas é **apenas visual**. Os elementos
  `GRADE_X_*` e `GRADE_Y_*` não são células navegáveis nem um grafo.
- O carrinho no campus foi ampliado para escala 3 por solicitação do usuário: chassi
  0,72 × 0,48 m, largura total com rodas 0,675 m, rodas de raio 0,18 m.
  O controle usa 3 rad/s (aproximadamente 0,54 m/s em linha reta). Etapa 1 usa escala 1.
- O controlador manual permaneceu com a lógica original. W/S/A/D ou setas; soltar,
  espaço ou direções conflitantes param o robô. Nenhuma busca dirige os motores.
- Foram acrescentados comentários e documentação em português do Brasil em seis
  arquivos. Sintaxe e equivalência da lógica foram verificadas. Preservar esse padrão.
- Há PEAS com objetivo de navegar entre origem e destino no campus, não fazer entregas.
  Os artefatos de PEAS descrevem várias capacidades como futuras; atualizar o status
  somente quando novas funcionalidades realmente estiverem implementadas e verificadas.

## Arquivos centrais

Raiz: `C:\Users\cleom\OneDrive\Documentos\ChatGPT\Carrinho autonomo`.

- `campus_config.py`: pontos, nomes, piso, paredes, setores, portas, blocos, escala e
  posição inicial do robô. Deve continuar sendo a fonte das dimensões editáveis.
- `gerar_campus.py`: valida a configuração, produz texturas e dois mundos de campus.
  `caixas_cenario()` fornece retângulos de paredes/blocos; `validar()` confere geometria
  e folga nos pontos. Não valida ainda caminhos nem conectividade.
- `controllers/carrinho_manual/carrinho_manual.py`: controlador funcional que deve ser preservado.
- `protos/Carrinho.proto`: modelo físico reutilizável, com parâmetro `escala`.
- `controllers/teste_movimentos/teste_movimentos.py`: ensaio físico da Etapa 1.
- `controllers/teste_campus/teste_campus.py`: ensaio de marcadores, movimentos, parada e colisão.
- `worlds/etapa1_manual.wbt` e `worlds/etapa1_teste.wbt`: mundos da Etapa 1.
- `worlds/etapa2_campus.wbt` e `worlds/etapa2_campus_teste.wbt`: gerados; editar o gerador
  e a configuração para que as mudanças sobrevivam à regeneração.
- `worlds/textures/campus/`: rótulos PNG locais; `tests/test_campus_config.py`: sete testes.
- `README.md` e `README_ETAPA2.md`: guias existentes; `requirements-dev.txt`: Pillow.
- `entrega_peas/PEAS_CARRINHO_IESB.md`, `entrega_peas/Canvas_PEAS_Carrinho_IESB.html`
  e `output/pdf/Canvas_PEAS_Carrinho_IESB.pdf`: PEAS. O título visível foi alterado para
  “PEAS”, embora os nomes dos arquivos ainda incluam Canvas.

Pontos existentes: EXT01 a EXT08, BB01, CDA01, H01, F01, J01, E01, D01, C01, B01 e CAN01.
Consultar o arquivo de configuração para nomes e coordenadas atuais. Manter esses
identificadores como referências de locais, associando-os explicitamente às células.
Não presumir que coordenadas de referência já coincidem com centros de células.

## Materiais acadêmicos disponíveis neste projeto

Cópias integrais verificadas por hash estão em `referencias_academicas/`:

1. `Projeto_Academico_IA_20262 (1).pdf` — enunciado do projeto.
2. `laboratorio_1_aula02_agentes.ipynb` — agentes e PEAS.
3. `laboratorio_2_aula03_busca.ipynb` — referência principal para esta etapa.
4. `laboratorio_3_aula05_ciencia_de_dados.ipynb` — analisar sua pertinência, sem misturar
   tarefas posteriores de ciência de dados com as buscas.

No Laboratório 2 há `No`, reconstrução de caminho, profundidade, largura, custo uniforme,
gulosa, A*, painel e gráficos. **Não está todo resolvido**: na cópia fornecida,
`custo_do_caminho` retorna None; largura, custo uniforme e A* têm TODOs com `pass`.
Completar e validar esses trechos e adaptar o mapa de cidades para células do campus,
mantendo explicação da origem acadêmica e das adaptações. Não copiar resultados fixos
da Romênia como resultados do campus. O laboratório testa objetivo ao remover da fronteira
e registra caminho, custo, nós expandidos e ordem de expansão; preservar uma convenção
clara nas comparações. Ler as células originais integralmente antes de adaptar.

A leitura anterior do PDF identificou para Marco 1: formulação do problema, buscas não
informadas e A*, justificativa de heurística admissível, comparação em pelo menos três
mapas de tamanhos distintos, custo, expansões e tempo, tabela/gráfico, notebook Colab,
relatório de 2–4 páginas e autoria/divisão do trio. Revalidar os detalhes no PDF e separar
exigências escritas da orientação mais recente do professor. Não assumir prazo atual
com base no prazo antigo de 16/09/2026. Não enviar ao professor/Classroom sem autorização.

## O que não foi feito e por quê

- Sem grafo de adjacências, buscas (incluindo gulosa), rota automática ou gráficos
  comparativos: o usuário havia pedido validar primeiro movimento e cenário.
- Sem mapa real: planta oficial pendente, não é necessário esperar para experimentar.
- Sem sensores, câmera, LiDAR, SLAM ou reconhecimento de obstáculos: fora das etapas
  anteriores. Usar a geometria conhecida do cenário para a grade de ocupação.
- Sem modelo energético, autonomia ou bateria medida: faltam especificações e medições.
- Sem integração de percurso planejado com posição/orientação e motores: é uma etapa
  distinta do planejamento e precisa ser testada separadamente, preservando modo manual.

## Como continuar em etapas

1. Inspecionar o estado atual, ler referências e requisitos locais. Explicar decisões.
2. Configurar células de 1 × 1 m; definir origem, índices, centros e IDs determinísticos;
   mostrar IDs de modo legível e localizar células na árvore Webots. Distinguir linhas
   da grade de nós/células reais. Documentar como converter mundo ↔ célula.
3. Construir ocupação e conexões com a geometria existente, respeitando o tamanho do robô
   e a passagem ao longo das arestas. Um centro livre não garante um trajeto livre.
   A margem conservadora atual do gerador é aproximadamente 0,544 m de raio: avaliar
   estreitamentos causados pela discretização sem reduzir o carrinho silenciosamente.
   Se um ponto não puder ser associado a célula acessível, informar e resolver explicitamente.
4. Adaptar e testar as buscas do Laboratório 2 (profundidade, largura, custo uniforme,
   gulosa e A*) usando a mesma grade, origem/destino e critérios de medição. Considerar
   quatro vizinhos inicialmente; documentar eventuais diagonais e impedir cortar quinas.
   Heurística deve corresponder ao modelo de movimentos e custos escolhido.
5. Produzir visualização de células livres/bloqueadas, rota e expansões, tabela e gráficos
   de distância/custo, nós expandidos e tempo de busca medido. Em grade de custos iguais,
   largura e custo uniforme podem coincidir: explicar, sem inventar diferenças.
6. Validar casos normais, origem=destino, destino inacessível e obstáculos; conferir custo
   somado e validade da rota. Confirmar A* contra custo uniforme nos casos testados.
7. Atualizar documentação e notebook Colab. Reportar o que foi executado de fato no Python,
   no Webots e no Colab, sem confundir testes locais com execução na nuvem.

## Colab e upload anterior

`colab/preparar_colab.py` gera `colab/Carrinho_IESB_Base.ipynb` e
`colab/Carrinho_IESB_Webots.zip`. A base atual extrai códigos, valida a configuração e
mostra mapa SVG. Quatro células foram executadas localmente em pasta vazia e sete testes
de configuração passaram. Não foi testada uma sessão real do Colab. O módulo `controller`
depende do Webots; não executar o controlador como Python comum no notebook.

Upload anterior confirmado no Google Drive:
- Pasta: https://drive.google.com/drive/folders/1XiY3lJaPNz_PdWan59NEJhC0OgXjopxc
- Notebook: https://drive.google.com/file/d/1smhZt7OpYNW3d7X5jVr_9faR9iC7xhIz/view
- ZIP: https://drive.google.com/file/d/1vpZFNIUaIIk8J-GBpE3ANx5KzEiEmAC-/view

As cópias locais empacotadas e as cópias do Drive são anteriores à última melhoria dos
comentários. Atualizar o pacote quando apropriado; preservar links existentes se houver
suporte a atualização, evitando duplicatas. O upload dos códigos foi autorizado antes;
compartilhamento público ou envio ao professor não foi autorizado.

## Ambiente e precauções práticas

Python disponível:
`C:\Users\cleom\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`.
Webots R2025a em `C:\Program Files\Webots`; executável usado anteriormente:
`C:\Program Files\Webots\msys64\mingw64\bin\webotsw.exe`.
Use diretório de trabalho `C:\Program Files\Webots` ao iniciar esse executável.
Não fechar uma sessão do usuário para fazer testes. Os `runtime.ini` dos controladores
contêm caminhos locais e não devem ir no pacote portátil. Manter UTF-8 e comentários PT-BR.

A pasta compartilhada também contém projetos sem relação com o carrinho:
audio_download, video_upscale, textura_madeira, modelo_uml, revisao_marco1 (banco de dados),
universidade_sql e um ZIP de PostgreSQL. Não alterar nem enviar esses arquivos.
Não pressupor checkout limpo ou descartar trabalho anterior. Não há necessidade de novo worktree.
