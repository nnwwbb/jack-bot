# JackBot (WIP)
A Python bot for controlling Jack avatars in Unreal, using data from the Twitch and Rally APIs.


## Setup
### Dev
Start a virtualenv using python 3.8 or 3.9 (older versions not tested), and install dependencies:
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

Put your login info for the dashboard in `tokens/dashboard.yml`:
```YAML
users:
  - name: username
    password: password
```


Open three terminal sessions. Run these commands:
```bash
python3 main.py -c configs/api.yml
python3 main.py -c configs/twitch-bot.yml
python3 main.py -c configs/dashboard.yml
```

This will open the API on port 6660, and a dashboard on port 8501.

### Docker
Make sure you have `docker` and `docker-compose` installed and working.
Now, build the docker image:
```bash
docker build -t jack-bot -f docker/Dockerfile .
```
