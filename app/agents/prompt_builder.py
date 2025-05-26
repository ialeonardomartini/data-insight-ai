from typing import List, Dict
import pandas as pd
from app.agents.data_analyzer import analyze_dataframe

def generate_data_alerts(df: pd.DataFrame, profile: Dict) -> str:
    alerts = []
    total_rows = len(df)

    for col in df.columns:
        col_type = profile['colunas'].get(col, '')
        n_nulos = profile['resumo'].get(col, {}).get("nulos", 0)
        percent_nulos = (n_nulos / total_rows) * 100 if total_rows else 0

        if percent_nulos > 20:
            alerts.append(f"- A coluna `{col}` possui {percent_nulos:.1f}% de valores ausentes.")

        if col_type == "numérica":
            non_numeric = df[col].apply(lambda x: isinstance(x, str)).sum()
            if non_numeric > 0:
                alerts.append(f"- A coluna `{col}` contém {non_numeric} valores que parecem texto e não números.")

        if col_type == "data":
            formatos = df[col].dropna().astype(str).apply(lambda x: x.count("/") + x.count("-"))
            if formatos.nunique() > 1:
                alerts.append(f"- A coluna `{col}` contém múltiplos formatos de data.")

    if alerts:
        return "⚠️ ALERTAS DE QUALIDADE DOS DADOS:\n" + "\n".join(alerts) + "\n"
    else:
        return ""

def classify_data_quality(profile: Dict, df: pd.DataFrame) -> dict:
    total_rows = len(df)
    ruim = 0
    media = 0
    problemas = []

    for col, stats in profile['resumo'].items():
        nulos = stats.get("nulos", 0)
        percent_nulos = (nulos / total_rows) * 100 if total_rows else 0

        if percent_nulos > 50:
            ruim += 1
            problemas.append(f"Coluna `{col}` possui mais de 50% de nulos")
        elif percent_nulos > 20:
            media += 1
            problemas.append(f"Coluna `{col}` possui mais de 20% de nulos")

    if ruim >= 2:
        nivel = "Ruim"
    elif media >= 2 or ruim == 1:
        nivel = "Média"
    else:
        nivel = "Boa"

    return {"nivel": nivel, "problemas": problemas}

def build_prompt(df: pd.DataFrame,
                 profile: Dict,
                 semantics: Dict,
                 objetivo: str = None) -> str:
    prompt = "Você é um analista de dados experiente. Gere insights úteis com base na tabela abaixo.\n\n"

    if objetivo:
        prompt += f"Objetivo informado pelo usuário: {objetivo}\n\n"

    # Alertas de qualidade
    data_alerts = generate_data_alerts(df, profile)
    if data_alerts:
        prompt += data_alerts + "\n"

    prompt += "🧾 Amostra dos dados:\n"
    prompt += df.head(5).to_csv(index=False) + "\n\n"

    prompt += "📊 Estatísticas resumidas por coluna:\n"
    for col, stats in profile['resumo'].items():
        prompt += f"- {col} ({profile['colunas'][col]}): "
        stats_txt = ", ".join(f"{k} = {v}" for k, v in stats.items())
        prompt += stats_txt + "\n"

    prompt += "\n🧠 Descrição das colunas:\n"
    for col, desc in semantics.items():
        prompt += f"- {col}: {desc}\n"

    # Análise complementar automática
    analysis = analyze_dataframe(df)

    prompt += "\n🔍 Correlações detectadas:\n"
    if analysis["correlacoes"]:
        for pair, corr in analysis["correlacoes"].items():
            prompt += f"- {pair}: coeficiente de correlação = {corr}\n"
    else:
        prompt += "Nenhuma correlação significativa detectada.\n"

    prompt += "\n⚠️ Outliers por coluna numérica:\n"
    for col, count in analysis["outliers"].items():
        prompt += f"- {col}: {count} possíveis outliers\n"

    prompt += "\n📌 Métricas por grupo categórico:\n"
    for cat_col, grupos in analysis["resumos_por_grupo"].items():
        prompt += f"- Agrupado por {cat_col}:\n"
        for linha in grupos:
            linha_str = ", ".join(f"{k} = {v}" for k, v in linha.items())
            prompt += f"    • {linha_str}\n"

    prompt += "\nGere abaixo um relatório de insights, destacando padrões, anomalias e recomendações de negócio.\n"
    return prompt