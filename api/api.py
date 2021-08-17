import os
import logging
from typing import Optional, List
from fastapi import FastAPI, APIRouter, Query
from utils import load_config, logging_setup
from api.api_service import APIService
from api.api_model import TwitchBotStatus, TwitchMessage


cfg = load_config(os.environ.get('CONFIG_FILE', 'configs/default.yml'))
logging_setup(log_level=cfg['log-level'])
logger = logging.getLogger(__name__)
api_service = APIService(cfg=cfg)
router = APIRouter()


@router.get('/')
def read_root():
    return {'status': 'Ready to chat!'}


@router.get('/items/{item_id}')
def read_item(item_id: int, q: Optional[str] = None):
    return {'item_id': item_id, 'q': q}


@router.get('/twitch/status', response_model=TwitchBotStatus)
def get_twitch_bot_status():
    return api_service.get_twitch_bot_status()


@router.patch('/twitch/status')
def set_twitch_bot_status(status: TwitchBotStatus):
    api_service.set_twitch_bot_status(status)


@router.post('/twitch/message')
def new_twitch_message(message: TwitchMessage):
    """Accepts new Twitch messages from the bot."""
    api_service.store_message(message)


@router.get('/twitch/get_messages')
def get_messages(seconds_history: int = None, channel_names: Optional[List[str]] = Query(None)):
    res = api_service.get_messages(
        seconds_history=seconds_history,
        channel_names=channel_names
    )
    return res


def main():
    # initialize the application
    if 'nginx-settings' in cfg:
        app = FastAPI(
            title='Jack Bot API',
            description='Something something moon',
            version='0.1',
            root_path=cfg['nginx-settings']['root_path'],
            # docs_url=cfg['nginx-settings']['docs_url'],
            # redoc_url=cfg['nginx-settings']['redoc_url'],
            # openapi_url=cfg['nginx-settings']['openapi_url']
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
