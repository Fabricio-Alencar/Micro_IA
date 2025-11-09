import os
import json
import time
from google import genai
from google.genai import types

# 🔹 Defina sua GEMINI API Key aqui
os.environ["GOOGLE_API_KEY"] = "AIzaSyAqB4F9bf6GUgT07HmIpSap3hqeIhgCCEI"

def selecionar_candidatos(dados_colaboradores: list, dados_projeto: dict, tecnologias: list, tentativas: int = 3) -> str:
    """
    Usa o modelo Gemini para selecionar os 5 melhores colaboradores
    para um determinado projeto.
    """
    client = genai.Client()  # A chave já será lida da variável de ambiente

    json_colaboradores = json.dumps(dados_colaboradores, indent=2, ensure_ascii=False)
    json_projeto = json.dumps(dados_projeto, indent=2, ensure_ascii=False)
    json_tecnologias = json.dumps(tecnologias, indent=2, ensure_ascii=False)

    prompt = f"""
    Você é um Assistente de RH especializado em montar equipes técnicas.

    Projeto: {json_projeto}
    Tecnologias: {json_tecnologias}
    Colaboradores: {json_colaboradores}

    Selecione os 5 colaboradores mais compatíveis.
    """

    config = types.GenerateContentConfig(
        system_instruction="Você é um especialista em RH e IA."
    )

    for tentativa in range(1, tentativas + 1):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-pro",
                contents=prompt,
                config=config
            )
            return response.text.strip()
        except Exception as e:
            erro_str = str(e)
            if "503" in erro_str or "UNAVAILABLE" in erro_str:
                if tentativa < tentativas:
                    time.sleep(3 * tentativa)
                    continue
                else:
                    return "Erro: Modelo temporariamente indisponível."
            if "API Key not found" in erro_str:
                return "Erro: Chave GEMINI_API_KEY não configurada corretamente."
            return f"Erro ao processar requisição: {erro_str}"

    return "Erro: Não foi possível obter resposta do modelo."
