"""Executa todas as células de código em pasta nova, sem Webots nem sessão Colab.

Rodar em processo Python novo. Não simula bibliotecas nem pula os experimentos.
Fora do IPython, o notebook salva imagens e informa onde abri-las.
"""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
from zipfile import ZipFile

RAIZ = Path(__file__).resolve().parents[1]


def main():
    notebook = RAIZ / "colab/Carrinho_IESB_Base.ipynb"
    pacote = RAIZ / "colab/Carrinho_IESB_Webots.zip"
    with ZipFile(pacote) as arquivo:
        nomes = arquivo.namelist()
        assert not any(n.endswith("runtime.ini") for n in nomes)
        assert all(n.split("/")[0] not in {"tmp", "audio_download", "video_upscale",
                   "textura_madeira", "modelo_uml", "revisao_marco1", "universidade_sql"} for n in nomes)
    dados = json.loads(notebook.read_text(encoding="utf-8"))
    contexto, executadas = {"__name__": "__main__"}, []
    original = Path.cwd()
    with tempfile.TemporaryDirectory(prefix="validar_carrinho_") as pasta:
        try:
            os.chdir(pasta)
            for indice, celula in enumerate(dados["cells"]):
                if celula["cell_type"] == "code":
                    print(f"EXECUTANDO CÉLULA {indice}", flush=True)
                    exec(compile("".join(celula["source"]), f"celula_{indice}", "exec"), contexto)
                    executadas.append(indice)
            assert contexto["resultado_testes"].wasSuccessful()
            assert len(contexto["tabela"]) == 15
            assert len(list(contexto["saida"].glob("rota_*.png"))) == 15
            assert (Path.cwd()/pacote.name).read_bytes() == pacote.read_bytes()
        finally:
            os.chdir(original)
    registro = {"data_utc": datetime.now(timezone.utc).isoformat(), "celulas_codigo": executadas,
                "quantidade_testes": contexto["resultado_testes"].testsRun,
                "comparacoes": len(contexto["tabela"]), "sucesso": True,
                "ambiente": "Python local em processo novo e pasta temporária vazia; não é nuvem Colab",
                "notebook_sha256": hashlib.sha256(notebook.read_bytes()).hexdigest(),
                "zip_sha256": hashlib.sha256(pacote.read_bytes()).hexdigest()}
    destino = RAIZ / "test-results/etapa3_notebook.json"
    destino.parent.mkdir(exist_ok=True)
    destino.write_text(json.dumps(registro, ensure_ascii=False, indent=2), encoding="utf-8")
    print("NOTEBOOK LOCAL APROVADO:", len(executadas), "células de código; 15 comparações.")


if __name__ == "__main__":
    main()
