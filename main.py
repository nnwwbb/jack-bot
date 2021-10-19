import click
import uvicorn
import logging
import os
import subprocess
from utils import load_config, logging_setup, run_osc_listener
from bots.twitch_bot import external_run_bot


@click.command()
@click.option('-c', '--config',
              default='config/api-playground.yml',
              help='Config file to be used. Mode specific.')
def main(config):
    os.environ['CONFIG_FILE'] = config
    cfg = load_config(config)
    logging_setup(cfg['log-level'])
    logger = logging.getLogger(__name__)

    if cfg['mode'] == 'run-api':
        # launch the API
        uvicorn.run(
            "api.api:main",
            host=cfg['api']['host'],
            port=cfg['api']['port'],
            reload_delay=1.0,
            reload=cfg['api']['reload'],
            factory=True,
            log_config=None
        )
    elif cfg['mode'] == 'run-twitch-bot':
        # run the bot using multiprocess for token expiration checking
        external_run_bot(cfg)
    elif cfg['mode'] == 'run-dashboard':
        # run the dash as a subprocess so the session state works
        subprocess.run(["streamlit", "run", "dashboard/dashboard.py"])
    elif cfg['mode'] == 'run-osc-listener':
        run_osc_listener(cfg)
    else:
        logger.error(f"Unrecognized mode: {cfg['mode']}")


if __name__ == '__main__':
    main()
