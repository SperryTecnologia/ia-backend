import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

async def ask_openai(prompt: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
