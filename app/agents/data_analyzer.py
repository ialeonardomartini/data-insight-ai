import pandas as pd
import numpy as np
from scipy.stats import pearsonr


def analyze_dataframe(df: pd.DataFrame) -> dict:
    analysis = {
        "correlacoes": {},
        "outliers": {},
        "resumos_por_grupo": {}
    }

    # Correlações entre colunas numéricas
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for i, col1 in enumerate(numeric_cols):
        for col2 in numeric_cols[i+1:]:
            corr, _ = pearsonr(df[col1], df[col2])
            analysis["correlacoes"][f"{col1} ~ {col2}"] = round(corr, 3)

    # Detecção de outliers (método do IQR)
    for col in numeric_cols:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        outlier_rows = df[(df[col] < lower) | (df[col] > upper)]
        analysis["outliers"][col] = len(outlier_rows)

    # Agrupamentos por colunas categóricas
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns
    for cat_col in categorical_cols:
        if df[cat_col].nunique() <= 20:
            resumo = df.groupby(cat_col)[numeric_cols].mean().round(2).reset_index()
            analysis["resumos_por_grupo"][cat_col] = resumo.to_dict(orient="records")

    return analysis

# Exemplo de uso
if __name__ == "__main__":
    df = pd.read_csv("exemplo_colaboradores.csv")
    result = analyze_dataframe(df)
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))
