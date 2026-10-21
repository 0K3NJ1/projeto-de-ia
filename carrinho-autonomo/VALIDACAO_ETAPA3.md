# Registro de validação — 01/10/2026

> Etapa posterior (05/10/2026): navegação física implementada; consulte
> `VALIDACAO_NAVEGACAO.md`. Os registros abaixo são históricos da visualização.

## Complemento: interface de busca no Webots

**02/10/2026:** o usuário testou a interface e confirmou que tudo funcionou
após a correção do teclado descrita abaixo. A pendência de uso físico registrada
no ensaio anterior está resolvida por essa confirmação. A pedido do usuário,
os pontos de expansão no Webots passaram de azul para magenta vivo.

### Correção do teclado após teste de uso

O Enter não iniciava a busca porque o controlador aceitava apenas ASCII 10/13.
No Webots R2025a, Return chega como 4, Enter numérico como 5 e Backspace como 3.
Corrigidos confirmação, execução e apagar texto. Q cancela a edição/animação,
pois Escape é interceptado pela janela 3D. O ensaio passou a usar 4, 5 e 3,
incluindo correção do ID digitado antes de executar as cinco buscas.
Fonte da conversão: [WbRobot::keyPressed](https://github.com/cyberbotics/webots/blob/R2025a/src/webots/nodes/WbRobot.cpp#L674).
Os testes anteriores com ASCII 13 não cobriam essa integração e não eram
evidência suficiente de funcionamento do Enter físico.

- Mundo interativo: `worlds/etapa3_buscas.wbt`; guia: `GUIA_BUSCAS_WEBOTS.md`.
- 24 testes Python passaram, incluindo escolha por ID/local e posição atual.
- Ensaio `etapa3_buscas_teste.wbt` aprovado nos cinco algoritmos: seleção por
  texto, pausa, passo a passo, desenho final e verificação de que o carrinho não andou.
- Célula bloqueada recusada; célula livre desconectada retornou sem rota.
- Origem editável, origem=destino e retorno a EXT01 aprovados.
- Corrigido desempate de associação sob ruído numérico de aproximadamente 1e-15 m.
  Distâncias iguais após arredondamento a 1e-9 m usam o ID como desempate;
  a validação geométrica dos conectores continua usando as coordenadas reais.
- Painel, seleção, grafo e busca em Python. O modelo físico não foi alterado.
- Controlador manual com o mesmo SHA-256 registrado abaixo.
- Logs: `test-results/buscas_interface_stdout.log` e `buscas_interface_stderr.log`.
- Captura: `test-results/etapa3_buscas_webots.png`.
- Notebook atualizado executado localmente: sete células de código, 24 testes
  e 15 comparações. Registro com hashes em `test-results/etapa3_notebook.json`.
- O ensaio chama os comandos da interface diretamente dentro do Webots.
  A injeção de teclas rápidas pela automação da janela não confirmou o
  recebimento pelo controlador; a seleção com mouse físico requer conferência
  pelo usuário. Não confundir esse limite do teste com validação de clique real.

Os registros abaixo preservam a validação anterior, antes da interface interativa.

## Python local

- 18 testes unitários passaram (7 anteriores e 11 novos).
- Grade: 780 células; 368 centros livres; 588 arestas; 7 componentes.
- 18 referências associadas à componente da entrada, com conectores livres.
- A*, custo uniforme e largura com mesmo custo nos 324 pares de locais.
- Regressão dos resultados originais da Romênia aprovada nas cinco buscas.
- Casos origem=destino, estado inválido, destino desconectado e melhoria posterior
  de caminho aprovados. Rotas e custos foram recalculados a partir das arestas.
- Três mapas: 60, 186 e 368 nós livres; 103, 303 e 588 arestas, respectivamente.
- 31 amostras de tempo por algoritmo e mapa, além de aquecimento.
- 15 gráficos de rotas/expansões, mapa de IDs e painel comparativo gerados.
- Gráficos e imagem do Webots inspecionados visualmente.

Para EXT01 → H01: custo ótimo na grade 21 m; 0,848528 m adicionais de conectores
(total geométrico 21,848528 m). Largura/uniforme expandiram 223 nós, A* 72,
gulosa 21; profundidade produziu 163 m e 312 expansões. A gulosa acertou o ótimo
neste exemplo, mas não possui essa garantia. A* reduziu expansões em 67,7% frente
ao custo uniforme. Consulte `output/buscas/comparacao.csv` para os tempos medidos
mais recentes, e `resultados.json` para as amostras brutas e hashes das fontes.

## Webots R2025a

Foi usada uma instância separada, minimizada, com o mundo `etapa2_campus_teste.wbt`.
A sessão já aberta pelo usuário foi preservada.

- 18 marcadores e 57 objetos de colisão conferidos.
- 780 células encontradas por DEF, posições verificadas, sem colisão física.
- Rota A* EXT01 → H01 calculada (21 m), sem acionar motores pela rota.
- Robô parado na entrada e orientação inicial corretos.
- Frente: +0,554 m; ré: −0,554 m; giros: +1,642 e −1,644 rad.
- Parada e colisão com parede aprovadas; controlador imprimiu a conclusão de sucesso
  e chamou `simulationQuit(0)`.
- Único aviso: porta 1234 já ocupada pela outra instância; Webots usou 1235.

Logs locais: `test-results/etapa3_webots_stdout.log` e `etapa3_webots_stderr.log`.
Captura: `test-results/etapa2_campus.png`. O nome da captura é o do ensaio existente;
agora mostra as células adicionadas.

SHA-256 do controlador manual, antes e depois:
`2f5375e961f70e22686f511c28aa3a2453e9f52902b1703e47f219c06d3a532e`.
O PROTO físico e os mundos da Etapa 1 não foram modificados nesta etapa.

## Notebook e publicação

Notebook e ZIP locais: `colab/Carrinho_IESB_Base.ipynb` e `Carrinho_IESB_Webots.zip`.
As seis células de código foram executadas em sequência, em processo Python novo
e pasta temporária vazia: 18 testes passaram, 15 comparações foram produzidas e
o ZIP incorporado foi conferido byte a byte. Fora do IPython, a exibição inline
é substituída pela indicação da pasta; os cálculos e gráficos são executados.
Logs: `test-results/etapa3_notebook.log` e `etapa3_notebook.json`.
Após o ensaio, somente este registro documental foi atualizado dentro do pacote;
a igualdade dos demais arquivos e células de código foi conferida novamente.
Não foi executada uma sessão real na nuvem do Colab.
Os links históricos do Drive não foram atualizados. Nada foi enviado ao professor,
ao Classroom ou publicado. Relatório acadêmico final e AUTORES dependem da revisão
e das informações reais do trio.
