import requests

async def ask_superagi(prompt: str) -> str:
    try:
        response = requests.post("http://localhost:3000/api/agent/ask", json={"prompt": prompt})
        return response.json().get("response", "")
    except Exception:
        return "Falha ao consultar SuperAGI"
