from crewai import Agent
from pathlib import Path
import yaml

# Caminho para o agents.yaml
AGENT_CONFIG_PATH = Path(__file__).parent / "config" / "agents.yaml"

# Carrega o YAML de agentes
with open(AGENT_CONFIG_PATH, "r", encoding="utf-8") as f:
    AGENTS_YAML = yaml.safe_load(f)

def get_agent(agent_key: str) -> Agent:
    config = AGENTS_YAML[agent_key]
    return Agent(config=config, verbose=True, memory=True)

# Agente de qualidade dos dados
def get_quality_analyst_agent():
    return Agent(
        role="Analista de Qualidade de Dados",
        goal="Analisar a qualidade da base de dados",
        backstory="Especialista em identificar problemas, inconsistências e oportunidades de melhoria em bases de dados.",
        verbose=True
    )


# Agente de geração de insights
def get_insight_agent():
    return Agent(
        role="Analista de Insights de Negócio",
        goal="Gerar insights de valor a partir de dados",
        backstory="Você é um analista experiente em encontrar padrões, oportunidades e tendências em dados de e-commerce.",
        verbose=True
    )


# Agente de perguntas e respostas com base em dados
def get_qa_agent():
    return Agent(
        role="Analista de Dados Interativo",
        goal="Responder perguntas com base em dados CSV",
        backstory="Você é um assistente de dados treinado para responder perguntas objetivas com base nas informações disponíveis.",
        verbose=True
    )


# Agente que descreve gráficos
def get_chart_describer_agent():
    return Agent(
        role="Especialista em Visualização de Dados",
        goal="Analisar gráficos e gerar descrições úteis com base nos dados apresentados",
        backstory=(
            "Você é um analista de dados altamente qualificado, especializado em interpretar gráficos "
            "e comunicar padrões de forma clara e objetiva. Sua habilidade é transformar dados visuais em informações compreensíveis."
        ),
        verbose=True
    )


# ⚡️ Novo agente: recomenda os melhores gráficos para análise
def get_chart_advisor_agent():
    return Agent(
        role="Consultor de Visualização de Dados",
        goal="Recomendar os melhores gráficos para visualização de um conjunto de dados",
        backstory="Você é um especialista em visualização de dados. Seu trabalho é sugerir os 8 gráficos mais úteis, indicando colunas ideais para o eixo X, eixo Y e o tipo de gráfico (Barra, Linha ou Pizza).",
        verbose=True
    )
