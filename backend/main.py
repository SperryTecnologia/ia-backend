import os
import logging
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import requests
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # você pode limitar depois se quiser mais segurança
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.options("/{rest_of_path:path}")
async def preflight_handler(rest_of_path: str, request: Request):
    response = Response()
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

class PromptRequest(BaseModel):
    prompt: str

@app.post("/ask")
def ask(req: PromptRequest):
    prompt = req.prompt

    # 1. Tenta com SuperAGI (local)
    try:
        sa_resp = requests.post("http://localhost:3000/api/agent/ask", json={"prompt": prompt}, timeout=5)
        if sa_resp.ok:
            sa_json = sa_resp.json()
            if sa_json.get("response"):
                return {"response": sa_json["response"]}
    except Exception as e:
        logging.warning(f"SuperAGI indisponível ou erro: {e}")

    # 2. Claude como fallback
    try:
        headers = {
            "x-api-key": CLAUDE_API_KEY,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        data = {
            "model": "claude-3-opus-20240229",
            "max_tokens": 500,
            "messages": [{"role": "user", "content": prompt}]
        }
        resp = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=data)
        resp.raise_for_status()
        result = resp.json()
        if result.get("content"):
            return {"response": result["content"][0]["text"]}
    except Exception as e:
        logging.warning(f"Claude falhou: {e}")

    # 3. GPT como fallback final
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return {"response": response.choices[0].message.content}
    except Exception as e:
        logging.error(f"OpenAI falhou: {e}")
        raise HTTPException(status_code=500, detail="Nenhuma IA conseguiu responder.")
