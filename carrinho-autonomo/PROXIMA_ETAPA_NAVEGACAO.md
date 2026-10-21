# Próxima etapa: seguir a rota no Webots

> **Implementada em 05/10/2026, após autorização para continuar neste novo chat.**
> Guia atual: `README_NAVEGACAO.md`; evidências: `VALIDACAO_NAVEGACAO.md`.
> O restante preserva o planejamento histórico anterior à implementação.

Estado em 02/10/2026. O usuário confirmou o funcionamento da seleção e das
cinco buscas no mundo `worlds/etapa3_buscas.wbt`. Solicitou destacar as expansões:
agora são magenta vivo; rota vermelha, origem verde, conectores roxos.
Perguntou como implementar navegação automática e se convém um chat novo.
Este documento prepara a continuidade; não autoriza por si só iniciar a etapa.

## Arquivos e cuidados

- `planejamento.py`: `planejar` devolve caminho, origem, destino, posições reais,
  custo e expansões. Compartilhado com o Colab, sem importar Webots.
- `grade_navegacao.py`: grade de 1 m, grafo de centros e validação geométrica.
  Existem células livres desconectadas; não criar rotas atravessando paredes.
- `controllers/carrinho_buscas/carrinho_buscas.py`: Supervisor, interface,
  animação e motores atualmente parados em cada passo.
- `controllers/carrinho_manual/carrinho_manual.py`: controle manual Python
  existente; preservar. Modelo físico em `protos/Carrinho.proto`, escala 3.
- Enter no Webots R2025a chega como 4/5, Backspace como 3. Escape é interceptado
  pela janela; usamos Q. Não voltar a testar apenas ASCII 13.
- `controllers/teste_buscas/teste_buscas.py`: ensaio no Webots, com os códigos
  reais das teclas. `tests/`: 24 testes Python na última validação completa.
- `colab/preparar_colab.py`: atualiza ZIP e notebook; exclui runtime.ini local.
- `GUIA_BUSCAS_WEBOTS.md` e `README_ETAPA3.md`: uso e limitações do mapa.

## Implementação sugerida, quando solicitada

1. Converter o caminho em alvos geométricos, incluindo a ligação da posição
   atual ao primeiro centro e do último centro ao destino. Validar o percurso
   inteiro com a margem do robô; não cortar esquinas ao simplificar pontos.
2. Criar controlador de movimento em Python separado do algoritmo de busca:
   primeiro girar até o rumo do próximo ponto, depois avançar e corrigir o rumo.
   Verificar eixos e sinal dos motores no modelo antes de aplicar fórmulas.
3. Para a primeira demonstração, propor posição/orientação obtidas do Supervisor
   como localização ideal da simulação, explicitamente documentada. Não fingir
   que são sensores reais. Encoders/odometria podem ser uma etapa posterior.
4. Acrescentar estados parado, girando, avançando, pausado, concluído e falha;
   comando explícito para iniciar a rota e parada imediata. Mudança de destino
   ou origem deve cancelar movimento e invalidar a rota anterior.
5. Dirigir fisicamente pelos motores: não usar teleportes para executar a rota.
   Limitar velocidades, desacelerar na chegada e parar se não houver progresso
   ou se o robô sair do corredor seguro. Considerar erro de rastreamento na margem.
6. Testar trecho reto, curva de 90 graus, destino igual à origem, rota inexistente,
   pausa/parada e caminho completo sem contato com obstáculos. Medir erro final
   e tempo de deslocamento separadamente do tempo de cálculo da busca.

Todo o planejamento e controle novo deve ser Python. O Colab continua executando
buscas, gráficos e testes independentes do Webots; a física e os motores rodam
no simulador instalado. Não há implementação de condução automática ainda.
