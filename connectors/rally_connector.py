import logging
import requests as r
from connectors.base_connector import BaseConnector


class RallyConnector(BaseConnector):
    """Connect to the Rally API for NFT and user info."""
    def __init__(self, cfg):
        super().__init__(cfg)
        self.logger = logging.getLogger(__name__)

    def _connect(self):
        self.logger.info()
