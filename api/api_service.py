import pandas as pd
import logging
import os
import json
from datetime import datetime, timedelta
from api.api_model import TwitchBotStatus, TwitchMessage
from typing import List
from pythonosc import udp_client


class APIService:
    def __init__(self, cfg=None):
        self.cfg = cfg
        self.logger = logging.getLogger(__name__)
        self.logger.info('API Service starting with config')
        self.logger.info(self.cfg)

        self.user_df_cols = ['twitch_name', 'twitch_id', 'admin', 'rally_wallet_id', 'rally_auth_token']
        self.message_show_cols = ['channel_name', 'author_name', 'message_text', 'datetime', 'is_command', 'command_type']
        self.admin_acc = {'twitch_name': cfg}
        self.user_info_path = './data/users.json'

        self._init_twitch_status()
        self._init_df()
        self._load_user_data()

        self.logger.info('API service ready!')

    def _init_twitch_status(self):
        self.twitch_status = {
            'channel_names': self.cfg['api']['status']['channel-names'],
            'mode': self.cfg['api']['status']['mode'],
            'osc_ip': self.cfg['api']['status']['osc-ip'],
            'osc_port': self.cfg['api']['status']['osc-port']
        }
        self.logger.info('Initial Twitch Bot Status:')
        self.logger.info(self.twitch_status)

    def _init_df(self):
        """Initialize our dataframe."""
        col_names = [i for i, v in TwitchMessage.__fields__.items()] + ['timestamp']

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

    def _init_osc(self):
        self.client = udp_client.SimpleUDPClient(
            self.twitch_status['osc_ip'],
            self.twitch_status['osc_port']
        )

    def _load_user_data(self):
        """Try to load user auth data."""
        if os.path.isfile(self.user_info_path):
            self.logger.info(f'Found user data in {self.user_info_path}')
            with open(self.user_info_path, 'r') as f:
                data = json.load(f)
            self.user_infos = data['users']
        else:
            self.user_infos = []

    def _write_user_data(self):
        infos_nodups = [dict(t) for t in {tuple(d.items()) for d in self.user_infos}]
        with open(self.user_info_path, 'w') as f:
            json.dump({'users': infos_nodups}, f)

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

    def add_user_info(self, info):
        """Store a user's information for NFT check."""
        info = info.dict()
        self.logger.debug(f'Got user info {info}')
        self.user_infos.append(info)
        self._write_user_data()
