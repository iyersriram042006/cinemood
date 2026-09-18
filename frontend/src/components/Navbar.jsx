import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { logout, isAuthenticated } = useAuth();
  if (!isAuthenticated) return null;

  return (
    <nav style={{ display: "flex", gap: 16, padding: 16, borderBottom: "1px solid #ddd" }}>
      <Link to="/">Journal</Link>
      <Link to="/dashboard">Dashboard</Link>
      <Link to="/recommendations">Recommendations</Link>
      <button onClick={logout} style={{ marginLeft: "auto" }}>Logout</button>
    </nav>
  );
}
