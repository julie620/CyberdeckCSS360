import { useState, useEffect } from "react";
import "./PlaylistsAlbums.css";

function AlbumBrowser() {
  const [albums, setAlbums] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("/api/albums", { credentials: "include" })
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        setAlbums(data.albums || []);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const playAlbum = async (albumUri) => {
    try {
      await fetch("/api/play-browse", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ context_uri: albumUri }),
      });
    } catch (err) {
      console.error("Error playing album:", err);
    }
  };

  return (
    <div className="browser">
      {loading && <p>Loading…</p>}
      {error && <p>Error: {error}</p>}
      {!loading && !error && (
        <div className="browser-grid">
          {albums.map((album) => (
            <div key={album.id} className="browse-card">
              {album.cover_url && (
                <button onClick={() => playAlbum(album.uri)}>
                  <img
                    src={album.cover_url}
                    alt={album.name}
                    className="browse-cover"
                  />
                </button>
              )}
              <h3 onClick={() => playAlbum(album.uri)}>{album.name}</h3>
              <p>{album.artist}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default AlbumBrowser;
