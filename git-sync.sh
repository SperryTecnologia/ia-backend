#!/bin/bash

# Verifica se estamos em um repositório Git
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
  echo "❌ Este diretório não é um repositório Git."
  exit 1
fi

echo "🔄 Atualizando com mudanças remotas primeiro (rebase)..."
git pull origin main --rebase

# Adiciona arquivos
echo "📂 Adicionando todos os arquivos alterados..."
git add .

# Mensagem de commit
echo "✍️ Mensagem do commit:"
read msg

# Faz o commit se houver mudanças
if git diff --cached --quiet; then
  echo "⚠️ Nenhuma mudança para commitar."
else
  git commit -m "$msg"
fi

# Push final
echo "⬆️ Enviando alterações para o GitHub..."
git push origin main

echo "✅ Sincronização concluída!"

