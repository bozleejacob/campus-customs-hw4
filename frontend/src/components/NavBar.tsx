import { NavLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import './NavBar.css'

const NAV_LINKS = [
  { to: '/', label: 'Home' },
  { to: '/products', label: 'Products' },
  { to: '/about', label: 'About Us' },
]

function NavBar() {
  const { user, logout } = useAuth()

  return (
    <header className="nav-bar">
      <div className="nav-bar__brand">Campus Customs</div>
      <nav>
        <ul className="nav-bar__links">
          {NAV_LINKS.map(({ to, label }) => (
            <li key={to}>
              <NavLink
                to={to}
                end={to === '/'}
                className={({ isActive }) =>
                  isActive ? 'nav-bar__link nav-bar__link--active' : 'nav-bar__link'
                }
              >
                {label}
              </NavLink>
            </li>
          ))}
          {user ? (
            <>
              <li className="nav-bar__greeting">Hi, {user.first_name}</li>
              <li>
                <button type="button" className="nav-bar__link nav-bar__logout" onClick={logout}>
                  Log Out
                </button>
              </li>
            </>
          ) : (
            <>
              <li>
                <NavLink
                  to="/login"
                  className={({ isActive }) =>
                    isActive ? 'nav-bar__link nav-bar__link--active' : 'nav-bar__link'
                  }
                >
                  Login
                </NavLink>
              </li>
              <li>
                <NavLink
                  to="/create-account"
                  className={({ isActive }) =>
                    isActive ? 'nav-bar__link nav-bar__link--active' : 'nav-bar__link'
                  }
                >
                  Create Account
                </NavLink>
              </li>
            </>
          )}
        </ul>
      </nav>
    </header>
  )
}

export default NavBar
