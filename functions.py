from flask import render_template, redirect, request, jsonify
import config
import base64
import os
import random as rand
import string as string
import requests
import time
import logging
from iteration_utilities import unique_everseen
from localStoragePy import localStoragePy

localStorage = localStoragePy('sound-explorer', 'json')



def create_playlist_obscure(app, session, url, id, limit, energy):
    params = {"seed_tracks": id, "target_energy": energy, "target_popularity": 0, "limit": 100}
    tracks = makeGetRequest(app, session, url, params)
    tracks_sorted = sorted(tracks["tracks"], key=lambda x: x["popularity"])
    obscure = tracks_sorted
    for track in tracks_sorted[0:4]:
        params = {"seed_tracks": track["id"], "target_energy": energy, "target_popularity": 0, "limit": 100}
        tracks = makeGetRequest(app, session, url, params)
        tracks = tracks["tracks"]
        obscure.extend(tracks)
        # obscure = list(unique_everseen(obscure))
    obscure = list(unique_everseen(obscure))
    obscure = sorted(obscure, key=lambda x: x["popularity"])
    response_json = jsonify(tracks=obscure[:limit:])
    return (response_json, 200)


def create_playlist_any(app, session, url, id, limit, energy):
    params = {"seed_tracks": id, "target_energy": energy, "limit": limit}
    response = makeGetRequest(app, session, url, params)
    response_json = jsonify(tracks=response["tracks"])
    return (response_json, 200)


def create_playlist_popular(app, session, url, id, limit, energy):
    params = {"seed_tracks": id, "target_energy": energy, "target_popularity": 100, "limit": limit}
    response = makeGetRequest(app, session, url, params)
    response_json = jsonify(tracks=response["tracks"])
    return (response_json, 200)



def getToken(app, session, code=None, refreshToken=None):
    token_url = 'https://accounts.spotify.com/api/token'
    authorization = app.config['AUTHORIZATION']
    redirect_uri = app.config['REDIRECT_URI']
    headers = {'Authorization': authorization, 'Accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}

    if code:
        body = {'code': code, 'redirect_uri': redirect_uri, 'grant_type': 'authorization_code'}
    elif refreshToken:
        body = {'refresh_token': refreshToken, 'grant_type': 'refresh_token'}
    else:
        body = {"grant_type": "client_credentials"}

    post_response = requests.post(token_url, headers=headers, data=body)

    if post_response.status_code == 200:
        json = post_response.json()
        session['token'] = json['access_token']
        session['token_expiration'] = time.time() + json['expires_in']
        if 'refresh_token' in json:
            session['refresh_token'] = json['refresh_token']
            localStorage.setItem('loggedInUser', True)
        return 200
    else:
        logging.error('getToken:' + str(post_response.status_code))
        return None


def checkTokenStatus(app, session):
    if time.time() > session['token_expiration']:
        if user in session:
            return getToken(app, session, None, session['refresh_token'])
        else:
            return getToken(app, session)


def getUserInformation(app, session):
	url = 'https://api.spotify.com/v1/me'
	payload = makeGetRequest(app, session, url)

	if payload == None:
		return None

	return payload



def makeGetRequest(app, session, url, params={}):
    headers = {"Authorization": "Bearer {}".format(session['token'])}
    response = requests.get(url, headers=headers, params=params)

    # 200 code indicates request was successful
    if response.status_code == 200:
        return response.json()

    # if a 401 error occurs, update the access token
    elif response.status_code == 401 and checkTokenStatus(app, session) != None:
        return makeGetRequest(app, session, url, params)
    else:
        logging.error('makeGetRequest:' + str(response.status_code))
        return None
