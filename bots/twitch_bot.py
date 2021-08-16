import asyncio
import os
import logging
import requests as r
from twitchio.ext import commands
from utils import load_config, logging_setup
from connectors.twitch_connector import TwitchConnector
from rich import print
from urllib.parse import urljoin


class TwitchBot(commands.Bot):

    def __init__(self, cfg=None, sec_between_check=3):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...
        if cfg:
            self.cfg = cfg
        else:
            self.cfg = load_config(os.environ.get('CONFIG_FILE', 'configs/twitch-bot.yml'))
        self.bot_mode = cfg['bot-mode']
        self.sec_between_check = sec_between_check
        self.command_prefix = '?'
        self.logger = logging.getLogger(__name__)

        self.twitch_connector = TwitchConnector(self.cfg)

        # TODO: handle token expiration
        super().__init__(
            token=self.twitch_connector.get_oauth_token(),
            prefix=self.command_prefix,
            initial_channels=self.cfg['channel-names']
        )
        asyncio.run(self._init_jack_api())

    async def _init_jack_api(self):
        """Set up for connecting to the Jack API."""
        self.api_url = f'http://{self.cfg["api"]["host"]}:{self.cfg["api"]["port"]}/'
        self.twitch_status_endpoint = urljoin(self.api_url, 'twitch/status/')
        self.twitch_message_endpoint = urljoin(self.api_url, 'twitch/message/')
        self.status = {'mode': self.bot_mode}

        self.logger.info(f'TwitchBot using {self.api_url} as API url. Status:')
        loop = asyncio.get_event_loop()
        api_status = await loop.run_in_executor(None, r.get, self.api_url)
        self.logger.info(api_status.json())

    async def event_ready(self):
        # Make sure we regularly check the API for a new status
        asyncio.create_task(self._check_api_status())
        self.logger.info(f'Logged in as | {self.nick}')

    async def _check_api_status(self):
        """Check the API for a new status continuously."""
        while True:
            try:
                twitch_status = r.get(self.twitch_status_endpoint).json()
                if self.status != twitch_status:
                    self.status = twitch_status
                    self.logger.warning('Changed status!')
                    self.logger.warning(twitch_status)
                    self.logger.warning(twitch_status['channel_names'])
                    await self.join_channels(channels=twitch_status['channel_names'])
                await asyncio.sleep(self.sec_between_check)
            except Exception as ex:
                self.logger.error(ex)
                await asyncio.sleep(self.sec_between_check)
            # time.sleep(self.sec_between_check)

    @commands.command()
    async def hello(self, ctx: commands.Context):
        # Here we have a command hello, we can invoke our command with our prefix and command name
        # e.g ?hello
        # We can also give our commands aliases (different names) to invoke with.

        # Send a hello back!
        # Sending a reply back to the channel is easy... Below is an example.
        self.logger.warning(f'Got a hello command from: {ctx.author.name}')
        await ctx.send(f'/color Green Hello {ctx.author.name}!')
        await self.send_message_to_api(ctx.message, command_type='greeting')

    @commands.command()
    async def talk(self, ctx: commands.Context):
        """Tries to send a message using an avatar."""
        self.logger.warning(ctx)
        self.logger.warning(ctx.message)
        self.logger.warning('---------------------- ')
        self.logger.warning(ctx.message.content)
        self.logger.warning(ctx.message.author)
        self.logger.warning(ctx.author)
        await self.send_message_to_api(ctx.message, command_type='talk')

    @commands.command()
    async def donate(self, ctx: commands.Context):
        """User donation using creator token."""

        self.logger.warning(f'Got a donation request from {ctx.message.author}:')
        self.logger.warning(ctx.message.content)
        try:
            parts = ctx.message.content.split(' ')
            amount = float(parts[1])
            token_name = parts[2]
            self.logger.warning(f'User {ctx.message.author.name} donates {amount} of {token_name}')
            await self.send_message_to_api(ctx.message, command_type='donate')
        except Exception as ex:
            self.logger.error(ex)

    async def event_message(self, message):
        # Messages with echo set to True are messages sent by the bot...
        # For now we just want to ignore them...
        if message.echo:
            return

        self.logger.info(f'[grey]{message.author.name} in {message.author.channel.name} - {message.content}[/grey]')

        if message.content[0] != self.command_prefix:
            await self.send_message_to_api(message)
        # Since we have commands and are overriding the default `event_message`
        # We must let the bot know we want to handle and invoke our commands...
        await self.handle_commands(message)

    def message_to_dict(self, message, command_type=None):
        msg = {
            'channel_name': message.author.channel.name,
            'author_name': message.author.name,
            'author_id': message.author.id,
            'message_text': message.content,
            'is_command': False
        }
        if command_type:
            msg['is_command'] = True
            msg['command_type'] = command_type

        return msg

    async def send_message_to_api(self, message, command_type=None):
        msg_dict = self.message_to_dict(message, command_type=command_type)
        # this function is already async so we don't bother with async request
        try:
            resp = r.post(
                self.twitch_message_endpoint,
                json=msg_dict
            )
            if not resp.status_code == 200:
                self.logger.warning('Failed sending message:')
                self.logger.warning(resp)
                self.logger.warning(resp.status_code)
                self.logger.warning(resp.text)
                self.logger.warning(resp.json())
        except Exception as ex:
            self.logger.error('Failed sending message:')
            self.logger.error(ex)


def main():
    logging_setup(log_level='INFO')
    bot = TwitchBot()
    bot.run()


if __name__ == '__main__':
    main()
