function Tabs({ active, onChange }) {
  return (
    <div className="tabs">
      <button
        className={`tab ${active === "now-playing" ? "active" : ""}`}
        onClick={() => onChange("now-playing")}
      >
        Now Playing
      </button>
      <button
        className={`tab ${active === "discover" ? "active" : ""}`}
        onClick={() => onChange("discover")}
      >
        Discover
      </button>
      <button
        className={`tab ${active === "playlists" ? "active" : ""}`}
        onClick={() => onChange("playlists")}
      >
        Playlists
      </button>
      <button
        className={`tab ${active === "albums" ? "active" : ""}`}
        onClick={() => onChange("albums")}
      >
        Albums
      </button>
    </div>
  );
}

export default Tabs;
