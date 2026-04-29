import os


from flask import Flask, request, redirect, session, url_for, jsonify
from flask_cors import CORS

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler


app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['SECRET_KEY'] = 'dev-secret-key'  # In production, use a secure random key and keep it secret

client_id = 'a47d794efc9842608f2b633029d35f96'
client_secret = 'fd70260cca7b4cc48d5132fb188ffbd0'

FLASK_URL = 'http://127.0.0.1:5000'
REACT_URL = 'http://localhost:5173'

redirect_url = f"{FLASK_URL}/callback"
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
    return redirect(REACT_URL)

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
    return redirect(REACT_URL)


@app.route('/playback')
def playback():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return jsonify({
            "auth_required": True,
            "auth_url": f"{FLASK_URL}/login"
        })
    
    playback_info = sp.current_playback()

    if playback_info and playback_info.get("item"):
        return jsonify({
            "auth_required": False,
            "track_name": playback_info["item"]["name"],
            "artist_name": playback_info["item"]["artists"][0]["name"],
            "is_playing": playback_info["is_playing"],
            "progress_ms": playback_info["progress_ms"]
        })
    else:
        return jsonify({
            "auth_required": False,
            "message": "No track currently playing",
            "is_playing": False
        })

if __name__ == '__main__':
    app.run(debug=True)


