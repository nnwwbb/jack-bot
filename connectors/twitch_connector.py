import logging
from connectors.base_connector import BaseConnector
from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator, refresh_access_token
from twitchAPI.types import AuthScope


class TwitchConnector(BaseConnector):
    """Connect to the Twitch API for chat and user info."""
    def __init__(self, cfg):
        super().__init__(cfg)
        self.cfg = cfg
        self.logger = logging.getLogger(__name__)
        self.refresh_token = None
        if 'twitch_refresh_token' in cfg['twitch']:
            self.logger.info('Found Twitch refresh token, using that for auth.')
            self.refresh_token = cfg['twitch']['twitch_refresh_token']
        self._connect()

    def _connect(self):
        self.twitch = Twitch(
            self.cfg['twitch']['twitch_ID'],
            self.cfg['twitch']['twitch_secret']
        )
        self.logger.info('Twitch API connected!')

    def get_oauth_token(self):
        if self.refresh_token:
            return self.get_oauth_token_refresh()
        else:
            return self.get_oauth_token_browser()

    def get_oauth_token_browser(self):
        target_scope = [AuthScope.BITS_READ, AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]
        auth = UserAuthenticator(self.twitch, target_scope, force_verify=False)
        # this will open your default browser and prompt you with the twitch verification website
        token, refresh_token = auth.authenticate()
        self.token = token
        return token

    def get_oauth_token_refresh(self):
        new_token, new_refresh_token = refresh_access_token(
            self.refresh_token,
            self.cfg['twitch']['twitch_ID'],
            self.cfg['twitch']['twitch_secret']
        )
        self.token = new_token
        self.refresh_token = new_refresh_token
        return new_token
