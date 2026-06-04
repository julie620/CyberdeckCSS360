import { useState, useEffect, useCallback } from "react";
import "./App.css";
import previousButton from "./assets/previous.png";
import playButton from "./assets/play.png";
import pauseButton from "./assets/pause.png";
import nextButton from "./assets/next.png";
import Tabs from "./Tabs";
import Discover from "./Discover";
import PlaylistBrowser from "./PlaylistBrowser";
import AlbumBrowser from "./AlbumBrowser";
import TrackCard from "./TrackCard";

const fmt = (ms) => {
  const s = Math.max(0, Math.floor(ms / 1000));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
};

function App() {
  const [activeTab, setActiveTab] = useState("now-playing");
  const [currentPlayback, setPlayback] = useState(null);
  const [showQueue, setShowQueue] = useState(false);
  const [queueItems, setQueueItems] = useState([]);

  useEffect(() => {
    const fetchPlayback = () => {
      fetch("/api/playback", { credentials: "include" })
        .then((res) => res.json())
        .then((data) => setPlayback(data))
        .catch((error) =>
          console.error("Error fetching playback data:", error),
        );
    };

    fetchPlayback();
    const interval = setInterval(fetchPlayback, 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!showQueue) return;
    let cancelled = false;
    const fetchQueue = () => {
      fetch("/api/queue", { credentials: "include" })
        .then((res) => res.json())
        .then((data) => {
          if (!cancelled) setQueueItems(data.items || []);
        })
        .catch(() => {});
    };
    fetchQueue();
    const interval = setInterval(fetchQueue, 5000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [showQueue]);

  const togglePlayback = useCallback(async () => {
    await fetch("/api/playpause", {
      credentials: "include",
      method: "POST",
    });
  }, []);

  const skipNext = useCallback(async () => {
    await fetch("/api/next", {
      credentials: "include",
      method: "POST",
    });
  }, []);

  const skipPrevious = useCallback(async () => {
    await fetch("/api/previous", {
      credentials: "include",
      method: "POST",
    });
  }, []);

  const jumpToTrack = useCallback(async (index) => {
    const res = await fetch("/api/queue/skip-to", {
      credentials: "include",
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ count: index + 1 }),
    });
    if (!res.ok) return;
    const data = await fetch("/api/queue", { credentials: "include" })
      .then((r) => r.json())
      .catch(() => null);
    if (data) setQueueItems(data.items || []);
  }, []);

  const nowPlayingView = (() => {
    if (currentPlayback?.auth_required) {
      return (
        <div className="now-playing">
          <div className="login">
            <a href={currentPlayback.auth_url}>Sign in with Spotify</a>
          </div>
        </div>
      );
    }

    if (!currentPlayback?.track_name) {
      return (
        <div className="now-playing">
          <div className="idle">
            <h1 className="title">{currentPlayback?.message}</h1>
          </div>
        </div>
      );
    }

    const pct = Math.min(
      100,
      (currentPlayback.progress_ms / Math.max(1, currentPlayback.duration_ms)) *
        100,
    );

    return (
      <div className={`now-playing${showQueue ? " queue-open" : ""}`}>
        <div className="device">
          <div className="cover">
            <img src={currentPlayback.cover_URL} alt="album cover" />
          </div>

          <div className="meta">
            <h1 className="title">{currentPlayback.track_name}</h1>
            <div className="artist">{currentPlayback.artist_name}</div>
          </div>

          <div className="progress">
            <div className="bar">
              <div className="fill" style={{ width: `${pct}%` }} />
            </div>
            <div className="times">
              <span className="left">{fmt(currentPlayback.progress_ms)}</span>
              <span className="status">
                {currentPlayback.is_playing ? "PLAYING" : "PAUSED"}
              </span>
              <span className="right">{fmt(currentPlayback.duration_ms)}</span>
            </div>
          </div>

          <div className="controls">
            <div id="playback-controls">
              <button className="btn-skip" onClick={skipPrevious}>
                <img src={previousButton} alt="Previous" />
              </button>

              <button className="btn-play" onClick={togglePlayback}>
                <img
                  src={currentPlayback.is_playing ? pauseButton : playButton}
                  alt={currentPlayback.is_playing ? "pause" : "play"}
                />
              </button>

              <button className="btn-skip" onClick={skipNext}>
                <img src={nextButton} alt="Next" />
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  })();

  return (
    <>
      <Tabs active={activeTab} onChange={setActiveTab} />
      {activeTab === "now-playing" && nowPlayingView}
      {activeTab === "now-playing" && (
        <>
          <button
            className="queue-toggle-btn"
            onClick={() => setShowQueue((v) => !v)}
          >
            {showQueue ? "Hide Queue" : "Show Queue"}
          </button>
          {showQueue && (
            <div className="queue-drawer">
              <h2 className="queue-drawer-title">Up Next</h2>
              {queueItems.length === 0 ? (
                <div className="queue-drawer-empty">Queue is empty</div>
              ) : (
                <div className="queue-drawer-list">
                  {queueItems.map((t, i) => (
                    <button
                      key={`${t.id}-${i}`}
                      className="queue-jump"
                      onClick={() => jumpToTrack(i)}
                      title="Jump to this track"
                    >
                      <TrackCard
                        cover_url={t.cover_url}
                        name={t.name}
                        subtitle={t.artist}
                      />
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
        </>
      )}
      {activeTab === "discover" && <Discover />}
      {activeTab === "playlists" && <PlaylistBrowser />}
      {activeTab === "albums" && <AlbumBrowser />}
    </>
  );
}

export default App;
