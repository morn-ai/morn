import os


class AgentConfig:
    morn_port: int = int(os.getenv("MORN_PORT", "8000"))
    morn_auth_mode: str = os.getenv("MORN_AUTH_MODE", "none")
    morn_admin_username: str = os.getenv("MORN_ADMIN_USERNAME", "admin")
    morn_admin_password: str = os.getenv("MORN_ADMIN_PASSWORD")
    openai_model: str = os.getenv("OPENAI_MODEL", "deepseek-chat")
