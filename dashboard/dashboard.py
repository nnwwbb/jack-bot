import os
import sys
import time
import streamlit as st
import pandas as pd
sys.path.insert(0, os.getcwd())  # so we can import from utils
from utils import load_config, logging_setup  # noqa
from connectors.jack_connector import JackConnector  # noqa


def get_messages(channel_name, seconds_history=None):
    return st.session_state.api.get_twitch_messages(
        seconds_history=60,
        channel_names=[channel_name]
    )


def remove_dups(large_l):
    seen = set()
    new_l = []
    for d in large_l:
        t = tuple(d.items())
        if t not in seen:
            seen.add(t)
            new_l.append(d)
    return new_l


def show_twitch_chat(current_channel_name):
    seconds_history = 120
    stopped = st.button('stop monitoring.')
    if st.button('start monitoring.'):
        st.experimental_rerun()
    messages = get_messages(current_channel_name, seconds_history=seconds_history)
    if not stopped:
        chat_placeholder = st.empty()
        new_messages = get_messages(current_channel_name, seconds_history=seconds_history)

        messages = remove_dups(messages + new_messages)
        df = pd.DataFrame(messages)
        if len(messages) > 0:
            chat_placeholder.table(
                df[['datetime', 'author_name', 'message_text']].iloc[-10:][::-1]
            )
        time.sleep(1)
        st.experimental_rerun()


def show_main_dash():
    st.sidebar.write('logged in!')
    st.session_state.twitch_status = st.session_state.api.get_twitch_bot_status()
    current_channel_name = st.sidebar.selectbox(
        'Please select a channel', st.session_state.twitch_status['channel_names']
    )

    show_twitch_chat(current_channel_name)


def check_credentials():
    if st.session_state.logged_in:
        return True
    username = st.sidebar.text_input('username')
    password = st.sidebar.text_input('password')

    if len(username) > 0 and len(password) > 0:
        for user in st.session_state.cfg['dashboard']['users']:
            if username == user['name'] and password == user['password']:
                return True

        st.write('username/password incorrect')

    return False


def run_dash():
    cfg = load_config(os.environ['CONFIG_FILE'])
    logging_setup(log_level=cfg['log-level'])
    st.session_state.cfg = cfg
    st.session_state.api = JackConnector(cfg)
    st.set_page_config(layout="wide")
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    # st.write(cfg)
    if check_credentials():
        show_main_dash()


if __name__ == '__main__':
    # https://share.streamlit.io/streamlit/release-demos/0.84/0.84/streamlit_app.py?page=headliner
    # https://share.streamlit.io/daniellewisdl/streamlit-cheat-sheet/app.py
    run_dash()
