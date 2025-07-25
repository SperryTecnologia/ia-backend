#!/bin/bash

echo "🛑 Encerrando serviços em execução..."

# Mata os processos do backend, frontend, Ollama
pkill -f "ollama serve"
pkill -f "uvicorn"
pkill -f "npm run dev"
pkill -f "python3 -m http.server"

# Libera as portas
fuser -k 8080/tcp || true
fuser -k 8081/tcp || true
fuser -k 3000/tcp || true
fuser -k 8000/tcp || true

# Para os containers do Docker Compose
echo "🛑 Parando containers do Docker Compose..."
docker-compose down

echo "✅ Todos os serviços foram encerrados."

