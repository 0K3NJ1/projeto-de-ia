# Rascunho de PEAS — Carrinho no Campus Edson Machado

**Disciplina:** Inteligência Artificial — 2026/2, IESB  
**Professor:** Rodrigo Gonçalves Pinto  
**Integrantes:** |Arthur de Oliveira Borges 2512130009| Izaias Lopes 2512082018| Leonardo Alencar 2512082039|

**Situação:** especificação do agente proposto; protótipo atual controlado manualmente.

## 1. Domínio e objetivo propostos

Desenvolver um agente para planejar e executar a navegação de um carrinho entre
pontos do térreo do Campus Edson Machado do IESB. O escopo inicial é o
deslocamento entre uma origem e um destino escolhido pelo usuário. A simulação
utiliza Webots e Python. A futura adaptação para um carrinho físico será tratada
em outra etapa.

O objetivo inicial do agente planejado é encontrar um caminho válido entre uma
origem e um destino, minimizando a distância total percorrida. A representação
discreta utilizará pontos de referência como estados e passagens permitidas como
conexões. A integração entre planejamento de rota e motores ainda não existe.

O cenário atual é provisório: a planta oficial foi solicitada e ainda não foi
recebida. As coordenadas em metros são estimativas para desenvolvimento, não
medidas reais do campus. O recorte inicial de navegação entre pontos do campus
deve estar alinhado com o professor, pois o enunciado geral propõe roteirização
de entregas em uma cidade.

## 2. Especificação PEAS do agente proposto

PEAS reúne medida de desempenho (Performance), ambiente (Environment),
atuadores (Actuators) e sensores/percepções (Sensors).

| Componente | Especificação para o projeto |
| --- | --- |
| **P — Medida de desempenho** | Concluir o deslocamento até o destino solicitado, utilizando passagens válidas e minimizando a distância total em metros. Na execução física simulada, chegar e parar sem colisões é um critério de sucesso. Na avaliação futura das buscas, registrar custo da rota, nós expandidos e tempo de execução separadamente. Menos expansões não significa necessariamente melhor rota. |
| **E — Ambiente** | Térreo do campus representado inicialmente por um cenário simplificado no Webots: piso, paredes, portas, áreas de circulação e setores. Há 18 pontos identificados, incluindo entrada, biblioteca, atendimento, cantina e blocos. Para a primeira modelagem de busca, assumir mapa conhecido e estático, sem pessoas ou obstáculos móveis, com distâncias fixas. |
| **A — Atuadores** | No robô simulado, dois motores de rodas independentes permitem frente, ré, giro à esquerda, giro à direita e parada. No futuro planejamento discreto, a ação abstrata será deslocar-se de um ponto para um ponto vizinho permitido. Converter essa ação em comandos de motor será uma integração posterior. |
| **S — Sensores/percepções** | Para o planejador inicial, fornecer como entradas o mapa cadastrado, o estado inicial e o destino; o estado corrente será mantido pela simulação discreta. Essas informações são dados conhecidos do modelo, não medições de sensores físicos. No protótipo atual, o controlador recebe comandos do teclado: não há sensores de localização ou de obstáculos. Os sensores do futuro carrinho físico ainda serão definidos. |

As medidas de desempenho acima são critérios propostos. Não constituem resultados
de uma navegação autônoma já implementada. No protótipo manual, quem escolhe as
ações é o operador; o carrinho ainda não toma decisões de rota sozinho.

## 3. Formulação preliminar em cinco componentes

Esta seção atende ao tipo de preparação citado no encerramento do Laboratório 2.
É uma formulação escrita, não uma implementação de busca.

**Representação de estado:** identificador do ponto ocupado pelo agente no
modelo discreto, por exemplo `EXT01` ou `BB01`.

| Componente | Definição proposta |
| --- | --- |
| **1. Estado inicial** | Ponto informado como origem. No exemplo inicial, `EXT01` — Entrada IESB. |
| **2. Ações** | Escolher um ponto vizinho acessível por uma passagem cadastrada. As conexões entre pontos ainda precisam ser definidas; proximidade no mapa não basta para autorizar uma passagem. |
| **3. Modelo de transição** | Ao executar a ação abstrata de ir de `u` a um vizinho `v`, o estado passa a ser `v`. Nesta primeira abstração, assume-se que a ação permitida tem sucesso. |
| **4. Teste de objetivo** | Verificar se o ponto atual é o destino solicitado. Exemplo: destino `BB01` — Entrada Biblioteca. |
| **5. Custo de passo** | Comprimento em metros da passagem cadastrada entre os dois pontos. O custo do caminho é a soma dos trechos. A distância em linha reta só deve ser usada como comprimento do trecho quando a passagem representada for efetivamente direta. |

