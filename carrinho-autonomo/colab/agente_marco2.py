"""Agente do Marco 2: pedido em português -> ferramenta -> resposta.

Este módulo usa apenas Python puro. O modelo de linguagem é recebido como uma
função ``conversar(mensagens, ferramentas)``; o notebook carrega o Qwen e fornece
essa função. Separar as duas partes permite testar as regras sem baixar o modelo.

O A* continua em ``buscas.py``. Este módulo nunca controla os motores do Webots.
"""

import json
import re
import time
import unicodedata

from colab import rotas_comentadas


# Cada chave é uma versão preservada do prompt. Na avaliação, trocamos a versão
# sem alterar as funções de busca nem reescrever as regras anteriores.
PROMPTS = {
    "v1": (
        "Você ajuda a consultar rotas no mapa provisório do campus IESB. "
        "Responda em português."
    ),
    "v2": (
        "Você ajuda a consultar rotas no mapa provisório do campus IESB. "
        "Use calcular_rota para perguntas sobre caminho ou distância entre dois "
        "locais. Use listar_locais para perguntar quais locais estão cadastrados. "
        "Para conversa comum, responda sem ferramenta. Não invente rotas, "
        "distâncias, tempos de viagem nem locais. Os argumentos devem conter "
        "nomes ou IDs cadastrados. Se faltar origem ou destino, peça esclarecimento. "
        "Responda em português e cite a distância total que a ferramenta devolveu."
    ),
    "v3": (
        "Você ajuda a consultar rotas no mapa provisório do campus IESB. "
        "Use calcular_rota para perguntas sobre caminho ou distância entre dois "
        "locais. Use listar_locais para perguntar quais locais estão cadastrados. "
        "Para conversa comum, responda sem ferramenta. Não invente rotas, "
        "distâncias, tempos de viagem nem locais. Os argumentos devem conter "
        "nomes ou IDs cadastrados. Se faltar origem ou destino, peça esclarecimento. "
        "Responda em português e cite a distância total que a ferramenta devolveu. "
        "Use no máximo duas frases e não liste todos os IDs das células. "
        "Exemplos: 'Tô na Biblioteca, quero ir ao Bloco H' pede "
        "calcular_rota(Biblioteca, Bloco H); 'Quais lugares posso escolher?' pede "
        "listar_locais(); 'Bom dia' não pede ferramenta. "
        "Uma resposta de erro da ferramenta significa que não há rota confirmada."
    ),
    "v4": (
        "Você é um agente do mapa provisório do campus IESB. "
        "Locais válidos (nomes e IDs): "
        + ", ".join(f"{identificador}={nome}"
                    for identificador, nome in rotas_comentadas.grade.config.nomes.items())
        + ". Para QUALQUER pedido de rota ou distância entre dois locais válidos, "
        "sua PRIMEIRA resposta deve ser SOMENTE uma chamada de calcular_rota com "
        "origem e destino. Não dê rota nem número de memória. Depois que receber "
        "o resultado da ferramenta, responda em português em até duas frases, "
        "copiando o campo distancia_total_formatada_m exatamente, seguido de m. "
        "Para pedir a lista de lugares, chame listar_locais. Para cumprimento "
        "ou pergunta sobre suas capacidades, responda sem ferramenta. Se um "
        "local não estiver na lista, avise que está fora do mapa sem inventar "
        "rota. Se faltar origem ou destino, peça esclarecimento. "
        "Não copie texto do pedido como resposta e não use exemplos imaginários. "
        "Nunca liste todos os IDs das células na resposta final."
    ),
    "v5": (
        "Você ajuda com rotas no mapa provisório do campus IESB. "
        "Quando a pessoa pedir caminho ou distância, chame calcular_rota com "
        "a origem e o destino extraídos do pedido. Nunca responda rota ou "
        "distância de memória. Quando pedir locais disponíveis, chame "
        "listar_locais. Para saudação ou pergunta geral, responda sem ferramenta. "
        "Se a ferramenta devolver erro, avise que a rota não foi confirmada. "
        "Após receber uma rota, copie distancia_total_formatada_m exatamente "
        "e diga que é em metros no mapa provisório. Responda em português."
    ),
    "v6": (
        "Você decide se precisa de uma ferramenta para responder pedidos sobre "
        "o campus IESB. Se o pedido perguntar uma rota ou distância ENTRE DOIS "
        "locais, responda APENAS um objeto JSON com as chaves name e arguments; "
        "name deve ser calcular_rota, arguments deve conter origem e destino "
        "copiados do pedido. Se pedir os locais cadastrados, use name "
        "listar_locais e arguments como objeto vazio. "
        "Para saudação ou pergunta geral, responda diretamente em português. "
        "Quando receber o resultado de uma ferramenta, explique-o em português "
        "sem criar números; copie distancia_total_formatada_m e diga metros. "
        "Nunca calcule a rota de memória."
    ),
    "v7": (
        "Você atende consultas ao mapa provisório do campus IESB. "
        "Catálogo exato de locais (ID=nome): "
        + "; ".join(f"{identificador}={nome}"
                    for identificador, nome in rotas_comentadas.grade.config.nomes.items())
        + ". Decida a ação para o pedido atual. Na PRIMEIRA resposta, se houver "
        "origem e destino cadastrados e o pedido tratar de rota, caminho ou "
        "distância, chame calcular_rota com origem e destino do pedido. "
        "Se pedir os locais disponíveis, chame listar_locais. "
        "Se algum local pedido não constar do catálogo, responda que está fora "
        "do mapa e não chame ferramenta. Se faltar um local, peça o nome ausente. "
        "Para saudação ou pergunta sobre capacidades, responda sem ferramenta. "
        "A chamada deve ser somente o JSON de ferramenta do formato solicitado "
        "pela interface, sem texto anterior ou posterior. "
        "Depois do resultado de calcular_rota, responda em uma frase com origem, "
        "destino e distancia_total_formatada_m seguida de m. Não enumere células "
        "nem estime outro valor. Depois de listar_locais, inclua todos os pares "
        "ID: nome, sem omissões. Responda em português e não copie o pedido."
    ),
    "v8": (
        "Você decide qual ferramenta usar para o pedido atual sobre o campus IESB. "
        "Responda somente um objeto JSON com duas chaves: name e arguments. "
        "name deve ser calcular_rota, listar_locais ou null. "
        "Se for pedido de rota ou distância entre dois locais cadastrados, "
        "use calcular_rota e arguments com origem e destino. Copie os nomes ou "
        "IDs que aparecem no pedido, sem trocá-los por acessos próximos. "
        "Se pedirem locais disponíveis, use listar_locais e arguments vazio. "
        "Para conversa comum, local ausente ou fora do catálogo, use null e "
        "arguments vazio. Não escreva rota, custo ou explicação. Catálogo: "
        + "; ".join(f"{identificador}={nome}"
                    for identificador, nome in rotas_comentadas.grade.config.nomes.items())
    ),
    "v9": (
        "Você seleciona uma ação para um assistente de rotas do campus IESB. "
        "Responda SOMENTE um objeto JSON válido. A chave name deve ser calcular_rota, "
        "listar_locais ou null. A chave arguments deve ser um objeto. Para "
        "calcular_rota, use exatamente origem e destino com nomes ou IDs do catálogo. "
        "Para listar_locais ou null, use arguments vazio. Selecione calcular_rota "
        "para um pedido de trajeto ou distância com origem e destino do catálogo; "
        "listar_locais para pedir locais disponíveis; null para conversa, local "
        "ausente ou local fora do catálogo. Não escreva caminho, custo nem "
        "explicação. Catálogo: "
        + "; ".join(f"{identificador}={nome}"
                    for identificador, nome in rotas_comentadas.grade.config.nomes.items())
    ),
}

