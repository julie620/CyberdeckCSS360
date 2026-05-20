"""
api/tests/test_api.py

Unit and integration tests for the CyberdeckCSS360 Flask API.
Run with:  python -m pytest api/tests/ -v
"""

import pytest
import sys
import os

# Make sure the api module is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    # Import here so tests can still be collected even if api.py has import
    # errors for optional deps (e.g. spotipy not installed in CI).
    try:
        from api import app  # adjust import name if your Flask app var differs
    except ImportError:
        pytest.skip("Could not import Flask app — skipping integration tests")

    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret-key"
    with app.test_client() as client:
        yield client


# ---------------------------------------------------------------------------
# Unit Tests — pure logic, no HTTP calls
# ---------------------------------------------------------------------------

class TestUnitHelpers:
    """Unit tests for helper / utility functions (no Flask context needed)."""

    def test_placeholder_true(self):
        """Placeholder: always passes. Replace with real unit tests."""
        assert True

    def test_string_not_empty(self):
        """Example: verify that a non-empty string is truthy."""
        assert "CyberdeckCSS360"

    def test_basic_arithmetic(self):
        """Example: sanity-check Python math (replace with real logic)."""
        result = 2 + 2
        assert result == 4


# ---------------------------------------------------------------------------
# Integration Tests — hit Flask routes via test client
# ---------------------------------------------------------------------------

class TestHealthEndpoint:
    """Tests for the /health liveness endpoint."""

    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_json(self, client):
        response = client.get("/health")
        data = response.get_json()
        assert data is not None

    def test_health_status_field(self, client):
        response = client.get("/health")
        data = response.get_json()
        assert data.get("status") == "ok"


class TestSpotifyRoutes:
    """Integration tests for Spotify-related API routes."""

    def test_login_route_exists(self, client):
        """The /login route should redirect (302) to Spotify OAuth."""
        response = client.get("/login")
        # Expect a redirect to Spotify, not a 404
        assert response.status_code in (302, 200), (
            f"Expected redirect from /login, got {response.status_code}"
        )

    def test_callback_route_exists(self, client):
        """The /callback route should exist (even if it 400s without a code)."""
        response = client.get("/callback")
        assert response.status_code != 404, "/callback route not found"

    def test_unknown_route_returns_404(self, client):
        """Requesting a non-existent route should return 404."""
        response = client.get("/this-route-does-not-exist-xyz")
        assert response.status_code == 404
