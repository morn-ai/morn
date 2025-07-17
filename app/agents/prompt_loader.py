from app.config.agent_config import config


def load_prompt(name: str) -> str:
    """Load a prompt from the prompts' directory."""
    base_path = config.morn_prompt_dir
    prompt_path = base_path / f"{name}.txt"
    if prompt_path.exists():
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""
