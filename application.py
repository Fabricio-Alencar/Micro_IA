# ============================================================
# 🔹 app.py — API principal integrando projeto + IA + Azure APIs
# ============================================================

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from IA import selecionar_candidatos

# ============================================================
# 🧩 Inicialização do aplicativo FastAPI
# ============================================================
app = FastAPI(title="API Principal - Projack Impulse")

# ============================================================
# 🌐 Habilitar CORS (necessário para requisições do front-end)
# ============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],         
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# 📡 Endpoint principal: projeto completo com IA
# ============================================================
@app.get("/projetos/{id_projeto}")
def get_projeto_completo(id_projeto: int):
    """
    Retorna o projeto, suas tecnologias associadas,
    colaboradores solicitados e os 5 melhores selecionados pela IA.
    """

    # ============================================================
    # 1️⃣ Buscar o projeto
    # ============================================================
    projeto_url = f"https://fabricioapis.azurewebsites.net/projeto/{id_projeto}"
    print(f"📡 [DEBUG] Requisitando projeto: {projeto_url}")

    projeto_resp = requests.get(projeto_url)
    if projeto_resp.status_code != 200:
        raise HTTPException(status_code=projeto_resp.status_code, detail="Erro ao buscar projeto")

    projeto_dados = projeto_resp.json().get("projeto")
    print("✅ [DEBUG] Projeto encontrado:", projeto_dados)

    # ============================================================
    # 2️⃣ Buscar tecnologias associadas
    # ============================================================
    tecnologias_url = f"https://fabricioapis.azurewebsites.net/tecnologias?id_projeto={id_projeto}"
    print(f"📡 [DEBUG] Requisitando tecnologias: {tecnologias_url}")

    tecnologias_resp = requests.get(tecnologias_url)
    tecnologias = tecnologias_resp.json().get("tecnologias", []) if tecnologias_resp.status_code == 200 else []
    print(f"✅ [DEBUG] {len(tecnologias)} tecnologias encontradas.")

    # Adiciona tecnologias dentro do dicionário do projeto
    projeto_dados["tecnologias"] = tecnologias

    # ============================================================
    # 3️⃣ Buscar colaboradores com status "Solicitado"
    # ============================================================
    colaboradores_url = f"https://aulaazuremack.azurewebsites.net/colaborador_projeto/solicitado/{id_projeto}"
    print(f"📡 [DEBUG] Requisitando colaboradores: {colaboradores_url}")

    colaboradores_resp = requests.get(colaboradores_url)
    colaboradores = colaboradores_resp.json().get("colaboradores", []) if colaboradores_resp.status_code == 200 else []
    print(f"✅ [DEBUG] {len(colaboradores)} colaboradores encontrados.")

    # ============================================================
    # 4️⃣ Enviar dados à IA para selecionar os 5 melhores
    # ============================================================
    print("🧠 [DEBUG] Enviando dados para a IA...")
    analise_ia = selecionar_candidatos(colaboradores, projeto_dados, tecnologias)

    # ============================================================
    # 5️⃣ Montar resposta final
    # ============================================================
    resultado_final = {
        "projeto": projeto_dados,
        "tecnologias": tecnologias,
        "colaboradores_solicitados": colaboradores,
        "analise_IA": analise_ia
    }

    print("\n🚀 [DEBUG] Resultado final enviado ao cliente:")
    print(resultado_final)

    return resultado_final


# ============================================================
# 🧭 Endpoint de status (para teste rápido da API)
# ============================================================
@app.get("/")
def status():
    return {"status": "API do Projack Impulse está online 🚀"}