PROMPT_RESPOSTA_V8 = (
    "Responda em português usando somente o resultado da ferramenta. "
    "Para rota, informe origem, destino e distancia_total_formatada_m em metros "
    "no mapa provisório, sem enumerar células ou inventar outro custo. "
    "Para lista, inclua todos os pares ID: nome recebidos. "
    "Se a ferramenta der erro, explique que não há rota confirmada."
)


def calcular_rota(origem: str, destino: str) -> str:
    """Calcula uma rota em metros entre dois locais do campus com o A*.

    Args:
        origem: nome ou ID do local de partida cadastrado no mapa
        destino: nome ou ID do local de chegada cadastrado no mapa
    """
    # O retorno em texto é o formato esperado pela interface de ferramentas do
    # Qwen. Quem calcula a rota é a função existente, nunca o modelo.
    resultado = rotas_comentadas.calcular_rota(origem, destino)
    if resultado["status"] == "ok":
        # Fornecemos ao modelo uma representação pronta para copiar. O valor
        # original permanece no campo numérico e na referência do Python.
        resultado["distancia_total_formatada_m"] = f"{resultado['distancia_total_m']:.2f}"
    return json.dumps(resultado, ensure_ascii=False)


def listar_locais() -> str:
    """Lista nomes e IDs de locais disponíveis no mapa provisório do campus."""
    # Uma segunda ferramenta permite avaliar se o modelo escolhe corretamente
    # entre calcular caminho, mostrar locais ou apenas conversar.
    nomes = rotas_comentadas.grade.config.nomes
    return json.dumps({"status": "ok", "locais": nomes}, ensure_ascii=False)


