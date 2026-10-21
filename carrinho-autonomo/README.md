# Carrinho IESB — Webots e Python

**21/10/2026 — blocos ampliados:** abra `worlds/etapa3_buscas.wbt` (interativo).
T → **Bloco H** → Enter → Enter → G leva ao centro do bloco. Também pode usar
T e clicar dentro dele. Todos os dez interiores têm acesso; carrinho mantido
na escala 3. Leia [CAMPUS_INTERIORES.md](CAMPUS_INTERIORES.md).

**Para escolher quadrados e visualizar buscas dentro do Webots:** abra
`worlds/etapa3_buscas.wbt` e consulte [GUIA_BUSCAS_WEBOTS.md](GUIA_BUSCAS_WEBOTS.md).

**Etapa 1:** movimentos manuais, confirmados pelo usuário.
**Etapa 2:** cenário provisório do campus, com 18 pontos de referência.

Para abrir o campus, use `worlds/etapa2_campus.wbt`. O controlador manual é o
mesmo da Etapa 1. Consulte o [guia da Etapa 2](README_ETAPA2.md) para editar
coordenadas, setores, portas, paredes e dimensões em `campus_config.py`.
**Etapa 3:** grade navegável de 1 m, cinco buscas do Laboratório 2 e métricas.
Consulte [README_ETAPA3.md](README_ETAPA3.md) e abra `output/buscas/index.html`.
**Etapa 4:** condução automática em Python no mundo `etapa3_buscas.wbt`:
G inicia, C pausa/retoma e espaço para. Localização ideal por Supervisor,
seguimento por motores e manual preservado. Leia [README_NAVEGACAO.md](README_NAVEGACAO.md).

## Etapa 1 — movimentos básicos

O projeto começou com uma pasta vazia, contendo somente `.git`. Esta etapa cria
um carrinho de tração diferencial em um piso plano de 6 × 6 metros. O piso é
apenas uma área de teste; ainda não representa o térreo do IESB Edson Machado.

## Arquivos

| Arquivo | Função |
| --- | --- |
| `worlds/etapa1_manual.wbt` | Mundo para dirigir pelo teclado. |
| `protos/Carrinho.proto` | Modelo reutilizável: chassi, duas rodas com motores e dois apoios esféricos passivos de baixo atrito. A faixa amarela indica a frente. |
| `controllers/carrinho_manual/carrinho_manual.py` | Controlador Python: leitura do teclado e cinco comandos de movimento. |
| `worlds/etapa1_teste.wbt` | Mesmo piso e robô, com controlador de teste. |
| `controllers/teste_movimentos/teste_movimentos.py` | Verifica comandos, deslocamentos, giros e parada na simulação. |
| `controllers/*/runtime.ini` | Configuração local do executável Python, ignorada pelo Git. |
| `.gitignore` | Evita versionar caches, configurações locais e logs. |

## Abrir e testar manualmente

1. Abra o **Webots R2025a** instalado neste computador.
2. Em **File → Open World**, abra `worlds/etapa1_manual.wbt` nesta pasta.
3. Inicie a simulação no modo **Real-time** (velocidade normal).
4. Confira a mensagem `Pronto. Clique na cena 3D...` no console.
5. Clique dentro da cena 3D para que ela receba o teclado.
6. Segure cada tecla por aproximadamente um segundo e solte antes de testar a próxima.

| Tecla | Comando | Resultado esperado |
| --- | --- | --- |
| W ou ↑ | Frente | Anda na direção da faixa amarela. |
| S ou ↓ | Ré | Anda no sentido oposto à faixa amarela. |
| A ou ← | Esquerda | Gira para a esquerda no próprio eixo. |
| D ou → | Direita | Gira para a direita no próprio eixo. |
| Espaço ou soltar as teclas | Parar | Zera a velocidade dos dois motores. |

A frente acompanha a orientação do carrinho, não a orientação da tela. Duas
direções diferentes pressionadas juntas também mandam parar. Espaço tem
prioridade sobre os comandos de movimento. W e ↑ juntas continuam sendo frente.

Faça a sequência **frente → parar → ré → parar → esquerda → parar → direita → parar**.
Confirme que o carrinho inicia parado, que ambos os giros correspondem aos
comandos e que o console mostra as mudanças de comando. Para voltar ao ponto
inicial, use **Simulation → Reset**. O piso não tem paredes; mantenha o teste
perto do centro.

## Executar o teste automático

Abra `worlds/etapa1_teste.wbt` e inicie a simulação. Ele usa o mesmo modelo e a
mesma classe `Carrinho` do controlador manual. O teste verifica:

