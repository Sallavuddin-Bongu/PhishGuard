import { BrowserRouter, Navigate, Route, Routes, Link } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import ProtectedRoute from "./components/common/ProtectedRoute";
import Sidebar from "./components/common/Sidebar";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import Scanner from "./pages/Scanner";
import History from "./pages/History";
import Analytics from "./pages/Analytics";
import ThreatIntelligence from "./pages/ThreatIntelligence";
import SecurityTips from "./pages/SecurityTips";
import Profile from "./pages/Profile";
import Settings from "./pages/Settings";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import NotFound from "./pages/NotFound";
import "./index.css";

function Home() {
  const {user,loading} = useAuth();
  if (loading) return <div className="loading">Loading PhishGuard...</div>;
  return <Navigate to={user ? "/dashboard" : "/login"} replace/>;
}

function Layout({title,subtitle,children}) {
  const {user,logout} = useAuth();
  return <div className="app-shell">
    <aside className="sidebar">
      <Link className="brand" to="/dashboard"><span className="brand-shield">◆</span><span>Phish<b>Guard</b></span></Link>
      <div className="nav-label">WORKSPACE</div><Sidebar/>
      <div className="sidebar-bottom"><div className="avatar">{(user?.name || "U")[0].toUpperCase()}</div>
        <div className="user-meta"><strong>{user?.name}</strong><small>{user?.email}</small></div>
        <button className="logout" onClick={logout} title="Sign out">↗</button>
      </div>
    </aside>
    <main className="main-area"><header className="topbar"><span>PHISHGUARD / <b>{title.toUpperCase()}</b></span><span className="status"><i/>SECURITY WORKSPACE</span></header>
      <div className="page-content"><div className="page-heading"><span className="eyebrow">SECURITY CENTER</span><h1>{title}</h1><p>{subtitle}</p></div>
      {children}<footer>PhishGuard · Analyze responsibly. Verify independently.</footer></div>
    </main>
  </div>;
}

function Wrapped({title,subtitle,children}) {
  return <Layout title={title} subtitle={subtitle}>{children}</Layout>;
}

function DashboardRoute() { return <Dashboard/>; }

function AppRoutes() {
  return <Routes>
    <Route path="/" element={<Home/>}/>
    <Route path="/login" element={<Login/>}/>
    <Route path="/signup" element={<Signup/>}/>
    <Route path="/forgot-password" element={<ForgotPassword/>}/>
    <Route path="/reset-password" element={<ResetPassword/>}/>
    <Route element={<ProtectedRoute/>}>
      <Route path="/dashboard" element={<DashboardRoute/>}/>
      <Route path="/scanner" element={<Scanner/>}/>
      <Route path="/history" element={<History/>}/>
      <Route path="/analytics" element={<Analytics/>}/>
      <Route path="/threat-intelligence" element={<ThreatIntelligence/>}/>
      <Route path="/security-tips" element={<SecurityTips/>}/>
      <Route path="/profile" element={<Profile/>}/>
      <Route path="/settings" element={<Settings/>}/>
    </Route>
    <Route path="*" element={<NotFound/>}/>
  </Routes>;
}

export default function App() {
  return <BrowserRouter><AuthProvider><AppRoutes/></AuthProvider></BrowserRouter>;
}
