import pandas as pd
import logging
from datetime import datetime, timedelta
from api.api_model import TwitchBotStatus, TwitchMessage
from typing import List


class APIService:
    def __init__(self, cfg=None):
        self.cfg = cfg
        print(self.cfg)
        self.logger = logging.getLogger(__name__)
        self.user_df_cols = ['twitch_name', 'twitch_id', 'admin', 'rally_wallet_id', 'rally_auth_token']
        self.message_show_cols = ['channel_name', 'author_name', 'message_text', 'datetime', 'is_command', 'command_type']
        self.admin_acc = {'twitch_name': cfg}
        self._init_twitch_status()
        self._init_df()
        self.logger.info('API service ready!')

    def _init_twitch_status(self):
        self.twitch_status = {
            'channel_names': ['colinbenders'],
            'mode': 'testing'
        }
        self.logger.info('Initial Twitch Bot Status:')
        self.logger.info(self.twitch_status)

    def _init_df(self):
        """Initialize our dataframe."""
        col_names = [i for i, v in TwitchMessage.__fields__.items()] + ['timestamp']
        print(col_names)
        self.df_message = pd.DataFrame(columns=col_names)
        self.df_user = pd.DataFrame(columns=self.user_df_cols)
        self.logger.info('Dataframes initialized:')
        self.logger.info(self.df_message)
        self.logger.info(self.df_user)
        if 'twitch' in self.cfg:
            for username in self.cfg['twitch']['twitch_admins']:
                admin_acc = {
                    'twitch_name': username,
                    'admin': True
                }
                self.df_user = self.df_user.append(admin_acc, ignore_index=True)
        self.logger.info(self.df_user)

    def get_twitch_bot_status(self):
        """Return the settings made for the Twitch bot."""
        self.logger.info('Returning Twitch Bot Status:')
        self.logger.info(self.twitch_status)
        return self.twitch_status

    def set_twitch_bot_status(self, status: TwitchBotStatus):
        """Change the settings for the Twitch bot."""
        self.logger.info('Setting Twitch Bot status:')
        self.logger.info(status.dict())
        self.twitch_status = status.dict()

    def store_message(self, message: TwitchMessage):
        """Store the message in the dataframe."""
        msg_dict = message.dict()
        msg_dict['timestamp'] = datetime.now()
        self.logger.debug(f'Storing message: {msg_dict}')
        self.df_message = self.df_message.append(msg_dict, ignore_index=True)

        if len(self.df_message) % 100 == 0:
            self.logger.info(f'API has {len(self.df_message)} messages stored:')
            self.logger.info(self.df_message[['channel_name', 'author_name', 'message_text']].tail())

    def get_messages(self, seconds_history: int = None, channel_names: List[str] = None):
        """Return the messages in our dataframe."""
        sub_df = self.df_message
        if seconds_history:
            past = datetime.now() - timedelta(seconds=seconds_history)
            sub_df = sub_df[sub_df['timestamp'] >= past]

        if channel_names:
            sub_df = sub_df[sub_df['channel_name'].isin(channel_names)]
        sub_df = sub_df[self.message_show_cols]
        return sub_df.to_dict('records')
