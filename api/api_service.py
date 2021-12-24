import pandas as pd
import logging
import os
import json
from datetime import datetime, timedelta
from api.api_model import TwitchBotStatus, TwitchMessage
from connectors.rally_connector import RallyConnector
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
        self._init_rally_connector()
        self._init_osc()
        self._load_user_data()
        self.get_all_nfts()

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
        self.logger.info('Message dataframe initiated.')

    def _init_rally_connector(self):
        self.rally = RallyConnector(self.cfg)
        self.logger.info('Rally connector ready.')

    def _init_osc(self):
        self.logger.info('Initializing OSC client...')
        self.logger.info(f'OSC target IP: {self.twitch_status["osc_ip"]}')
        self.logger.info(f'OSC target port: {int(self.twitch_status["osc_port"])}')
        self.osc_client = udp_client.SimpleUDPClient(
            self.twitch_status['osc_ip'],
            int(self.twitch_status['osc_port'])
        )
        self.logger.info('OSC client ready.')

    def _load_user_data(self):
        """Try to load user auth data."""
        if os.path.isfile(self.user_info_path):
            self.logger.info(f'Found user data in {self.user_info_path}')
            with open(self.user_info_path, 'r') as f:
                data = json.load(f)
            self.user_infos = {d['username']: d for d in data['users']}
        else:
            self.user_infos = {}

    def _write_user_data(self):
        """Persist user data to disk."""
        infos_nodups = [val for _, val in self.user_infos.items()]
        with open(self.user_info_path, 'w') as f:
            json.dump({'users': infos_nodups}, f, indent=4)

    def _load_nft_templates(self):
        """Load NFT Template info for all known template IDs."""
        self.nft_templates = self.get_nft_templates()
        self.nft_templates_byid = {nft['id']: nft for nft in self.nft_templates}
        self.logger.info(f'Loaded {len(self.nft_templates)} NFT templates.')

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
        self._init_osc()

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
        self.logger.debug(f'Got user info {info}. Looking up NFTs...')
        rally_account_info = self.get_rally_account_info(info['username'])
        if 'rallyNetworkWalletIds' in rally_account_info:
            info['rally'] = rally_account_info
            info = self.get_wallet_nfts(info)
        self.user_infos[info['username']] = info
        self._write_user_data()

    def get_wallet_nfts(self, user_info):
        """Get all the NFTs in a wallet."""
        self.logger.info(f'Checking NFTs for {user_info}...')
        self.get_all_nfts(return_value=False)
        user_info['nfts'] = []

        for nft_template_id, nfts in self.nfts.items():
            for nft in nfts:
                if nft['rallyNetworkWalletId'] in user_info['rally']['rallyNetworkWalletIds']:
                    self.logger.info(f'Found NFT: {nft}')
                    user_info['nfts'].append(nft)

        return user_info

    def set_rally_tokens(self, info):
        info = info.dict()
        self.logger.info(f'Setting Rally tokens to {info}...')
        self.rally.set_app_tokens(info)
        self.logger.info('Tokens set!')

    def get_nft_templates(self):
        return self.rally.get_nft_templates()

    def get_all_nfts(self, return_value=True):
        self._load_nft_templates()
        self.logger.info('Getting all NFTs...')
        nfts = {}

        for key, nft_template in self.nft_templates_byid.items():
            res = self.rally.get_nft(key)
            self.logger.debug(f'Found {res}')
            nfts[key] = res

        self.nfts = nfts
        self.logger.info(f'Found {len(nfts)} unique NFTs.')
        if return_value:
            return nfts

    def get_rally_account_info(self, id_):
        self.logger.info(f'Retrieving user data for {id_}...')
        res = self.rally.get_account_info(id_)
        self.logger.info(res)
        return res

    def get_all_account_infos(self):
        return list(self.user_infos.values())

    def form_osc_message(self, data, message_type='twitch-chat'):
        if message_type == 'twitch-chat':
            osc_address = '/twitch-chat'
            osc_message = [f'{key}:::{val}' for key, val in data.items()]

        return osc_address, osc_message

    async def handle_twitch_message(self, message):
        """Store the message and send it through OSC."""
        self.store_message(message)
        await self.send_twitch_message_osc(message)

    async def send_twitch_message_osc(self, message):
        self.logger.info(f'Sending Twitch chat OSC: {message}')
        osc_address, osc_message = self.form_osc_message(
            message.dict(),
            message_type='twitch-chat'
        )
        self.osc_client.send_message(osc_address, osc_message)