- mapeamento de W/S/A/D e setas, ausência de teclas, espaço e conflitos;
- estado inicial parado;
- deslocamento para frente e para trás, sem desvio significativo;
- giros para os dois lados, com pouco deslocamento do centro;
- ausência de deslocamento e giro após cada comando de parada.

O console deve exibir linhas `PASS` e terminar com
`RESULTADO: TODOS OS TESTES PASSARAM`. **O mundo de teste encerra a instância do
Webots automaticamente**, com código 0 em sucesso ou 1 em falha. Salve outros
trabalhos antes de abri-lo. Depois abra novamente o mundo manual para dirigir.
O teste também salva uma imagem da cena em `test-results/etapa1.png`.

O `Supervisor` está habilitado somente no mundo de teste para medir a posição
real simulada. Não é um sensor do carrinho nem um algoritmo de navegação. O
controlador manual usa apenas `Robot`, teclado e os dois motores. A entrega de
teclas pela janela gráfica deve ser conferida pelo teste manual acima.

## Python neste computador

Foi encontrado Webots R2025a, mas nenhum `python` no PATH da sessão. Para esta
etapa, os dois `runtime.ini` locais apontam para o Python 3.12.14 disponível em:

```text
C:/Users/cleom/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe
```

Nenhuma biblioteca adicional precisa ser instalada. O módulo `controller` é
fornecido pelo Webots quando ele inicia o controlador. Portanto, não execute o
controlador diretamente com `python carrinho_manual.py` nem instale um pacote
chamado `controller` pelo pip.

Esse caminho é específico deste computador e pode mudar com o ambiente do
Codex. Para usar outro Python, edite os dois `runtime.ini`:

```ini
[python]
COMMAND = C:/caminho/para/python.exe
```

Em outro computador, crie esses arquivos ou configure **Tools → Preferences →
General → Python command** no Webots. Os arquivos `runtime.ini` têm prioridade
sobre essa preferência. Os mundos e o PROTO usam caminhos relativos e não
dependem de modelos baixados da internet.

## Como os movimentos funcionam

Cada roda tem um `RotationalMotor`. O controlador chama `setPosition(float("inf"))`
para ativar o controle contínuo por velocidade, depois usa `setVelocity()` em
rad/s. As rodas têm raio de 0,06 m e separação de 0,20 m.

| Movimento | Motor esquerdo | Motor direito |
| --- | ---: | ---: |
| Frente | +3 rad/s | +3 rad/s |
| Ré | −3 rad/s | −3 rad/s |
| Esquerda | −3 rad/s | +3 rad/s |
| Direita | +3 rad/s | −3 rad/s |
| Parar | 0 | 0 |

A velocidade reta ideal é `0,06 × 3 = 0,18 m/s`. A cada passo de 32 ms o
controlador lê o teclado e atualiza os motores. Os apoios passivos estabilizam
o chassi; não adicionam rodas motorizadas. Estes parâmetros são da simulação e
ainda não foram validados em um carrinho físico.

## Limite desta etapa

Não há A*, sensores, câmera, visão computacional, mapa do campus nem navegação
autônoma. Antes de avançar, confirme também o funcionamento manual no Webots.

## Validação realizada em 11/09/2026

Teste executado no Webots R2025a com Python 3.12.14: **todos os testes passaram**,
processo encerrado com código 0 e log de erros vazio. A imagem da cena também
foi inspecionada para conferir o enquadramento e o modelo.

| Comando por aproximadamente 1 segundo | Medição |
| --- | --- |
| Frente | +0,184 m |
| Ré | −0,184 m |
| Esquerda | +1,642 rad |
| Direita | −1,642 rad |
| Parar após cada movimento | Dentro das tolerâncias de 5 mm e 0,02 rad após estabilização. |

O código usa passos inteiros de 32 ms; a duração solicitada é arredondada para
cima. Os valores são medições físicas da simulação, não apenas velocidades
enviadas aos motores. Logs locais em `test-results/webots-stdout.log` e
`test-results/webots-stderr.log`. **Funcionamento manual confirmado pelo usuário
antes do início da Etapa 2.** Nenhuma etapa de navegação foi iniciada.

Referências oficiais da versão utilizada: [Python](https://github.com/cyberbotics/webots/blob/R2025a/docs/guide/using-python.md),
[teclado](https://github.com/cyberbotics/webots/blob/R2025a/docs/reference/keyboard.md)
e [motores](https://github.com/cyberbotics/webots/blob/R2025a/docs/reference/motor.md).
