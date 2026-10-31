import { ShieldCheck } from "lucide-react";
import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <Link to="/dashboard" className="brand">
      <ShieldCheck /><span>Phish<b>Guard</b></span>
    </Link>
  );
}
