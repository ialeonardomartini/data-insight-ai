import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import streamlit as st
import pandas as pd
from app.agents.data_profiler import profile_dataframe
from app.agents.column_semantics_agent import infer_column_semantics
from app.agents.chart_generator import generate_charts
from app.agents.prompt_builder import build_prompt, generate_data_alerts, classify_data_quality
from app.agents.insight_generator import generate_insights
from app.agents.chart_describer import describe_chart
from app.utils.pdf_generator import gerar_relatorio_com_graficos

st.set_page_config(page_title="DataInsightAI", layout="wide")
st.title("📊 DataInsightAI — Geração automática de insights e dashboards")

uploaded_file = st.file_uploader("Envie seu arquivo CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("📄 Visualização da Tabela")
    st.dataframe(df.head())

    # Etapa 1: Profiling
    profile = profile_dataframe(df)

    # Etapa 1.5: Classificação de qualidade dos dados
    qualidade = classify_data_quality(profile, df)
    if qualidade["nivel"] == "Boa":
        st.success(f"🧪 Qualidade dos Dados: {qualidade['nivel']}")
    elif qualidade["nivel"] == "Média":
        st.warning(f"🧪 Qualidade dos Dados: {qualidade['nivel']}")
    else:
        st.error(f"🧪 Qualidade dos Dados: {qualidade['nivel']}")

    for problema in qualidade["problemas"]:
        st.markdown(f"- {problema}")

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
    charts_data = []
    charts = generate_charts(df, profile["colunas"])
    for fig, meta in charts:
        st.plotly_chart(fig, use_container_width=True)
        explanation = describe_chart(meta["title"], meta["x"], meta["y"], meta["data"])
        st.markdown(f"_💬 {explanation}_")
        charts_data.append({"fig": fig, "titulo": meta["title"]})

    # Etapa 4: Geração de insights
    st.subheader("🧠 Insights do negócio")
    objetivo = st.text_input("(Opcional) Informe o objetivo da análise")
    if st.button("Gerar relatório de insights"):
        with st.spinner("Analisando com IA..."):
            prompt = build_prompt(df, profile, semantics, objetivo)
            insights = generate_insights(prompt)
            st.markdown(insights)

            # PDF download
            pdf_bytes = gerar_relatorio_com_graficos(insights, charts_data)
            st.download_button(
                label="📄 Baixar relatório em PDF",
                data=pdf_bytes,
                file_name="relatorio_data_insight_ai.pdf",
                mime="application/pdf"
            )
