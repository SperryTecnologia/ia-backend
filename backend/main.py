
import os
import logging
import requests
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
from serpapi import GoogleSearch

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_API_KEY")
SUPERAGI_URL = os.getenv("SUPERAGI_URL", "http://localhost:3000/api/v1/chat")

client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://10.1.1.171:8081"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    prompt: str

@app.options("/{rest_of_path:path}")
async def preflight_handler(rest_of_path: str, request: Request):
    response = Response()
    response.headers["Access-Control-Allow-Origin"] = "http://10.1.1.171:8081"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

def send_to_superagi_learn(prompt, answer):
    try:
        logging.info("📥 Enviando para SuperAGI aprender...")
        r = requests.post(SUPERAGI_URL, json={"input": f"{prompt}\n\n{answer}"})
        r.raise_for_status()
        logging.info("✅ Aprendizado enviado ao SuperAGI.")
    except Exception as e:
        logging.warning(f"⚠️ SuperAGI não pôde aprender: {e}")

@app.post("/ask")
def ask(req: PromptRequest):
    prompt = req.prompt.lower()

    try:
        logging.info("🧩 Usando: SuperAGI local")
        res = requests.post(SUPERAGI_URL, json={"input": req.prompt})
        res.raise_for_status()
        resposta = res.json().get("response", "Sem resposta.")
        return {"response": resposta}
    except Exception as e:
        logging.error(f"Erro no SuperAGI: {e}")
        logging.warning("⚠️ SuperAGI falhou. Caindo para fallback...")

    if "claude" in prompt:
        try:
            logging.info("🧠 Usando: Claude")
            headers = {
                "x-api-key": CLAUDE_API_KEY,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
            data = {
                "model": "claude-3-haiku-20240307",
                "messages": [{"role": "user", "content": req.prompt}],
                "max_tokens": 512,
            }
            response = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=data)
            response.raise_for_status()
            answer = response.json().get("content", [{}])[0].get("text", "")
            send_to_superagi_learn(req.prompt, answer)
            return {"response": answer}
        except Exception as e:
            logging.error(f"Claude error: {e}")

    if any(k in prompt for k in ["pesquise", "busque", "temperatura", "horas", "cotação", "preço", "valor", "quando", "quem", "onde", "data"]):
        try:
            logging.info("🔎 Usando: SerpAPI")
            search = GoogleSearch({
                "q": req.prompt,
                "api_key": SERPAPI_KEY
            })
            results = search.get_dict()
            answer = results.get("answer_box", {}).get("answer") or                      results.get("organic_results", [{}])[0].get("snippet", "") or "Sem resposta."
            send_to_superagi_learn(req.prompt, answer)
            return {"response": answer}
        except Exception as e:
            logging.error(f"SerpAPI error: {e}")

    try:
        logging.info("🔷 Usando: OpenAI GPT")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": req.prompt}]
        )
        answer = response.choices[0].message.content
        send_to_superagi_learn(req.prompt, answer)
        return {"response": answer}
    except Exception as e:
        logging.error(f"OpenAI error: {e}")
        raise HTTPException(status_code=500, detail="Erro em todos os modelos de IA.")
