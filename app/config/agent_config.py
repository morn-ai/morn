import os
from pathlib import Path


class AgentConfig:
    # server config
    morn_port: int = int(os.getenv("MORN_PORT", "8000"))
    # auth config
    morn_auth_mode: str = os.getenv("MORN_AUTH_MODE", "none")
    morn_admin_username: str = os.getenv("MORN_ADMIN_USERNAME", "admin")
    morn_admin_password: str = os.getenv("MORN_ADMIN_PASSWORD", "")
    # morn conf config
    morn_conf_dir: Path = Path(os.getenv("MORN_CONF_DIR", Path(__file__).parents[2] / "conf"))
    morn_agent_conf_file: Path = morn_conf_dir / "agent-conf.yaml"
    morn_mcp_conf_file: Path = morn_conf_dir / "mcp-servers.yaml"
    morn_prompt_dir: Path = morn_conf_dir / "prompts"
    openai_model: str = os.getenv("OPENAI_MODEL", "deepseek-chat")
    # OpenAI API config
    openai_api_base: str = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
