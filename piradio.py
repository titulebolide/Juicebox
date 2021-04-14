import subprocess
import flask

app = flask.Flask(__name__)

p = None

@app.route('/start/')
def start():
    global p
    p = subprocess.Popen(['mplayer', 'http://streaming.radio.rtl.fr/rtl-1-44-128'])
    return ""

@app.route('/stop/')
def stop():
    global p
    if p is not None:
        p.kill()
        p = None
    return ""

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000)
