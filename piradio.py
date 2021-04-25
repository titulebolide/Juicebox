import flask
import json
import os
import alsaaudio
import mpv
import threading
import requests
import config

app = flask.Flask(__name__, static_folder='static')
radios = json.load(open('radios.json', 'r'))['radios']
player = mpv.MPV(ytdl=True, video='no')
selected_radio = 0
stopped = False
mixer = alsaaudio.Mixer(alsaaudio.mixers()[0])
playYT = False
YTHandlingThread = None

@app.route('/')
def frontend():
    global selected_radio, stopped
    html = """
<html>
<head>
    <link rel="apple-touch-icon" sizes="57x57" href="/static/favicon/apple-icon-57x57.png">
    <link rel="apple-touch-icon" sizes="60x60" href="/static/favicon/apple-icon-60x60.png">
    <link rel="apple-touch-icon" sizes="72x72" href="/static/favicon/apple-icon-72x72.png">
    <link rel="apple-touch-icon" sizes="76x76" href="/static/favicon/apple-icon-76x76.png">
    <link rel="apple-touch-icon" sizes="114x114" href="/static/favicon/apple-icon-114x114.png">
    <link rel="apple-touch-icon" sizes="120x120" href="/static/favicon/apple-icon-120x120.png">
    <link rel="apple-touch-icon" sizes="144x144" href="/static/favicon/apple-icon-144x144.png">
    <link rel="apple-touch-icon" sizes="152x152" href="/static/favicon/apple-icon-152x152.png">
    <link rel="apple-touch-icon" sizes="180x180" href="/static/favicon/apple-icon-180x180.png">
    <link rel="icon" type="image/png" sizes="192x192"  href="/static/favicon/android-icon-192x192.png">
    <link rel="icon" type="image/png" sizes="32x32" href="/static/favicon/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="96x96" href="/static/favicon/favicon-96x96.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/static/favicon/favicon-16x16.png">
    <link rel="manifest" href="/static/manifest.json">
    <meta name="msapplication-TileColor" content="#ffffff">
    <meta name="msapplication-TileImage" content="/static/ms-icon-144x144.png">
    <meta name="theme-color" content="#ffffff">
    <meta charset="UTF-8"/><meta name="viewport" content="initial-scale = 1.0,maximum-scale = 1.0" />
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
</head>
<body>
"""
    html += """<center style="width:100vw"/><div style="width:50%;min-width:350px;">"""

    html += """
<div style='display:flex;'>
    <div style='flex:1'>
        <center>
            <a
                class = "btn btn-outline-secondary"
                style = "width:100%;margin-top:10px;font-weight:bold;"
                href="/volumedown/">
                -
            </a>
        </center>
    </div>
    <div style='padding-top:18px;flex:3;'>
        <center>
            Volume : {} %
        </center>
    </div>
    <div style='flex:1'>
        <center>
            <a
                class = "btn btn-outline-secondary"
                style = "width:100%;margin-top:10px;font-weight:bold;"
                href="/volumeup/">
                +
            </a>
        </center>
    </div>
</div>
""".format(getvolume())

    if stopped:
        btn_type='success'
        href='/radio/'+str(selected_radio)
        text='Play'
    else:
        btn_type='danger'
        href='/stop'
        text='Pause'

    html += """
<div>
    <a
        class = "btn btn-outline-{}"
        style = "width:100%;margin-top:10px;"
        href="{}">
        {}
    </a>
</div>
""".format(btn_type, href, text)

    html += """
<div style='margin-top:20px;margin-bottom:10px'>
    <form action="/yt" style="margin:0">
        <div style='display:flex'>
            <input style='flex:4; margin-right:20px;' type="text" id="url" name="url" placeholder='Youtube Video URL'>
            <button class="btn btn-outline-primary" style='flex:1' type='submit'>Play</button>
        </div>
    </form>
</div>
"""


    for radio_id, radio in enumerate(radios):
        additionnal_style = ""
        if radio_id == selected_radio:
            additionnal_style = "font-weight:bold; color:red"
        html += """
<div>
    <a
        class = "btn btn-outline-secondary"
        style = "width:100%;margin-top:10px;{}"
        href="/radio/{}">
        {}
    </a>
</div>
""".format(additionnal_style, radio_id, radio['name'])

    html += "</div></center></body></html>"
    return html


@app.route('/radio/<radio_id>')
def select_radio(radio_id):
    global player, selected_radio,stopped
    stopped = False
    with open('default_radio.txt', 'w') as f:
        f.write(radio_id)
    radio_id = int(radio_id)
    selected_radio = radio_id
    stopPlaying()
    player.play(radios[radio_id]['url'])
    return frontend()

@app.route('/yt/')
def youtube():
    global YTHandlingThread
    url = flask.request.args.get('url')
    stopPlaying()
    ytid = url.split('/')[-1].split('=')[-1]
    YTHandlingThread = threading.Thread(target=handleYT, args=(ytid,))
    YTHandlingThread.start()
    return frontend()

@app.route('/stop/')
def stop():
    global player, stopped
    stopPlaying()
    stopped = True
    return frontend()

@app.route('/volumeup/')
def volumeup():
    setvolume(getvolume()+3)
    return frontend()

@app.route('/volumedown/')
def volumedown():
    setvolume(getvolume()-3)
    return frontend()

def handleYT(ytid):
    global playYT
    playYT = True
    while playYT:
        player.stop()
        player.play("https://www.youtube.com/watch?v="+ytid)
        player.wait_until_playing()
        player.wait_for_playback()
        ytid = requests.get(
            "https://www.googleapis.com/youtube/v3/search?part=snippet&relatedToVideoId={}&type=video&key={}".format(
                ytid, config.API_KEY
            )
        ).json()["items"][0]['id']['videoId']
    return

def stopPlaying():
    global playYT, YTHandlingThread
    if playYT:
        playYT = False
        player.stop()
        YTHandlingThread.join()
        YTHandlingThread = None
    else:
        player.stop()
    return

def getvolume():
    global mixer
    return int(mixer.getvolume()[0])

def setvolume(vol):
    global mixer
    mixer.setvolume(max(0,min(100,vol)))

if os.path.isfile('default_radio.txt'):
    with open('default_radio.txt', 'r') as f:
        selected_radio = f.readline()
    try:
        selected_radio = int(selected_radio)
    except ValueError:
        selected_radio = 0
    if selected_radio>=len(radios) and selected_radio<0:
        selected_radio = 0
else:
    selected_radio=0
if not stopped:
    select_radio(str(selected_radio))


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000)
