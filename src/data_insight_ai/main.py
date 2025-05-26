import pandas as pd
from crewai import Crew, Task, Process
from data_insight_ai.agent_loader import (
    get_data_profiler_agent,
    get_quality_analyst_agent,
    get_insight_agent,
    get_qa_agent,
    get_chart_agent,
    get_chart_describer_agent
)
from data_insight_ai.tools.chart_generator_tool import gerar_graficos_automaticamente
from data_insight_ai.utils.pdf_generator import gerar_relatorio_completo


def dataframe_para_texto(df: pd.DataFrame, linhas: int = 20) -> str:
    return df.head(linhas).to_csv(index=False)

# ✅ Helper para garantir fallback
def get_output(resultado):
    return resultado.output if hasattr(resultado, "output") else resultado

# 1. Avaliação de qualidade dos dados
def avaliar_qualidade_dados(df: pd.DataFrame) -> str:
    df_str = dataframe_para_texto(df)
    agente = get_quality_analyst_agent()
    tarefa = Task(
        description="Analise a qualidade dos dados com base na amostra abaixo:\n\n{dataframe}",
        expected_output="Resumo da qualidade dos dados e eventuais problemas.",
        agent=agente
    )
    crew = Crew(agents=[agente], tasks=[tarefa], process=Process.sequential)
    return get_output(crew.kickoff(inputs={"dataframe": df_str}))

# 2. Geração de insights
def gerar_insights_analise(df: pd.DataFrame, objetivo: str = "") -> str:
    df_str = dataframe_para_texto(df)
    agente = get_insight_agent()
    tarefa = Task(
        description=(
            "Gere um relatório de insights com base nos dados fornecidos abaixo.\n\n"
            "Objetivo do usuário: {objetivo}\n\n"
            "Amostra dos dados:\n{dataframe}"
        ),
        expected_output="Relatório com padrões, anomalias e recomendações de negócio.",
        agent=agente
    )
    crew = Crew(agents=[agente], tasks=[tarefa], process=Process.sequential)
    return get_output(crew.kickoff(inputs={"dataframe": df_str, "objetivo": objetivo}))

# 3. Q&A com IA
def responder_pergunta(df: pd.DataFrame, pergunta: str) -> str:
    df_str = dataframe_para_texto(df)
    agente = get_qa_agent()
    tarefa = Task(
        description=(
            "Com base na seguinte tabela de dados:\n{dataframe}\n\n"
            "Responda à pergunta do usuário:\n{pergunta}"
        ),
        expected_output="Resposta objetiva baseada somente nos dados fornecidos.",
        agent=agente
    )
    crew = Crew(agents=[agente], tasks=[tarefa], process=Process.sequential)
    return get_output(crew.kickoff(inputs={"dataframe": df_str, "pergunta": pergunta}))

# 4. Geração de gráficos com explicação
def gerar_graficos(df: pd.DataFrame) -> list[dict]:
    csv = dataframe_para_texto(df)
    graficos = gerar_graficos_automaticamente(csv)

    lista_final = []
    for fig, meta in graficos:
        try:
            x_col = fig.data[0].xaxis.title.text if hasattr(fig.data[0].xaxis, 'title') else "x"
            y_col = fig.data[0].yaxis.title.text if hasattr(fig.data[0].yaxis, 'title') else "y"
        except Exception:
            x_col, y_col = "x", "y"

        titulo = fig.layout.title.text or "Gráfico gerado"
        try:
            dados_x = list(fig.data[0].x)
            dados_y = list(fig.data[0].y)
            df_amostra = pd.DataFrame({x_col: dados_x, y_col: dados_y})
        except Exception:
            df_amostra = pd.DataFrame()

        descricao = descrever_grafico_com_agente(titulo, x_col, y_col, df_amostra)
        if not descricao:
            descricao = "Gráfico gerado automaticamente. Nenhuma descrição disponível."

        lista_final.append({
            "fig": fig,
            "descricao": descricao
        })

    return lista_final

# Descrição de gráfico via IA
def descrever_grafico_com_agente(titulo: str, x_col: str, y_col: str, df: pd.DataFrame) -> str:
    agente = get_chart_describer_agent()
    try:
        sample = df[[x_col, y_col]].head(10).to_csv(index=False)
    except Exception:
        sample = ""

    task = Task(
        description=(
            f"Você deve analisar um gráfico com o título '{titulo}'\n"
            f"Eixo X: {x_col} | Eixo Y: {y_col}\n"
            f"Amostra de dados:\n{sample}\n\n"
            f"Escreva uma explicação clara e objetiva sobre o que o gráfico representa.\n"
            f"Use no máximo 3 frases e destaque conclusões ou padrões importantes."
        ),
        expected_output="Texto explicativo do gráfico",
        agent=agente
    )

    crew = Crew(agents=[agente], tasks=[task], process=Process.sequential)
    return get_output(crew.kickoff())

# 5. Geração de PDF completo (sem agentes)
def gerar_pdf_completo(df, qualidade_texto, insights, graficos, perguntas_respostas):
    return gerar_relatorio_completo(df, qualidade_texto, insights, graficos, perguntas_respostas)
