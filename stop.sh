#!/bin/bash

echo "🔁 Parando processos existentes para evitar conflito..."
pkill -f "ollama serve"
pkill -f "uvicorn"
pkill -f "npm run dev"
pkill -f "python3 -m http.server"
fuser -k 8080/tcp || true
fuser -k 8081/tcp || true
fuser -k 3000/tcp || true
fuser -k 8000/tcp || true

sleep 2

echo "🔁 Iniciando modelo LLM (Ollama - mistral)..."
ollama serve &

sleep 3

echo "🚀 Iniciando backend em http://localhost:8000"
cd ./backend
source ../venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &

echo "🌐 Iniciando frontend (Vite) em http://localhost:8081"
cd ../frontend
nohup npm run dev -- --host > vite.log 2>&1 &

echo "📦 Iniciando SuperAGI via Docker Compose"
cd ../
docker-compose up -d --build super__postgres superagi

echo "✅ Todos os serviços foram iniciados!"
echo ""
echo "Frontend (Vite): http://<IP-DA-VM>:8081"
echo "Backend API: http://<IP-DA-VM>:8000"
echo "SuperAGI: http://<IP-DA-VM>:3000"

