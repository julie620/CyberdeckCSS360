import { useState } from "react";

function Tabs({ active, onChange }) {
  const [visible, setVisible] = useState(true);

  return (
    <div className="tabs-container">
      {visible && (
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
      )}
      <button className="tab tab-toggle" onClick={() => setVisible(v => !v)}>
        {visible ? "Hide Tabs" : "Show Tabs"}
      </button>
    </div>
  );
}

export default Tabs;
