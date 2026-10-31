import { ShieldCheck } from "lucide-react";
import Layout from "../components/common/Layout";

const tips = [
  ["Inspect the full domain", "Look for misspellings, unexpected subdomains, and lookalike characters."],
  ["Treat urgency with caution", "Unexpected threats of account closure or demands for immediate action may be deceptive."],
  ["HTTPS is not enough", "Encryption does not prove that a website owner is legitimate."],
  ["Protect verification codes", "Never share passwords or one-time codes through unsolicited links."],
  ["Navigate independently", "When unsure, type the known official website address yourself."],
  ["Verify unusual requests", "Contact the organization through a trusted, independently obtained channel."]
];

export default function SecurityTips() {
  return <Layout title="Security Tips" subtitle="Practical habits for reducing phishing risk.">
    <div className="tips">{tips.map(([title, text], i)=><section className="panel tip" key={title}>
      <span className="tip-number">0{i+1}</span><ShieldCheck/><h3>{title}</h3><p>{text}</p>
    </section>)}</div>
  </Layout>;
}
