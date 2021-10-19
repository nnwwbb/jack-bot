import os
import logging
from typing import Optional, List
from fastapi import FastAPI, APIRouter, Query
from utils import load_config, logging_setup
from api.api_service import APIService
from api.api_model import TwitchBotStatus, TwitchMessage, UserAuth, RallyInfo


cfg = load_config(os.environ.get('CONFIG_FILE', 'configs/default.yml'))
logging_setup(log_level=cfg['log-level'])
logger = logging.getLogger(__name__)
api_service = APIService(cfg=cfg)
router = APIRouter()


@router.get('/')
def read_root():
    return {'status': 'Ready to chat!'}


@router.get('/twitch/status', response_model=TwitchBotStatus)
def get_twitch_bot_status():
    return api_service.get_twitch_bot_status()


@router.patch('/twitch/status')
def set_twitch_bot_status(status: TwitchBotStatus):
    """Set config status for the API and twitch bot."""
    api_service.set_twitch_bot_status(status)


@router.post('/twitch/message')
async def new_twitch_message(message: TwitchMessage):
    """Accepts new Twitch messages from the bot."""
    await api_service.handle_twitch_message(message)


@router.get('/twitch/get_messages')
def get_messages(seconds_history: int = None, channel_names: Optional[List[str]] = Query(None)):
    res = api_service.get_messages(
        seconds_history=seconds_history,
        channel_names=channel_names
    )
    return res


@router.post('/user/auth')
def post_user_auth(info: UserAuth):
    api_service.add_user_info(info)


@router.get('/user/all_infos')
def get_user_infos():
    return api_service.get_account_infos()


@router.post('/rally/tokens')
def post_rally_token(info: RallyInfo):
    api_service.set_rally_tokens(info)


@router.get('/rally/nft-templates')
def get_nft_templates():
    return api_service.get_nft_templates()


@router.get('/rally/all-nfts')
def get_all_nfts():
    return api_service.get_all_nfts()


def main():
    # initialize the application
    if 'nginx-settings' in cfg:
        app = FastAPI(
            title='Jack Bot API',
            description='Something something moon',
            version='0.1',
            root_path=cfg['nginx-settings']['root_path']
        )
    else:
        app = FastAPI(
            title='Jack Bot API',
            description='Something something moon',
            version='0.1'
        )

    app.include_router(router)
    return app


if __name__ == '__main__':
    main()
