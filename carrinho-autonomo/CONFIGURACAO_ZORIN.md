# Configuração local no Zorin OS 18.1

Atualizado em 27/10/2026 para este computador. As evidências desta máquina ficam em `test-results/linux-2026-10-27/`.

## Sistema

- Zorin OS 18.1, base Ubuntu 24.04 (Noble), arquitetura x86_64.
- Kernel `6.17.0-20-generic`.
- Python do sistema `3.12.3`.
- Gráfico Intel Raptor Lake-P com aceleração Mesa/OpenGL 4.6. A NVIDIA RTX 3050 6 GB também aparece no hardware, mas `nvidia-smi` não está disponível; os testes feitos até agora não exigiram o driver NVIDIA.

## Webots

- Webots **R2025a** instalado para este usuário em `$HOME/.local/opt/webots-R2025a`.
- Comando `webots` disponível por `$HOME/.local/bin/webots`; o menu do sistema também recebeu o atalho criado pelo instalador oficial.
- O pacote oficial para Ubuntu 22.04/24.04 veio da [versão R2025a da Cyberbotics](https://github.com/cyberbotics/webots/releases/tag/R2025a). Foi verificado por tamanho, teste bzip2 e inspeção dos caminhos do arquivo antes da instalação.
- A biblioteca `libsndio.so.7`, ausente no Zorin, veio do pacote `libsndio7.0` do repositório Ubuntu Noble configurado neste computador. Ela foi colocada apenas nas bibliotecas locais do Webots, sem instalação global.
- Os sete `controllers/*/runtime.ini` agora apontam para o Python do `.venv` deste projeto, substituindo o caminho `C:/.../python.exe` do Windows. A [documentação do Webots](https://github.com/cyberbotics/webots/blob/R2025a/docs/guide/using-python.md) prevê essa configuração por controlador.

Para abrir o mundo interativo do projeto, execute nesta pasta:

```bash
./iniciar_webots.sh
```

No mundo `etapa3_buscas.wbt`, clique na cena 3D. Para ir ao Bloco H: **T**, digite `Bloco H`, **Enter**, **Enter**, **G**. **C** pausa ou retoma; **espaço** para. Consulte `CAMPUS_INTERIORES.md` para os demais comandos.

## Python e notebooks

O ambiente isolado está em `.venv/` e usa Python 3.12.3 com pip 26.2.2. As bibliotecas diretas instaladas são NumPy 2.5.4, pandas 2.3.3, scikit-learn 1.9.1, Matplotlib 3.11.2, Pillow 12.3.0, ReportLab 4.5.1, JupyterLab 4.6.4, ipykernel 7.4.0, PyTorch 2.15.0 (com suporte CUDA) e Transformers 4.57.6. `requirements-linux.txt` registra as dependências diretas; `requirements-linux.lock.txt` registra todas as versões instaladas.

Para abrir os notebooks locais:

```bash
./iniciar_jupyter.sh
```

Para executar os testes Python puros:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

O PDF PEAS foi gerado com sucesso em uma pasta temporária usando as fontes Arimo do Zorin. O gerador `entrega_peas/gerar_canvas_peas.py` agora procura Arial no Windows, Arimo no Linux e DejaVu como alternativa.

## Verificações nesta máquina

- 39 testes Python puros: aprovados.
- Webots R2025a e controlador pelo `.venv`: aprovados.
- Etapa 1, movimentos: aprovada.
- Etapa 2, campus: aprovada.
- Etapa 3, cinco buscas: aprovada.
- Etapa 4, navegação automática: aprovada, incluindo rota até H01, pausa/retomada, parada e falha sem progresso.
- Interiores do campus: 51 trechos aprovados em sequência, cobrindo os dez setores, circulação interna e retorno à entrada; `test-results/linux-2026-10-27/interiores_full_console.log` terminou com `RESULTADO INTERIORES: TODOS OS 10 SETORES E CIRCULACAO INTERNA APROVADOS`.
- Notebook local: 8 células de código executadas, 15 comparações e testes internos aprovados por `colab/validar_notebook.py`; registro em `test-results/etapa3_notebook.json`. Esta execução foi local, não em uma sessão hospedada do Colab.

Esses ensaios são da simulação local. O projeto ainda não valida sensores, obstáculos dinâmicos ou o carrinho físico.
