import { useState } from 'react';

// Mock des constantes (à remplacer par les imports réels)
const COLORS = {
  positive: '#10B981',
  negative: '#EF4444',
  neutral: '#6B7280',
  text: '#e5e7eb'
};

const metricCardStyles = {
  card: {
    position: 'relative',
    background: 'rgba(30, 41, 59, 0.5)',
    backdropFilter: 'blur(20px)',
    borderRadius: '20px',
    padding: '24px',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    transition: 'all 0.3s ease',
    cursor: 'pointer',
    overflow: 'hidden'
  },
  title: {
    fontSize: '0.875rem',
    color: '#94a3b8',
    marginBottom: '12px',
    fontWeight: '500'
  },
  value: {
    fontSize: '2rem',
    fontWeight: '700',
    color: COLORS.text,
    marginBottom: '12px',
    letterSpacing: '-0.02em'
  },
  changeContainer: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '6px',
    padding: '6px 12px',
    borderRadius: '8px',
    fontSize: '0.875rem',
    fontWeight: '600',
    transition: 'all 0.3s ease'
  }
};

// Composant MetricCard
export default function MetricCard({ title, value, change = 0 }) {
  const [isHovered, setIsHovered] = useState(false);

  // Déterminer la couleur selon le changement
  const getChangeColor = () => {
    if (change > 0) return COLORS.positive;
    if (change < 0) return COLORS.negative;
    return COLORS.neutral;
  };

  // Récupérer l'icône de flèche
  const getArrowIcon = () => {
    if (change > 0) {
      return (
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path
            d="M8 3L8 13M8 3L12 7M8 3L4 7"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      );
    }
    if (change < 0) {
      return (
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path
            d="M8 13L8 3M8 13L4 9M8 13L12 9"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      );
    }
    return null;
  };

  // Formater le changement
  const formatChange = () => {
    const formatted = Math.abs(change).toFixed(2);
    return change > 0 ? `+${formatted}%` : `${formatted}%`;
  };

  const changeColor = getChangeColor();

  // Styles dynamiques avec hover
  const cardStyle = {
    ...metricCardStyles.card,
    transform: isHovered ? 'translateY(-4px)' : 'translateY(0)',
    boxShadow: isHovered
      ? `0 20px 40px rgba(0, 0, 0, 0.3), 0 0 30px ${changeColor}30`
      : '0 4px 6px rgba(0, 0, 0, 0.1)',
    borderColor: isHovered ? `${changeColor}40` : 'rgba(255, 255, 255, 0.1)'
  };

  const changeContainerStyle = {
    ...metricCardStyles.changeContainer,
    color: changeColor,
    background: `${changeColor}26`,
    boxShadow: isHovered ? `0 0 15px ${changeColor}40` : 'none'
  };

  const gradientOverlayStyle = {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: `linear-gradient(135deg, ${changeColor}14 0%, transparent 50%)`,
    opacity: isHovered ? 1 : 0,
    transition: 'opacity 0.3s ease',
    pointerEvents: 'none',
    borderRadius: '20px'
  };

  return (
    <div
      style={cardStyle}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Gradient overlay */}
      <div style={gradientOverlayStyle} />

      {/* Content */}
      <div style={{ position: 'relative', zIndex: 1 }}>
        <p style={metricCardStyles.title}>{title}</p>
        <p style={metricCardStyles.value}>{value}</p>
        <div style={changeContainerStyle}>
          {getArrowIcon()}
          <span>{formatChange()}</span>
        </div>
      </div>
    </div>
  );
}

// Demo avec plusieurs cartes
function Demo() {
  const metrics = [
    { title: 'Bitcoin (BTC)', value: '$43,250.00', change: 2.45 },
    { title: 'Ethereum (ETH)', value: '$2,280.50', change: -1.32 },
    { title: 'Cardano (ADA)', value: '$0.58', change: 5.67 },
    { title: 'Solana (SOL)', value: '$98.42', change: 0 },
    { title: 'Polkadot (DOT)', value: '$7.23', change: -3.12 },
    { title: 'Chainlink (LINK)', value: '$14.87', change: 8.34 }
  ];

  return (
    <div
      style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
        padding: '60px 40px'
      }}
    >
      <h1
        style={{
          background: 'linear-gradient(135deg, #10B981 0%, #3B82F6 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
          fontWeight: '800',
          fontSize: '2.5rem',
          marginBottom: '40px',
          textAlign: 'center'
        }}
      >
        Crypto Metrics Dashboard
      </h1>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '24px',
          maxWidth: '1400px',
          margin: '0 auto'
        }}
      >
        {metrics.map((metric, index) => (
          <MetricCard
            key={index}
            title={metric.title}
            value={metric.value}
            change={metric.change}
          />
        ))}
      </div>

      <div
        style={{
          marginTop: '60px',
          padding: '24px',
          background: 'rgba(59, 130, 246, 0.1)',
          borderRadius: '16px',
          border: '1px solid rgba(59, 130, 246, 0.2)',
          maxWidth: '800px',
          margin: '60px auto 0',
          textAlign: 'center'
        }}
      >
        <p
          style={{
            color: '#60a5fa',
            fontSize: '0.9375rem',
            margin: 0,
            lineHeight: '1.6'
          }}
        >
          💡 Survolez les cartes pour voir les effets de hover avec lift, glow et
          gradient overlay colorés
        </p>
      </div>
    </div>
  );
}

export { Demo };