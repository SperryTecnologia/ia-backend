#!/bin/bash

echo "🛑 Parando Ollama..."
pkill -f "ollama serve"

echo "🛑 Parando backend uvicorn..."
pkill -f "uvicorn"

echo "🛑 Parando frontend HTTP server na porta 8080..."
fuser -k 8080/tcp

echo "✅ Todos os serviços foram parados."

