
import { useEffect, useState } from "react";
import {
  Search,
  History as HistoryIcon,
  Trash2,
  CheckCircle
} from "lucide-react";

import Layout from "../components/common/Layout";
import RiskBadge from "../components/common/RiskBadge";
import { apiRequest } from "../services/api";

export default function History() {
  const [items, setItems] = useState([]);
  const [query, setQuery] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  // Load scan history
  const loadHistory = async () => {
    try {
      setError("");

      const data = await apiRequest("/api/history/?limit=100");
      setItems(data.items || []);
    } catch (err) {
      setError(err.message || "Unable to load scan history.");
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  // Format date and time
  const formatDate = (value) => {
    if (!value) return "Date unavailable";

    let dateValue = value;

    if (
      typeof value === "string" &&
      !/(Z|[+-]\d{2}:?\d{2})$/i.test(value)
    ) {
      dateValue += "Z";
    }

    const date = new Date(dateValue);

    if (Number.isNaN(date.getTime())) {
      return "Invalid date";
    }

    return date.toLocaleString();
  };

  // Clear all scan history
  const clearHistory = async () => {
    if (items.length === 0) return;

    const confirmed = window.confirm(
      "Are you sure you want to permanently delete all your scan history?"
    );

    if (!confirmed) return;

    try {
      setLoading(true);
      setError("");
      setSuccess("");

      const response = await apiRequest("/api/history/", {
        method: "DELETE"
      });

      setItems([]);
      setQuery("");

      setSuccess(
        response.message || "Scan history cleared successfully!"
      );
    } catch (err) {
      setError(err.message || "Unable to clear scan history.");
    } finally {
      setLoading(false);
    }
  };

  // Search scans
  const filtered = items.filter((item) =>
    (item.url || "").toLowerCase().includes(query.toLowerCase()) ||
    (item.risk_level || "").toLowerCase().includes(query.toLowerCase())
  );

  return (
    <Layout
      title="Security Scan History"
      subtitle="Review and manage your previous URL analyses."
    >
      {/* Clear History Button - Top Right */}
      <div className="mb-5 flex justify-end">
        <button
  type="button"
  onClick={clearHistory}
  disabled={loading || items.length === 0}
  style={{
    backgroundColor: "#dc2626",
    color: "#ffffff",
    border: "none",
    padding: "10px 20px",
    borderRadius: "8px",
    fontSize: "14px",
    fontWeight: "600",
    display: "flex",
    alignItems: "center",
    gap: "8px",
    cursor: loading || items.length === 0 ? "not-allowed" : "pointer",
    opacity: loading || items.length === 0 ? 0.5 : 1
  }}
>
  <Trash2 size={17} color="#ffffff" />
  {loading ? "Clearing..." : "Clear History"}
</button>
      </div>

      {/* History Panel */}
      <section className="panel">
        <div className="panel-head">
          <div>
            <h2>Recent Scan Activity</h2>
            <p>{filtered.length} results</p>
          </div>

          {/* Search */}
          <div className="search">
            <Search size={16} />

            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search scanned URLs..."
            />
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="error mb-4">
            {error}
          </div>
        )}

        {/* Success Message */}
        {success && (
          <div className="mb-4 flex items-center gap-2 rounded-lg border border-green-700 bg-green-950/40 p-3 text-sm text-green-400">
            <CheckCircle size={18} />
            {success}
          </div>
        )}

        {/* Scan History Table */}
        {filtered.length > 0 ? (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>URL</th>
                  <th>RISK</th>
                  <th>SCORE</th>
                  <th>DATE</th>
                </tr>
              </thead>

              <tbody>
                {filtered.map((item) => (
                  <tr key={item.id}>
                    <td className="truncate">
                      {item.url}
                    </td>

                    <td>
                      <RiskBadge level={item.risk_level} />
                    </td>

                    <td>
                      {item.risk_score}/100
                    </td>

                    <td>
                      {formatDate(item.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          /* Empty State */
          <div className="empty">
            <HistoryIcon />

            <h3>
              {items.length === 0
                ? "No scan history"
                : "No matching scans"}
            </h3>

            <p>
              {items.length === 0
                ? "Your scan history is empty. Scan a URL to get started."
                : "Try a different search filter."}
            </p>

            <a href="/scanner">
              Open scanner →
            </a>
          </div>
        )}
      </section>
    </Layout>
  );
}
