# Etapa 2 — ambiente provisório do campus

> Geometria histórica. Para a ampliação de 21/10/2026 e destinos internos,
> leia `CAMPUS_INTERIORES.md`. A configuração atual está em `campus_config.py`.

O cenário é um **esquema didático de 30 × 26 metros**, com entrada, circulação
central, biblioteca, atendimento, cantina e blocos E/B/C/D/H/F/J. As posições,
proporções e relações espaciais foram escolhidas apenas para testar o projeto.
**Não representam a planta oficial do Campus Edson Machado.**

Os setores usam paredes baixas de 0,70 m, sem teto, para permitir a inspeção
superior. Cada um possui uma porta de 1,80 m. Paredes e bancos têm colisão;
grade, rótulos e marcadores são visuais e não impedem a passagem do carrinho.
A grade e as buscas foram acrescentadas na Etapa 3; veja `README_ETAPA3.md`.
Sensores e condução automática continuam pendentes.

## Tamanho do carrinho — atualizado em 16/09/2026

O carrinho do campus está com **escala 3**, configurada em
`robo["escala"]` no arquivo `campus_config.py`. O chassi mede **0,72 × 0,48 m**;
a largura incluindo as rodas é **0,675 m** e o raio das rodas é **0,18 m**.
Para mudar novamente o tamanho, altere `"escala": 3.0`, execute
`gerar_campus.py` e recarregue o mundo. A altura inicial, colisões, apoios,
massas e capacidade de torque acompanham a escala. São parâmetros de simulação,
não especificações do futuro carrinho físico.

O controlador manual permanece igual. Com os motores a 3 rad/s, a velocidade
reta no campus agora é aproximadamente **0,54 m/s**; o giro no próprio eixo
mantém aproximadamente a mesma velocidade angular. Os mundos da Etapa 1
continuam usando escala 1 e foram testados novamente.

## Arquivos criados

| Arquivo ou pasta | Função |
| --- | --- |
| `campus_config.py` | Fonte das coordenadas, nomes, dimensões, portas e posição inicial. |
| `gerar_campus.py` | Valida a configuração e gera os dois mundos e as texturas. |
| `worlds/etapa2_campus.wbt` | Campus para controle manual, já pronto para abrir. |
| `worlds/etapa2_campus_teste.wbt` | Mesmo campus para ensaios automáticos de validação. |
| `worlds/textures/campus/` | 31 imagens PNG locais com IDs, nomes de setores e legendas. |
| `controllers/teste_campus/teste_campus.py` | Testa coordenadas, colisões e os cinco movimentos. |
| `controllers/teste_campus/runtime.ini` | Python local, copiado da configuração manual e ignorado pelo Git. |
| `tests/test_campus_config.py` | Testes da configuração, executados fora do Webots. |
| `requirements-dev.txt` | Pillow, necessário somente para regenerar as imagens de texto. |
| `README_ETAPA2.md` | Este guia. |

Os logs e a imagem de verificação são gravados em `test-results/`, que não é
versionado. Os arquivos de mundos e as texturas geradas devem acompanhar o
projeto, permitindo abri-lo sem executar o gerador.

## Arquivos modificados e compatibilidade

- `protos/Carrinho.proto`: expõe `translation` e `rotation` para escolher a
  posição e a orientação do carrinho. Os valores padrão da Etapa 1 foram mantidos.
- `.gitignore`: passa a ignorar as preferências locais dos mundos de ambas as etapas.
- `README.md`: inclui o acesso à Etapa 2 e registra sua confirmação da Etapa 1.

O arquivo `controllers/carrinho_manual/carrinho_manual.py`, os dois mundos da
Etapa 1 e seu controlador de teste **não foram alterados**. Foram comparados
por hash antes e depois. Não é necessário trocar o controlador para usar o campus.

## Coordenadas em metros

- Origem `(0, 0, 0)`: `EXT01`, Entrada IESB, na superfície do piso.
- Plano de deslocamento: **XY**. Cada ponto armazena somente `(x, y)`.
- **+X**: direita na vista superior; **+Y**: interior do esquema; **+Z**: para cima.
- Piso em `z = 0`; grade com espaçamento de **1 metro**.
- O carrinho começa em `EXT01`, com a frente apontando para **+Y**.

A orientação é local e arbitrária; não implica norte geográfico. Os lados
N/S/L/O das portas significam apenas +Y/−Y/+X/−X neste esquema.
Marcadores azuis identificam `EXT`; os laranjas identificam destinos.
O centro de cada disco corresponde exatamente ao `(x, y)` configurado.
O texto é deslocado visualmente para não cobrir o disco.

