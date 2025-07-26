from sqlalchemy import Column, Integer, String, DateTime
from database import Base

class HistoricoModel(Base):
    __tablename__ = "historico"

    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(String, nullable=False)
    resposta = Column(String, nullable=False)
    agente = Column(String, nullable=True)
    timestamp = Column(DateTime, nullable=False)

