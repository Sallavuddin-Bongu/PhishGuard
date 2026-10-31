
import { useState } from "react";
import { ScanSearch, ShieldCheck } from "lucide-react";
import Layout from "../components/common/Layout";
import URLScanner from "../components/scanner/URLScanner";
import ScanResult from "../components/scanner/ScanResult";
import { apiRequest } from "../services/api";

export default function Scanner() {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setResult(null);
    setError("");

    try {
      const data = await apiRequest("/api/scans/", {
        method: "POST",
        body: JSON.stringify({ url })
      });

      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <Layout
      title="URL Scanner"
      subtitle="Analyze URLs for suspicious characteristics."
    >
      <section className="panel scanner">
        <span className="scanner-icon">
          <ScanSearch size={25} />
        </span>

        <span className="eyebrow">URL RISK ANALYSIS</span>

        <h2>Is this link trustworthy?</h2>

        <p>
          The scanner inspects URL characteristics without
          opening the destination website.
        </p>

        <URLScanner
          url={url}
          setUrl={setUrl}
          busy={busy}
          onSubmit={submit}
        />

        {error && <div className="error">{error}</div>}

        <p className="note">
          <ShieldCheck size={15} />
          Calibrated ML, URL security indicators and threat
          intelligence analysis. No scanner guarantees perfect detection.
        </p>
      </section>

      <ScanResult result={result} />
    </Layout>
  );
}
