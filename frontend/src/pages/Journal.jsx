import { useState, useEffect } from "react";
import { movieAPI, journalAPI } from "../services/api";

export default function Journal() {
  const [entries, setEntries] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [rating, setRating] = useState(4);
  const [review, setReview] = useState("");
  const [watchedAt, setWatchedAt] = useState(new Date().toISOString().split("T")[0]);
  const [moods, setMoods] = useState("");

  const loadJournal = async () => {
    const res = await journalAPI.list();
    setEntries(res.data);
  };

  useEffect(() => { loadJournal(); }, []);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    const res = await movieAPI.search(searchQuery);
    setSearchResults(res.data);
  };

  const handleAdd = async () => {
    if (!selectedMovie) return;
    await journalAPI.create({
      tmdb_id: selectedMovie.tmdb_id,
      rating: parseFloat(rating),
      review,
      watched_at: watchedAt,
      is_rewatch: false,
      moods: moods.split(",").map((m) => m.trim()).filter(Boolean),
    });
    setSelectedMovie(null);
    setSearchResults([]);
    setSearchQuery("");
    setReview("");
    setMoods("");
    loadJournal();
  };

  const handleDelete = async (id) => {
    await journalAPI.delete(id);
    loadJournal();
  };

  return (
    <div style={{ maxWidth: 700, margin: "0 auto", padding: 24 }}>
      <h1>My Journal</h1>

      <form onSubmit={handleSearch} style={{ marginBottom: 16 }}>
        <input
          placeholder="Search a movie..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{ padding: 8, width: "70%" }}
        />
        <button type="submit" style={{ padding: 8 }}>Search</button>
      </form>

      {searchResults.length > 0 && !selectedMovie && (
        <div style={{ marginBottom: 16 }}>
          {searchResults.slice(0, 5).map((m) => (
            <div key={m.tmdb_id} onClick={() => setSelectedMovie(m)} style={{ cursor: "pointer", padding: 8, border: "1px solid #ddd", marginBottom: 4 }}>
              {m.title} {m.release_date ? `(${m.release_date.slice(0, 4)})` : ""}
            </div>
          ))}
        </div>
      )}

      {selectedMovie && (
        <div style={{ border: "1px solid #ccc", padding: 16, marginBottom: 16 }}>
          <h3>{selectedMovie.title}</h3>
          <label>Rating (0-5): <input type="number" step="0.5" min="0" max="5" value={rating} onChange={(e) => setRating(e.target.value)} /></label><br />
          <label>Watched on: <input type="date" value={watchedAt} onChange={(e) => setWatchedAt(e.target.value)} /></label><br />
          <label>Moods (comma separated): <input value={moods} onChange={(e) => setMoods(e.target.value)} placeholder="comfort, relaxing" /></label><br />
          <textarea placeholder="Review" value={review} onChange={(e) => setReview(e.target.value)} style={{ width: "100%", marginTop: 8 }} />
          <button onClick={handleAdd} style={{ marginTop: 8 }}>Add to Journal</button>
          <button onClick={() => setSelectedMovie(null)} style={{ marginTop: 8, marginLeft: 8 }}>Cancel</button>
        </div>
      )}

      <h2>Logged Movies ({entries.length})</h2>
      {entries.map((e) => (
        <div key={e.id} style={{ display: "flex", gap: 12, marginBottom: 12, padding: 8, borderBottom: "1px solid #eee" }}>
          {e.movie.poster_path && (
            <img src={`https://image.tmdb.org/t/p/w92${e.movie.poster_path}`} alt={e.movie.title} width={60} />
          )}
          <div style={{ flex: 1 }}>
            <strong>{e.movie.title}</strong> — ★ {e.rating}
            <p style={{ margin: "4px 0", fontSize: 14, color: "#555" }}>{e.review}</p>
            <p style={{ margin: 0, fontSize: 12, color: "#888" }}>
              {e.moods.join(", ")} · {e.watched_at}
            </p>
            <button onClick={() => handleDelete(e.id)} style={{ fontSize: 12, marginTop: 4 }}>Delete</button>
          </div>
        </div>
      ))}
    </div>
  );
}
