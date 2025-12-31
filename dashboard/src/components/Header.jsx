import { useState } from 'react';

// Mock des styles (à remplacer par l'import réel)
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
    transition: 'all 0.2s ease',
    cursor: 'pointer',
    border: 'none',
    background: 'transparent'
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

// Composant NavLink simplifié (simulation sans react-router-dom)
function NavLink({ to, children, isActive, onClick }) {
  return (
    <button
      onClick={() => onClick(to)}
      style={{
        ...headerStyles.link,
        ...(isActive ? headerStyles.activeLink : {})
      }}
    >
      {children}
    </button>
  );
}

// Composant Header
export default function Header({ activePath = '/', onNavigate = () => {} }) {
  return (
    <header style={headerStyles.header}>
      <h1 style={headerStyles.title}>◈ Crypto Dashboard</h1>
      
      <nav style={headerStyles.nav}>
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            isActive={activePath === item.path}
            onClick={onNavigate}
          >
            <span>{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>
    </header>
  );
}

// Demo interactif
function Demo() {
  const [currentPath, setCurrentPath] = useState('/');
  
  const pageContent = {
    '/': '📊 Overview Page - Dashboard principal avec métriques et graphiques',
    '/timeline': '📈 Timeline Page - Évolution temporelle des crypto-monnaies',
    '/analysis': '🔍 Analysis Page - Analyses détaillées et insights',
    '/events': '📰 Events Page - Actualités et événements du marché'
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)'
    }}>
      <Header 
        activePath={currentPath} 
        onNavigate={setCurrentPath}
      />
      
      <div style={{
        padding: '60px 40px',
        color: '#e5e7eb',
        textAlign: 'center'
      }}>
        <div style={{
          background: 'rgba(30, 41, 59, 0.5)',
          backdropFilter: 'blur(20px)',
          borderRadius: '20px',
          padding: '60px 40px',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          maxWidth: '800px',
          margin: '0 auto'
        }}>
          <h2 style={{
            fontSize: '2.5rem',
            marginBottom: '20px',
            color: '#10B981'
          }}>
            {pageContent[currentPath].split(' - ')[0]}
          </h2>
          <p style={{
            fontSize: '1.125rem',
            color: '#94a3b8',
            lineHeight: '1.8'
          }}>
            {pageContent[currentPath].split(' - ')[1]}
          </p>
        </div>
        
        <div style={{
          marginTop: '40px',
          padding: '20px',
          background: 'rgba(59, 130, 246, 0.1)',
          borderRadius: '12px',
          border: '1px solid rgba(59, 130, 246, 0.2)',
          maxWidth: '600px',
          margin: '40px auto 0'
        }}>
          <p style={{ 
            color: '#60a5fa', 
            fontSize: '0.875rem',
            margin: 0
          }}>
            💡 Cliquez sur les éléments de navigation pour changer de page
          </p>
        </div>
      </div>
    </div>
  );
}

export { Demo };