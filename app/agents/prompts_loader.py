import logging

from app.config.agent_config import AgentConfig

def load_prompt(name: str) -> str:
    """Load a prompt from the prompts' directory."""
    prompt_path = AgentConfig.morn_agent_conf_file / f"{name}.txt"
    if prompt_path.exists():
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    logging.warning(f"Prompt {name} not found.")
    return ""
