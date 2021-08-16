
class BaseConnector:
    """Parent class for API connectors."""
    def __init__(self, cfg):
        self.cfg = cfg

    def _connect(self, options: dict):
        raise NotImplementedError