FERRAMENTAS = [calcular_rota, listar_locais]


def ler_pedido_de_ferramenta(resposta):
    """Lê uma chamada em <tool_call> ou JSON puro; None indica fala comum.

    Uma marca malformada gera erro explícito. Assim, um pedido quebrado não vira
    silenciosamente uma resposta final e nenhum texto é executado como código.
    """
    if not isinstance(resposta, str):
        raise ValueError("A resposta do modelo precisa ser texto.")
    if "<tool_call" not in resposta:
        # No ensaio local o Qwen produziu apenas o objeto JSON, sem as marcas
        # do template. Às vezes ele usa um bloco ```json. Aceitamos somente
        # um objeto completo com os dois campos da chamada.
        corpo = resposta.strip()
        bloco = re.fullmatch(r"```(?:json)?\s*(\{.*\})\s*```", corpo, re.S | re.I)
        if bloco:
            corpo = bloco.group(1)
        try:
            pedido = json.loads(corpo)
        except json.JSONDecodeError:
            return None
        if isinstance(pedido, dict) and set(pedido) == {"name", "arguments"}:
            return pedido
        return None
    blocos = re.findall(r"<tool_call>\s*(.*?)\s*</tool_call>", resposta, re.S)
    if len(blocos) != 1:
        raise ValueError("Era esperada exatamente uma chamada de ferramenta válida.")
    try:
        pedido = json.loads(blocos[0])
    except json.JSONDecodeError as erro:
        raise ValueError("A chamada de ferramenta não contém JSON válido.") from erro
    if not isinstance(pedido, dict):
        raise ValueError("A chamada de ferramenta precisa ser um objeto JSON.")
    return pedido


def executar_pedido(pedido):
    """Executa somente ferramentas registradas e devolve o resultado em texto.

    Erros retornam como dados para o modelo explicar. Nenhum nome de função vindo
    do modelo é passado a eval, exec, getattr ou ao sistema operacional.
    """
    if not isinstance(pedido, dict):
        return json.dumps({"status": "erro", "erro": "Pedido de ferramenta inválido."})
    nome = pedido.get("name")
    argumentos = pedido.get("arguments")
    if not isinstance(argumentos, dict):
        return json.dumps({"status": "erro", "erro": "Argumentos devem ser um objeto JSON."})

    try:
        if nome == "calcular_rota":
            # Exigir os dois campos evita que o modelo injete parâmetros extras
            # ou chame a busca com valores ausentes e receba um resultado confuso.
            if set(argumentos) != {"origem", "destino"}:
                raise ValueError("calcular_rota exige somente origem e destino.")
            if not all(isinstance(argumentos[k], str) for k in ("origem", "destino")):
                raise ValueError("Origem e destino precisam ser textos.")
            return calcular_rota(argumentos["origem"], argumentos["destino"])
        if nome == "listar_locais":
            if argumentos:
                raise ValueError("listar_locais não recebe argumentos.")
            return listar_locais()
        raise ValueError(f"Ferramenta não autorizada: {nome!r}.")
    except ValueError as erro:
        # Um local desconhecido é informado como erro, sem substituição por um
        # destino parecido. O A* nem é chamado quando a validação falha.
        return json.dumps({"status": "erro", "erro": str(erro)}, ensure_ascii=False)


