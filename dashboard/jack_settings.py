import os
import sys
import logging
import streamlit as st
sys.path.insert(0, os.getcwd())  # so we can import from utils
from utils import load_config, logging_setup  # noqa
from connectors.jack_connector import JackConnector  # noqa

logger = logging.getLogger(__name__)


def show_main_settings():
    st.write(f'Token: {st.session_state.query_params}')
    st.write('Getting user info, please wait...')


def run_dash():
    cfg = load_config(os.environ['CONFIG_FILE'])
    logging_setup(service_name='jack-settings', log_level=cfg['log-level'])
    logger.info(query_params := st.experimental_get_query_params())
    st.session_state.cfg = cfg
    st.session_state.api = JackConnector(cfg)
    st.session_state.query_params = query_params

    if 'token' in query_params:
        show_main_settings()
    else:
        st.write('Malformed URL, missing token.')
        st.write(query_params)


if __name__ == '__main__':
    run_dash()
