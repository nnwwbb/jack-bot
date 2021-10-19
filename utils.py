import logging
import yaml
from rich.logging import RichHandler
from rich.console import Console
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer


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


def print_handler(address, *args):
    print(f"{address}: {args}")


def default_handler(address, *args):
    print(f"DEFAULT {address}: {args}")


def run_osc_listener(cfg):
    """Run a simple OSC server that listens to incoming messages for debugging."""
    dispatcher = Dispatcher()
    dispatcher.map("/something/*", print_handler)
    dispatcher.set_default_handler(default_handler)

    server = BlockingOSCUDPServer(
        (cfg['listener']['osc-ip'], cfg['listener']['osc-port']),
        dispatcher
    )
    server.serve_forever()  # Blocks forever
