import { useEffect, useState, useCallback } from "react";
import TrackCard from "./TrackCard";
import "./Discover.css";

function Discover() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    fetch("/api/discover", { credentials: "include" })
      .then((res) => res.json())
      .then((d) => {
        setData(d);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  useEffect(load, [load]);

  if (loading && !data) {
    return (
      <div className="discover">
        <div className="discover-state">Loading…</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="discover">
        <div className="discover-state">
          <p>Couldn’t load suggestions.</p>
          <button onClick={load}>Try again</button>
        </div>
      </div>
    );
  }

  if (data?.auth_required) {
    return (
      <div className="discover">
        <div className="discover-state">
          <a href={data.auth_url}>Sign in with Spotify</a>
        </div>
      </div>
    );
  }

  const allEmpty = !data?.suggestions?.length;

  if (allEmpty) {
    return (
      <div className="discover">
        <div className="discover-state">
          Couldn’t load suggestions yet, play some music on Spotify first.
        </div>
      </div>
    );
  }

  const sections = [
    {
      key: "suggestions",
      title: "Suggested for You",
      items: data.suggestions,
      renderItem: (t) => (
        <TrackCard
          key={t.id}
          cover_url={t.cover_url}
          name={t.name}
          subtitle={t.artist}
        />
      ),
    },
  ];

  return (
    <div className="discover">
      <h1 className="discover-title">Discover</h1>
      {sections.map((section) =>
        section.items?.length ? (
          <section key={section.key} className="discover-section">
            <h2 className="discover-section-title">{section.title}</h2>
            <div className="discover-section-items">
              {section.items.map(section.renderItem)}
            </div>
          </section>
        ) : null
      )}
    </div>
  );
}

export default Discover;
