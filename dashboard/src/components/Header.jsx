import { NavLink } from 'react-router-dom';

// Styles du header
const headerStyles = {
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    background: 'rgba(10, 15, 26, 0.8)',
    backdropFilter: 'blur(20px)',
    borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
    position: 'sticky',
    top: 0,
    zIndex: 100,
    padding: '20px 40px'
  },
  title: {
    background: 'linear-gradient(135deg, #10B981 0%, #3B82F6 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
    fontWeight: '800',
    fontSize: '1.75rem',
    margin: 0
  },
  nav: {
    display: 'flex',
    gap: '8px',
    background: 'rgba(30, 41, 59, 0.4)',
    backdropFilter: 'blur(10px)',
    borderRadius: '14px',
    padding: '6px',
    border: '1px solid rgba(255, 255, 255, 0.1)'
  },
  link: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '10px 20px',
    borderRadius: '10px',
    textDecoration: 'none',
    color: '#94a3b8',
    fontSize: '0.9375rem',
    fontWeight: '500',
    transition: 'all 0.2s ease'
  },
  activeLink: {
    background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(59, 130, 246, 0.15) 100%)',
    color: '#10B981',
    boxShadow: '0 0 20px rgba(16, 185, 129, 0.3)',
    fontWeight: '600'
  }
};

// Données de navigation
const navItems = [
  { path: '/', label: 'Overview', icon: '📊' },
  { path: '/timeline', label: 'Timeline', icon: '📈' },
  { path: '/analysis', label: 'Analysis', icon: '🔍' },
  { path: '/events', label: 'Events', icon: '📰' }
];

// Composant Header
export default function Header() {
  return (
    <header style={headerStyles.header}>
      <h1 style={headerStyles.title}>◈ Crypto Dashboard</h1>

      <nav style={headerStyles.nav}>
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/'}
            style={({ isActive }) => ({
              ...headerStyles.link,
              ...(isActive ? headerStyles.activeLink : {})
            })}
          >
            <span>{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>
    </header>
  );
}
