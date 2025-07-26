from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class HistoricoItem(BaseModel):
    prompt: str
    resposta: str
    agente: str
    timestamp: datetime = datetime.now()

historico_db = []

@router.post("/", status_code=200)
def salvar_historico(item: HistoricoItem):
    historico_db.append(item)
    return {"status": "salvo", "total_registros": len(historico_db)}

@router.get("/", status_code=200)
def visualizar_status():
    return {
        "status": "ok",
        "mensagem": "Rota /historico está ativa e funcionando.",
        "total_registros": len(historico_db)
    }

@router.get("/todos", status_code=200)
def listar_todos():
    return historico_db

