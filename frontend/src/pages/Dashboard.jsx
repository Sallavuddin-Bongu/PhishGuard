import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ShieldCheck, ScanSearch, ShieldAlert, AlertTriangle, Activity } from "lucide-react";
import Layout from "../components/common/Layout";
import StatsCards from "../components/analytics/StatsCards";
import RiskBadge from "../components/common/RiskBadge";
import { apiRequest } from "../services/api";

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [items, setItems] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([
      apiRequest("/api/analytics/"),
      apiRequest("/api/history/?limit=5")
    ]).then(([a, h]) => {
      setStats(a);
      setItems(h.items || []);
    }).catch(err => setError(err.message));
  }, []);

  return <Layout title="Dashboard" subtitle="Your security activity at a glance.">
    <section className="hero-card">
      <div><span className="eyebrow">PHISHGUARD PROTECTION</span>
        <h2>See the risks. Make safer clicks.</h2>
        <p>Analyze suspicious URLs and review warning signs before trusting them.</p>
        <Link to="/scanner" className="primary"><ScanSearch size={17}/>Scan a URL</Link>
      </div><ShieldCheck size={78}/>
    </section>
    {error && <div className="error">{error} — check that the backend is running and you're signed in.</div>}
    <div className="section-title"><h2>Security overview</h2><span><i className="green-dot"/> YOUR ACTIVITY</span></div>
    <StatsCards stats={stats}/>
    <section className="panel">
      <div className="panel-head"><div><h2>Recent scans</h2><p>Your latest saved URL analyses</p></div><Link to="/history">View all →</Link></div>
      {items.length ? <div className="table-wrap"><table><thead><tr><th>URL</th><th>RISK</th><th>SCORE</th><th>DATE</th></tr></thead>
        <tbody>{items.map(x=><tr key={x.id}><td className="truncate">{x.url}</td><td><RiskBadge level={x.risk_level}/></td><td>{x.risk_score}/100</td><td>{new Date(x.created_at).toLocaleDateString()}</td></tr>)}</tbody></table></div>
        : <div className="empty"><Activity/><h3>No scans yet</h3><p>Run your first URL analysis to populate your dashboard.</p></div>}
    </section>
  </Layout>;
}
