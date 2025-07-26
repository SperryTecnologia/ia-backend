import os
import logging
import requests
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path
from openai import OpenAI
from serpapi import GoogleSearch
from typing import Optional
from datetime import datetime

# 🔐 Carrega variáveis do .env da raiz
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# 🔧 Configurações iniciais
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# ✅ CORS (permite acesso de fora do backend, como do frontend React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ajuste para seu domínio se quiser restringir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Importa o router de histórico
from historico import router as historico_router
app.include_router(historico_router, prefix="/api/historico")

# 🔧 URLs do SuperAGI
SUPERAGI_URL = os.getenv("SUPERAGI_URL", "http://localhost:3000/api/v1/chat")
SUPERAGI_LEARN_URL = os.getenv("SUPERAGI_LEARN_URL", "http://localhost:3000/api/v1/memory/learn")

# 🔧 Modelos para a rota /ask
class Pergunta(BaseModel):
    prompt: str

# ✅ Função para resposta local alternativa
def responder_localmente(prompt: str) -> Optional[str]:
    prompt_lower = prompt.lower()

    if "hora" in prompt_lower:
        return f"A hora atual é: {datetime.now().strftime('%H:%M:%S')}"

    elif "data" in prompt_lower:
        return f"A data de hoje é: {datetime.now().strftime('%d/%m/%Y')}"

    elif "seu nome" in prompt_lower or "quem é você" in prompt_lower:
        return "Sou a debuga.ai, sua assistente pessoal!"

    return None  # fallback

# ✅ Rota principal
@app.post("/ask")
async def ask(pergunta: Pergunta):
    prompt = pergunta.prompt
    logger.info(f"🧩 Usando: SuperAGI local")
    try:
        resposta = requests.post(SUPERAGI_URL, json={"input": prompt})
        resposta.raise_for_status()
        resposta_json = resposta.json()
        texto_resposta = resposta_json.get("response", "Sem resposta do SuperAGI.")
        logger.info("✅ SuperAGI respondeu com sucesso.")
        ia_usada = "SuperAGI"
    except Exception as e:
        logger.warning("⚠️ SuperAGI falhou. Caindo para OpenAI.")
        logger.error(f"Erro no SuperAGI: {e}")
        texto_resposta = responder_localmente(prompt)
        ia_usada = "local"
        if not texto_resposta:
            try:
                client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                completion = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}]
                )
                texto_resposta = completion.choices[0].message.content
                ia_usada = "OpenAI GPT"
                logger.info("🔷 Usando: OpenAI GPT")
            except Exception as e2:
                logger.error(f"❌ OpenAI também falhou: {e2}")
                texto_resposta = "Erro ao buscar resposta com IA externa."
                ia_usada = "Falha total"

    # ✅ Tenta enviar para aprendizado SuperAGI
    try:
        requests.post(SUPERAGI_LEARN_URL, json={
            "input": prompt,
            "output": texto_resposta
        })
    except Exception as e:
        logger.warning(f"⚠️ Falha ao enviar aprendizado ao SuperAGI: {e}")

    return {
        "resposta": texto_resposta,
        "ia_usada": ia_usada
    }
