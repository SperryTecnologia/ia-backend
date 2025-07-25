import os
import logging
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
import requests

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

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

@app.options("/{rest_of_path:path}")
async def preflight_handler(rest_of_path: str, request: Request):
    response = Response()
    response.headers["Access-Control-Allow-Origin"] = "http://10.1.1.171:8081"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

class PromptRequest(BaseModel):
    prompt: str

@app.post("/ask/gpt")
def ask_gpt(req: PromptRequest):
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
    try:
        headers = {
            "x-api-key": CLAUDE_API_KEY,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        data = {
            "model": "claude-v1",
            "prompt": f"\n\nHuman: {req.prompt}\n\nAssistant:",
            "max_tokens_to_sample": 512,
            "stop_sequences": ["\n\nHuman:"]
        }
        resp = requests.post("https://api.anthropic.com/v1/complete", headers=headers, json=data)
        resp.raise_for_status()
        result = resp.json()
        return {"response": result.get("completion", "")}
    except Exception as e:
        logging.error(f"Claude API error: {e}")
        raise HTTPException(status_code=500, detail=f"Claude error: {str(e)}")

@app.post("/ask")
def ask(req: PromptRequest):
    text = req.prompt.lower()
    if "claude" in text:
        return ask_claude(req)
    else:
        return ask_gpt(req)
