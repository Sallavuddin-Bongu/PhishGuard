
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Mail } from "lucide-react";
import { apiRequest } from "../services/api";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setMessage("");
    setLoading(true);

    try {
      const result = await apiRequest("/api/auth/forgot-password", {
        method: "POST",
        body: JSON.stringify({ email }),
      });

      setMessage(result.message);

      const cleanEmail = email.trim().toLowerCase();

      sessionStorage.setItem("phishguard_reset_email", cleanEmail);

      navigate("/reset-password", {
        state: { email: cleanEmail },
      });

    } catch (err) {
      setError(err.message || "Unable to request a verification code.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="simple-page">
      <section className="simple-card">

        <span className="auth-icon">
          <Mail />
        </span>

        <h2>Password recovery</h2>

        <p>
          Enter your registered email address to receive a six-digit OTP.
        </p>

        <form onSubmit={handleSubmit}>
          <label htmlFor="reset-email">
            Email address
          </label>

          <div className="field">
            <input
              id="reset-email"
              type="email"
              autoComplete="email"
              placeholder="Enter your email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </div>

          {message && (
            <p className="success" role="status">
              {message}
            </p>
          )}

          {error && (
            <p className="error" role="alert">
              {error}
            </p>
          )}

          <button
            className="primary wide"
            type="submit"
            disabled={loading}
          >
            {loading ? "Sending OTP..." : "Send OTP"}
          </button>
        </form>

        <p>
          Remember your password?{" "}
          <Link to="/login">Sign in</Link>
        </p>

      </section>
    </div>
  );
}
