import logging
import requests as r
from connectors.base_connector import BaseConnector


class JackConnector(BaseConnector):
    """Connect to the Jack Bot API for chat and user info."""
    def __init__(self, cfg):
        super().__init__(cfg)
        assert 'api' in cfg, 'Please supply a url or host/port combination for the Jack API.'

        if 'host' in cfg['api']:
            self.api_url = f"http://{cfg['api']['host']}:{cfg['api']['port']}"
        else:
            self.api_url = cfg['api']['url']
        self.twitch_status_url = self.api_url + '/twitch/status'
        self.twitch_messages_url = self.api_url + '/twitch/get_messages'
        self.logger = logging.getLogger(__name__)

        self._connect()

    def _connect(self):
        res = r.get(self.api_url)
        self.logger.info(res.status_code)
        self.logger.info(res.json())

    def get_twitch_bot_status(self):
        return r.get(self.twitch_status_url).json()

    def set_twitch_bot_status(self, new_status):
        print(type(new_status))
        res = r.patch(self.twitch_status_url, json=new_status)
        if res.status_code == 200:
            return 'Success!'
        else:
            return res.json()

    def get_twitch_messages(self, seconds_history=None, channel_names=None):
        url = self.twitch_messages_url
        if any([seconds_history, channel_names]):
            url += '?'

        if seconds_history:
            url += 'seconds_history=' + str(seconds_history)

        if channel_names:
            for channel_name in channel_names:
                url += '&channel_names=' + channel_name
        return r.get(url).json()
