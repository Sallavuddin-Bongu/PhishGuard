import { NavLink } from "react-router-dom";
import {
  Home, ScanSearch, History, BarChart3, Radar, BookOpen,
  UserRound, Settings
} from "lucide-react";

const items = [
  ["/dashboard", Home, "Dashboard"],
  ["/scanner", ScanSearch, "URL Scanner"],
  ["/history", History, "Scan History"],
  ["/analytics", BarChart3, "Analytics"],
  ["/threat-intelligence", Radar, "Threat Intelligence"],
  ["/security-tips", BookOpen, "Security Tips"],
  ["/profile", UserRound, "Profile"],
  ["/settings", Settings, "Settings"]
];

export default function Sidebar() {
  return (
    <nav className="side-nav">
      {items.map(([path, Icon, label]) => (
        <NavLink key={path} to={path}
          className={({isActive}) => isActive ? "nav active" : "nav"}>
          <Icon size={18} /><span>{label}</span>
        </NavLink>
      ))}
    </nav>
  );
}
