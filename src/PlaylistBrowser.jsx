import { useState, useEffect } from "react";
import "./PlaylistsAlbums.css";

function PlaylistBrowser() {
  const [playlists, setPlaylists] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("/api/playlists", { credentials: "include" })
      .then((res) => res.json())
      .then((data) => {
        setPlaylists(data.playlists || []);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const playPlaylist = async (playlistId) => {
    try {
      await fetch("/api/play-browse", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          context_uri: `spotify:playlist:${playlistId}`,
        }),
      });
    } catch (err) {
      console.error("Error playing playlist: ", err);
    }
  };

  return (
    <div className="browser">
      {loading && <p>Loading...</p>}
      {error && <p>Error: {error}</p>}
      {!loading && (
        <div className="browser-grid">
          {playlists.map((playlist) => (
            <div key={playlist.id} className="browse-card">
              {playlist.cover_url && (
                <button onClick={() => playPlaylist(playlist.id)}>
                  <img
                    src={playlist.cover_url}
                    alt={playlist.name}
                    className="browse-cover"
                  />
                </button>
              )}
              <h3 onClick={() => playPlaylist(playlist.id)}>{playlist.name}</h3>
              <p>By: {playlist.owner}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default PlaylistBrowser;
