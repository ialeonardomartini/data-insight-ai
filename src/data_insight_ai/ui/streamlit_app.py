import streamlit as st
import pandas as pd
from data_insight_ai.main import (
    avaliar_qualidade_dados,
    gerar_insights_analise,
    gerar_graficos,
    responder_pergunta,
    gerar_pdf_completo  # ✅ nova função
)

st.set_page_config(page_title="DataInsightAI", layout="wide")
st.title("📊 DataInsightAI — Geração automática de insights e dashboards")

# Inicialização do estado
for chave in ["df", "insights", "graficos", "qualidade_texto", "chat_history"]:
    if chave not in st.session_state:
        st.session_state[chave] = None if chave != "chat_history" else []

# =======================
# SEÇÃO 1 — Upload e Tabela
# =======================
uploaded_file = st.file_uploader("📤 Envie seu arquivo CSV", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    if df.shape[0] > 1000:
        df = df.sample(n=1000, random_state=42)
        st.warning("⚠️ Amostragem aplicada: até 1000 linhas.")
    if df.shape[1] > 15:
        df = df.iloc[:, :15]
        st.warning("⚠️ Limitado às 15 primeiras colunas.")
    st.session_state.df = df

if st.session_state.df is not None:
    st.subheader("📄 Visualização da Tabela")
    st.dataframe(st.session_state.df.head())

# =======================
# SEÇÃO 2 — Avaliação de Qualidade
# =======================
    st.subheader("🧪 Avaliação da Qualidade dos Dados")
    if st.button("Avaliar Qualidade"):
        with st.spinner("Analisando..."):
            resultado = avaliar_qualidade_dados(st.session_state.df)
            st.session_state.qualidade_texto = resultado
            st.markdown(resultado)
    elif st.session_state.qualidade_texto:
        st.markdown(st.session_state.qualidade_texto)

# =======================
# SEÇÃO 3 — Geração de Insights
# =======================
    st.subheader("🧠 Geração de Insights")
    objetivo = st.text_input("Objetivo da análise (opcional):")
    if st.button("Gerar Insights"):
        with st.spinner("Gerando insights..."):
            insights = gerar_insights_analise(st.session_state.df, objetivo)
            st.session_state.insights = insights
            st.markdown(insights)
    elif st.session_state.insights:
        st.markdown("### 📄 Últimos Insights")
        st.markdown(st.session_state.insights)

# =======================
# SEÇÃO 4 — Geração de Gráficos
# =======================
    st.subheader("📊 Visualizações com Análise")
    if st.button("Gerar Gráficos"):
        with st.spinner("Gerando gráficos..."):
            graficos = gerar_graficos(st.session_state.df)
            st.session_state.graficos = graficos

    if st.session_state.graficos:
        for g in st.session_state.graficos:
            st.plotly_chart(g["fig"], use_container_width=True)
            st.markdown(f"_💬 {g['descricao']}_")

# =======================
# SEÇÃO 5 — Q&A com IA
# =======================
    st.subheader("💬 Perguntas sobre os Dados")
    with st.form("chat_form"):
        pergunta = st.text_input("Digite sua pergunta")
        enviar = st.form_submit_button("Perguntar")

    if enviar and pergunta:
        with st.spinner("Respondendo..."):
            resposta = responder_pergunta(st.session_state.df, pergunta)
            st.session_state.chat_history.append((pergunta, resposta))

    for pergunta, resposta in reversed(st.session_state.chat_history):
        st.markdown(f"**👤 Pergunta:** {pergunta}")
        st.markdown(f"**🤖 Resposta:** {resposta}")


# =======================
# SEÇÃO 6 — Download do Relatório em PDF
# =======================
    st.subheader("📥 Baixar Relatório Completo (PDF)")
    if (
        st.session_state.insights
        and st.session_state.qualidade_texto
        and st.session_state.graficos
        and st.session_state.chat_history
    ):
        if st.button("📄 Gerar e Baixar PDF Completo"):
            with st.spinner("Gerando relatório completo..."):
                pdf_bytes = gerar_pdf_completo(
                    st.session_state.df,
                    st.session_state.qualidade_texto,
                    st.session_state.insights,
                    st.session_state.graficos,
                    st.session_state.chat_history
                )
                st.download_button(
                    label="📥 Clique aqui para baixar",
                    data=pdf_bytes,
                    file_name="relatorio_data_insight_ai.pdf",
                    mime="application/pdf"
                )
    else:
        st.info("⚠️ Para gerar o PDF, complete as seções anteriores.")