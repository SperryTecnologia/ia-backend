import os
import requests

CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

async def ask_claude(prompt: str) -> str:
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    body = {
        "model": "claude-3-opus-20240229",
        "max_tokens": 500,
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(url, headers=headers, json=body)
    return response.json()["content"][0]["text"]
