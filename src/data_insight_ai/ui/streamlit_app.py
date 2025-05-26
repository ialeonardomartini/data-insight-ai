import streamlit as st
import pandas as pd
from data_insight_ai.main import (
    avaliar_qualidade_dados,
    gerar_insights_analise,
    responder_pergunta,
    gerar_graficos_interativos,
    calcular_kpis_negocio
)

st.set_page_config(page_title="Data Insight AI", layout="wide")
st.title("📊 Data Insight AI - E-commerce")

if "df" not in st.session_state:
    st.session_state.df = None

# 📁 Seção 1: Upload do arquivo
st.header("1. Upload de Arquivo CSV")
file = st.file_uploader("Envie um arquivo CSV com dados do e-commerce", type=["csv"])

if file:
    df = pd.read_csv(file)
    st.session_state.df = df
    st.success(f"✅ {df.shape[0]} linhas carregadas com sucesso!")
    st.dataframe(df.head(10))

# 📉 Seção 2: Avaliação da Qualidade
if st.session_state.df is not None:
    st.header("2. Avaliação de Qualidade dos Dados")
    if "qualidade" not in st.session_state:
        with st.spinner("Analisando qualidade dos dados..."):
            st.session_state.qualidade = avaliar_qualidade_dados(st.session_state.df)
    st.markdown(st.session_state.qualidade)

# 📈 Seção 2.5: KPIs estratégicos
if st.session_state.df is not None:
    st.header("📊 KPIs Estratégicos")
    if "kpis" not in st.session_state:
        with st.spinner("Calculando KPIs do e-commerce..."):
            st.session_state.kpis = calcular_kpis_negocio(st.session_state.df)

    kpis = st.session_state.kpis
    st.subheader("Resumo de Indicadores:")
    col1, col2, col3 = st.columns(3)
    col1.metric("🎯 Ticket Médio por Pedido", f"R$ {kpis['ticket_medio_pedido']}")
    col2.metric("🛍️ Ticket Médio por Cliente", f"R$ {kpis['ticket_medio_cliente']}")
    col3.metric("🔁 Média de Pedidos por Cliente", f"{kpis['media_pedidos_por_cliente']}")

    st.markdown("### 💰 Faturamento por Categoria")
    st.bar_chart(pd.Series(kpis["faturamento_categoria"]))

    st.markdown("### 🥇 Top 5 Clientes (Valor Total)")
    st.table(pd.DataFrame.from_dict(kpis["top_clientes"], orient="index", columns=["Valor Total"]))

# 📋 Seção 3: Geração de Insights
if st.session_state.df is not None:
    st.header("3. Insights de Negócio")
    objetivo = st.text_input("Objetivo da análise", "Identificar padrões de compra e comportamento de clientes")
    if "insights" not in st.session_state:
        with st.spinner("Gerando insights..."):
            st.session_state.insights = gerar_insights_analise(st.session_state.df, objetivo)
    st.markdown(st.session_state.insights)

# 📊 Seção 4: Visualização de Gráficos Interativos
if st.session_state.df is not None:
    st.header("4. Análise Visual Interativa")

    kpi_opcao = st.selectbox("Escolha o KPI para análise:", ["valor_total", "quantidade"])
    with st.spinner("Gerando gráficos..."):
        st.session_state.graficos = gerar_graficos_interativos(st.session_state.df, kpi=kpi_opcao)

    graficos = st.session_state.graficos
    st.subheader("📈 Evolução Temporal")
    st.plotly_chart(graficos["linha"], use_container_width=True)

    st.subheader("📊 Comparação por Produto")
    st.plotly_chart(graficos["barra"], use_container_width=True)

    st.subheader("🥧 Distribuição por Categoria e Canal")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(graficos["pizza_categoria"], use_container_width=True)
    with col2:
        st.plotly_chart(graficos["pizza_canal"], use_container_width=True)

# 💬 Seção 5: Pergunte algo sobre os dados
if st.session_state.df is not None:
    st.header("5. Pergunte algo sobre os dados")
    pergunta = st.text_input("Digite sua pergunta:", "")
    if pergunta:
        with st.spinner("Analisando pergunta..."):
            resposta = responder_pergunta(st.session_state.df, pergunta)
            st.session_state.resposta_qa = resposta
        st.markdown(f"**💬 Resposta:** {resposta}")
