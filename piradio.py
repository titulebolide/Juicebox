import subprocess
import flask
import json
import os

app = flask.Flask(__name__)
radios = json.load(open('radios.json', 'r'))['radios']
p = None

@app.route('/')
def main():
    html = "<html><head></head><body><center>"

    for radio_id, radio in enumerate(radios):
        html += """
<div
    style="cursor:pointer;border: solid 1px black; margin:10px; padding: 10px; border-radius: 5px; text-align: center; width: 300px;"
    onclick="fetch(window.location.origin+'/radio/{}')">
    {}
</div>
""".format(radio_id,radio['name'])

    html += "</center></body></html>"
    return html


@app.route('/radio/<radio_id>')
def select_radio(radio_id):
    global p
    with open('default_radio.txt', 'w') as f:
        f.write(radio_id)
    radio_id = int(radio_id)
    if p is not None:
        p.kill()
    p = subprocess.Popen(['mplayer', radios[radio_id]['url']])
    return ""


if os.path.isfile('default_radio.txt'):
    with open('default_radio.txt', 'r') as f:
        radio_id = f.readline()
        print(radio_id)
    try:
        radio_id = int(radio_id)
    except ValueError:
        radio_id = 0
    if radio_id>=len(radios) and radio_id<0:
        radio_id = 0
else:
    radio_id=0
select_radio(str(radio_id))



if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000)
