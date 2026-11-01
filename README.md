# Projeto de Inteligência Artificial — IESB 2026/2

> **Atualização de 01/11/2026:** para baixar e executar em outro computador, leia
> o [guia para o grupo](carrinho-autonomo/GUIA_PARA_O_GRUPO.md).
> O mundo atual está funcional; a adaptação ao croqui medido ainda está em preparação.
> As referências e o progresso dessa adaptação também estão incluídos.

**Centro Universitário IESB — Campus Asa Sul**  
**Disciplina:** Inteligência Artificial (MDC050)  
**Professor:** Rodrigo Gonçalves Pinto  
**Projeto:** *Um agente que evolui: da busca ao agente com LLM*

---

## 📌 Visão Geral do Repositório

Este repositório reúne os artefatos, algoritmos, experimentos e simulações do projeto acadêmico de Inteligência Artificial. O objetivo central é desenvolver um agente inteligente para roteirização e navegação de entregas autônomas no térreo do Campus Edson Machado do IESB.

O projeto está estruturado na evolução contínua do agente ao longo de três fases:

1. **Fase 1 — Busca Clássica (Marco 1):** Planejamento de rota ótima em grafo de estados utilizando buscas cegas e busca informada $A^*$ com heurística Manhattan admissível e consistente, sobre um mapa ingênuo com custo em distância.
2. **Fase 2 — Aprendizado de Máquina (Entrega 11/11):** Previsão do custo real de travessia (tempo em segundos) com base em características observáveis dos trechos (horário de pico/intervalo, rampas, pisos, tráfego e bloqueios temporários) usando modelos de Machine Learning (Regressão e Random Forest). O $A^*$ passa a otimizar tempo real previsto com heurística ajustada.
3. **Fase 3 — Agente com LLM e IA Responsável (Entrega 11/11):** Orquestração do agente através de um Large Language Model que recebe pedidos em linguagem natural, aciona as ferramentas de roteirização e estimativa de tempo (*Function Calling* / *Tool Use*) e devolve a resposta explicada em português.

---

## 📂 Estrutura do Repositório

```text
projeto-de-ia/
├── README.md                     # Visão geral do repositório e contexto acadêmico
├── .gitignore                    # Regras de exclusão para Git e ambientes virtuais
└── carrinho-autonomo/            # Módulo completo do carrinho autônomo (Simulação + Colab)
    ├── buscas.py                 # 5 algoritmos de busca (Profundidade, Largura, Custo Uniforme, Gulosa, A*)
    ├── planejamento.py           # Interface de planejamento e suporte a rotas multiparadas
    ├── grade_navegacao.py        # Discretização do campus em grade de 1.500 células (1.090 centros livres)
    ├── campus_config.py          # Geometria do campus (blocos, setores, dimensões e pontos)
    ├── navegacao.py              # Controlador cinemático diferencial (máquina de estados do seguidor)
    ├── experimentos_buscas.py    # Bateria de ensaios e métricas comparativas em 3 mapas
    ├── gerar_campus.py           # Gerador procedural de mundos e texturas para o Webots
    ├── protos/                   # Modelo 3D físico do robô (Carrinho diferencial com sensores)
    ├── controllers/              # Controladores em Python para o Webots (manual, buscas e testes)
    ├── worlds/                   # Mundos de simulação Webots R2025a
    ├── tests/                    # 42 testes unitários automatizados
    ├── colab/                    # Pacote oficial e notebook para execução no Google Colab
    ├── entrega_peas/             # Formulação PEAS e canvas do agente
    ├── output/                   # Relatórios visuais HTML, CSVs e métricas de desempenho
    └── referencias_academicas/   # PDF oficial do projeto e referências dos laboratórios
```

---

## 🚀 Como Executar

### 1. Testes Automatizados (Python Puro)
Acesse a pasta `carrinho-autonomo` e execute a suíte de testes:
```bash
cd carrinho-autonomo
python -m unittest discover tests -v
```

### 2. Simulação 3D no Webots
1. Abra o **Webots R2025a**.
2. Em **File → Open World**, selecione `carrinho-autonomo/worlds/etapa3_buscas.wbt`.
3. Inicie a simulação em modo **Real-time**:
   - Pressione **T** para selecionar o destino (ex.: `H01`, `Cantina`, `Biblioteca`).
   - Pressione **Enter** para executar a busca de caminho.
   - Pressione **G** para acionar a navegação física autônoma.
   - Pressione **C** para pausar/retomar ou **Espaço** para parar.

### 3. Google Colab
Abra o notebook `carrinho-autonomo/colab/Carrinho_IESB_Base.ipynb` no Google Colab para executar os experimentos comparativos de busca e a validação autônoma.
