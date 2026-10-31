
import { Activity, Radar, ShieldCheck, Brain, Database } from "lucide-react";
import Layout from "../components/common/Layout";

export default function ThreatIntelligence() {
  return (
    <Layout
      title="Threat Intelligence"
      subtitle="Review the detection capabilities currently connected to PhishGuard."
    >
      <section className="panel prose">
        <span className="large-icon"><Radar /></span>
        <h2>Threat intelligence status</h2>

        <p>
          PhishGuard combines URL-characteristic heuristics with a trained
          machine-learning URL classifier.
        </p>

        <div className="info">
          <ShieldCheck />
          <div>
            <b>Available now</b>
            <p>
              URL structure analysis, heuristic risk scores, ML-based URL
              classification, explanations, scan history and analytics.
            </p>
          </div>
        </div>

        <div className="info">
          <Brain />
          <div>
            <b>Machine-learning model</b>
            <p>
              The trained URL model classifies submitted URLs as phishing
              or legitimate. Its classification is not a probability or
              a guarantee of safety.
            </p>
          </div>
        </div>

        <div className="info">
          <Database />
          <div>
            <b>Not connected yet</b>
            <p>
              Live malicious URL feeds and external website-reputation
              services have not been integrated.
            </p>
          </div>
        </div>

        <p className="note">
          Results are indicators, not a definitive safety verdict.
          A low risk score does not guarantee that a URL is safe.
        </p>
      </section>
    </Layout>
  );
}
