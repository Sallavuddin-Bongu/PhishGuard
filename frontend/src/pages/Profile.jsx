import { useEffect, useState } from "react";
import Layout from "../components/common/Layout";
import { useAuth } from "../context/AuthContext";
import { apiRequest } from "../services/api";

export default function Profile() {
  const {user, refreshUser} = useAuth();
  const [name,setName] = useState(user?.name || "");
  const [message,setMessage] = useState("");
  const [error,setError] = useState("");
  useEffect(()=>setName(user?.name || ""),[user]);

  async function save(e) {
    e.preventDefault(); setMessage(""); setError("");
    try {
      await apiRequest("/api/users/me", {
        method:"PATCH", body:JSON.stringify({name})
      });
      await refreshUser(); setMessage("Profile updated.");
    } catch(err) { setError(err.message); }
  }

  return <Layout title="Profile" subtitle="Manage your account profile.">
    <section className="panel profile-panel"><div className="profile-head">
      <span className="avatar large-avatar">{(user?.name || "U")[0].toUpperCase()}</span>
      <div><h2>{user?.name}</h2><p>{user?.email}</p></div>
    </div>
    <form onSubmit={save}><label>Full name</label><input value={name} onChange={e=>setName(e.target.value)} minLength={2} required/>
      <label>Email address</label><input value={user?.email || ""} readOnly/>
      {message && <p className="success">{message}</p>}{error && <div className="error">{error}</div>}
      <button className="primary">Save profile</button>
    </form></section>
  </Layout>;
}
