function TrackCard({ cover_url, name, subtitle }) {
  return (
    <div className="track-card">
      <div className="track-card-cover">
        {cover_url ? (
          <img src={cover_url} alt="" />
        ) : (
          <div className="track-card-cover-placeholder" />
        )}
      </div>
      <div className="track-card-text">
        <div className="track-card-name">{name}</div>
        {subtitle && <div className="track-card-subtitle">{subtitle}</div>}
      </div>
    </div>
  );
}

export default TrackCard;
