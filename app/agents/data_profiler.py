import pandas as pd
import numpy as np

def profile_dataframe(df: pd.DataFrame, sample_size: int = 5) -> dict:
    profile = {
        "colunas": {},
        "resumo": {},
        "amostras": df.head(sample_size).to_dict(orient="records")
    }

    for col in df.columns:
        col_data = df[col]
        tipo = infer_column_type(col_data)
        profile["colunas"][col] = tipo

        resumo = {
            "nulos": int(col_data.isna().sum()),
            "valores_unicos": int(col_data.nunique())
        }

        if tipo == "numérica":
            resumo.update({
                "min": float(col_data.min()),
                "max": float(col_data.max()),
                "média": float(col_data.mean()),
                "desvio_padrão": float(col_data.std())
            })
        elif tipo == "data":
            resumo.update({
                "min": str(col_data.min()),
                "max": str(col_data.max())
            })

        profile["resumo"][col] = resumo

    return profile

def infer_column_type(series: pd.Series) -> str:
    if pd.api.types.is_numeric_dtype(series):
        return "numérica"
    elif pd.api.types.is_datetime64_any_dtype(series):
        return "data"
    elif pd.api.types.is_bool_dtype(series):
        return "booleana"
    elif series.nunique() < 30:
        return "categórica"
    else:
        return "texto"