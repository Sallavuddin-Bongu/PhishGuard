
export default function ScanResult({ result }) {
  if (!result) return null;

  const rawProbability = result.ml_phishing_probability;

  const riskScore =
    rawProbability !== null &&
    rawProbability !== undefined &&
    Number.isFinite(Number(rawProbability))
      ? Number(rawProbability) * 100
      : Number(result.risk_score ?? 0);

  const safeRisk = Math.min(100, Math.max(0, riskScore));
  const displayRisk = Math.round(safeRisk);

  const riskLevel =
    safeRisk >= 70
      ? "High Risk"
      : safeRisk >= 30
      ? "Medium Risk"
      : "Low Risk";

  const riskColor =
    safeRisk >= 70
      ? "#ef4444"
      : safeRisk >= 30
      ? "#eab308"
      : "#22c55e";

  // SVG circular chart settings
  const radius = 80;
  const circumference = 2 * Math.PI * radius;
  const progress = (safeRisk / 100) * circumference;

  return (
    <div className="mt-6 rounded-xl border border-slate-700 bg-slate-900 p-6 text-white">

      <h2 className="mb-4 text-xl font-bold">
        Scan Result
      </h2>

      <p className="mb-4 break-all text-sm text-slate-300">
        {result.url}
      </p>

      {/* Circular Pie / Risk Chart */}
      <div className="my-8 flex flex-col items-center justify-center">

        <svg
          viewBox="0 0 200 200"
          width="200"
          height="200"
          role="img"
          aria-label={`Phishing risk ${displayRisk}%`}
          style={{
            display: "block",
            width: "200px",
            height: "200px",
            maxWidth: "100%",
            overflow: "visible"
          }}
        >
          {/* Background circle */}
          <circle
            cx="100"
            cy="100"
            r={radius}
            fill="none"
            stroke="#334155"
            strokeWidth="20"
          />

          {/* Risk percentage circle */}
          <circle
            cx="100"
            cy="100"
            r={radius}
            fill="none"
            stroke={riskColor}
            strokeWidth="20"
            strokeDasharray={`${progress} ${circumference}`}
            strokeLinecap="round"
            transform="rotate(-90 100 100)"
          />

          {/* Percentage text */}
          <text
            x="100"
            y="95"
            textAnchor="middle"
            dominantBaseline="middle"
            fill={riskColor}
            fontSize="34"
            fontWeight="bold"
          >
            {displayRisk}%
          </text>

          <text
            x="100"
            y="125"
            textAnchor="middle"
            fill="#94a3b8"
            fontSize="11"
          >
            PHISHING RISK
          </text>
        </svg>

        <p
          className="mt-4 text-xl font-bold"
          style={{ color: riskColor }}
        >
          {riskLevel}
        </p>

        <p className="mt-1 text-sm text-slate-400">
          ML Phishing Probability
        </p>

      </div>

      {/* Result Details */}
      <div className="space-y-3 border-t border-slate-700 pt-5">

        <p>
          <strong>Verdict:</strong>{" "}
          {result.verdict ?? "Unavailable"}
        </p>

        <p>
          <strong>ML Classification:</strong>{" "}
          {result.ml_label ?? "Unavailable"}
        </p>

        <p>
          <strong>Binary Prediction:</strong>{" "}
          {result.ml_prediction ?? "Unavailable"}
        </p>

        <p>
          <strong>Risk Level:</strong> {riskLevel}
        </p>

        <p>
          <strong>Explanation:</strong>{" "}
          {result.explanation ?? "No explanation available."}
        </p>

        <p>
          <strong>Possible Harm:</strong>{" "}
          {result.harm_explanation ?? "No information available."}
        </p>

      </div>

      {/* Detection Findings */}
      {result.findings?.length > 0 && (
        <div className="mt-5">
          <h3 className="mb-2 font-semibold">
            Detection Findings
          </h3>

          <ul className="list-disc space-y-2 pl-5 text-sm text-slate-300">
            {result.findings.map((finding, index) => (
              <li key={index}>{finding}</li>
            ))}
          </ul>
        </div>
      )}

      <p className="mt-5 text-xs text-slate-400">
        The percentage represents the model's estimated
        phishing probability, not a guarantee of safety.
      </p>

    </div>
  );
}
