import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { LockKeyhole, Mail, ShieldCheck, UserRound } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Signup() {
  const { signup, user } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  if (user) return <Navigate to="/dashboard" replace />;

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await signup(name, email, password);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return <div className="auth">
    <section className="auth-art">
      <div className="brand"><ShieldCheck/><span>Phish<b>Guard</b></span></div>
      <div className="hero"><span className="eyebrow">BUILD SAFER HABITS</span>
        <h1>Make every click<br/><em>safer.</em></h1>
        <p>Create an account to start reviewing suspicious URL characteristics.</p>
        <div className="orb"><ShieldCheck size={70}/></div>
      </div>
    </section>
    <section className="auth-side">
      <form className="auth-form" onSubmit={submit}>
        <span className="auth-icon"><UserRound/></span>
        <span className="eyebrow">CREATE ACCOUNT</span>
        <h2>Join PhishGuard</h2><p>Set up your security workspace.</p>
        {error && <div className="error">{error}</div>}
        <label>Full name</label>
        <div className="field"><UserRound size={18}/><input value={name} onChange={e=>setName(e.target.value)} minLength={2} required placeholder="Your name"/></div>
        <label>Email address</label>
        <div className="field"><Mail size={18}/><input type="email" value={email} onChange={e=>setEmail(e.target.value)} required placeholder="you@example.com"/></div>
        <label>Password</label>
        <div className="field"><LockKeyhole size={18}/><input type="password" value={password} onChange={e=>setPassword(e.target.value)} minLength={8} maxLength={128} required placeholder="At least 8 characters"/></div>
        <button className="primary wide" disabled={busy}>{busy ? "Creating account..." : "Create account"}</button>
        <p className="center">Already registered? <Link to="/login">Sign in</Link></p>
      </form>
    </section>
  </div>;
}