def distancia_aparece(texto, distancia):
    """Verifica se o total em metros aparece com duas casas decimais.

    Esta é uma checagem numérica simples, não uma avaliação completa da qualidade
    da explicação. Aceita vírgula ou ponto decimal e rejeita número maior que
    contenha os mesmos dígitos como sufixo.
    """
    valor = f"{distancia:.2f}"
    for representacao in (valor, valor.replace(".", ",")):
        if re.search(r"(?<![\d.,])" + re.escape(representacao) + r"(?![\d.,])", texto):
            return True
    return False


def normalizar_frase(texto):
    """Remove acentos e caixa, mantendo espaços para localizar palavras."""
    decomposicao = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in decomposicao if unicodedata.category(c) != "Mn")


def pedido_parece_rota(texto):
    """Reconhece apenas pedidos óbvios de rota para bloquear resposta sem A*."""
    texto = normalizar_frase(texto)
    return bool(re.search(r"\b(rota|caminho|distancia|ir|vou|vai|chego|chegar|"
                          r"leve|levar|bora|saio|sair|saindo|partida|destino)\b", texto)
                or re.search(r"\bde\b.+\b(ate|para|pra)\b", texto))


def pedido_pede_lista(texto):
    """Identifica consulta explícita ao catálogo, que requer listar_locais."""
    texto = normalizar_frase(texto)
    return bool(re.search(r"\b(liste|listar|quais)\b", texto) and
                re.search(r"\b(locais|lugares|destinos)\b", texto))


def resposta_recusa(texto):
    """Sinal simples de recusa; a leitura humana continua necessária."""
    texto = normalizar_frase(texto)
    return (any(marca in texto for marca in (
        "nao esta no mapa", "nao esta cadastrado", "nao e um local", "nao existe",
        "fora do mapa", "fora do dominio", "nao posso calcular", "nao consigo calcular",
    )) or bool(re.search(r"nao (?:ha|tenho) (?:informacoes|dados).{0,80}\bmapa\b", texto)))


def lista_fiel(texto, resultado):
    """Confere cada par ID/nome, sem confundir Cantina com Acesso Cantina."""
    frase = normalizar_frase(texto)
    return all(normalizar_frase(f"{identificador}: {nome}") in frase
               for identificador, nome in resultado["locais"].items())


def lista_de_referencia(resultado):
    """Monta a lista diretamente do catálogo quando o modelo a omite."""
    return "Locais cadastrados: " + "; ".join(
        f"{identificador}: {nome}" for identificador, nome in resultado["locais"].items())


def resposta_de_referencia(resultado):
    """Monta o valor verificado que o notebook mostra ao lado da fala do Qwen."""
    if resultado["status"] != "ok":
        return resultado.get("erro", "Não há rota confirmada.")
    total = resultado["distancia_total_m"]
    return (f"A*: {resultado['origem']} → {resultado['destino']}; "
            f"distância total {total:.2f} m no mapa provisório.")


def argumentos_citados_no_pedido(pedido_usuario, argumentos):
    """Confere se os locais escolhidos aparecem no texto como nome ou ID.

    A checagem não extrai nem corrige argumentos: o Qwen continua decidindo.
    Ela só impede executar uma rota para um acesso próximo ou outro local que
    a pessoa não citou. Um apelido não presente no catálogo pode ser recusado.
    """
    frase = normalizar_frase(pedido_usuario)
    for chave in ("origem", "destino"):
        try:
            identificador = rotas_comentadas.encontrar_local(argumentos[chave])
        except (KeyError, TypeError, ValueError):
            return False
        nome = rotas_comentadas.grade.config.nomes[identificador]
        if not any(re.search(r"(?<!\w)" + re.escape(normalizar_frase(valor)) + r"(?!\w)", frase)
                   for valor in (identificador, nome)):
            return False
    return True


def resultado_para_modelo(resultado, nome, versao):
    """Reduz a mensagem de rota das versões recentes sem alterar o A* registrado.

    O caminho completo continua em ``chamadas[].resultado``. Na conversa, a
    enumeração de células consumia a geração curta e desviava a resposta do
    total. O modelo recebe somente os campos necessários para explicar a rota.
    """
    if versao not in ("v7", "v8", "v9") or nome != "calcular_rota" or resultado["status"] != "ok":
        return resultado
    return {chave: resultado[chave] for chave in (
        "status", "origem", "destino", "algoritmo", "distancia_total_m",
        "distancia_total_formatada_m", "mapa")}


