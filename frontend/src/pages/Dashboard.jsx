import { useState, useEffect } from "react";
import { analyticsAPI } from "../services/api";

export default function Dashboard() {
  const [overview, setOverview] = useState(null);
  const [genres, setGenres] = useState([]);
  const [directors, setDirectors] = useState([]);
  const [summary, setSummary] = useState("");

  useEffect(() => {
    analyticsAPI.overview().then((r) => setOverview(r.data));
    analyticsAPI.genres().then((r) => setGenres(r.data));
    analyticsAPI.directors().then((r) => setDirectors(r.data));
    analyticsAPI.summary().then((r) => setSummary(r.data.summary));
  }, []);

  if (!overview) return <p style={{ padding: 24 }}>Loading...</p>;

  return (
    <div style={{ maxWidth: 700, margin: "0 auto", padding: 24 }}>
      <h1>Dashboard</h1>

      <div style={{ display: "flex", gap: 16, marginBottom: 24 }}>
        <Stat label="Total Watched" value={overview.total_movies} />
        <Stat label="This Year" value={overview.movies_this_year} />
        <Stat label="Avg Rating" value={overview.average_rating} />
        <Stat label="Rewatches" value={overview.rewatches} />
      </div>

      <div style={{ background: "#f5f5f5", padding: 16, borderRadius: 8, marginBottom: 24 }}>
        <h3>Your Cinema Personality</h3>
        <p>{summary}</p>
      </div>

      <h3>Genre Breakdown</h3>
      {genres.map((g) => (
        <div key={g.genre} style={{ marginBottom: 6 }}>
          {g.genre}: {g.count} movies (avg {g.average_rating}★)
        </div>
      ))}

      <h3 style={{ marginTop: 24 }}>Favorite Directors</h3>
      {directors.map((d) => (
        <div key={d.director}>{d.director}: {d.count} movies</div>
      ))}
    </div>
  );
}

function Stat({ label, value }) {
  return (
    <div style={{ border: "1px solid #ddd", padding: 12, borderRadius: 8, flex: 1, textAlign: "center" }}>
      <div style={{ fontSize: 22, fontWeight: "bold" }}>{value}</div>
      <div style={{ fontSize: 12, color: "#666" }}>{label}</div>
    </div>
  );
}
