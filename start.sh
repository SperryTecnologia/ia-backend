#!/bin/bash

echo "🔁 Parando processos existentes para evitar conflito..."
pkill -f "ollama serve"
pkill -f "uvicorn"
pkill -f "npm run dev"
pkill -f "python3 -m http.server"

# Libera as portas usadas
for port in 8000 8080 8081 3000 3001 5433; do
  fuser -k ${port}/tcp || true
done

sleep 2

echo "🔁 Iniciando modelo LLM (Ollama - mistral)..."
ollama serve &

sleep 3

echo "🚀 Iniciando backend em http://localhost:8000"
cd ./backend
source ../venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &
echo $! > ../backend.pid
cd ..

echo "🌐 Iniciando frontend (Vite) em http://localhost:8081"
cd ./frontend
nohup npm run dev -- --host > vite.log 2>&1 &
echo $! > ../frontend.pid
cd ..

echo "📦 Iniciando SuperAGI via Docker Compose"
docker-compose up -d --build super__postgres superagi backend

echo "🔄 Iniciando learn_receiver.py na porta 3001..."
nohup uvicorn superagi.learn_receiver:app --host 0.0.0.0 --port 3001 --reload > superagi/learn_receiver.log 2>&1 &
echo $! > superagi/learn_receiver.pid

echo "✅ Todos os serviços foram iniciados!"
echo ""
echo "🧠  SuperAGI:       http://<IP-DA-VM>:3000"
echo "🔗 Backend API:    http://<IP-DA-VM>:8000"
echo "🖥️  Frontend (Vite): http://<IP-DA-VM>:8081"

