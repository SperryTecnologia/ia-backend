from fastapi import FastAPI, Request
from pydantic import BaseModel
import logging

app = FastAPI()

class LearnData(BaseModel):
    input: str
    output: str
    source: str = "fallback"

@app.post("/api/v1/memory/learn")
async def learn_from_fallback(data: LearnData):
    try:
        logging.info(f"🧠 Aprendizado recebido de {data.source}")
        logging.info(f"🔹 Pergunta: {data.input}")
        logging.info(f"🔹 Resposta: {data.output}")

        # Aqui você pode armazenar em arquivo, banco de dados, ou log para reprocessar depois.
        with open("learned_data.log", "a", encoding="utf-8") as f:
            f.write(f"FROM: {data.source}\nPROMPT: {data.input}\nRESPONSE: {data.output}\n---\n")

        return {"status": "success", "message": "Aprendizado registrado"}
    except Exception as e:
        logging.error(f"Erro ao registrar aprendizado: {e}")
        return {"status": "error", "message": str(e)}

