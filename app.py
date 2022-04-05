from flask import Flask, request, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User
from forms import SearchSongForm, SavePlaylistForm
from config import Config
from base_functions import makeGetRequest, makePostRequest, getToken, checkTokenStatus, authorizeUser, authorizeCallback, logoutUser, localStorage
from seed_functions import searchTrack, seedPlaylist
from user_functions import getUserPlaylists, createPlaylist, replacePlaylistLink


app = Flask(__name__)
app.config.from_object(Config)

toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()



# Main app routes

@app.route("/", methods=["GET", "POST"])
def homepage():
    form1 = SearchSongForm()
    form2 = SavePlaylistForm()

    if request.method == 'POST':
        data = request.json
        return searchTrack(app, session, data)

    if "token" in session:
        return render_template("home.html", form1=form1, form2=form2)
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



@app.route("/seed-playlist", methods=["POST"])
def seed_playlist():
    data = request.json
    return seedPlaylist(app, session, data)




# User Routes

@app.route('/authorize-user')
def authorize_user():
    return authorizeUser(app, session)


@app.route('/callback/')
def callback():
    if request.args.get('state') != session['state_key']:
    	return render_template('unauthorized.html', error='State failed.')
    if request.args.get('error'):
    	return render_template('unauthorized.html', error='Spotify error.')
    else:
        payload = authorizeCallback(app, session)
        if payload != None:
            if User.query.get(payload["id"]):
                user = User.query.get(payload["id"])
            else:
                user = User.register(payload["id"], payload["display_name"], payload["images"][0]["url"])
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
    playlists = getUserPlaylists(app, session)

    for playlist in playlists:
        playlist["link"] = replacePlaylistLink(playlist["uri"])

    return render_template("users/user_account.html", user=user, playlists=playlists)



@app.route("/logout", methods=["GET", "POST"])
def logout():
    logoutUser(session)
    return redirect("/")



@app.route('/save-playlist', methods=["POST"])
def create_palylist():
    user = session["user"]
    data = request.json
    payload = createPlaylist(app, session, user, data);
    if payload != None:
        flash("Playlist created successfully.")
        return user
