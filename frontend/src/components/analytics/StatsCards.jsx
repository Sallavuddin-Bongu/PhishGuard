import { Activity, ShieldAlert, AlertTriangle, ShieldCheck } from "lucide-react";

export default function StatsCards({ stats }) {
  const cards = [
    [Activity, "Total scans", stats?.total_scans ?? "—", ""],
    [ShieldAlert, "High risk", stats?.high_risk ?? "—", "red"],
    [AlertTriangle, "Medium risk", stats?.medium_risk ?? "—", "amber"],
    [ShieldCheck, "Low risk", stats?.low_risk ?? "—", "green"]
  ];
  return <div className="stats">
    {cards.map(([Icon, label, value, tone]) => (
      <div className="stat" key={label}>
        <span className={`stat-icon ${tone}`}><Icon size={19}/></span>
        <small>{label}</small><strong>{value}</strong>
        <p>Based on your saved scans</p>
      </div>
    ))}
  </div>;
}
