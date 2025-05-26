import os
import pandas as pd
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def responder_pergunta_sobre_dados(df: pd.DataFrame, pergunta: str) -> str:
    descricao = df.describe(include="all").fillna("").to_markdown()
    amostra = df.head().to_markdown()
    colunas = ", ".join(df.columns)

    prompt = f"""
Você é um analista de dados. O usuário fez a seguinte pergunta sobre o conjunto de dados:

Pergunta: {pergunta}

As colunas disponíveis são: {colunas}

Amostra dos dados:
{amostra}

Estatísticas descritivas:
{descricao}

Responda com base apenas nos dados fornecidos. Seja direto, objetivo e, se possível, quantifique sua resposta.
"""

    resposta = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return resposta.choices[0].message.content.strip()
