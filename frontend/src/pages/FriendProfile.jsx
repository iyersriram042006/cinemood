import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { socialAPI } from "../services/api";

export default function FriendProfile() {
  const { userId } = useParams();
  const [entries, setEntries] = useState([]);
  const [openComments, setOpenComments] = useState({});
  const [comments, setComments] = useState({});
  const [commentText, setCommentText] = useState({});

  const load = async () => {
    const res = await socialAPI.publicJournal(userId);
    setEntries(res.data);
  };

  useEffect(() => { load(); }, [userId]);

  const handleLike = async (entryId) => {
    await socialAPI.like(entryId);
    load();
  };

  const toggleComments = async (entryId) => {
    if (!openComments[entryId]) {
      const res = await socialAPI.getComments(entryId);
      setComments((prev) => ({ ...prev, [entryId]: res.data }));
    }
    setOpenComments((prev) => ({ ...prev, [entryId]: !prev[entryId] }));
  };

  const handleComment = async (entryId) => {
    const text = commentText[entryId];
    if (!text?.trim()) return;
    await socialAPI.comment(entryId, text);
    const res = await socialAPI.getComments(entryId);
    setComments((prev) => ({ ...prev, [entryId]: res.data }));
    setCommentText((prev) => ({ ...prev, [entryId]: "" }));
    load();
  };

  return (
    <div style={{ maxWidth: 700, margin: "0 auto", padding: 24 }}>
      <h1>Friend's Journal</h1>
      {entries.map((e) => (
        <div key={e.id} style={{ display: "flex", gap: 12, marginBottom: 16, padding: 8, borderBottom: "1px solid #eee" }}>
          {e.poster_path && (
            <img src={`https://image.tmdb.org/t/p/w92${e.poster_path}`} alt={e.title} width={60} />
          )}
          <div style={{ flex: 1 }}>
            <strong>{e.title}</strong> — ★ {e.rating}
            <p style={{ margin: "4px 0", fontSize: 14, color: "#555" }}>{e.review}</p>
            <p style={{ margin: 0, fontSize: 12, color: "#888" }}>{e.moods.join(", ")} · {e.watched_at}</p>
            <div style={{ marginTop: 6 }}>
              <button onClick={() => handleLike(e.id)}>
                {e.liked_by_me ? "❤️" : "🤍"} {e.like_count}
              </button>
              <button onClick={() => toggleComments(e.id)} style={{ marginLeft: 8 }}>
                💬 {e.comment_count}
              </button>
            </div>

            {openComments[e.id] && (
              <div style={{ marginTop: 8, paddingLeft: 8, borderLeft: "2px solid #eee" }}>
                {(comments[e.id] || []).map((c) => (
                  <p key={c.id} style={{ fontSize: 13, margin: "4px 0" }}>
                    <strong>{c.user_name}:</strong> {c.text}
                  </p>
                ))}
                <input
                  placeholder="Add a comment..."
                  value={commentText[e.id] || ""}
                  onChange={(ev) => setCommentText((prev) => ({ ...prev, [e.id]: ev.target.value }))}
                  onKeyDown={(ev) => ev.key === "Enter" && handleComment(e.id)}
                  style={{ padding: 6, width: "70%", marginTop: 4 }}
                />
                <button onClick={() => handleComment(e.id)} style={{ padding: 6, marginLeft: 4 }}>Post</button>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
