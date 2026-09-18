import { useState } from "react";
import { recommendAPI } from "../services/api";

export default function Recommendations() {
  const [mood, setMood] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!mood.trim()) return;
    setLoading(true);
    const res = await recommendAPI.getRecommendations(mood);
    setResults(res.data.recommendations);
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: 700, margin: "0 auto", padding: 24 }}>
      <h1>What should I watch?</h1>
      <form onSubmit={handleSearch}>
        <input
          placeholder="I'm bored, want something light..."
          value={mood}
          onChange={(e) => setMood(e.target.value)}
          style={{ padding: 10, width: "70%" }}
        />
        <button type="submit" style={{ padding: 10 }}>Find Movies</button>
      </form>

      {loading && <p>Thinking...</p>}

      <div style={{ marginTop: 24 }}>
        {results.map((r) => (
          <div key={r.movie_id} style={{ display: "flex", gap: 12, marginBottom: 16, padding: 8, border: "1px solid #eee" }}>
            {r.poster_path && (
              <img src={`https://image.tmdb.org/t/p/w92${r.poster_path}`} alt={r.title} width={60} />
            )}
            <div>
              <strong>{r.title}</strong> — ★ {r.rating}
              <p style={{ fontSize: 13, color: "#666" }}>{r.reason}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
