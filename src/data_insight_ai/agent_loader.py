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

# Funções específicas
def get_data_profiler_agent(): return get_agent("data_profiler")
def get_quality_analyst_agent(): return get_agent("data_alert_analyst")
def get_insight_agent(): return get_agent("insight_generator")
def get_qa_agent(): return get_agent("qa_agent")
def get_chart_agent(): return get_agent("chart_generator")
def get_chart_describer_agent(): return get_agent("chart_describer")