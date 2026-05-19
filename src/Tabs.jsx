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
    </div>
  );
}

export default Tabs;
