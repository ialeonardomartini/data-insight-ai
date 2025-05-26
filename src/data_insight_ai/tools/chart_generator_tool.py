from typing import List, Tuple
import pandas as pd
import plotly.express as px
from plotly.graph_objects import Figure
from io import StringIO

# ✅ Importa o decorador @tool (ou define fallback se necessário)
def tool(description): return lambda func: func  # fallback fixo

@tool("Gera automaticamente gráficos a partir de uma string CSV. Retorna lista de tuplas (plotly.Figure, {'descricao': texto}).")
def gerar_graficos_automaticamente(csv: str) -> List[Tuple[Figure, dict]]:
    df = pd.read_csv(StringIO(csv))
    graficos = []

    # Detecta tipos de coluna
    col_types = {}
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            col_types[col] = "numerica"
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            col_types[col] = "data"
        elif pd.api.types.is_string_dtype(df[col]) and df[col].nunique() < 30:
            col_types[col] = "categorica"

    # Gera gráficos úteis com base nas colunas
    for col1 in df.columns:
        tipo1 = col_types.get(col1)
        if tipo1 == "categorica":
            for col2 in df.columns:
                if col_types.get(col2) == "numerica":
                    data = df.groupby(col1)[col2].mean().reset_index()
                    fig = px.bar(data, x=col1, y=col2, title=f"Média de {col2} por {col1}")
                    graficos.append((fig, {"descricao": f"Média de {col2} por categoria {col1}"}))
        elif tipo1 == "data":
            for col2 in df.columns:
                if col_types.get(col2) == "numerica":
                    df_sorted = df.sort_values(by=col1)
                    fig = px.line(df_sorted, x=col1, y=col2, title=f"{col2} ao longo do tempo ({col1})")
                    graficos.append((fig, {"descricao": f"Evolução de {col2} ao longo do tempo por {col1}"}))

    return graficos
