import os
import logging
logging.basicConfig(level=logging.INFO)
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
import requests
from serpapi import GoogleSearch

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_API_KEY")  # Também pode ser usado como fallback
SUPERAGI_URL = os.getenv("SUPERAGI_URL", "http://localhost:3000/api/v1/chat")

if not OPENAI_API_KEY or not CLAUDE_API_KEY:
    raise RuntimeError("API keys not set")

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

@app.post("/ask/gpt")
def ask_gpt(req: PromptRequest):
    logging.info("🔷 Usando: OpenAI GPT")
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": req.prompt}]
        )
        return {"response": response.choices[0].message.content}
    except Exception as e:
        logging.error(f"OpenAI API error: {e}")
        raise HTTPException(status_code=500, detail=f"OpenAI error: {str(e)}")

@app.post("/ask/claude")
def ask_claude(req: PromptRequest):
    logging.info("🟠 Usando: Claude")
    try:
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
        return {"response": response.json().get("content", [{}])[0].get("text", "")}
    except Exception as e:
        logging.error(f"Claude API error: {e}")
        raise HTTPException(status_code=500, detail=f"Claude error: {str(e)}")

@app.post("/ask/serpapi")
def ask_serpapi(req: PromptRequest):
    logging.info("🟡 Usando: SerpAPI")
    try:
        search = GoogleSearch({
            "q": req.prompt,
            "api_key": SERPAPI_KEY
        })
        results = search.get_dict()
        answer_box = results.get("answer_box", {})
        snippet = results.get("organic_results", [{}])[0].get("snippet", "")
        return {"response": answer_box.get("answer") or snippet or "Sem resposta."}
    except Exception as e:
        logging.error(f"SerpAPI error: {e}")
        raise HTTPException(status_code=500, detail=f"SerpAPI error: {str(e)}")

@app.post("/ask/superagi")
def ask_superagi(req: PromptRequest):
    logging.info("🟢 Usando: SuperAGI local")
    try:
        response = requests.post(SUPERAGI_URL, json={"input": req.prompt})
        response.raise_for_status()
        return {"response": response.json().get("response", "Sem resposta.")}
    except Exception as e:
        logging.error(f"Erro no SuperAGI: {e}")
        raise HTTPException(status_code=500, detail="SuperAGI não respondeu.")

@app.post("/ask")
def ask(req: PromptRequest):
    prompt = req.prompt.lower()

    if "claude" in prompt:
        return ask_claude(req)
    elif "pesquise" in prompt or "busque" in prompt:
        return ask_serpapi(req)
    elif "superagi" in prompt or "sua ia" in prompt:
        return ask_superagi(req)
    else:
        return ask_gpt(req)

