import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { friendsAPI } from "../services/api";

export default function Friends() {
  const [friends, setFriends] = useState([]);
  const [pending, setPending] = useState([]);
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");

  const load = async () => {
    const [f, p] = await Promise.all([friendsAPI.list(), friendsAPI.pending()]);
    setFriends(f.data);
    setPending(p.data);
  };

  useEffect(() => { load(); }, []);

  const handleSend = async (e) => {
    e.preventDefault();
    setMessage("");
    try {
      await friendsAPI.send(email);
      setMessage("Request sent!");
      setEmail("");
    } catch (err) {
      setMessage(err.response?.data?.detail || "Failed to send request");
    }
  };

  const handleAccept = async (id) => {
    await friendsAPI.accept(id);
    load();
  };

  const handleReject = async (id) => {
    await friendsAPI.reject(id);
    load();
  };

  return (
    <div style={{ maxWidth: 700, margin: "0 auto", padding: 24 }}>
      <h1>Friends</h1>

      <form onSubmit={handleSend} style={{ marginBottom: 24 }}>
        <input
          placeholder="Friend's email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={{ padding: 8, width: "60%" }}
        />
        <button type="submit" style={{ padding: 8 }}>Send Request</button>
        {message && <p style={{ fontSize: 13 }}>{message}</p>}
      </form>

      {pending.length > 0 && (
        <div style={{ marginBottom: 24 }}>
          <h3>Pending Requests</h3>
          {pending.map((p) => (
            <div key={p.id} style={{ display: "flex", justifyContent: "space-between", padding: 8, border: "1px solid #eee", marginBottom: 6 }}>
              <span>{p.other_user_name} ({p.other_user_email})</span>
              <div>
                <button onClick={() => handleAccept(p.id)} style={{ marginRight: 8 }}>Accept</button>
                <button onClick={() => handleReject(p.id)}>Reject</button>
              </div>
            </div>
          ))}
        </div>
      )}

      <h3>Your Friends</h3>
      {friends.length === 0 && <p style={{ color: "#888" }}>No friends yet.</p>}
      {friends.map((f) => (
        <div key={f.id} style={{ display: "flex", justifyContent: "space-between", padding: 8, border: "1px solid #eee", marginBottom: 6 }}>
          <span>{f.other_user_name} ({f.other_user_email})</span>
          <div>
            <Link to={`/profile/${f.other_user_id}`} style={{ marginRight: 12 }}>View Journal</Link>
            <Link to={`/compare/${f.other_user_id}`}>Compare Taste</Link>
          </div>
        </div>
      ))}
    </div>
  );
}
