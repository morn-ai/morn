import os
from pathlib import Path
from typing import Optional


class AgentConfig:
    _instance: Optional['AgentConfig'] = None
    _initialized: bool
    
    # server config
    morn_host: str
    morn_port: int
    # auth config
    morn_auth_mode: str
    morn_admin_username: str
    morn_admin_password: str
    # JWT config
    jwt_secret_key: str
    jwt_algorithm: str
    jwt_access_token_expire_minutes: int
    # morn conf config
    morn_conf_dir: Path
    morn_agent_conf_file: Path
    morn_mcp_conf_file: Path
    morn_prompt_dir: Path
    openai_model: str
    # OpenAI API config
    openai_api_base: str
    openai_api_key: str
    # HugeGraph config
    hugegraph_host: str
    hugegraph_port: int
    hugegraph_username: str
    hugegraph_password: str
    hugegraph_graph_name: str
    
    def __new__(cls) -> 'AgentConfig':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        if self._initialized:
            return
        
        # server config
        self.morn_host = os.getenv("MORN_HOST", "localhost")
        self.morn_port = int(os.getenv("MORN_PORT", "8000"))
        # auth config
        self.morn_auth_mode = os.getenv("MORN_AUTH_MODE", "jwt")
        self.morn_admin_username = os.getenv("MORN_ADMIN_USERNAME", "admin")
        self.morn_admin_password = os.getenv("MORN_ADMIN_PASSWORD", "")
        # JWT config
        self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", "")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.jwt_access_token_expire_minutes = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
        # morn conf config
        self.morn_conf_dir = Path(os.getenv("MORN_CONF_DIR", Path(__file__).parents[2] / "conf"))
        self.morn_agent_conf_file = self.morn_conf_dir / "agent-conf.yaml"
        self.morn_mcp_conf_file = self.morn_conf_dir / "mcp-servers.yaml"
        self.morn_prompt_dir = self.morn_conf_dir / "prompts"
        self.openai_model = os.getenv("OPENAI_MODEL", "deepseek-chat")
        # OpenAI API config
        self.openai_api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        # HugeGraph config
        self.hugegraph_host = os.getenv("HUGEGRAPH_HOST", "localhost")
        self.hugegraph_port = int(os.getenv("HUGEGRAPH_PORT", "8080"))
        self.hugegraph_username = os.getenv("HUGEGRAPH_USERNAME", "admin")
        self.hugegraph_password = os.getenv("HUGEGRAPH_PASSWORD", "")
        self.hugegraph_graph_name = os.getenv("HUGEGRAPH_GRAPH_NAME", "hugegraph")
        
        self._initialized = True


# Global configuration instance
config = AgentConfig()
