# Projeto de IA — Carrinho IESB

Esta pasta é uma cópia de trabalho do projeto recuperado de `backup-documentos.zip`. O ZIP e a recuperação original não foram alterados. O objetivo acadêmico é simular no Webots um carrinho que navega pelo térreo do IESB Edson Machado, com planejamento em Python.

## Estado recuperado

- **Etapa 1:** carrinho com duas rodas e controle manual, documentado em `README.md`.
- **Etapa 2:** cenário provisório do campus e pontos de referência em `campus_config.py` e `worlds/etapa2_campus.wbt`.
- **Etapa 3:** grade de 1 m, cinco buscas e visualizações. Ver `README_ETAPA3.md` e `GUIA_BUSCAS_WEBOTS.md`.
- **Etapa 4:** navegação automática por motores, com localização ideal fornecida pelo Supervisor do Webots. Ver `README_NAVEGACAO.md`.
- **Atualização de 21/10/2026:** interiores dos dez setores ampliados e acessíveis. Ver `CAMPUS_INTERIORES.md` e `VALIDACAO_INTERIORES.md`.
- **Marco 2 em 06/11/2026:** notebook de agente com Qwen e ferramentas de rota/listagem, prompts versionados e bateria de 15 pedidos. Ver `README_AGENTE_MARCO2.md` e `VALIDACAO_AGENTE_MARCO2.md`. A avaliação do modelo é separada dos testes Python e ainda exige revisão do grupo em uma sessão nova do Colab.
- **Reavaliação em 08/11/2026:** a v9 registra a decisão JSON do Qwen, bloqueia argumentos de rota que não constam do pedido e foi medida com os mesmos 15 casos. Os resultados e as falhas permanecem documentados em `VALIDACAO_AGENTE_MARCO2.md`.

O projeto também inclui o notebook Colab, referências acadêmicas, testes Python e resultados locais. Materiais únicos adicionais da disciplina estão em `materiais_faculdade/`. Conversas antigas, backups, evidências históricas e duplicatas foram transferidos para um arquivo recuperável externo em 01/11/2026; veja `LIMPEZA_PROJETO.md`.

As medições de 29/10 e sua interpretação estão em `referencias_medicoes/2026-10-29/`. O mapa medido ainda não substituiu o campus ativo; o estado compartilhado mais recente está em `GUIA_PARA_O_GRUPO.md`.

## Verificação neste Linux

Em 27/10/2026, **39 testes Python** passaram no ambiente virtual. Webots R2025a foi instalado para este usuário no Zorin; as etapas 1 a 4 e os 51 trechos dos interiores passaram em simulações locais. O notebook também executou 15 comparações localmente. Consulte `CONFIGURACAO_ZORIN.md` para versões, comandos, registros e limites da validação.

## Para retomar

1. Leia `GUIA_PARA_O_GRUPO.md`, `CAMPUS_INTERIORES.md` e `README_NAVEGACAO.md` para conhecer o estado atual. O plano antigo `PROXIMA_ETAPA_NAVEGACAO.md`, já implementado, está no arquivo externo indicado em `LIMPEZA_PROJETO.md`.
2. Execute `./iniciar_webots.sh` para abrir o mundo interativo no Webots R2025a instalado neste computador.
3. Confira o fluxo documentado em `GUIA_BUSCAS_WEBOTS.md`. Não altere a geometria antes de verificar o projeto recuperado.
4. Escolha a próxima etapa acadêmica com base nos requisitos do professor. O projeto atual usa localização ideal do simulador; não há validação de um carrinho físico ou de obstáculos dinâmicos.

Os arquivos `.zip` dentro do projeto foram preservados como vieram no backup; o conteúdo deles não foi extraído para esta cópia.
