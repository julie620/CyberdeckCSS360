"""
Python/flask backend module for the Cyberdeck CSS 360 project.

Uses the Spotipy library to interact with the Spotify Web API,
allowing users to authenticate and control their Spotify playback.
"""
import os
import random

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
SCOPE = """user-read-playback-state user-modify-playback-state user-top-read
user-read-recently-played playlist-read-private playlist-read-collaborative user-library-read"""

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
            "duration_ms": playback_info["item"]["duration_ms"],
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


@app.route('/discover')
def discover():
    """
    Retrieve suggested tracks for the Discover page.

    Returns:
        Response: JSON response containing a list of suggested tracks.
    """
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        return jsonify({
            "auth_required": True,
            "auth_url": f"{FLASK_URL}/login"
        })

    known_ids = set()
    seen_artist_ids = set()

    recent_seed_artists = []
    try:
        recent = sp.current_user_recently_played(limit=50)
        for item in recent["items"]:
            track = item["track"]
            known_ids.add(track["id"])
            if track["artists"]:
                a = track["artists"][0]
                if a["id"] not in seen_artist_ids and len(recent_seed_artists) < 5:
                    seen_artist_ids.add(a["id"])
                    recent_seed_artists.append({"id": a["id"], "name": a["name"]})
    except Exception:
        pass

    top_seed_artists = []
    try:
        top_artists = sp.current_user_top_artists(limit=5, time_range="medium_term")
        for a in top_artists["items"]:
            if a["id"] in seen_artist_ids:
                continue
            seen_artist_ids.add(a["id"])
            top_seed_artists.append({"id": a["id"], "name": a["name"]})
    except Exception:
        pass

    if not recent_seed_artists and not top_seed_artists:
        return jsonify({
            "auth_required": False,
            "suggestions": []
        })

    for time_range in ("short_term", "medium_term", "long_term"):
        try:
            top_tracks = sp.current_user_top_tracks(limit=50, time_range=time_range)
            known_ids.update(t["id"] for t in top_tracks["items"])
        except Exception:
            pass

    def pick_tracks_for_artist(artist, n):
        picks = []
        for offset in (20, 10, 0):
            try:
                results = sp.search(
                    q=f'artist:"{artist["name"]}"',
                    type="track",
                    limit=10,
                    offset=offset,
                    market="US",
                )
            except Exception:
                continue
            for t in results["tracks"]["items"]:
                if len(picks) >= n:
                    break
                if t["id"] in known_ids:
                    continue
                if not any(a["id"] == artist["id"] for a in t["artists"]):
                    continue
                picks.append({
                    "id": t["id"],
                    "name": t["name"],
                    "artist": t["artists"][0]["name"],
                    "cover_url": t["album"]["images"][0]["url"] if t["album"]["images"] else None,
                    "uri": t["uri"],
                    "source_artist": artist["name"]
                })
                known_ids.add(t["id"])
            if len(picks) >= n:
                break
        return picks

    suggestions = []
    for artist in recent_seed_artists:
        suggestions.extend(pick_tracks_for_artist(artist, 3))
    for artist in top_seed_artists:
        suggestions.extend(pick_tracks_for_artist(artist, 2))

    random.shuffle(suggestions)

    return jsonify({
        "auth_required": False,
        "suggestions": suggestions
    })

@app.route("/playlists")
def get_playlists():
    """
    Retrieves user's Spotify playlists

    Returns:
        Response:
            - whether user needs to authenticate
            - login URL where user needs to authenticate
            - a list of formatted playlist objects
                - id
                - name
                - cover_url
                - owner
    """
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        return jsonify({"auth_required": True, "auth_url": f"{FLASK_URL}/login"})

    playlists = sp.current_user_playlists(limit=50)
    playlists = playlists.get("items", [])

    formatted_playlists = []
    for playlist in playlists:
        formatted_playlists.append(
            {
                "id": playlist.get("id"),
                "name": playlist.get("name"),
                "cover_url": (
                    playlist["images"][0]["url"] if playlist.get("images") else None
                ),
                "owner": playlist.get("owner", {}).get("display_name", "Unknown"),
            }
        )
    return jsonify({"auth_required": False, "playlists": formatted_playlists})


@app.route("/play-browse", methods=["POST"])
def play_playlist():
    """
    Start playback for Spotify playlist

    Returns:
        Response: JSON success response
    """
    data = request.json
    sp.start_playback(context_uri=data["context_uri"])
    return jsonify({"success": True})


@app.route("/albums")
def get_albums():
    """
    Retrieves user's Saved Albums

    Returns:
        Response:
            - whether user needs to authenticate
            - login URL where user needs to authenticate
            - a list of formatted album objects
                - id
                - name
                - artist
                - uri
                - cover_url
    """
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        return jsonify({"auth_required": True, "auth_url": f"{FLASK_URL}/login"})

    results = sp.current_user_saved_albums(limit=50)
    albums = []
    for item in results.get("items", []):
        album = item["album"]
        albums.append(
            {
                "id": album["id"],
                "name": album["name"],
                "artist": album["artists"][0]["name"],
                "uri": album["uri"],
                "cover_url": album["images"][0]["url"] if album.get("images") else None,
            }
        )
    return jsonify({"auth_required": False, "albums": albums})

@app.route('/health')
def health():
    return {"status": "ok"}, 200

if __name__ == '__main__':
    app.run(debug=True)
