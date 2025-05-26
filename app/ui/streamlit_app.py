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
from app.agents.qa_agent import responder_pergunta_sobre_dados

st.set_page_config(page_title="DataInsightAI", layout="wide")
st.title("📊 DataInsightAI — Geração automática de insights e dashboards")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

uploaded_file = st.file_uploader("Envie seu arquivo CSV", type="csv")

# Processamento inicial só uma vez
if uploaded_file and "df" not in st.session_state:
    df_original = pd.read_csv(uploaded_file)

    linhas_originais = df_original.shape[0]
    colunas_originais = df_original.shape[1]

    if linhas_originais > 1000:
        df_original = df_original.sample(n=1000, random_state=42)
    if colunas_originais > 15:
        df_original = df_original.iloc[:, :15]

    st.warning(f"⚠️ O arquivo enviado possui {linhas_originais} linhas e {colunas_originais} colunas.\n"
               f"Aplicamos uma amostragem de até 1000 linhas e limitamos para as 15 primeiras colunas para melhor performance.")

    colunas_disponiveis = list(df_original.columns)
    colunas_selecionadas = st.multiselect("Selecione as colunas que deseja manter:", colunas_disponiveis, default=colunas_disponiveis)

    if colunas_selecionadas:
        df = df_original.loc[:, colunas_selecionadas]
        st.session_state.df = df
        st.session_state.profile = profile_dataframe(df)

        semantics = {}
        for col in df.columns:
            valores = df[col].dropna().astype(str).unique().tolist()
            sem = infer_column_semantics(col, valores)
            semantics[col] = sem
        st.session_state.semantics = semantics

        st.session_state.charts_data = []
        charts = generate_charts(df, st.session_state.profile["colunas"])
        for fig, meta in charts:
            st.session_state.charts_data.append({
                "fig": fig,
                "titulo": meta["title"],
                "x": meta["x"],
                "y": meta["y"],
                "data": meta["data"]
            })
        st.rerun()

# Interface principal
if "df" in st.session_state:
    df = st.session_state.df
    profile = st.session_state.profile
    semantics = st.session_state.semantics
    charts_data = st.session_state.charts_data

    st.subheader("📄 Visualização da Tabela")
    st.dataframe(df.head())

    qualidade = classify_data_quality(profile, df)
    if qualidade["nivel"] == "Boa":
        st.success(f"🧪 Qualidade dos Dados: {qualidade['nivel']}")
    elif qualidade["nivel"] == "Média":
        st.warning(f"🧪 Qualidade dos Dados: {qualidade['nivel']}")
    else:
        st.error(f"🧪 Qualidade dos Dados: {qualidade['nivel']}")
    for problema in qualidade["problemas"]:
        st.markdown(f"- {problema}")

    st.subheader("🔍 Descrição das colunas (via IA)")
    for col, sem in semantics.items():
        st.markdown(f"**{col}**: {sem}")

    st.subheader("📈 Visualizações automáticas")
    for item in charts_data:
        st.plotly_chart(item["fig"], use_container_width=True)
        explanation = describe_chart(item["titulo"], item["x"], item["y"], item["data"])
        st.markdown(f"_💬 {explanation}_")

    st.subheader("🧠 Insights do negócio")
    objetivo = st.text_input("(Opcional) Informe o objetivo da análise")
    if st.button("Gerar relatório de insights"):
        with st.spinner("Analisando com IA..."):
            prompt = build_prompt(df, profile, semantics, objetivo)
            insights = generate_insights(prompt)
            st.session_state.insights = insights

            pdf_bytes = gerar_relatorio_com_graficos(insights, charts_data)
            st.download_button(
                label="📄 Baixar relatório em PDF",
                data=pdf_bytes,
                file_name="relatorio_data_insight_ai.pdf",
                mime="application/pdf"
            )

    if "insights" in st.session_state:
        st.subheader("📄 Último relatório de insights")
        st.markdown(st.session_state.insights)

    st.subheader("💬 Pergunte algo sobre seus dados")
    with st.form(key="chat_form"):
        pergunta = st.text_input("Digite sua pergunta")
        submit = st.form_submit_button("Enviar")

    if submit and pergunta:
        with st.spinner("Respondendo com IA..."):
            resposta = responder_pergunta_sobre_dados(df, pergunta)
            st.session_state.chat_history.append((pergunta, resposta))

    if st.session_state.chat_history:
        for pergunta, resposta in reversed(st.session_state.chat_history):
            st.markdown(f"**👤 Pergunta:** {pergunta}")
            st.markdown(f"**🤖 Resposta:** {resposta}")