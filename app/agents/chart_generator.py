import pandas as pd
import plotly.express as px
from typing import List, Tuple

def generate_charts(df: pd.DataFrame, col_types: dict) -> List[Tuple]:
    charts = []

    for col1 in df.columns:
        tipo1 = col_types.get(col1)
        if tipo1 == "categórica":
            for col2 in df.columns:
                tipo2 = col_types.get(col2)
                if tipo2 == "numérica":
                    data = df.groupby(col1)[col2].mean().reset_index()
                    fig = px.bar(data, x=col1, y=col2, title=f"Média de {col2} por {col1}")
                    charts.append((fig, {"title": f"Média de {col2} por {col1}", "x": col1, "y": col2, "data": data}))
        elif tipo1 == "data":
            for col2 in df.columns:
                tipo2 = col_types.get(col2)
                if tipo2 == "numérica":
                    df_sorted = df.sort_values(by=col1)
                    fig = px.line(df_sorted, x=col1, y=col2, title=f"{col2} ao longo do tempo ({col1})")
                    charts.append((fig, {"title": f"{col2} ao longo do tempo ({col1})", "x": col1, "y": col2, "data": df_sorted[[col1, col2]]}))

    return charts
