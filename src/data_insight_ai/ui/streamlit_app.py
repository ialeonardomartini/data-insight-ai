import streamlit as st
import pandas as pd
import plotly.express as px
from data_insight_ai.main import (
    avaliar_qualidade_dados,
    gerar_insights_analise,
    responder_pergunta,
    sugerir_graficos_via_agente,
    identificar_colunas_csv,
    descrever_grafico_via_agente
)

st.set_page_config(page_title="📊 Data Insight AI", layout="wide")

st.markdown(
    "<h1 style='font-size: 62px; color: #3366cc; margin-bottom: 0;'>📊 DATA INSIGHT AI</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='font-size: 22px; color: #777; margin-top: 16px; margin-bottom: 0;'>"
    "Obtenha insights estratégicos diretamente dos seus dados. Upload, análise automática, visualização e perguntas inteligentes com IA."
    "</p>",
    unsafe_allow_html=True
)

# ✅ CSS para deixar filtros compactos
st.markdown("""
    <style>
    div[data-baseweb="select"] > div {
        font-size: 0.85rem;
        padding-top: 0.25rem;
        padding-bottom: 0.25rem;
    }

    .stSelectbox, .stTextInput, .stRadio {
        margin-bottom: 0.5rem;
    }

    label {
        font-size: 0.85rem !important;
        color: #ddd !important;
    }

    section.main > div {
        padding-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- Inicialização
if "df" not in st.session_state:
    st.session_state.df = None

# --- Seção 1: Upload
with st.container():
    st.markdown("<h2 style='font-size: 36px; color: #333; margin-bottom: 0;'>1. Upload de Arquivo CSV</h2>", unsafe_allow_html=True)
    file = st.file_uploader("", type=["csv"])
    
    if file:
        df = pd.read_csv(file)
        
        st.session_state.df = df
        st.session_state.colunas_csv = list(df.columns)

        st.dataframe(df, use_container_width=True)

        if "sugestoes_graficos" not in st.session_state or st.button("🔄 Recarregar sugestões de gráfico via IA"):
            st.session_state.sugestoes_graficos = sugerir_graficos_via_agente(df)

        if "colunas_csv" not in st.session_state:
            st.session_state.colunas_csv = identificar_colunas_csv(df)

        st.divider()

# --- Seção 2: Qualidade
if st.session_state.df is not None:
    with st.container():
        st.markdown("<h2 style='font-size: 36px; color: #333;'>2. Avaliação da Qualidade dos Dados</h2>", unsafe_allow_html=True)
        if "qualidade" not in st.session_state:
            with st.spinner("Analisando qualidade dos dados..."):
                st.session_state.qualidade = avaliar_qualidade_dados(st.session_state.df)

        st.markdown(
                        f"<div style='color:#777; font-size:18px; margin-top:40px; margin-bottom:40px;'>{st.session_state.qualidade}</div>",
                        unsafe_allow_html=True
                    )

        st.divider()

# --- Seção 3: Visualização IA + Personalização
if st.session_state.df is not None and "sugestoes_graficos" in st.session_state:
    with st.container():
        st.markdown("<h2 style='font-size: 36px; color: #333; margin-bottom: 16px''>3. Visualização Inteligente com IA</h2>", unsafe_allow_html=True)
       
        df = st.session_state.df
        sugestoes = st.session_state.sugestoes_graficos

        colunas_numericas = list(df.select_dtypes(include=["int64", "float64"]).columns)

        def colunas_categoricas_validas(df):
            return [
                col for col in df.select_dtypes(include=["object", "category"]).columns
            ] or list(df.select_dtypes(include=["object", "category"]).columns)

        col_x_validas = colunas_categoricas_validas(df)

        layout_indices = [("unico", 0), ("unico", 1), ("unico", 2), ("unico", 3), ("unico", 4)]

        for bloco in layout_indices:
            tipo = bloco[0]
            if tipo == "unico":         
                i = bloco[1]

                if i >= len(sugestoes): continue
                
                sugestao = sugestoes[i]
                
                st.markdown(f"<h3 style='font-size: 28px; color: #555; margin-top: 12px'>Gráfico eixo_y por eixo_x</h3>", unsafe_allow_html=True)

                col1, col2, col3, col4 = st.columns([1, 1, 1, 3])

                with col1:
                    eixo_x = st.selectbox(
                        "",
                        col_x_validas,
                        index=col_x_validas.index(sugestao["eixo_x"]) if sugestao["eixo_x"] in col_x_validas else 0,
                        key=f"x_{i}"
                    )
                with col2:
                    eixo_y = st.selectbox(
                        "",
                        colunas_numericas,
                        index=colunas_numericas.index(sugestao["eixo_y"]) if sugestao["eixo_y"] in colunas_numericas else 0,
                        key=f"y_{i}"
                    )
                with col3: 
                    tipo_grafico = st.selectbox(
                        "",  # deixa o selectbox sem label, pois já usamos st.markdown acima
                        ["Barra", "Linha", "Pizza"],
                        index=["Barra", "Linha", "Pizza"].index(sugestao["tipo"]),
                        key=f"tipo_{i}"
                    )

                try:
                    df_grouped = df.groupby(eixo_x)[eixo_y].sum().reset_index()

                    if tipo_grafico == "Barra":
                        fig = px.bar(
                            df_grouped, 
                            x=eixo_x, 
                            y=eixo_y, 
                            color=eixo_x, 
                            color_discrete_sequence=px.colors.qualitative.G10
                            )
                        fig.update_layout(showlegend=False)

                    elif tipo_grafico == "Linha":
                        fig = px.line(
                            df_grouped, 
                            x=eixo_x, 
                            y=eixo_y,
                            color_discrete_sequence=px.colors.qualitative.G10
                            )
                        fig.update_layout(showlegend=False)

                    elif tipo_grafico == "Pizza":
                        fig = px.pie(
                            df_grouped, 
                            names=eixo_x, 
                            values=eixo_y, 
                            color=eixo_x, 
                            color_discrete_sequence=px.colors.qualitative.G10
                            )
                        
                    # ⬇️ Ajuste fino de layout
                    fig.update_layout(
                        height=360,
                        margin=dict(t=60, b=40, l=150, r=180),
                        #template="simple_white",
                        legend=dict(
                            orientation="v",
                            yanchor="auto",
                            y=1.02,
                            xanchor="auto",
                            x=1,
                            font=dict(size=18),
                            traceorder="normal"
                        )
                    )

                    fig.update_xaxes(
                        title=dict(
                            text=eixo_x,
                            standoff=40,
                            font=dict(size=16)
                        )
                    )

                    fig.update_yaxes(
                        title=dict(
                            text=eixo_y,
                            standoff=40,
                            font=dict(size=16)
                        )
                    )

                    st.plotly_chart(fig, use_container_width=True, key=f"fig_{i}")

                    descricao = descrever_grafico_via_agente(
                        titulo=f"{eixo_y} por {eixo_x}",
                        eixo_x=eixo_x,
                        eixo_y=eixo_y,
                        df_amostra=df_grouped
                    )

                    st.markdown(
                        f"<div style='color:#777; font-size:18px; margin-top: 40px; margin-bottom: 40px; margin-left: 40px; margin-right: 40px;'>🧠 <strong>Insight:</strong> {descricao}</div>",
                        unsafe_allow_html=True
                    )

                except Exception as e:
                    st.error(f"Erro ao gerar gráfico {i+1}: {e}")

                st.divider()

# --- Seção 4: Insights de Negócio
if st.session_state.df is not None:
    with st.container():
        st.markdown("<h2 style='font-size: 36px; color: #333;'>4. Insights Estratégicos do Negócio</h2>", unsafe_allow_html=True)
        objetivo = st.text_input("Objetivo da análise", "Identificar padrões e oportunidades de negócio")
        if "insights" not in st.session_state:
            with st.spinner("Gerando insights..."):
                st.session_state.insights = gerar_insights_analise(st.session_state.df, objetivo)

        st.markdown(
                        f"<div style='color:#777; font-size:18px; margin-top:40px; margin-bottom:40px;'>{st.session_state.insights}</div>",
                        unsafe_allow_html=True
                    )

        st.divider()

# --- Seção 5: Perguntas com IA
if st.session_state.df is not None:
    with st.container():
        st.markdown("<h2 style='font-size: 36px; color: #333;'>5. Pergunte algo sobre os dados</h2>", unsafe_allow_html=True)
        pergunta = st.text_input("Digite sua pergunta:")
        if pergunta:
            with st.spinner("Analisando pergunta..."):
                resposta = responder_pergunta(st.session_state.df, pergunta)
                st.session_state.resposta_qa = resposta

            st.markdown(
                        f"<div style='color:#777; font-size:18px; margin-top:40px; margin-bottom:40px;'>**💬 Resposta da IA:** {resposta}</div>",
                        unsafe_allow_html=True
                    )

            st.divider()
