import { useState, useEffect } from "react";
import { movieAPI, watchlistAPI } from "../services/api";

export default function Watchlist() {
  const [items, setItems] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);

  const load = async () => {
    const res = await watchlistAPI.list();
    setItems(res.data);
  };

  useEffect(() => { load(); }, []);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    const res = await movieAPI.search(searchQuery);
    setSearchResults(res.data);
  };

  const handleAdd = async (tmdb_id) => {
    try {
      await watchlistAPI.add(tmdb_id);
      setSearchResults([]);
      setSearchQuery("");
      load();
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to add");
    }
  };

  const handleRemove = async (id) => {
    await watchlistAPI.remove(id);
    load();
  };

  return (
    <div style={{ maxWidth: 700, margin: "0 auto", padding: 24 }}>
      <h1>Watchlist</h1>

      <form onSubmit={handleSearch} style={{ marginBottom: 16 }}>
        <input
          placeholder="Search a movie to add..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{ padding: 8, width: "70%" }}
        />
        <button type="submit" style={{ padding: 8 }}>Search</button>
      </form>

      {searchResults.length > 0 && (
        <div style={{ marginBottom: 16 }}>
          {searchResults.slice(0, 5).map((m) => (
            <div key={m.tmdb_id} style={{ display: "flex", justifyContent: "space-between", padding: 8, border: "1px solid #ddd", marginBottom: 4 }}>
              <span>{m.title} {m.release_date ? `(${m.release_date.slice(0, 4)})` : ""}</span>
              <button onClick={() => handleAdd(m.tmdb_id)}>Add</button>
            </div>
          ))}
        </div>
      )}

      <h2>Want to Watch ({items.length})</h2>
      {items.map((item) => (
        <div key={item.id} style={{ display: "flex", gap: 12, marginBottom: 12, padding: 8, borderBottom: "1px solid #eee" }}>
          {item.movie.poster_path && (
            <img src={`https://image.tmdb.org/t/p/w92${item.movie.poster_path}`} alt={item.movie.title} width={60} />
          )}
          <div style={{ flex: 1 }}>
            <strong>{item.movie.title}</strong>
            <p style={{ margin: "4px 0", fontSize: 12, color: "#888" }}>{(item.movie.genres || []).join(", ")}</p>
            <button onClick={() => handleRemove(item.id)} style={{ fontSize: 12 }}>Remove</button>
          </div>
        </div>
      ))}
    </div>
  );
}
