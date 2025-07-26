#!/bin/bash

echo "🛑 Encerrando serviços do Debuga.ai..."

# Parar backend
if [ -f backend.pid ]; then
  kill $(cat backend.pid) && rm backend.pid
  echo "✅ Backend parado."
fi

# Parar frontend (vite)
if [ -f frontend.pid ]; then
  kill $(cat frontend.pid) && rm frontend.pid
  echo "✅ Frontend parado."
fi

# Parar learn_receiver
if [ -f superagi/learn_receiver.pid ]; then
  kill $(cat superagi/learn_receiver.pid) && rm superagi/learn_receiver.pid
  echo "✅ Learn_receiver parado."
fi

# Parar containers docker
docker-compose down

# Parar ollama
pkill -f "ollama serve" && echo "✅ Ollama parado."

echo "🧼 Limpeza de logs antigos (opcional)..."
rm -f backend/uvicorn.log frontend/vite.log superagi/learn_receiver.log

echo "✅ Todos os serviços foram encerrados com sucesso!"

