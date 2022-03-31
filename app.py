from flask import Flask, request, render_template, redirect, session, flash, make_response, jsonify
import requests
from werkzeug.urls import url_encode
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User
from forms import SearchSongForm, DeleteForm
import os
import string, random, logging, time
from config import Config
from functions import makeGetRequest, getToken, checkTokenStatus, getUserInformation, localStorage
from functions import create_playlist_obscure, create_playlist_any, create_playlist_popular



app = Flask(__name__)
app.config.from_object(Config)

toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()



spotify = "https://api.spotify.com/v1"

@app.route("/", methods=["GET", "POST"])
def homepage():
    form = SearchSongForm()
    # if form.validate_on_submit():
    if request.method == 'POST':
        data = request.json
        url = f"{spotify}/search"
        params = {"type": "track", "q": data["q"], "limit": 10}
        response = makeGetRequest(app, session, url, params)
        response_json = jsonify(tracks=response["tracks"]["items"])
        return (response_json, 200)

    if "token" in session:
        return render_template("home.html", form=form)
    else:
        if localStorage.getItem("loggedInUser"):
            return redirect("/authorize-user")
        else:
            return redirect("/authorize-client")


@app.route('/authorize-client')
def authorize_client():
    response = getToken(app, session)
    if response == 200:
        return redirect("/")
    else:
        return render_template('index.html', error='Failed to access token.')



@app.route("/playlist", methods=["POST"])
def show_track_feat():
    data = request.json
    id = data["id"]
    popularity = data["popularity"]
    limit = int(data["limit"])
    url1 = f"{spotify}/audio-features/{id}"
    url2 = f"{spotify}/recommendations"
    features = makeGetRequest(app, session, url1)
    return globals()["create_playlist_" + popularity](app, session, url2, id, limit, features["energy"])






# User Routes


@app.route('/authorize-user')
def authorize_user():
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


@app.route('/callback/')
def callback():
    # make sure the response came from Spotify
    if request.args.get('state') != session['state_key']:
    	return render_template('unauthorized.html', error='State failed.')
    if request.args.get('error'):
    	return render_template('unauthorized.html', error='Spotify error.')
    else:
        code = request.args.get('code')
        session.pop('state_key', None)
        response = getToken(app, session, code)
        if response == 200:
            user_response = getUserInformation(app, session)

            if User.query.get(user_response["id"]):
                user = User.query.get(user_response["id"])
            else:
                user = User.register(user_response["id"], user_response["display_name"], user_response["images"][0]["url"])
                db.session.add(user)
                db.session.commit()
            session['user'] = user.spotify_id
            session['user_name'] = user.display_name
            session['user_image'] = user.image
            return redirect("/")

        else:
            return render_template('unauthorized.html', error='Failed to access token.')




@app.route('/users/<user>')
def show_user(user):
    if "user" not in session or user != session["user"]:
        return redirect("/unauthorized")

    user = User.query.get_or_404(user)

    return render_template("users/show.html", user=user)


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.pop("token")
    session.pop("token_expiration")
    session.pop("refresh_token")
    session.pop("user")
    session.pop("user_name")
    session.pop("user_image")
    localStorage.removeItem("loggedInUser")
    flash("Successfully logged out.")
    return redirect("/")
