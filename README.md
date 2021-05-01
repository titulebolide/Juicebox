# Juicebox
Turn your raspberry pi (or whatever linux server using ALSA for audio) into a jukebox, with a web interface.

## Install

Install mpv and mpv devels. Then run
```
cd api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Build the frontend with yarn
```
cd gui
yarn
yarn build
```

Create the file `config.json` based on `config.sample.json`.

Setup a service with unicorn, replacing PIRADIO_FOLDER by the actual folder and PIRADIO_PORT by the desired port:

```systemd
[Unit]
Description=piradio daemon
After=network.target

[Service]
Type=Simple
Restart=always
RestartSec=1
WorkingDirectory=PIRADIO_FOLDER/api
ExecStart=PIRADIO_FOLDER/api/venv/bin/gunicorn --workers=1 --threads=1 --bind 0.0.0.0:PIRADIO_PORT wsgi


[Install]
WantedBy=multi-user.target
```