| ID | Nome | X | Y |
| --- | --- | ---: | ---: |
| EXT01 | Entrada IESB | 0 | 0 |
| EXT02 | Cruzamento Central | 0 | 10 |
| EXT03 | Acesso Biblioteca | −2 | 4 |
| EXT04 | Acesso Central de Atendimento | 2 | 4 |
| EXT05 | Acesso Bloco E | −2 | 10 |
| EXT06 | Acesso Blocos B/C/D | −7,2 | 15 |
| EXT07 | Acesso Blocos H/F/J | 7,2 | 15 |
| EXT08 | Acesso Cantina | 2 | 10 |
| BB01 | Entrada Biblioteca | −4,5 | 4 |
| CDA01 | Entrada Central de Atendimento | 4,5 | 4 |
| H01 | Entrada Bloco H | 2,4 | 17,4 |
| F01 | Entrada Bloco F | 7,2 | 17,4 |
| J01 | Entrada Bloco J | 12 | 17,4 |
| E01 | Entrada Bloco E | −4,5 | 10 |
| D01 | Entrada Bloco D | −2,4 | 17,4 |
| C01 | Entrada Bloco C | −7,2 | 17,4 |
| B01 | Entrada Bloco B | −12 | 17,4 |
| CAN01 | Cantina | 4,5 | 10 |

Esta tabela registra a configuração inicial. Depois de uma alteração, a fonte
correta é sempre `campus_config.py`.

## Como adicionar ou mover um ponto

Edite o dicionário `pontos` em `campus_config.py`. Para mover `EXT02`, por exemplo:

```python
"EXT02": (0.0, 9.0),
```

Para adicionar um ponto, acrescente uma entrada em **ambos** os dicionários:

```python
# Dentro de pontos:
"NOVO01": (0.0, 7.0),

# Dentro de nomes:
"NOVO01": "Novo acesso",
```

Use IDs únicos com letras maiúsculas, números e sublinhado, começando por letra.
O gerador cria o disco, o rótulo e um `DEF NOVO01` no mundo. Mover um ponto
**não move a sala nem sua porta**: esses elementos são configurados separadamente.
A Etapa 3 associa os locais às células; regenere também seus experimentos após editar.

## Como alterar o cenário

Todas estas opções estão em `campus_config.py`:

| Configuração | O que alterar |
| --- | --- |
| `piso` | Limites `x_min`, `x_max`, `y_min`, `y_max` e espessura do piso. |
| `paredes_padrao` | Espessura e altura das paredes externas e dos setores. |
| `entrada` | Centro X e largura da abertura na borda `y_min`. |
| `setores` | Centro XY, tamanho XY e porta de cada setor. |
| `paredes` | Paredes adicionais em posições específicas. |
| `blocos` | Bancos ou outros volumes simples com colisão. |
| `robo` | ID do ponto inicial e ângulo em radianos ao redor de Z. |
| `robo["escala"]` | Fator de tamanho do carrinho; 3 no campus, 1 é o tamanho original. |
| `marcadores` | Raio dos discos, tamanho e deslocamento dos rótulos. |
| `vista` | Campo visual, margem e proporção de janela para o enquadramento superior. |

Exemplo de setor:

```python
{"id": "BIBLIOTECA", "nome": "Biblioteca",
 "centro": (-8.0, 4.0), "tamanho": (6.0, 4.0),
 "porta": ("L", 1.8, 0.0)}
```

O centro determina a posição da sala. `tamanho` é a largura em X e o
comprimento em Y, medidos entre os eixos das paredes. A porta acima fica no
lado +X, tem 1,80 m de abertura e está centralizada. O terceiro valor desloca
a porta ao longo da parede: em Y nas faces L/O e em X nas faces N/S.

Para uma parede adicional, inclua em `paredes`, por exemplo:

```python
{"id": "DIVISORIA01", "centro": (0.0, 13.0),
 "tamanho": (2.0, 0.16, 0.70)},
```

Aqui `tamanho` é `(X, Y, Z)`, em metros, e a base fica sobre o piso. A mesma
estrutura serve para `blocos`. Nesta etapa os volumes são alinhados aos eixos;
para uma parede perpendicular, troque as dimensões X e Y.

Alterar o piso recalcula suas bordas, a grade e o enquadramento, mas **não
escala automaticamente os setores e pontos**. Isso permite substituir medidas
individualmente quando chegar a planta oficial.

