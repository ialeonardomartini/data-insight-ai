from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def infer_column_semantics(col_name: str, sample_values: list[str]) -> str:
    prompt = f"""
    Você é um assistente de análise de dados. Diga o que esta coluna representa, com base no nome e nos exemplos de valores.

    Nome da coluna: {col_name}
    Exemplos de valores: {sample_values[:5]}

    Resposta (descreva o que representa, em 1 linha):
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Você é um analista de dados."},
            {"role": "user", "content": prompt.strip()}
        ],
        temperature=0.2,
        max_tokens=60
    )

    return response.choices[0].message.content.strip()