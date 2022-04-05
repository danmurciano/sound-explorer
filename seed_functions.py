from flask import jsonify
from base_functions import makeGetRequest, makePostRequest
import requests
import logging
from iteration_utilities import unique_everseen

SPOTIFY = "https://api.spotify.com/v1"


def searchTrack(app, session, data):
    url = f"{SPOTIFY}/search"
    params = {"type": "track", "q": data["q"], "limit": 10}
    response = makeGetRequest(app, session, url, params)
    response_json = jsonify(tracks=response["tracks"]["items"])
    return (response_json, 200)



def seedPlaylist(app, session, data):
    user = "user" in session
    id = data["id"]
    popularity = data["popularity"]
    limit = int(data["limit"])
    url1 = f"{SPOTIFY}/audio-features/{id}"
    url2 = f"{SPOTIFY}/recommendations"
    features = makeGetRequest(app, session, url1)
    energy = features["energy"]

    if popularity == "obscure":
        params = {"seed_tracks": id, "target_energy": energy, "target_popularity": 0, "limit": 100}
        tracks = makeGetRequest(app, session, url2, params)
        tracks_sorted = sorted(tracks["tracks"], key=lambda x: x["popularity"])
        obscure = tracks_sorted
        for track in tracks_sorted[0:4]:
            params = {"seed_tracks": track["id"], "target_energy": energy, "target_popularity": 0, "limit": 100}
            tracks = makeGetRequest(app, session, url2, params)
            tracks = tracks["tracks"]
            obscure.extend(tracks)
        obscure = list(unique_everseen(obscure))
        obscure = sorted(obscure, key=lambda x: x["popularity"])
        response_json = jsonify(tracks=obscure[:limit:], user=user)

    else:
        if popularity == "any":
            params = {"seed_tracks": id, "target_energy": energy, "limit": limit}
        elif popularity == "high":
            params = {"seed_tracks": id, "target_energy": energy, "target_popularity": 100, "limit": limit}
        elif popularity == "low":
            params = {"seed_tracks": id, "target_energy": energy, "target_popularity": 0, "limit": limit}

        response = makeGetRequest(app, session, url2, params)
        response_json = jsonify(tracks=response["tracks"], user=user)

    return (response_json, 200)
