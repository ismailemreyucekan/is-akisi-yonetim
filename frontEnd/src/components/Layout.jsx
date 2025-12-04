import { Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, Workflow, Plus, Sun, Moon, ClipboardList } from 'lucide-react'
import { useTheme } from '../contexts/ThemeContext'
import './Layout.css'

const Layout = ({ children }) => {
  const location = useLocation()
  const { theme, toggleTheme } = useTheme()

  return (
    <div className="layout">
      <nav className="navbar">
        <div className="nav-container">
          <div className="nav-left">
            <button
              onClick={toggleTheme}
              className="theme-toggle"
              title={theme === 'light' ? 'Karanlık moda geç' : 'Aydınlık moda geç'}
            >
              {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
            </button>
            <div className="nav-brand">
              <Workflow className="brand-icon" />
              <span>İş Akışı Yönetimi</span>
            </div>
          </div>
          <div className="nav-links">
            <Link
              to="/"
              className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
            >
              <LayoutDashboard size={18} />
              <span>Dashboard</span>
            </Link>
            <Link
              to="/workflows"
              className={`nav-link ${
                location.pathname.startsWith('/workflows') ? 'active' : ''
              }`}
            >
              <Workflow size={18} />
              <span>İş Akışları</span>
            </Link>
            <Link
              to="/issues"
              className={`nav-link ${
                location.pathname.startsWith('/issues') ? 'active' : ''
              }`}
            >
              <ClipboardList size={18} />
              <span>Issue Yönetimi</span>
            </Link>
            <Link
              to="/workflows/new"
              className="nav-link btn-primary"
            >
              <Plus size={18} />
              <span>Yeni İş Akışı</span>
            </Link>
          </div>
        </div>
      </nav>
      <main className="main-content">{children}</main>
    </div>
  )
}

export default Layout

