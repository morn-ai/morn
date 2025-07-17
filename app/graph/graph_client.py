from pyhugegraph.client import PyHugeClient  # type: ignore

from app.config.agent_config import config
from typing import Optional


class GraphClient:
    _instance: Optional['GraphClient'] = None
    _initialized: bool
    client: PyHugeClient

    def __new__(cls) -> 'GraphClient':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return

        self.client = PyHugeClient(config.hugegraph_host, config.hugegraph_port, user=config.hugegraph_username,
                                   pwd=config.hugegraph_password, graph=config.hugegraph_graph_name)

        self._initialized = True


graph_client = GraphClient()
