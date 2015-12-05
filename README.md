# Home automation endpoints

This is a collection of endpoints that will be useful if you own the following products:

* A Sonos speaker
* Philips Hue lightbulbs
* A bttn (optional, but so much more awesome with one; see the bttn section below)
* An Android phone with tasker (optional, only required for the 'arriving home' endpoint)

## Instructions

You need to have a home server that can serve these endpoints. I use nginx and have included `server_uwsgi.ini` to help with this if you wish to go down this route.

This project uses Flask, amongst other libraries. You can find all requirements in `requirements.txt` which you can install using `pip`.

There are plenty of good tutorials online about the above so I will skip straight to how to set up this project once you have it being served by a webserver.

## bttn

The bttn is a wifi-connected button. You can make it send a GET request when you press it. This is why having these endpoints is so awesome; you can set up a bookmark widget on your phone, or you can have a big red button attached to your wall that does the same thing. When coupled with a "DO NO PRESS" plaque (£2.99 on eBay) underneath the bttn you can see why it is the better option (especially for the "Sexy Time" endpoint).

You can find more details here:
https://bt.tn/

## Filling in the details

I am going to assume that you have a Sonos speaker and a Philips Hue lightbulb system (Lux or not, I don't think it makes a difference).

We are using basic HTTP authentication for the endpoints so that people can't just randomly fuck with your lights and music. Open up `server.py` and fill in a username and password in the `users` dict.

* `SONOS_IP` is the IP address of your Sonos speaker
* `HUE_IP` is the IP address of your Hue bridge.
* `HUE_USERNAME` is your Hue username. This URL explains how to generate one: http://www.developers.meethue.com/documentation/getting-started

Okay, now onto the endpoints.

## Sexy Time

When activated the Sexy Time endpoint plays a playlist on your Sonos system (the name is defined in `SEXY_TIME_PLAYLIST_NAME`, default "Sexy Time"). It works best with the bttn because it's just cooler. When activated it plays the playlist on your Sonos system and dims the lights to `SEXY_TIME_DIMMER_BRIGHTNESS` (default: 125, about 20%) over `SEXY_TIME_DIMMER_SECONDS` (default: 10 seonds).

It also skips tracks when activated again. However we need to know the name of the first track in the playlist in order to do this as we just add the playlist to the queue and I don't think that you can get the playlist name from this. This is `SEXY_TIME_FIRST_TRACK`.

## Party Time

This just affects your Sonos, not your lights. It plays `PARTY_TIME_PLAYLIST_NAME` in shuffle mode (and skips the first track, otherwise we always end up with the same first track). When the endpoint is activated again it skips to the next track.

As you can imagine, a big red party button on your wall is better than visiting a URL.

## Arriving Home

This requires Tasker on Android. You need to set it up so that:

* When you connect to your WiFi network
* Between the hours of 16:00 and 22:00 (suggested)
* On a weekday (again, just a suggestion; whatever, works for you)

It sends a GET request to to this endpoint (with HTTP auth; I find it easier to include in the URL, like `http://username:password@server/automation/arriving-home/`).

It turns the lights on to 80% and plays `ARRIVING_HOME_PLAYLIST_NAME` at a sensible (quiet) volume to provide a nice "arriving home" experience. I suggest filling `ARRIVING_HOME_PLAYLIST_NAME` with chilled music. Again, it plays in shuffle mode and skips the first track; it's nice to have a different track every day when you arrive home. Then it just keeps playing until you turn it off.

Imagine... when you arrive home the lights are on at a nice level and soft music is playing. I have this set up already and can confirm that it is almost magical :)

## Stop

I've also created a "stop" endpoint that brings everything to an end. It does the following:

* Clears the Sonos queue
* Sets the volume to a sensible level (45%)
* Sets the play mode to 'normal' (no shuffle or repeat)
* Stops all playback
* Sets the lights to 80% over 3 seconds (nobody likes a jarring transition)

I've set this up as an icon (Chrome bookmark widget) on my phone.

## Notes

* The endpoints all return JSON, `{'status': 'success'}`.
* In order to make this work you need to initiate a venv (Google it).
* When in your activated venv you need to run `pip install -r requirements.txt` in order to install all of the libraries that this project uses.
* If you want to test this out without setting up a proper web server you can just run `python server.py`. It runs on port 9000 by default.
* If you have any questions then feel free to ask.
