import React from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import {
  ShieldCheck, LayoutDashboard, ScanSearch, History,
  ChartNoAxesColumn, ShieldAlert, BookOpen, UserRound,
  Settings, LogOut, Activity
} from 'lucide-react'
import { useAuth } from '../../context/AuthContext'

const links = [
  { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
  { label: 'URL Scanner', path: '/scanner', icon: ScanSearch },
  { label: 'Scan History', path: '/history', icon: History },
  { label: 'Analytics', path: '/analytics', icon: ChartNoAxesColumn },
  { label: 'Threat Intelligence', path: '/threat-intelligence', icon: ShieldAlert },
  { label: 'Security Tips', path: '/security-tips', icon: BookOpen },
  { label: 'Profile', path: '/profile', icon: UserRound },
  { label: 'Settings', path: '/settings', icon: Settings },
]

export default function Layout({ children }) {
  const auth = useAuth()
  const navigate = useNavigate()
  const user = auth?.user

  async function handleLogout() {
    try {
      if (auth?.logout) await auth.logout()
    } finally {
      navigate('/login')
    }
  }

  return (
    <div className="pg-shell">
      <aside className="pg-sidebar">
        <div className="pg-brand">
          <div className="pg-brand-icon"><ShieldCheck size={26} /></div>
          <div>
            <strong>PhishGuard</strong>
            <span>THREAT DETECTION</span>
          </div>
        </div>

        <div className="pg-nav-label">WORKSPACE</div>
        <nav className="pg-nav">
          {links.map(({ label, path, icon: Icon }) => (
            <NavLink
              key={path}
              to={path}
              className={({ isActive }) =>
                `pg-nav-link${isActive ? ' pg-nav-active' : ''}`
              }
            >
              <Icon size={18} strokeWidth={1.8} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="pg-sidebar-footer">
          <div className="pg-online"><span /> Protection system ready</div>
          <div className="pg-user">
            <div className="pg-avatar">
              {(user?.name || user?.email || 'U').charAt(0).toUpperCase()}
            </div>
            <div className="pg-user-text">
              <strong>{user?.name || 'Security Analyst'}</strong>
              <span>{user?.email || 'Signed-in user'}</span>
            </div>
          </div>
          <button className="pg-logout" onClick={handleLogout}>
            <LogOut size={17} /> Sign out
          </button>
        </div>
      </aside>

      <main className="pg-main">
        <header className="pg-topbar">
          <div>
            <div className="pg-breadcrumb">
              <Activity size={14} /> SECURITY CENTER
            </div>
            <h1>{links.find(x => x.path === window.location.pathname)?.label || 'PhishGuard'}</h1>
          </div>
          <div className="pg-top-status"><span /> SYSTEM ACTIVE</div>
        </header>
        <div className="pg-page">
          {children || <Outlet />}
        </div>
      </main>
    </div>
  )
}
