import pandas as pd
from crewai import Crew, Task, Process
from data_insight_ai.agent_loader import (
    get_quality_analyst_agent,
    get_insight_agent,
    get_qa_agent,
    get_chart_describer_agent
)

from data_insight_ai.tools.chart_generator_tool import gerar_graficos_automaticamente
import plotly.express as px


def dataframe_para_texto(df: pd.DataFrame, linhas: int = None) -> str:
    if linhas is None:
        return df.to_csv(index=False)
    return df.head(linhas).to_csv(index=False)


def get_output(resultado):
    return resultado.output if hasattr(resultado, "output") else resultado


# 1. Qualidade dos dados
def avaliar_qualidade_dados(df: pd.DataFrame) -> str:
    df_str = dataframe_para_texto(df)
    agente = get_quality_analyst_agent()
    tarefa = Task(
        description="Analise a qualidade da base de dados completa a seguir:\n\n{dataframe}",
        expected_output="Resumo da qualidade dos dados, incluindo possíveis falhas e sugestões de melhoria.",
        agent=agente
    )
    crew = Crew(agents=[agente], tasks=[tarefa], process=Process.sequential)
    return get_output(crew.kickoff(inputs={"dataframe": df_str}))


# 2. Insights de negócio
def gerar_insights_analise(df: pd.DataFrame, objetivo: str = "") -> str:
    df_str = dataframe_para_texto(df)
    agente = get_insight_agent()
    tarefa = Task(
        description=(
            "Com base na base de dados completa abaixo, gere um relatório de insights úteis para o negócio.\n\n"
            "Objetivo do usuário: {objetivo}\n\n"
            "Base de dados:\n{dataframe}"
        ),
        expected_output="Relatório com padrões, anomalias, oportunidades e recomendações de negócio.",
        agent=agente
    )
    inputs = {
        "dataframe": df_str,
        "objetivo": objetivo or "Analisar dados de vendas e comportamento dos clientes em e-commerce."
    }
    crew = Crew(agents=[agente], tasks=[tarefa], process=Process.sequential)
    return get_output(crew.kickoff(inputs=inputs))


# 3. Perguntas e respostas
def responder_pergunta(df: pd.DataFrame, pergunta: str) -> str:
    df_str = dataframe_para_texto(df)
    agente = get_qa_agent()
    tarefa = Task(
        description=(
            "Com base na seguinte base de dados completa:\n{dataframe}\n\n"
            "Responda à pergunta do usuário com base apenas nessas informações:\n{pergunta}"
        ),
        expected_output="Resposta objetiva e clara, com base apenas nos dados fornecidos.",
        agent=agente
    )
    crew = Crew(agents=[agente], tasks=[tarefa], process=Process.sequential)
    return get_output(crew.kickoff(inputs={"dataframe": df_str, "pergunta": pergunta}))


# 4. Geração de gráficos interativos
def gerar_graficos_interativos(df: pd.DataFrame, kpi: str = "valor_total") -> dict:
    df_aprovado = df[df["status_pagamento"] == "Aprovado"]

    linha = px.line(
        df_aprovado.groupby("data_compra")[kpi].sum().reset_index(),
        x="data_compra", y=kpi,
        title=f"Evolução diária de {kpi.replace('_', ' ').title()}",
    )

    barra = px.bar(
        df_aprovado.groupby("produto")[kpi].sum().nlargest(10).reset_index(),
        x="produto", y=kpi,
        title=f"Top 10 Produtos por {kpi.replace('_', ' ').title()}",
    )

    pizza_categoria = px.pie(
        df_aprovado, names="categoria", values=kpi,
        title=f"Distribuição por Categoria ({kpi.replace('_', ' ').title()})"
    )

    pizza_canal = px.pie(
        df_aprovado, names="canal_origem", values=kpi,
        title=f"Distribuição por Canal de Origem ({kpi.replace('_', ' ').title()})"
    )

    return {
        "linha": linha,
        "barra": barra,
        "pizza_categoria": pizza_categoria,
        "pizza_canal": pizza_canal,
    }


# 5. Descrição dos gráficos via IA
def descrever_grafico_com_agente(titulo: str, x_col: str, y_col: str, df: pd.DataFrame) -> str:
    agente = get_chart_describer_agent()
    try:
        sample = df[[x_col, y_col]].head(10).to_csv(index=False)
    except Exception:
        sample = ""

    task = Task(
        description=(
            f"Analise o seguinte gráfico gerado a partir da base de dados completa:\n"
            f"Título: {titulo}\n"
            f"Eixo X: {x_col} | Eixo Y: {y_col}\n\n"
            f"Amostra dos dados usados para o gráfico:\n{sample}\n\n"
            f"Descreva em no máximo 3 frases o que esse gráfico mostra e destaque qualquer padrão ou insight relevante."
        ),
        expected_output="Descrição objetiva e clara sobre o que o gráfico representa.",
        agent=agente
    )

    crew = Crew(agents=[agente], tasks=[task], process=Process.sequential)
    return get_output(crew.kickoff())


# 7. KPIs de negócio
def calcular_kpis_negocio(df: pd.DataFrame) -> dict:
    df_aprovado = df[df["status_pagamento"] == "Aprovado"]

    ticket_medio_pedido = round(df_aprovado["valor_total"].mean(), 2)
    ticket_medio_cliente = round(df_aprovado.groupby("cliente_id")["valor_total"].sum().mean(), 2)
    media_pedidos_por_cliente = round(df_aprovado.groupby("cliente_id")["pedido_id"].nunique().mean(), 2)

    faturamento_categoria = df_aprovado.groupby("categoria")["valor_total"].sum().sort_values(ascending=False)
    top_clientes = df_aprovado.groupby("cliente_id")["valor_total"].sum().nlargest(5).to_dict()

    return {
        "ticket_medio_pedido": ticket_medio_pedido,
        "ticket_medio_cliente": ticket_medio_cliente,
        "media_pedidos_por_cliente": media_pedidos_por_cliente,
        "faturamento_categoria": faturamento_categoria,
        "top_clientes": top_clientes
    }
