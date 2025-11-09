import os
import json
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 🔹 Carrega variáveis de ambiente (incluindo GEMINI_API_KEY)
load_dotenv()

def selecionar_candidatos(dados_colaboradores: list, dados_projeto: dict, tecnologias: list, tentativas: int = 3) -> str:
    """
    Usa o modelo Gemini para selecionar os 5 melhores colaboradores
    para um determinado projeto, dando prioridade total às tecnologias
    exigidas no projeto.
    """
    client = genai.Client()

    json_colaboradores = json.dumps(dados_colaboradores, indent=2, ensure_ascii=False)
    json_projeto = json.dumps(dados_projeto, indent=2, ensure_ascii=False)
    json_tecnologias = json.dumps(tecnologias, indent=2, ensure_ascii=False)

    # 🧠 Prompt otimizado para priorizar tecnologias do projeto
    prompt = f"""
    Você é um Assistente de RH especializado em montar equipes técnicas para projetos de software.

    Dê **prioridade total** às tecnologias exigidas pelo projeto.
    Isso significa:
    - A compatibilidade com as tecnologias do projeto é o critério **mais importante**.
    - Apenas depois de garantir essa compatibilidade, avalie experiência e sinergia.

    🧩 **Projeto:**
    {json_projeto}

    🧠 **Tecnologias prioritárias:**
    {json_tecnologias}

    👥 **Colaboradores disponíveis:**
    {json_colaboradores}

    Sua tarefa:
    1. Selecione os **5 colaboradores mais compatíveis com as tecnologias do projeto**.
    2. Para cada um, forneça:
       - Nome completo
       - Tecnologias que coincidem com o projeto
       - Principais habilidades adicionais relevantes
       - Justificativa breve (até 3 frases)

    ⚙️ Critério de decisão:
    - 70% peso para **tecnologias coincidentes**
    - 20% peso para **experiência geral**
    - 10% peso para **complementaridade com o time**

    Retorne a resposta formatada em **Markdown**, exemplo:

    ### Equipe Ideal para o Projeto
    ---
    **1. Nome:** João Silva  
    **Tecnologias em comum:** Python, FastAPI, SQLite  
    **Outras habilidades:** Docker, REST APIs  
    **Justificativa:** João possui alta compatibilidade técnica e experiência com o stack do projeto...
    """

    config = types.GenerateContentConfig(
        system_instruction=(
            "Você é um especialista em RH e IA que monta equipes técnicas, "
            "sempre priorizando as tecnologias do projeto como fator principal de seleção."
        )
    )

    # 🔁 Tentativas automáticas em caso de erro 503
    for tentativa in range(1, tentativas + 1):
        try:
            print(f"🤖 [IA] Tentando enviar análise (tentativa {tentativa}/{tentativas})...")
            response = client.models.generate_content(
                model="gemini-2.5-pro",
                contents=prompt,
                config=config
            )
            print("✅ [IA] Análise concluída com sucesso.")
            return response.text.strip()

        except Exception as e:
            erro_str = str(e)
            print(f"⚠️ [IA] Erro: {erro_str}")

            if "503" in erro_str or "UNAVAILABLE" in erro_str:
                if tentativa < tentativas:
                    espera = 3 * tentativa
                    print(f"⏳ Modelo ocupado. Tentando novamente em {espera} segundos...")
                    time.sleep(espera)
                    continue
                else:
                    return "Erro: O modelo está temporariamente indisponível. Tente novamente mais tarde."

            if "API Key not found" in erro_str:
                return "Erro: A chave GEMINI_API_KEY não foi configurada corretamente."
            
            return f"Erro ao processar requisição: {erro_str}"

    return "Erro: Não foi possível obter resposta do modelo após várias tentativas."