## Aplicar as alterações

Os mundos são arquivos gerados. Edite a configuração, execute o gerador e
**recarregue o mundo no Webots**. Mudanças feitas diretamente no `.wbt` da
Etapa 2 serão substituídas na próxima geração. Reset apenas reinicia a simulação;
para ler o arquivo regenerado, use **File → Reload World** ou reabra o mundo.

No PowerShell, aberto na pasta do projeto, use o Python já disponível aqui:

```powershell
$pythonCampus = 'C:\Users\cleom\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $pythonCampus gerar_campus.py --validar
& $pythonCampus gerar_campus.py
```

Com seu próprio Python no PATH, os comandos equivalentes são:

```text
python -m pip install -r requirements-dev.txt
python gerar_campus.py
```

Pillow já está disponível no Python local usado para esta entrega. **Abrir e
controlar o campus no Webots não exige instalar Pillow**. O gerador precisa dele
apenas para desenhar as texturas dos rótulos. O módulo `controller` continua
sendo fornecido pelo próprio Webots.

O gerador rejeita configurações como pontos dentro de paredes, pontos fora do
piso, dimensões negativas e portas maiores que a parede. Ao redor de cada ponto,
reserva o raio que engloba o carrinho na escala escolhida, mais uma margem
de 0,05 m (aproximadamente 0,54 m no total com escala 3).
Essa função valida a geometria local. A Etapa 3 acrescenta ocupação, arestas
e análise de conectividade em `grade_navegacao.py`.

## Testar no Webots

1. Abra `worlds/etapa2_campus.wbt` com **File → Open World**.
2. Inicie em **Real-time** e clique dentro da cena 3D.
3. Confira a mensagem `Pronto. Clique na cena 3D...` no console.
4. O carrinho está no disco `EXT01`, na parte inferior do mapa. A faixa amarela
   continua indicando a frente. Aproxime a vista com a roda do mouse para
   enxergar o carrinho e ler os IDs; a vista inicial mostra todo o campus.
5. Use **W/↑**, **S/↓**, **A/←**, **D/→**; solte as teclas ou pressione **Espaço**
   para parar. As setas são comandos relativos ao carrinho, não à tela.
6. Valide a entrada, a área de circulação, as portas e os marcadores. O robô
   pode atravessar os discos e rótulos, mas deve ser bloqueado pelas paredes.

A velocidade com o tamanho ampliado é aproximadamente 0,54 m/s. Percorrer os
10 metros entre a entrada e o cruzamento central leva cerca de 19 segundos
em tempo simulado. Para inspecionar outro trecho sem percorrer tudo, altere
`robo["ponto_inicial"]`, regenere e reabra o mundo.

Para rodar os testes de configuração fora do Webots:

```powershell
& $pythonCampus -m unittest discover -s tests -v
```

Para a verificação física, abra `worlds/etapa2_campus_teste.wbt` e execute a
simulação. O console deve terminar com `RESULTADO ETAPA 2: TODOS OS TESTES PASSARAM`.
**O mundo de teste encerra a própria instância do Webots ao terminar**; salve
seu trabalho antes de usá-lo. O controlador `teste_campus` é apenas uma bancada
de ensaio. Seu acesso `Supervisor` à cena não existe no mundo manual, e a
sequência fixa de comandos usada no teste não é navegação autônoma.

## Resultado da validação após ampliar o carrinho (16/09/2026)

- 7 testes da configuração passaram.
- Os 18 marcadores foram encontrados nas coordenadas previstas, sem colisão.
- Os 57 volumes de paredes e blocos foram conferidos quanto a posição, dimensão
  e presença de geometria de colisão.
- Robô inicialmente parado em `EXT01`, apontando para +Y.
- Frente e ré: aproximadamente +0,554 m e −0,554 m em cada ensaio.
- Esquerda e direita: aproximadamente +1,642 rad e −1,644 rad.
- Parada aprovada após os quatro movimentos; colisão física com a parede aprovada.
- Teste de regressão da Etapa 1 aprovado.
- Processos encerrados com código 0; logs de erros vazios.
- Vista superior renderizada e inspecionada em `test-results/etapa2_campus.png`.

Os ensaios reutilizam a classe `Carrinho` do controlador manual. A escolha do
layout provisório e a experiência de direção pelo teclado no campus ficam para
sua validação. **A Etapa 3 foi autorizada e implementada; consulte seu guia.**
