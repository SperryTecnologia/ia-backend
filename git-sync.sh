#!/bin/bash
git add .
echo "Mensagem do commit:"
read msg
git commit -m "$msg"
git push origin main

