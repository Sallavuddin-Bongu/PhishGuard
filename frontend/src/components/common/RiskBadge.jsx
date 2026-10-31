export default function RiskBadge({ level = "Low" }) {
  return (
    <span className={`risk risk-${String(level).toLowerCase()}`}>
      <i />{level} risk
    </span>
  );
}
