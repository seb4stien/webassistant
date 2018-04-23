# stdlib
import os
import re
import requests
import time

# dependencies
from flask import Flask, request
app = Flask(__name__)

# local
from myconfig import LOG_PATH, TTS_URL, sensors, playlist

#import beets.library

#lib = beets.library.Library("/root/.config/beets/newlib.db")


def parse_sensor(line):
    res = {
        'temp': None,
        'age': None
    }

    m = re.match(".*temp: (-?\d+\.\d+)", line)

    if m:
        res['temp'] = m.groups()[0].replace(".", ",")

    m = re.match(".*ts: (\d+)", line)
    if m:
        ts = int(m.groups()[0])
        res['age'] = int(time.time()) - ts

    return res


def get_temp(room):

    if room not in sensors:
        return ("bad sensor", "n/a", "bad sensor")

    comment = sensors[room]["comment"]

    log_filename = "%s/%s.log" % (LOG_PATH, room)

    if not os.path.exists(log_filename):
        return (0, -1, "Unknown sensor")

    with open(log_filename, "r") as fh:
        last_line = fh.readlines()[-1]
        sensor_dict = parse_sensor(last_line)
        temp = sensor_dict['temp']
        age = sensor_dict['age']

    return (temp, age, comment)


def say(msg):
    res = requests.get("%s/say/?lang=fr&text=%s" % (TTS_URL, msg))
    return res.status_code

def pause():
    res = requests.get("%s/pause" % TTS_URL)
    return res.status_code

@app.route("/webhooks/jukebox/")
def jukebox():
    command = request.args.get('command')

    if not command:
        return "Nothing"

    command = command.lower()

    if command == "pause":
        pause()

    if command.startswith("lire"):
        query = command[5:]
        playlist = lib.items(query)
        if len(playlist):
            songpath = playlist[0].path
            res = requests.get("%s/play/%s" % (TTS_URL, songpath))
            return res.status_code

    return command


@app.route("/webhooks/temp/<string:room>")
def temp(room):
    (temp, age, comment) = get_temp(room)

    if age > -1:
        text = "Il y a %s secondes il faisait %s degrés %s" % (age, temp, comment)
    else:
        text = comment

    res = say(text)

    return "Temp: %s Message: %s Status: %s" % (temp, text, res)


def fbx_remote(key):
    res = requests.get("http://hd1.freebox.fr/pub/remote_control?code=%s&key=%s" % (FREEBOX_KEY, key))
    return res.status_code


@app.route("/webhooks/tv/")
def tv():
    command = request.args.get('command').lower()
    if not command:
        return "Nothing"

    # http://tutoriels.domotique-store.fr/content/51/90/fr/api-de-la-freebox-tv-_-player-v5-_-v6-via-requ%C3%AAtes-http.html
    mymap = {
            'un': 1,
            'deux': 2,
            'de': 2,
            'trois': 3,
            'quatre': 4,
            'cinq': 5,
            'six': 6,
            'sept': 7,
            'huit': 8,
            'neuf': 9,
            'zero': 0,
            'green': 'green',
            'lecture': 'play',
            'pause': 'play',
            'Bose': 'play',
            'play': 'play',
            'programme': 'epg',
            'plus fort': 'vol_inc',
            'moins fort': 'vol_dec',
            'sourdine': 'mute',
            'mute': 'mute',
            'silence': 'mute',
            'éteindre': 'power',
            'stop': 'power',
            'allumer': 'power',
            'swap': 'swap',
            'home': 'home',
            'accueil': 'home',
            'tv': 'tv',
            'recul': 'bwd',
            'recule': 'bwd',
            'avance': 'fwd',
            'précédent': 'prev',
            'suivant': 'next',
            'ok': 'ok',
            'menu': 'green',
            'haut': 'up',
            'bas': 'down',
            'gauche': 'left',
            'droite': 'right'
    }

    if command.isdigit():
        real_command = command
    else:
        real_command = mymap.get(command, None)

    if real_command == "epg":
        fbx_remote("green")
        time.sleep(1)
        fbx_remote("down")
        time.sleep(1)
        fbx_remote("right")
        time.sleep(1)
        fbx_remote("ok")
        time.sleep(1)
        fbx_remote(1)
    elif real_command:
        res = fbx_remote(real_command)
        return "Done: %s" % real_command
    else:
        return "Command not found: %s" % command


if __name__ == "__main__":
    app.run()
