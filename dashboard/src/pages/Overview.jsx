import { useCrypto } from '../store';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import { TrendingUp, TrendingDown, Activity, BarChart3 } from 'lucide-react';
import Chatbot from '../components/Chatbot';
import '../styles/overview.css';

// Crypto icons
const CryptoIcon = ({ symbol }) => {
  const icons = {
    BTC: 'https://cryptologos.cc/logos/bitcoin-btc-logo.svg',
    ETH: 'https://cryptologos.cc/logos/ethereum-eth-logo.svg',
    SOL: 'https://cryptologos.cc/logos/solana-sol-logo.svg'
  };
  return icons[symbol] ? (
    <img src={icons[symbol]} alt={symbol} style={{ width: 28, height: 28 }} />
  ) : (
    <span>{symbol}</span>
  );
};

// Custom Tooltip
const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload) return null;
  return (
    <div style={{
      background: 'rgba(15, 15, 25, 0.95)',
      backdropFilter: 'blur(10px)',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      borderRadius: '12px',
      padding: '14px 18px',
      boxShadow: '0 10px 40px rgba(0, 0, 0, 0.4)'
    }}>
      <p style={{ color: '#fff', fontWeight: '600', marginBottom: '8px' }}>{label}</p>
      {payload.map((entry, index) => (
        <p key={index} style={{ color: entry.color, margin: '4px 0', fontSize: '0.9rem' }}>
          {entry.name}: <strong>${entry.value?.toLocaleString()}</strong>
        </p>
      ))}
    </div>
  );
};

export default function Overview() {
  const { cryptos, chartData, sentiment, loading, error } = useCrypto();

  if (loading) {
    return (
      <div className="overview-page">
        <div className="overview-loading">
          <div className="loading-spinner"></div>
          <p style={{ color: '#64748b' }}>Chargement...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="overview-page">
        <div className="overview-error">
          <p style={{ color: '#ef4444' }}>Erreur: {error}</p>
        </div>
      </div>
    );
  }

  const sentimentValue = Math.round(sentiment.score * 100);

  // Utiliser le label de l'API
  const apiLabel = sentiment.label || 'Neutral';

  // Mapper le label API vers la couleur
  const getSentimentColor = (label) => {
    const normalizedLabel = label.toLowerCase();
    if (normalizedLabel === 'positive' || normalizedLabel === 'positif') return '#10b981';
    if (normalizedLabel === 'negative' || normalizedLabel === 'negatif') return '#ef4444';
    return '#f59e0b'; // Neutral
  };

  // Mapper le label API vers le français
  const getSentimentLabelFr = (label) => {
    const normalizedLabel = label.toLowerCase();
    if (normalizedLabel === 'positive' || normalizedLabel === 'positif') return 'Positif';
    if (normalizedLabel === 'negative' || normalizedLabel === 'negatif') return 'Négatif';
    return 'Neutre';
  };

  const sentimentColor = getSentimentColor(apiLabel);
  const sentimentLabel = getSentimentLabelFr(apiLabel);

  // Gauge calculations
  const circumference = 2 * Math.PI * 70;
  const strokeDashoffset = circumference - (sentimentValue / 100) * circumference;

  return (
    <div className="overview-page">
      {/* Header */}
      <header className="overview-header">
        <h1>Dashboard Overview</h1>
        <p>Vue d'ensemble du marche crypto et sentiment</p>
      </header>

      {/* Metrics Grid */}
      <section className="metrics-grid">
        {cryptos.map((crypto, index) => (
          <div
            key={index}
            className="metric-card"
            style={{ '--accent-color': crypto.change24h >= 0 ? '#10b981' : '#ef4444' }}
          >
            <div className="metric-header">
              <div className={`metric-icon ${crypto.symbol.toLowerCase()}`}>
                <CryptoIcon symbol={crypto.symbol} />
              </div>
              <div className="metric-info">
                <h3>{crypto.name}</h3>
                <span className="symbol">{crypto.symbol}</span>
              </div>
            </div>
            <div className="metric-value">
              ${crypto.price.toLocaleString()}
            </div>
            <div className={`metric-change ${crypto.change24h >= 0 ? 'positive' : 'negative'}`}>
              {crypto.change24h >= 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
              {crypto.change24h >= 0 ? '+' : ''}{crypto.change24h.toFixed(2)}%
            </div>
          </div>
        ))}
      </section>

      {/* Main Content */}
      <section className="overview-content">
        {/* Chart Card */}
        <div className="chart-card">
          <div className="chart-header">
            <div className="chart-title">
              <div className="chart-title-icon">
                <BarChart3 size={20} />
              </div>
              <div>
                <h2>Bitcoin (7 jours)</h2>
                <span>Evolution du prix</span>
              </div>
            </div>
          </div>
          <div style={{ height: 320 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 10, right: 20, left: 10, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis
                  dataKey="name"
                  stroke="#4b5563"
                  tick={{ fill: '#6b7280', fontSize: 12 }}
                />
                <YAxis
                  stroke="#4b5563"
                  tick={{ fill: '#6b7280', fontSize: 12 }}
                  tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`}
                />
                <Tooltip content={<CustomTooltip />} />
                <Line
                  type="monotone"
                  dataKey="value"
                  name="Prix"
                  stroke="#6366f1"
                  strokeWidth={3}
                  dot={{ r: 4, fill: '#6366f1' }}
                  activeDot={{ r: 6, fill: '#818cf8' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Sentiment Card */}
        <div className="sentiment-card">
          <div className="sentiment-header">
            <h2>Sentiment Global</h2>
            <span>Analyse du marche</span>
          </div>

          <div className="sentiment-gauge">
            <div className="gauge-circle">
              <svg width="180" height="180" viewBox="0 0 180 180">
                <circle
                  className="gauge-bg"
                  cx="90"
                  cy="90"
                  r="70"
                />
                <circle
                  className="gauge-fill"
                  cx="90"
                  cy="90"
                  r="70"
                  stroke={sentimentColor}
                  strokeDasharray={circumference}
                  strokeDashoffset={strokeDashoffset}
                  style={{ transform: 'rotate(-90deg)', transformOrigin: '90px 90px' }}
                />
              </svg>
              <div className="gauge-value">
                <span className="number" style={{ color: sentimentColor }}>{sentimentValue}</span>
                <span className="label">{sentimentLabel}</span>
              </div>
            </div>
          </div>

          <div className="sentiment-bar">
            <div className="sentiment-bar-track">
              <div
                className="sentiment-bar-fill"
                style={{
                  width: `${sentimentValue}%`,
                  background: `linear-gradient(90deg, #ef4444 0%, #f59e0b 50%, #10b981 100%)`
                }}
              />
            </div>
            <div className="sentiment-bar-labels">
              <span>Bearish</span>
              <span>Bullish</span>
            </div>
          </div>
        </div>
      </section>

      <Chatbot />
    </div>
  );
}
