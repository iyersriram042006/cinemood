import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { compareAPI } from "../services/api";

export default function Compare() {
  const { userId } = useParams();
  const [data, setData] = useState(null);

  useEffect(() => {
    compareAPI.compare(userId).then((r) => setData(r.data));
  }, [userId]);

  if (!data) return <p style={{ padding: 24 }}>Loading...</p>;

  return (
    <div style={{ maxWidth: 700, margin: "0 auto", padding: 24 }}>
      <h1>Taste Comparison</h1>
      <p>Shared movies: {data.shared_movie_count}</p>

      {data.shared_movies.length > 0 && (
        <div style={{ marginBottom: 24 }}>
          <h3>Movies you both watched</h3>
          {data.shared_movies.map((m, i) => (
            <div key={i} style={{ padding: 6, borderBottom: "1px solid #eee" }}>
              {m.title} — You: ★{m.your_rating} · Them: ★{m.their_rating}
            </div>
          ))}
        </div>
      )}

      <h3>Genre Overlap</h3>
      {data.genre_overlap.map((g) => (
        <div key={g.genre} style={{ marginBottom: 6 }}>
          {g.genre} — You: {g.your_count} · Them: {g.their_count}
        </div>
      ))}
    </div>
  );
}
