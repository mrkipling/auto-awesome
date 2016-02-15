import requests

from flask import Flask, render_template, jsonify
from flask_httpauth import HTTPBasicAuth
from soco import SoCo
from phue import Bridge
from vars import *

app = Flask(__name__)
app.debug = False
auth = HTTPBasicAuth()


@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None


@app.route("/")
def index():
    return render_template('index.html', your_name=YOUR_NAME)


def get_sonos_playlist(sonos, title):
    playlists = sonos.get_sonos_playlists()
    for playlist in playlists:
        if playlist.title == title:
            return playlist
    return None


@app.route("/automation/bttn/sexy-time/")
@auth.login_required
def sexy_time():
    # connect to the Sonos
    sonos = SoCo(SONOS_IP)

    # connect to Philips Hue Bridge
    hue = Bridge(ip=HUE_IP,
                 username=HUE_USERNAME)

    # get queue
    queue = sonos.get_queue()

    # if we:
    # * already have a queue
    # * music is playing
    # * we are already playing a queue that begins with "Let's Get It On"
    # ...then skip to the next track

    if len(queue) > 0 and \
       sonos.get_current_transport_info()['current_transport_state'] == "PLAYING" and \
       queue[0].title == SEXY_TIME_FIRST_TRACK:
        sonos.next()

    # else, intitiate a fresh Sexy Time

    else:
        # clear Sonos queue
        sonos.clear_queue()

        # turn off shuffle and repeat
        sonos.play_mode = 'NORMAL'

        # set volume
        sonos.volume = 45

        # play Sexy Time playlist

        playlist = get_sonos_playlist(sonos, SEXY_TIME_PLAYLIST_NAME)

        if playlist:
            sonos.add_to_queue(playlist)
            sonos.play()

        # dim the lights (bri out of 254) over the pre-defined amount of time

        command = {
            'transitiontime': (SEXY_TIME_DIMMER_SECONDS * 10),
            'on': True,
            'bri': SEXY_TIME_DIMMER_BRIGHTNESS
        }

        hue.set_light(SEXY_TIME_LIGHTS, command)

    return jsonify(status="success")


@app.route("/automation/bttn/party/")
@auth.login_required
def party():
    # connect to the Sonos
    sonos = SoCo(SONOS_IP)

    # get queue
    queue = sonos.get_queue()

    # if we:
    # * already have a queue
    # * music is playing
    # ...then skip to the next track

    if len(queue) > 0 and sonos.get_current_transport_info()['current_transport_state'] == "PLAYING":
        sonos.next()

    # else, intitiate a fresh Party Time

    else:
        # clear Sonos queue
        sonos.clear_queue()

        # turn on shuffle, turn off repeat
        sonos.play_mode = 'SHUFFLE_NOREPEAT'

        # set volume
        sonos.volume = 45

        # play Party playlist

        playlist = get_sonos_playlist(sonos, PARTY_TIME_PLAYLIST_NAME)

        if playlist:
            sonos.add_to_queue(playlist)
            sonos.play()

    return jsonify(status="success")


@app.route("/automation/arriving-home/")
@auth.login_required
def arriving_home():
    # connect to Philips Hue Bridge
    hue = Bridge(ip=HUE_IP,
                 username=HUE_USERNAME)

    # set the lights to appropriate brightness over appropriate time

    command = {
        'transitiontime': (ARRIVING_HOME_DIMMER_SECONDS * 10),
        'on': True,
        'bri': ARRIVING_HOME_DIMMER_BRIGHTNESS
    }

    hue.set_light(ARRIVING_HOME_LIGHTS, command)

    # connect to the Sonos
    sonos = SoCo(SONOS_IP)

    # clear the queue
    sonos.clear_queue()

    # set volume
    sonos.volume = ARRIVING_HOME_VOLUME

    # play Arriving Home playlist
    playlist = get_sonos_playlist(sonos, ARRIVING_HOME_PLAYLIST_NAME)

    if playlist:
        sonos.add_to_queue(playlist)

        # turn on shuffle, turn off repeat
        sonos.play_mode = 'SHUFFLE_NOREPEAT'

        # play
        sonos.play()

        # we're in shuffle mode, but the first track is always the same
        sonos.next()

    return jsonify(status="success")


@app.route("/automation/stop/")
@auth.login_required
def bttn_stop():
    # connect to the Sonos
    sonos = SoCo(SONOS_IP)

    # connect to Philips Hue Bridge
    hue = Bridge(ip=HUE_IP,
                 username=HUE_USERNAME)

    # stop the Sonos and reset to sensible defaults

    queue = sonos.get_queue()
    sonos.clear_queue()
    sonos.volume = STOP_VOLUME
    sonos.play_mode = 'NORMAL'
    sonos.stop()

    # set the lights back to a sensible default

    command = {
        'transitiontime': (STOP_DIMMER_SECONDS * 10),
        'on': True,
        'bri': STOP_DIMMER_BRIGHTNESS
    }

    hue.set_light(STOP_LIGHTS, command)

    return jsonify(status="success")


if (app.debug):
    from werkzeug.debug import DebuggedApplication
    app.wsgi_app = DebuggedApplication(app.wsgi_app, True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=9000)
