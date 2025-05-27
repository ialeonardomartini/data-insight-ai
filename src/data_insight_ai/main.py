import pandas as pd
import plotly.express as px
import json
from crewai import Crew, Task, Process
from data_insight_ai.agent_loader import (
    get_quality_analyst_agent,
    get_insight_agent,
    get_qa_agent,
    get_chart_describer_agent,
    get_chart_advisor_agent
)
from data_insight_ai.task_loader import get_task

# Função auxiliar para conversão de DataFrame em string
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
    tarefa = get_task("avaliar_qualidade_dados", agent=agente)
    crew = Crew(agents=[agente], tasks=[tarefa], process=Process.sequential)
    resultado = crew.kickoff(inputs={"dataframe": df_str})
    return get_output(resultado)


# 2. Geração de insights
def gerar_insights_analise(df: pd.DataFrame, objetivo: str = "") -> str:
    df_str = dataframe_para_texto(df)
    agente = get_insight_agent()
    tarefa = get_task("gerar_insights_negocio", agent=agente)
    inputs = {
        "dataframe": df_str,
        "objetivo": objetivo or "Analisar dados de vendas e comportamento dos clientes em e-commerce."
    }
    crew = Crew(agents=[agente], tasks=[tarefa], process=Process.sequential)
    resultado = crew.kickoff(inputs=inputs)
    return get_output(resultado)


# 3. Perguntas e respostas
def responder_pergunta(df: pd.DataFrame, pergunta: str) -> str:
    df_str = dataframe_para_texto(df)
    agente = get_qa_agent()
    tarefa = get_task("responder_pergunta_csv", agent=agente)
    crew = Crew(agents=[agente], tasks=[tarefa], process=Process.sequential)
    resultado = crew.kickoff(inputs={"csv_text": df_str, "pergunta": pergunta})
    return get_output(resultado)


# 4. Colunas disponíveis no CSV
def identificar_colunas_csv(df: pd.DataFrame) -> list[str]:
    return list(df.columns)


# 5. Função para recomendar os melhores gráficos via agente
def sugerir_graficos_via_agente(df: pd.DataFrame) -> list[dict]:
    df_str = df.head(100).to_csv(index=False)
    agente = get_chart_advisor_agent()
    tarefa = get_task("sugerir_graficos_csv", agent=agente)

    crew = Crew(agents=[agente], tasks=[tarefa], process=Process.sequential)
    resultado = crew.kickoff(inputs={"csv_text": df_str})

    # ✅ Certifique-se de extrair o texto do CrewOutput
    raw = get_output(resultado)

    if not isinstance(raw, str):
        print("⚠️ O resultado não é uma string, convertendo...")
        raw = str(raw)

    try:
        sugestoes = json.loads(raw)
    except json.JSONDecodeError:
        print("❌ Erro ao decodificar JSON do agente.")
        return []

    if not isinstance(sugestoes, list):
        print("⚠️ O agente retornou algo que não é uma lista.")
        return []

    # ✅ Valida as colunas sugeridas
    colunas_validas = set(df.columns)
    sugestoes_validas = []
    for s in sugestoes:
        if (
            isinstance(s, dict)
            and s.get("eixo_x") in colunas_validas
            and s.get("eixo_y") in colunas_validas
            and s.get("tipo") in ["Barra", "Pizza", "Linha"]
        ):
            sugestoes_validas.append(s)

    if not sugestoes_validas:
        print("⚠️ Nenhuma sugestão válida foi retornada.")
    else:
        print(f"✅ {len(sugestoes_validas)} sugestões válidas geradas.")

    return sugestoes_validas

def descrever_grafico_via_agente(titulo: str, eixo_x: str, eixo_y: str, df_amostra: pd.DataFrame) -> str:
    agente = get_chart_describer_agent()
    task = get_task("descrever_grafico", agent=agente)

    dados_amostra = df_amostra[[eixo_x, eixo_y]].head(500).to_csv(index=False)

    crew = Crew(agents=[agente], tasks=[task], process=Process.sequential)
    resultado = crew.kickoff(inputs={
        "titulo": titulo,
        "eixo_x": eixo_x,
        "eixo_y": eixo_y,
        "dados_amostra": dados_amostra  # 👈 Aqui o nome precisa bater com o tasks.yaml
    })

    return get_output(resultado)