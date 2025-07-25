#!/bin/bash
echo "🔁 Parando processos existentes para evitar conflito..."
pkill -f "ollama serve"
pkill -f "uvicorn"
pkill -f "python3 -m http.server"
fuser -k 8080/tcp || true
fuser -k 3000/tcp || true
fuser -k 8000/tcp || true

sleep 2

echo "🔁 Iniciando modelo LLM (Ollama - mistral)..."
ollama serve &

sleep 3

echo "🚀 Iniciando backend em http://localhost:8000"
cd ./backend
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &

echo "🌐 Iniciando frontend em http://localhost:8080"
cd ./frontend
nohup python3 -m http.server 8080 > httpserver.log 2>&1 &

echo "📦 Iniciando SuperAGI via Docker Compose"
cd ../../
docker-compose up -d --build -d super__postgres superagi

echo "✅ Todos os serviços foram iniciados!"
echo ""
echo "Frontend: http://<IP-DA-VM>:8080"
echo "Backend API: http://<IP-DA-VM>:8000"
echo "SuperAGI: http://<IP-DA-VM>:3000"
