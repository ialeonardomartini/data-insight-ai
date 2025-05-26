from openai import OpenAI
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def describe_chart(title: str, x_col: str, y_col: str, df_chart: pd.DataFrame, model="gpt-4") -> str:
    amostra = df_chart[[x_col, y_col]].head(10).to_csv(index=False)

    prompt = f"""
    Você é um analista de dados.

    Dado o gráfico com título "{title}", descreva de forma clara e breve o que ele representa.
    Considere que o eixo X é '{x_col}' e o eixo Y é '{y_col}'.

    Aqui estão os dados utilizados (apenas os 10 primeiros registros):

    {amostra}

    Gera uma explicação simples, com no máximo 3 frases. Se possível, destaque um insight relevante.
    """

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Você é um analista de dados que gera descrições de gráficos."},
            {"role": "user", "content": prompt.strip()}
        ],
        temperature=0.3,
        max_tokens=150
    )

    return response.choices[0].message.content.strip()

# Exemplo de uso
if __name__ == "__main__":
    import pandas as pd
    df = pd.DataFrame({
        "setor": ["TI", "Vendas", "Marketing"],
        "salario": [12000, 10000, 8500]
    })
    print(describe_chart("Média salarial por setor", "setor", "salario", df))
