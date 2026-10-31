import { Link } from "react-router-dom";

export default function NotFound() {
  return <div className="simple-page"><section className="panel simple-card">
    <h2>404 — Page not found</h2><p>The requested PhishGuard page does not exist.</p>
    <Link className="primary wide link-button" to="/">Return home</Link>
  </section></div>;
}