def agente(pedido_usuario, conversar, versao="v3", max_passos=3):
    """Executa o ciclo do agente e guarda um registro para avaliação.

    ``conversar`` é o Qwen no notebook ou uma função simulada nos testes. O
    registro conserva a resposta bruta do modelo e o resultado da ferramenta:
    isso permite medir erros sem esconder uma falha atrás de uma frase corrigida.
    """
    if not isinstance(pedido_usuario, str) or not pedido_usuario.strip():
        raise ValueError("Digite um pedido em texto.")
    if versao not in PROMPTS:
        raise ValueError(f"Versão de prompt desconhecida: {versao!r}.")
    if not isinstance(max_passos, int) or max_passos < 1:
        raise ValueError("max_passos precisa ser um inteiro positivo.")

    mensagens = [
        {"role": "system", "content": PROMPTS[versao]},
        {"role": "user", "content": pedido_usuario.strip()},
    ]
    chamadas = []
    decisao_modelo = None
    inicio = time.perf_counter()
    for passo in range(1, max_passos + 1):
        # Na v8 o Qwen recebe uma tarefa de seleção em JSON, sem o template de
        # ferramentas. Ele ainda escolhe a função e ambos os argumentos; o
        # Python somente valida e executa a decisão registrada.
        resposta = conversar(mensagens, [] if versao in ("v8", "v9") else FERRAMENTAS)
        if passo == 1:
            decisao_modelo = resposta
        try:
            pedido = ler_pedido_de_ferramenta(resposta)
        except ValueError as erro:
            return {"resposta": "Não consegui interpretar a chamada de ferramenta.",
                    "resposta_modelo": resposta, "erro": str(erro),
                    "chamadas": chamadas, "versao": versao,
                    "decisao_modelo": decisao_modelo,
                    "segundos": time.perf_counter() - inicio}
        if versao in ("v8", "v9") and (resposta.strip() == "null" or
                (pedido is not None and pedido.get("name") is None)):
            # A seleção explícita de nenhuma ferramenta ainda precisa de uma
            # frase para a pessoa. A decisão JSON fica intacta no registro.
            resposta = conversar([
                {"role": "system", "content": "Responda ao pedido em português. "
                 "Se um local estiver fora do mapa, diga isso. Não invente rota ou custo."},
                {"role": "user", "content": pedido_usuario.strip()},
            ], [])
            pedido = None
        if pedido is None:
            # O texto bruto continua no registro para medir fidelidade. Quando
            # ele omite ou altera o custo, mostramos ao usuário a referência
            # calculada pelo Python. Isso não apaga o erro da avaliação.
            resposta_modelo = resposta.strip()
            resposta_final = resposta_modelo
            ajustada = False
            rotas = [c["resultado"] for c in chamadas if c["name"] == "calcular_rota"]
            listas = [c["resultado"] for c in chamadas if c["name"] == "listar_locais"]
            if rotas:
                ultima_rota = rotas[-1]
                if ultima_rota["status"] != "ok" or not distancia_aparece(
                        resposta_modelo, ultima_rota["distancia_total_m"]):
                    resposta_final = resposta_de_referencia(ultima_rota)
                    ajustada = True
            elif listas and listas[-1]["status"] == "ok":
                if not lista_fiel(resposta_modelo, listas[-1]):
                    resposta_final = lista_de_referencia(listas[-1])
                    ajustada = True
            elif pedido_parece_rota(pedido_usuario) and not resposta_recusa(resposta_modelo):
                # Sem A*, nenhuma frase do modelo pode ser apresentada como
                # rota confirmada, mesmo que soe plausível.
                resposta_final = ("Não consegui calcular uma rota confirmada. "
                                  "Informe dois locais cadastrados e tente novamente.")
                ajustada = True
            elif pedido_pede_lista(pedido_usuario):
                # Uma lista só é confiável quando vem do catálogo do projeto.
                resposta_final = "Não consegui consultar a lista de locais cadastrados."
                ajustada = True
            return {"resposta": resposta_final, "resposta_modelo": resposta_modelo,
                    "resposta_ajustada": ajustada,
                    "erro": None, "chamadas": chamadas, "versao": versao,
                    "decisao_modelo": decisao_modelo,
                    "segundos": time.perf_counter() - inicio}

        if (versao == "v9" and pedido.get("name") == "calcular_rota" and
                not argumentos_citados_no_pedido(pedido_usuario, pedido.get("arguments", {}))):
            # A chamada proposta continua registrada como erro do modelo.
            # Não alimentamos o A* com uma origem/destino que não está no pedido.
            resultado_texto = json.dumps({"status": "erro", "erro":
                "Os locais da chamada não correspondem aos citados no pedido. "
                "Confirme origem e destino."}, ensure_ascii=False)
        else:
            resultado_texto = executar_pedido(pedido)
        # A resposta de ferramenta volta à conversa antes da próxima geração.
        # O papel "tool" é formatado pelo chat template do Qwen.
        resultado = json.loads(resultado_texto)
        mensagens.append({"role": "assistant", "content": resposta})
        mensagens.append({"role": "tool", "content": json.dumps(
            resultado_para_modelo(resultado, pedido.get("name"), versao),
            ensure_ascii=False)})
        if versao in ("v8", "v9"):
            mensagens[0]["content"] = PROMPT_RESPOSTA_V8
        chamadas.append({"passo": passo, "name": pedido.get("name"),
                         "arguments": pedido.get("arguments"),
                         "resultado": resultado})

    return {"resposta": f"Não consegui concluir em {max_passos} passos.",
            "resposta_modelo": resposta, "erro": "limite_de_passos",
            "chamadas": chamadas, "versao": versao,
            "decisao_modelo": decisao_modelo,
            "segundos": time.perf_counter() - inicio}


