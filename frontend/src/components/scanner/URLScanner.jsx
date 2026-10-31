import { Globe, Search } from "lucide-react";

export default function URLScanner({ url, setUrl, busy, onSubmit }) {
  return (
    <form className="scan-form" onSubmit={onSubmit}>
      <div className="url-input">
        <Globe size={19} />
        <input value={url} onChange={e => setUrl(e.target.value)}
          placeholder="https://example.com" required maxLength={2048} />
      </div>
      <button className="primary" disabled={busy}>
        <Search size={17} />{busy ? "Analyzing..." : "Analyze URL"}
      </button>
    </form>
  );
}
