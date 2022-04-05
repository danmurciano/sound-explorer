from flask import request, redirect, session, flash, make_response, jsonify
import requests, string, random, logging, time
from werkzeug.urls import url_encode
from localStoragePy import localStoragePy

localStorage = localStoragePy('sound-explorer', 'json')



def makeGetRequest(app, session, url, params={}):
    headers = {"Authorization": "Bearer {}".format(session['token'])}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()

    elif response.status_code == 401 and checkTokenStatus(app, session) != None:
        return makeGetRequest(app, session, url, params)
    else:
        logging.error('makeGetRequest:' + str(response.status_code))
        return None


def makePostRequest(app, session, url, data):
    headers = {"Authorization": "Bearer {}".format(session['token']), 'Accept': 'application/json', 'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 201:
        return response.json()
    if response.status_code == 204:
        return response

    elif response.status_code == 401 and checkTokenStatus(app, session) != None:
        return makePostRequest(app, session, url, data)
    elif response.status_code == 403 or response.status_code == 404:
        return response.status_code
    else:
        logging.error('makePostRequest:' + str(response.status_code))
        return None



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
        if "user" in session:
            return getToken(app, session, None, session['refresh_token'])
        else:
            return getToken(app, session)



def authorizeUser(app, session):
    client_id = app.config['CLIENT_ID']
    redirect_uri = app.config['REDIRECT_URI']
    scope = app.config['SCOPE']
    state_key = ''.join(random.choice(string.ascii_lowercase) for x in range(16))
    session['state_key'] = state_key
    if localStorage.getItem("loggedInUser"):
        show_dialog = False
    else:
        show_dialog = True

    authorize_url = 'https://accounts.spotify.com/en/authorize?'
    params = {'response_type': 'code',
              'client_id': client_id,
              'redirect_uri': redirect_uri,
              'scope': scope,
              'state': state_key,
              'show_dialog': show_dialog}
    query_params = url_encode(params)
    response = make_response(redirect(authorize_url + query_params))
    return response


def authorizeCallback(app, session):
    code = request.args.get('code')
    session.pop('state_key', None)
    response = getToken(app, session, code)
    if response == 200:
        return getUserInformation(app, session)
    else:
        return


def getUserInformation(app, session):
	url = "https://api.spotify.com/v1/me"
	payload = makeGetRequest(app, session, url)

	if payload == None:
		return None

	return payload


def logoutUser(session):
    session.pop("token")
    session.pop("token_expiration")
    session.pop("refresh_token")
    session.pop("user")
    session.pop("user_name")
    session.pop("user_image")
    localStorage.removeItem("loggedInUser")
