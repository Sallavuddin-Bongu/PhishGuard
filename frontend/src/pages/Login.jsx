import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { LockKeyhole, Mail, ShieldCheck } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login, user } = useAuth();
  const navigate = useNavigate();
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
      await login(email, password);
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
      <div className="hero">
        <span className="eyebrow">INTELLIGENT URL PROTECTION</span>
        <h1>Stay one step<br/>ahead of <em>threats.</em></h1>
        <p>Analyze suspicious links, understand warning signs, and make safer browsing decisions.</p>
        <div className="orb"><ShieldCheck size={70}/></div>
      </div>
    </section>
    <section className="auth-side">
      <form className="auth-form" onSubmit={submit}>
        <span className="auth-icon"><LockKeyhole/></span>
        <span className="eyebrow">SECURE ACCESS</span>
        <h2>Welcome back</h2><p>Sign in to your security dashboard.</p>
        {error && <div className="error">{error}</div>}
        <label>Email address</label>
        <div className="field"><Mail size={18}/><input type="email" value={email} onChange={e=>setEmail(e.target.value)} required placeholder="you@example.com"/></div>
        <label>Password</label>
        <div className="field"><LockKeyhole size={18}/><input type="password" value={password} onChange={e=>setPassword(e.target.value)} required placeholder="Your password"/></div>
        <div className="form-meta"><span>Secure sign in</span><Link to="/forgot-password">Forgot password?</Link></div>
        <button className="primary wide" disabled={busy}>{busy ? "Signing in..." : "Sign in securely"}</button>
        <p className="center">New to PhishGuard? <Link to="/signup">Create account</Link></p>
      </form>
    </section>
  </div>;
}
