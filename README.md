# JackBot (WIP)
A Python bot for controlling Jack avatars in Unreal, using data from the Twitch and Rally APIs.


## Setup
Start a virtualenv and install dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip3 install -U pip wheel
pip3 install -r requirements.txt
```


Put your Twitch tokens in `tokens/twitch.yml`:
```YAML
twitch_ID: "1234abc"
twitch_secret": "456def"
twitch_admins:
  - "your_username"
```


Open two terminals. Run these commands:
```bash
python3 main.py -c configs/api.yml
python3 main.py -c configs/twitch-bot.yml
```
