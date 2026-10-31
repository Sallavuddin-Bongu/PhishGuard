import { useEffect, useState } from "react";
import { Activity, AlertTriangle, ShieldAlert, ShieldCheck } from "lucide-react";
import Layout from "../components/common/Layout";
import StatsCards from "../components/analytics/StatsCards";
import { apiRequest } from "../services/api";

export default function Analytics() {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => {
    apiRequest("/api/analytics/").then(setStats).catch(err=>setError(err.message));
  }, []);

  const total = stats?.total_scans || 0;
  const rows = [
    ["Low", stats?.low_risk || 0, "green"],
    ["Medium", stats?.medium_risk || 0, "amber"],
    ["High", stats?.high_risk || 0, "red"]
  ];

  return <Layout title="Analytics" subtitle="Understand the distribution of your recorded URL scans.">
    {error && <div className="error">{error}</div>}
    <StatsCards stats={stats}/>
    <section className="panel"><div className="panel-head"><div><h2>Risk distribution</h2><p>Breakdown of your scan history</p></div><Activity/></div>
      {rows.map(([label, count, tone])=><div className="distribution" key={label}>
        <div><span>{label} risk</span><b>{count} ({total ? Math.round(count/total*100) : 0}%)</b></div>
        <div className="distribution-track"><span className={tone} style={{width:`${total ? count/total*100 : 0}%`}}/></div>
      </div>)}
      {!total && <p className="note">Scan URLs to populate your analytics.</p>}
    </section>
  </Layout>;
}
