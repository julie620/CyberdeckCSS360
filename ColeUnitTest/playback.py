import os


from flask import Flask, request, redirect, session, url_for, jsonify

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)

client_id = 'your_id_here'
client_secret = 'your_secret_here'


redirect_url = "http://127.0.0.1:5000/callback"
scope = 'user-read-playback-state'

cache_handler = FlaskSessionCacheHandler(session)
sp_oauth = SpotifyOAuth(client_id, 
    client_secret, 
    redirect_url, 
    scope=scope, 
    cache_handler=cache_handler,
    show_dialog=True
)

sp = Spotify(auth_manager=sp_oauth)


@app.route('/')
def home():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    return redirect('http://localhost:5174')

@app.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get("code")

    if not code:
        return jsonify({"error": "No code returned from Spotify"}), 400

    sp_oauth.get_access_token(code)
    return redirect(url_for('playback'))


@app.route('/playback')
def playback():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    
    playback_info = sp.current_playback()

    if playback_info and playback_info.get("item"):
        track_name = playback_info["item"]["name"]
        artists = ", ".join(artist["name"] for artist in playback_info["item"]["artists"])
        progress_ms = playback_info["progress_ms"]
        return jsonify({"track": track_name, "artists": artists, "progress_ms": progress_ms})

    return jsonify({"message": "No track currently playing"}), 200

if __name__ == '__main__':
    app.run(debug=True)


