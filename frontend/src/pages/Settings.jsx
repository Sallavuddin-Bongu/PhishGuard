import { Activity, LockKeyhole, Radar, Shield } from "lucide-react";
import Layout from "../components/common/Layout";

const rows = [
  [LockKeyhole, "Authentication", "Bearer-token authentication is enabled.", "Enabled"],
  [Radar, "URL analysis", "Heuristic URL analysis is active.", "Local"],
  [Activity, "Threat intelligence", "Live threat feeds are not configured.", "Not connected"],
  [Shield, "Privacy", "Do not submit passwords, private tokens, or sensitive URLs.", "Reminder"]
];

export default function Settings() {
  return <Layout title="Settings" subtitle="Review the active configuration of this PhishGuard MVP.">
    <section className="panel">{rows.map(([Icon,title,description,status])=><div className="setting-row" key={title}>
      <span className="setting-icon"><Icon/></span><div><b>{title}</b><p>{description}</p></div><em>{status}</em>
    </div>)}</section>
  </Layout>;
}
