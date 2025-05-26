from typing import List, Tuple
import pandas as pd
import plotly.express as px
from plotly.graph_objects import Figure
from io import StringIO

def gerar_graficos_automaticamente(csv: str) -> List[Tuple[Figure, dict]]:
    df = pd.read_csv(StringIO(csv))

    print(f"\n🔍 Dados recebidos: {df.shape[0]} linhas, {df.shape[1]} colunas")
    if "produto" in df.columns:
        print(f"📦 Produtos únicos detectados: {df['produto'].nunique()}")

    graficos = []

    col_types = {}
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            col_types[col] = "numerica"
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            col_types[col] = "data"
        elif pd.api.types.is_string_dtype(df[col]):
            col_types[col] = "categorica"

    # Força visualização de todos os produtos
    if "produto" in df.columns and "valor_total" in df.columns:
        todos_produtos = sorted(df["produto"].dropna().unique())
        agrupado = df.groupby("produto")["valor_total"].mean().reindex(todos_produtos).reset_index()
        fig = px.bar(agrupado, x="produto", y="valor_total", title="Média de valor_total por produto")
        graficos.append((fig, {
            "descricao": "Comparativo da média de valor_total por produto, incluindo todos os produtos da base, mesmo com poucas vendas."
        }))

    # Exemplo extra: categoria x receita total
    if "categoria" in df.columns and "valor_total" in df.columns:
        agrupado = df.groupby("categoria")["valor_total"].sum().reset_index()
        fig = px.pie(agrupado, names="categoria", values="valor_total", title="Participação de receita por categoria")
        graficos.append((fig, {
            "descricao": "Distribuição da receita total por categoria de produto."
        }))

    return graficos