def avaliar_caso(caso, execucao):
    """Compara uma execução com expectativas escritas antes da geração.

    A fidelidade automática verifica o número devolvido pelo A*. A pertinência
    da explicação e o tratamento de pedidos fora do domínio ainda exigem revisão
    humana; o relatório não deve transformar esta função em nota definitiva.
    """
    chamadas = execucao["chamadas"]
    primeira = chamadas[0] if chamadas else None
    ferramenta_ok = (primeira["name"] if primeira else None) == caso["ferramenta"]
    esperado = caso.get("argumentos")
    argumentos_ok = None
    if esperado is not None:
        recebidos = primeira["arguments"] if primeira else None
        if caso["ferramenta"] == "calcular_rota" and isinstance(recebidos, dict):
            # Nome e ID de um mesmo local são entradas equivalentes para a
            # ferramenta. Comparamos os IDs canônicos sem aceitar local falso.
            try:
                argumentos_ok = all(
                    rotas_comentadas.encontrar_local(recebidos[chave]) ==
                    rotas_comentadas.encontrar_local(esperado[chave])
                    for chave in ("origem", "destino")
                ) and set(recebidos) == {"origem", "destino"}
            except (KeyError, ValueError, TypeError):
                argumentos_ok = False
        else:
            argumentos_ok = recebidos == esperado
    fidelidade = None
    lista_completa = None
    if primeira and primeira["name"] == "calcular_rota":
        resultado = primeira["resultado"]
        if resultado["status"] == "ok":
            fidelidade = distancia_aparece(execucao["resposta_modelo"],
                                           resultado["distancia_total_m"])
    if primeira and primeira["name"] == "listar_locais" and primeira["resultado"]["status"] == "ok":
        lista_completa = lista_fiel(execucao["resposta_modelo"], primeira["resultado"])
    recusa = resposta_recusa(execucao["resposta_modelo"]) if caso["categoria"] == "fora_do_dominio" else None
    if not ferramenta_ok:
        tipo_erro = "nao_chamou" if primeira is None and caso["ferramenta"] else "ferramenta_errada"
    elif argumentos_ok is False:
        tipo_erro = "argumento_errado"
    elif fidelidade is False:
        tipo_erro = "explicacao_infiel"
    elif lista_completa is False:
        tipo_erro = "lista_incompleta"
    elif recusa is False:
        tipo_erro = "recusa_ausente"
    else:
        tipo_erro = None
    return {"id": caso["id"], "categoria": caso["categoria"],
            "ferramenta_ok": ferramenta_ok, "argumentos_ok": argumentos_ok,
            "fidelidade": fidelidade, "lista_fiel": lista_completa, "recusa_ok": recusa,
            "tipo_erro": tipo_erro, "erro": execucao["erro"],
            "segundos": execucao["segundos"]}
