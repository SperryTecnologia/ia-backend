#!/bin/bash
echo "🛑 Parando todos os serviços..."

pkill -f "ollama serve"
pkill -f "uvicorn"
pkill -f "python3 -m http.server"

echo "🛑 Parando containers do Docker Compose..."
docker-compose down

echo "✅ Todos os serviços foram encerrados."
