"""
Python/flask backend module for the Cyberdeck CSS 360 project.

Uses the Spotipy library to interact with the Spotify Web API, 
allowing users to authenticate and control their Spotify playback.
"""
import os

from flask import Flask, request, redirect, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import CacheFileHandler

load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True)


client_id = os.getenv('SPOTIPY_CLIENT_ID')
client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')

FLASK_URL = 'http://127.0.0.1:5000'
REACT_URL = os.getenv('REACT_URL')

REDIRECT_URL = f"{FLASK_URL}/callback"
SCOPE = 'user-read-playback-state user-modify-playback-state'

cache_handler = CacheFileHandler(cache_path='.spotify_cache')

sp_oauth = SpotifyOAuth(client_id,
    client_secret,
    REDIRECT_URL,
    scope=SCOPE,
    cache_handler=cache_handler,
    show_dialog=True
)

sp = Spotify(auth_manager=sp_oauth)


@app.route('/')
def home():
    """
    Home route.

    Redirects the user to Spotify authentication if they are not
    authenticated. Otherwise, redirects to the React frontend.

    Returns:
        Response: Redirect response.
    """
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    return redirect(REACT_URL)


@app.route('/login')
def login():
    """
    Start Spotify authentication flow.

    Returns:
        Response: Redirect to Spotify authorization page.
    """
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route('/callback')
def callback():
    """
    Handle Spotify OAuth callback.

    Retrieves the authorization code, exchanges it for an access token,
    and redirects the user to the React frontend.

    Returns:
        Response: Redirect or JSON error response.
    """
    code = request.args.get("code")

    if not code:
        return jsonify({"error": "No code returned from Spotify"}), 400

    sp_oauth.get_access_token(code)
    return redirect(REACT_URL)


@app.route('/playback')
def playback():
    """
    Retrieve current Spotify playback information.

    Returns:
        Response: JSON response containing playback information.
    """
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        #auth_url = sp_oauth.get_authorize_url()
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
            "progress_ms": playback_info["progress_ms"],
            "cover_URL": playback_info["item"]["album"]["images"][0]["url"]
        })

    return jsonify({
        "auth_required": False,
        "message": "No track currently playing",
        "is_playing": False
    })



@app.route('/playpause', methods=["POST"])
def toggleplayback():
    """
    Toggle Spotify playback state.

    Pauses playback if music is currently playing,
    otherwise resumes playback.

    Returns:
        Response: JSON success response.
    """
    playback_info = sp.current_playback()

    if playback_info and playback_info["is_playing"]:
        sp.pause_playback()
        return jsonify({
            "success": True
        })

    sp.start_playback()
    return jsonify({
        "success": True
    })


@app.route('/next', methods=["POST"])
def skip_next():
    """
    Skip to the next Spotify track.

    Returns:
        Response: JSON success response.
    """
    sp.next_track()
    return jsonify({
        "success": True
    })


@app.route('/previous', methods=["POST"])
def skip_previous():
    """
    Skip to the previous Spotify track.

    Returns:
        Response: JSON success response.
    """
    sp.previous_track()
    return jsonify({
        "success": True
    })

if __name__ == '__main__':
    app.run(debug=True)
