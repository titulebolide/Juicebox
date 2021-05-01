import flask
import json
import os
import alsaaudio
import mpv
import threading
import requests

app = flask.Flask(__name__, static_folder = '../gui/build/', static_url_path="/")

if os.environ.get('PIRADIO_DEV') is not None:
    from flask_cors import CORS
    CORS(app)

config = json.load(open('../config.json', 'r'))
player = mpv.MPV(ytdl=True, video='no')
selected_radio = 0
stopped = False
mixer = alsaaudio.Mixer(alsaaudio.mixers()[0])
playYT = False
YTHandlingThread = None
playingTitle = ""


@app.route('/')
def index():
    return flask.redirect('/index.html', 301)


@app.route("/state/")
def state():
    return flask.jsonify({
        'title':playingTitle,
        'volume':getvolume(),
        'playing': not stopped,
        'radioId': -1 if playYT else selected_radio,
    })


@app.route("/radios/")
def getradios():
    return flask.jsonify({'radios':config['radios']})


@app.route('/radio/<radio_id>/')
def select_radio(radio_id):
    global player, selected_radio, stopped, playingTitle
    stopped = False
    with open('default_radio.txt', 'w') as f:
        f.write(radio_id)
    radio_id = int(radio_id)
    playingTitle = config['radios'][radio_id]['name']
    selected_radio = radio_id
    stopPlaying()
    player.play(config['radios'][radio_id]['url'])
    return "", 200


@app.route('/yt/')
def youtube():
    global YTHandlingThread, playingTitle
    url = flask.request.args.get('url')
    stopPlaying()
    ytid = url.split('/')[-1].split('=')[-1]
    playingTitle = getYTTitle(ytid)
    YTHandlingThread = threading.Thread(target=handleYT, args=(ytid,))
    YTHandlingThread.start()
    return "", 200


@app.route('/stop/')
def stop():
    stopPlaying()
    return "", 200


@app.route('/volumeup/')
def volumeup():
    setvolume(getvolume()+3)
    return "", 200


@app.route('/volumedown/')
def volumedown():
    setvolume(getvolume()-3)
    return "", 200


def handleYT(ytid):
    global playYT, playingTitle
    playYT = True
    firstVideo = True
    previousYTId = None
    while playYT:
        if not firstVideo:
            playingTitle = getYTTitle(ytid)
        player.stop()
        player.play("https://www.youtube.com/watch?v="+ytid)
        player.wait_until_playing()
        player.wait_for_playback()
        items = requests.get(
            "https://www.googleapis.com/youtube/v3/search?part=snippet&relatedToVideoId={}&type=video&key={}".format(
                ytid, config['YT_API_KEY']
            )
        ).json()["items"]

        tempytid = items[0]['id']['videoId']
        if not firstVideo:
            if tempYTId == previousYTId:
                tempytid = items[1]['id']['videoId']
        previousYTId = ytid
        ytid = tempYTId
        firstVideo = False
    return


def stopPlaying():
    global playYT, YTHandlingThread, stopped
    if playYT:
        playYT = False
        player.stop()
        YTHandlingThread.join()
        YTHandlingThread = None
    else:
        player.stop()
    stopped = True
    return


def getvolume():
    global mixer
    return int(mixer.getvolume()[0])


def setvolume(vol):
    global mixer
    mixer.setvolume(max(0,min(100,vol)))


def getYTTitle(ytid):
    return requests.get(
        "https://www.googleapis.com/youtube/v3/videos?part=snippet&id={}&key={}".format(
            ytid, config['YT_API_KEY']
        )
    ).json()['items'][0]['snippet']['title']


if os.path.isfile('default_radio.txt'):
    with open('default_radio.txt', 'r') as f:
        selected_radio = f.readline()
    try:
        selected_radio = int(selected_radio)
    except ValueError:
        selected_radio = 0
    if selected_radio>=len(config['radios']) and selected_radio<0:
        selected_radio = 0
else:
    selected_radio=0
if not stopped:
    select_radio(str(selected_radio))



if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000)
