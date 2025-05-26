from crewai import Crew, Agent, Task, Process
from pathlib import Path
import yaml

# Caminho dos arquivos de configuração
config_path = Path(__file__).parent / "config"

def load_yaml_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# ✅ Apenas os agentes usados atualmente
def create_agents():
    agents_yaml = load_yaml_file(config_path / "agents.yaml")

    return {
        "data_alert_analyst": Agent(
            config=agents_yaml["data_alert_analyst"],
            verbose=True,
            memory=True
        ),
        "insight_generator": Agent(
            config=agents_yaml["insight_generator"],
            verbose=True,
            memory=True
        ),
        "chart_describer": Agent(
            config=agents_yaml["chart_describer"],
            verbose=True,
            memory=True
        ),
        "qa_agent": Agent(
            config=agents_yaml["qa_agent"],
            verbose=True,
            memory=True
        )
    }

# ✅ Apenas as tasks ligadas às funções que o main.py usa
def create_tasks(agent_map):
    tasks_yaml = load_yaml_file(config_path / "tasks.yaml")

    mapping = {
        "classify_data_quality_task": "data_alert_analyst",
        "generate_insights_task": "insight_generator",
        "describe_charts_task": "chart_describer",
        "qa_on_dataframe_task": "qa_agent"
    }

    return [
        Task(
            config=tasks_yaml[task_id],
            agent=agent_map[agent_name]
        )
        for task_id, agent_name in mapping.items()
    ]

# ✅ Monta a crew com apenas os agentes e tasks utilizados
def build_crew():
    agent_map = create_agents()
    tasks = create_tasks(agent_map)

    return Crew(
        agents=list(agent_map.values()),
        tasks=tasks,
        process=Process.sequential
    )
