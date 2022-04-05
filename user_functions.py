from base_functions import makeGetRequest, makePostRequest
import requests

SPOTIFY = "https://api.spotify.com/v1"


def getUserPlaylists(app, session, offset = 0, limit=50):
    url = f"{SPOTIFY}/me/playlists"
    params = {'limit': limit, 'offset': offset}
    playlists = makeGetRequest(app, session, url, params)
    return playlists["items"]



def createPlaylist(app, session, user, data):
    name = data["name"]
    description = data["description"]
    image = data["image"]
    tracks = data["suggestedTracks"]

    tracks_uri = [track["uri"] for track in tracks]
    url1 = f"{SPOTIFY}/users/{user}/playlists"
    data = "{\"name\":\"" + name + "\",\"description\":\"" + description + "\"}"
    playlist = makePostRequest(app, session, url1, data)

    if playlist == None:
        return None

    url2 = f"{SPOTIFY}/playlists/{playlist['id']}/tracks"
    uri_str = ""
    for uri in tracks_uri:
        uri_str += "\"" + uri + "\","

    tracks_data = "{\"uris\": [" + uri_str[0:-1] + "]}"
    makePostRequest(app, session, url2, tracks_data)
    return {"user": user, "playlist_id": playlist['id']}


def replacePlaylistLink(uri):
    return uri.replace("spotify:playlist:", "https://open.spotify.com/playlist/")
