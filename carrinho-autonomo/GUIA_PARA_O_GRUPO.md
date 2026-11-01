# Baixar e executar o Carrinho IESB

Atualizado em 01/11/2026. Repositório: https://github.com/0K3NJ1/projeto-de-ia

## Baixar

```bash
git clone https://github.com/0K3NJ1/projeto-de-ia.git
cd projeto-de-ia/carrinho-autonomo
```

Quem já clonou deve salvar suas alterações e executar `git pull --ff-only`.
Também é possível baixar pelo GitHub em **Code → Download ZIP** e abrir a pasta
`carrinho-autonomo` depois de extrair esse download.

## Python

Use Python 3.12. Para testes, grade, planejamento e navegação independente,
não é necessário instalar o Webots nem bibliotecas externas.

Linux/macOS:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-linux.txt
.venv/bin/python -m unittest discover -s tests -v
```

Windows, no PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-linux.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Apesar do nome, `requirements-linux.txt` lista dependências Python do projeto;
`requirements-linux.lock.txt` registra as versões usadas no Linux do autor.
Para somente regenerar mundos e gráficos, basta `requirements-dev.txt`.

## Webots

1. Instale o **Webots R2025a** no seu computador.
2. Em **Tools → Preferences → General → Python command**, informe o caminho
   absoluto para o Python do seu `.venv` (`.venv/bin/python` no Linux/macOS ou
   `.venv\Scripts\python.exe` no Windows).
3. Abra `worlds/etapa3_buscas.wbt`, inicie a simulação e clique na cena 3D.
4. **T** escolhe destino: digite `Bloco H`, confirme com **Enter**, pressione
   **Enter novamente** para calcular a rota e **G** para o carrinho percorrê-la.
5. **O** escolhe/reposiciona a origem; **1–5** escolhem o algoritmo; **C** pausa ou
   retoma o movimento; **espaço** para. **R** retorna à entrada.

Para dirigir por teclado, abra `worlds/etapa2_campus.wbt` e use W/S/A/D ou setas.
Mundos terminados em `_teste.wbt` são ensaios automáticos e encerram a própria
instância ao terminar. O módulo `controller` vem do Webots: não instale pelo pip.

Arquivos `controllers/*/runtime.ini` não são compartilhados porque contêm o
caminho do Python de cada computador. Se criar um, ele terá prioridade sobre
as preferências do Webots. No Linux, o lançador aceita uma instalação diferente:

```bash
WEBOTS_HOME=/caminho/para/webots ./iniciar_webots.sh
```

## Estado compartilhado

- Mundo funcional: campus provisório ampliado de 21/10, cinco buscas, seleção
  interativa e navegação pelas rodas; controle manual preservado.
- Medições de 29/10: croqui, vista aérea, tabela de leitura e esquema em
  `referencias_medicoes/2026-10-29/`. O eixo de 210 m e a ausência de rampas nas
  escadas perguntadas foram confirmados.
- A infraestrutura de restrição aos corredores já está no código, mas **o mapa
  medido ainda não substituiu o campus ativo**. Faltam confirmações indicadas em
  `LEITURA_CROQUI.md`; não interpretar o esquema de leitura como planta concluída.
- Os testes físicos Linux de 27/10 são do cenário anterior. A preparação do mapa
  teve 42 testes Python aprovados em 29/10. Em 01/11, os 42 testes Python também passaram
  na cópia preparada para publicação; o registro permanece local.
- GPS, IMU e demais dispositivos são simulados; há também uso do Supervisor.
  Isso não constitui validação de sensores ou de um carrinho físico.
- O notebook e o ZIP de `colab/` são o pacote anterior, preservado. Para incorporar
  o código Python atual a uma nova cópia deles, execute `python colab/preparar_colab.py`.
  Esse comando escreve o notebook e o ZIP; não extrai backups. Webots não roda no Colab.

Ambiente virtual, caches, backups, conversas locais e configurações pessoais de
runtime não fazem parte do repositório. Esta atualização compartilha código, guias e referências do mapa; os mundos
e demais arquivos que já estavam no repositório foram preservados. Novos
materiais acadêmicos e evidências históricas ficaram fora do envio por escolha do autor.

Na cópia pública atualizada do gerador PEAS, nomes e matrículas foram substituídos
por campos para preenchimento local. A cópia adicional do PDF PEAS em
`materiais_faculdade/` não foi enviada por conter esses dados; os originais
locais estão preservados. Arquivos já existentes no GitHub não foram removidos.
