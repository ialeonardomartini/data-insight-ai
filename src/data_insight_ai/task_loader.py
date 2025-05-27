import yaml
from pathlib import Path
from crewai import Task

TASKS_YAML_PATH = Path(__file__).parent / "config" / "tasks.yaml"

def get_task(task_id: str, agent) -> Task:
    with open(TASKS_YAML_PATH, "r", encoding="utf-8") as file:
        tasks_config = yaml.safe_load(file)

    if task_id not in tasks_config:
        raise ValueError(f"Tarefa '{task_id}' não encontrada no tasks.yaml")

    config = tasks_config[task_id]
    return Task(
        description=config["description"],
        expected_output=config["expected_output"],
        agent=agent
    )
