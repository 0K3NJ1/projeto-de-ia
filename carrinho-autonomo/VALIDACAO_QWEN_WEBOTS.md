# Validação no Webots: A* calcula → Qwen explica (01/11/2026)

Esta etapa integra a explicação gerada pelo modelo de linguagem **Qwen2.5-1.5B-Instruct** (Laboratório 7) diretamente ao controlador interativo do **Webots R2025a**, mantendo a simulação em tempo real e os comandos físicos desacoplados.

---

## 1. Princípio de Funcionamento
1. **O A\* calcula:** a rota, distâncias (`distancia_grade_m`, `conectores_m`, `percurso_total_m`) e caminho de células continuam sendo gerados exclusivamente pelos módulos em Python puro (`planejamento.py` e `buscas.py`).
2. **O Qwen apenas explica:** o modelo recebe estritamente o JSON com os dados calculados via prompt padronizado (mesmo de `colab/rotas_comentadas.py`). Ele não é fonte de distâncias nem inventa caminhos.
3. **Execução desacoplada (processo separado):**
   - Um processo filho (`servidor_qwen.py`) carrega o modelo em GPU/CPU e processa as requisições via stdin/stdout JSON.
   - O controlador principal do Webots (`carrinho_buscas.py`) envia a requisição e continua o loop de controle a cada passo da física (`robot.step()`), sem bloquear o teclado ou os motores.
   - A tecla **G** continua disponível imediatamente para iniciar o movimento físico a qualquer momento.
   - Se uma nova rota for calculada ou invalidada (via T, O, Espaço ou troca de algoritmo), a explicação antiga pendente é descartada.

---

## 2. Resultados no Ambiente Zorin OS / Linux
- **GPU:** NVIDIA GeForce RTX 3050 Laptop GPU (6 GB VRAM) ativa via CUDA 13.2.
- **Carregamento inicial do modelo:** ~8,4 s.
- **Tempo de geração de texto pelo Qwen:** ~2,9 s a 6,3 s (em `float16` na GPU).
- **Consumo de disco:** ~2,9 GB em `.cache/huggingface/` (ignorado pelo Git).
- **Execução offline:** O servidor roda com `HF_HUB_OFFLINE=1`, sem requisitar internet durante as simulações.

---

## 3. Testes Automatizados e Ensaios Executados
1. **58 Testes Unitários Python:**
   - 49 testes anteriores (buscas, campus, grade, navegação, interiores e rotas comentadas).
   - 9 testes novos em `tests/test_explicador_qwen.py` (verificação de nomes de pontos, ruído numérico, preservação de posições intermediárias e comunicação assíncrona por pipes).
   - Resultado: **58 testes aprovados (OK)** em ~5,3 s.
2. **Execução Real do Modelo Isolado:**
   - Executado `servidor_qwen.py --exemplo` para a rota *Entrada IESB → Biblioteca* (15,71 m).
   - Texto gerado conferido contra os dados numéricos de referência.
3. **Ensaio Físico no Webots:**
   - Executado em modo batch (`webots --batch --mode=fast`) com controlador de ensaio automatizado.
   - Rota calculada com A* no Webots; resposta do Qwen recebida e formatada no console com sucesso.
   - Registro arquivado em `test-results/linux-2026-11-01/qwen-webots/`.

---

## 4. Limitações Conhecidas
- O Qwen gera um texto explicativo plausível, mas continua sujeito a pequenas imprecisões de redação (por exemplo, referir-se a conectores como parâmetros de cálculo). Os números de referência calculados pelo Python sempre são exibidos no console logo abaixo do texto gerado.
- Esta etapa cobre exclusivamente **"A\* calcula → Qwen explica"**. A interpretação de pedidos livres (Lab 8), chamadas de ferramentas (Lab 9) e previsão de tempo de viagem por aprendizado de máquina serão integradas nas etapas subsequentes.

