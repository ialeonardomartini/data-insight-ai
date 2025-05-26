from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_insights(prompt: str, model: str = "gpt-4") -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Você é um analista de dados especializado em gerar relatórios de negócio."},
            {"role": "user", "content": prompt.strip()}
        ],
        temperature=0.3,
        max_tokens=800
    )
    return response.choices[0].message.content.strip()
