import logging
import yaml
from rich.logging import RichHandler
from rich.console import Console


def logging_setup(log_level="DEBUG"):
    console = Console(force_terminal=True)
    logging.basicConfig(
        level=log_level,
        format="%(funcName)15s() - %(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, markup=True, console=console)]
    )


def load_config(cfg_path):
    with open(cfg_path, 'r') as file:
        data = yaml.safe_load(file)
    if 'tokens' in data:
        for cred_name, cred_path in data['tokens'].items():
            with open(cred_path, 'r') as file:
                data[cred_name] = yaml.safe_load(file)

    return data