O exemplo `EXT01` até `BB01` define apenas origem e destino. Ainda não há rota
calculada ou sequência de pontos validada entre eles.

Para esse modelo discreto inicial, propõe-se um ambiente conhecido,
completamente observável quanto ao mapa e estado modelados, estático,
determinístico, sequencial e de um único agente. Essas hipóteses não descrevem
automaticamente o campus real nem eliminam a física contínua do Webots.

## 4. Parte prática já disponível

- Projeto Webots configurado e carrinho com duas rodas motorizadas.
- Controlador Python com frente, ré, esquerda, direita e parar, acionado pelo teclado.
- Funcionamento manual já demonstrado ao professor, conforme relato do integrante.
- Cenário provisório com paredes, portas, blocos e marcadores dos 18 pontos.
- Coordenadas e dimensões editáveis em `campus_config.py`.
- Testes anteriores de movimentos, parada e colisão registrados no projeto.

**Arquivos de referência:** `worlds/etapa2_campus.wbt`,
`controllers/carrinho_manual/carrinho_manual.py`, `campus_config.py` e
`README_ETAPA2.md`, relativos à raiz do projeto.

**Ainda não implementado:** grafo com arestas e custos, algoritmos de busca,
planejamento e execução autônoma de rotas, sensores, aprendizado de máquina e LLM.

## 5. Pendências para finalizar este rascunho

1. O grupo revisar e conseguir explicar cada componente do PEAS.
2. Confirmar a orientação específica da atividade de hoje: formato, prazo e
   eventual pedido de demonstração ou anexo. Os laboratórios não definem um
   pacote formal de entrega do PEAS para 30/09.
3. Confirmar o alinhamento do recorte inicial de navegação no campus com o professor.

A ausência da planta oficial não impede descrever o agente. Deve-se declarar
que o mapa atual é provisório e substituir as coordenadas quando houver medidas
confiáveis. O enunciado geral do projeto permite mapas simulados documentados.

---

## Notas de conferência dos materiais — apoio ao grupo

Estas notas distinguem os pedidos dos arquivos e não acrescentam exigências à
atividade do professor.

- **Laboratório 1, “Encerramento / Para a Próxima Aula”:** solicita o rascunho
  de PEAS do domínio do trio. O checklist do próprio laboratório exige completar
  os TODOs 1–3 e a análise do agente aspirador. São tarefas do laboratório.
- **Laboratório 2, “Encerramento / Para a Próxima Aula”:** solicita o domínio
  escolhido e a formulação em cinco componentes para a oficina. O mesmo material
  relaciona busca não informada, A*, comparação e justificativa da heurística ao
  Marco 1; não afirma que esses algoritmos precisam acompanhar o rascunho de PEAS.
- **Arquivo de ciência de dados:** trata de preparação de dados do Titanic e
  possui seu próprio checklist de entrega. Não foi localizada exigência de anexar
  esse exercício ao PEAS. O título interno o identifica como Laboratório 4,
  embora o nome do arquivo recebido comece com `laboratorio_3`.
- **Enunciado geral do projeto, seções 3.1 e 5.1:** o Marco 1 completo é uma
  entrega diferente e mais ampla, com buscas, três mapas e relatório. A ausência
  de uma exigência de PEAS nesse PDF não anula instruções dadas nos laboratórios,
  oralmente ou no Google Sala de Aula.

**Fontes consultadas:**

- `laboratorio_1_aula02_agentes.ipynb` — encerramento, célula 52 (contagem a partir de 1).
- `laboratorio_2_aula03_busca.ipynb` — “Do mapa ao código”, célula 2, e encerramento, célula 46.
- `laboratorio_3_aula05_ciencia_de_dados.ipynb` — desafio final e checklist.
- `Projeto_Academico_IA_20262 (1).pdf` — páginas 2 e 4.

Rascunho elaborado com apoio de IA a partir dos materiais fornecidos e do estado
do projeto. Requer revisão dos integrantes antes de qualquer submissão.
