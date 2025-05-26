import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import streamlit as st
import pandas as pd
from app.agents.data_profiler import profile_dataframe
from app.agents.column_semantics_agent import infer_column_semantics
from app.agents.chart_generator import generate_charts
from app.agents.prompt_builder import build_prompt, generate_data_alerts
from app.agents.insight_generator import generate_insights
from app.agents.chart_describer import describe_chart

st.set_page_config(page_title="DataInsightAI", layout="wide")
st.title("📊 DataInsightAI — Geração automática de insights e dashboards")

uploaded_file = st.file_uploader("Envie seu arquivo CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("📄 Visualização da Tabela")
    st.dataframe(df.head())

    # Etapa 1: Profiling
    profile = profile_dataframe(df)

    # Etapa 1.5: Alertas de qualidade dos dados
    data_alerts = generate_data_alerts(df, profile)
    if data_alerts:
        st.subheader("⚠️ Qualidade dos Dados")
        for linha in data_alerts.strip().split("\n"):
            if linha.startswith("-"):
                st.warning(linha[2:])

    # Etapa 2: Inferência semântica por IA
    st.subheader("🔍 Interpretando colunas com IA...")
    semantics = {}
    for col in df.columns:
        valores = df[col].dropna().astype(str).unique().tolist()
        sem = infer_column_semantics(col, valores)
        semantics[col] = sem
        st.markdown(f"**{col}**: {sem}")

    # Etapa 3: Geração de gráficos com explicação
    st.subheader("📈 Visualizações automáticas")
    charts = generate_charts(df, profile["colunas"])
    for fig, meta in charts:
        st.plotly_chart(fig, use_container_width=True)
        explanation = describe_chart(meta["title"], meta["x"], meta["y"], meta["data"])
        st.markdown(f"_💬 {explanation}_")

    # Etapa 4: Geração de insights
    st.subheader("🧠 Insights do negócio")
    objetivo = st.text_input("(Opcional) Informe o objetivo da análise")
    if st.button("Gerar relatório de insights"):
        with st.spinner("Analisando com IA..."):
            prompt = build_prompt(df, profile, semantics, objetivo)
            insights = generate_insights(prompt)
            st.markdown(insights)
