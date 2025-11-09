import json
import time
from google import genai
from google.genai import types

# 🔹 Defina sua GEMINI API Key diretamente no código
GEMINI_API_KEY = "AIzaSyAqB4F9bf6GUgT07HmIpSap3hqeIhgCCEI"

def selecionar_candidatos(dados_colaboradores: list, dados_projeto: dict, tecnologias: list, tentativas: int = 3) -> str:
    """
    Usa o modelo Gemini para selecionar os 5 melhores colaboradores
    para um determinado projeto, sempre mantendo ordem fixa e tecnologias compatíveis como prioridade.
    """
    # Inicializa o cliente passando a chave diretamente
    client = genai.Client(api_key=GEMINI_API_KEY)

    json_colaboradores = json.dumps(dados_colaboradores, indent=2, ensure_ascii=False)
    json_projeto = json.dumps(dados_projeto, indent=2, ensure_ascii=False)
    json_tecnologias = json.dumps(tecnologias, indent=2, ensure_ascii=False)

    prompt = f"""
Você é um Assistente de RH especializado em montar equipes técnicas para projetos de software. 

Sua tarefa é selecionar **exatamente 5 colaboradores** para o projeto, seguindo estas regras:

1. **Tecnologias do projeto** são prioridade máxima.  
   - Cada colaborador deve ter listadas **as tecnologias que combinam com o projeto**.  
   - Em seguida, liste **outras tecnologias** que o colaborador domina.  
   - Forneça uma **justificativa curta** (até 3 frases) destacando experiência, habilidades complementares e como ele contribui para o projeto.

2. **Formato fixo por colaborador (ordem obrigatória):**
   - Nome: [Nome do colaborador]  
   - Tecnologias compatíveis: [Lista de tecnologias que combinam com o projeto]  
   - Outras tecnologias: [Lista de tecnologias adicionais do colaborador]  
   - Justificativa: [Texto breve explicativo, até 3 frases]

3. **Minitexto síntese da equipe:**  
   - Ao final, crie uma análise resumida da equipe como um todo:  
     - Compatibilidade técnica com o projeto  
     - Pontos fortes e equilíbrio do time  
     - Sugestão de como essa equipe pode entregar o projeto com eficiência

4. **Dados fornecidos:**
   - Projeto: {json_projeto}  
   - Tecnologias prioritárias: {json_tecnologias}  
   - Colaboradores disponíveis: {json_colaboradores}  

5. **Saída final:**  
   - Estrutura fixa, em Markdown, seguindo exatamente a ordem:  
     - Colaborador 1 → Colaborador 5  
     - Minitexto síntese da equipe
"""

    config = types.GenerateContentConfig(
        system_instruction="Você é um especialista em RH e IA, priorizando tecnologias do projeto e sempre retornando 5 colaboradores com justificativa e síntese da equipe."
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
            if "API Key not found" in erro_str or "API key not valid" in erro_str:
                return "Erro: Chave GEMINI_API_KEY não configurada ou inválida."
            return f"Erro ao processar requisição: {erro_str}"

    return "Erro: Não foi possível obter resposta do modelo."
