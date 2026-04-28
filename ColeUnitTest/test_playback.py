import pytest
from unittest.mock import patch

import playback


@pytest.fixture
def client():
    playback.app.config["TESTING"] = True
    return playback.app.test_client()


def test_callback_without_code_returns_400(client):
    response = client.get("/callback")

    assert response.status_code == 400
    assert response.get_json() == {"error": "No code returned from Spotify"}


@patch("playback.cache_handler.get_cached_token")
@patch("playback.sp_oauth.validate_token")
@patch("playback.sp.current_playback")
def test_playback_returns_track_info(mock_current_playback, mock_validate_token, mock_cached_token, client):
    mock_cached_token.return_value = {"access_token": "fake-token"}
    mock_validate_token.return_value = True

    mock_current_playback.return_value = {
        "progress_ms": 45000,
        "item": {
            "name": "Test Song",
            "artists": [
                {"name": "Artist One"},
                {"name": "Artist Two"}
            ]
        }
    }

    response = client.get("/playback")

    assert response.status_code == 200
    assert response.get_json() == {
        "track": "Test Song",
        "artists": "Artist One, Artist Two",
        "progress_ms": 45000
    }


@patch("playback.cache_handler.get_cached_token")
@patch("playback.sp_oauth.validate_token")
@patch("playback.sp.current_playback")
def test_playback_when_nothing_is_playing(mock_current_playback, mock_validate_token, mock_cached_token, client):
    mock_cached_token.return_value = {"access_token": "fake-token"}
    mock_validate_token.return_value = True
    mock_current_playback.return_value = None

    response = client.get("/playback")

    assert response.status_code == 200
    assert response.get_json() == {"message": "No track currently playing"}


@patch("playback.cache_handler.get_cached_token")
@patch("playback.sp_oauth.validate_token")
@patch("playback.sp_oauth.get_authorize_url")
def test_playback_redirects_if_not_logged_in(mock_auth_url, mock_validate_token, mock_cached_token, client):
    mock_cached_token.return_value = None
    mock_validate_token.return_value = False
    mock_auth_url.return_value = "https://accounts.spotify.com/authorize"

    response = client.get("/playback")

    assert response.status_code == 302
    assert response.location == "https://accounts.spotify.com/authorize"
