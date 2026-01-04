import { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';
import { TrendingUp, Activity, Info, Lightbulb } from 'lucide-react';
import { useCrypto } from '../store';
import { cryptoOptions } from '../data/mockData';
import Chatbot from '../components/Chatbot';
import '../styles/timeline.css';

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
          {entry.name}: <strong>{entry.value}</strong>
        </p>
      ))}
    </div>
  );
};

export default function Timeline() {
  const { fetchTimeline } = useCrypto();
  const [selectedCrypto, setSelectedCrypto] = useState('BTC');
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      setError(null);
      try {
        const result = await fetchTimeline(selectedCrypto, 30);
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [selectedCrypto, fetchTimeline]);

  const currentSentiment = data.length > 0 ? data[data.length - 1].sentiment : 0;
  const avgSentiment = data.length > 0
    ? Math.round(data.reduce((sum, item) => sum + item.sentiment, 0) / data.length)
    : 0;
  const selectedCryptoLabel = cryptoOptions.find(opt => opt.value === selectedCrypto)?.label || selectedCrypto;

  if (loading) {
    return (
      <div className="timeline-page">
        <div className="timeline-loading">
          <div className="loading-spinner"></div>
          <p style={{ color: '#64748b' }}>Chargement de la timeline...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="timeline-page">
        <div className="timeline-error">
          <p style={{ color: '#ef4444' }}>Erreur: {error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="timeline-page">
      {/* Header */}
      <header className="timeline-header">
        <div className="timeline-title-section">
          <h1>Sentiment Timeline</h1>
          <p>Evolution du sentiment sur les 30 derniers jours</p>
        </div>

        <div className="timeline-controls">
          <div className="crypto-selector">
            <label>Crypto:</label>
            <select
              className="crypto-select"
              value={selectedCrypto}
              onChange={(e) => setSelectedCrypto(e.target.value)}
            >
              {cryptoOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div className="timeline-stats">
            <div className="stat-mini-card">
              <div className="label">Actuel</div>
              <div className={`value ${currentSentiment >= 0 ? 'positive' : 'negative'}`}>
                {currentSentiment}
              </div>
            </div>
            <div className="stat-mini-card">
              <div className="label">Moyenne</div>
              <div className={`value ${avgSentiment >= 0 ? 'positive' : 'negative'}`}>
                {avgSentiment}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Chart Card */}
      <div className="chart-card">
        <div className="chart-header">
          <div className="chart-title">
            <div className="chart-title-icon">
              <Activity size={22} />
            </div>
            <div className="chart-title-text">
              <h2>Evolution du Sentiment - {selectedCryptoLabel}</h2>
              <span>Score: -100 (bearish) a +100 (bullish)</span>
            </div>
          </div>
          <div className="chart-legend">
            <div className="legend-item">
              <span className="legend-dot sentiment"></span>
              Sentiment
            </div>
            <div className="legend-item">
              <span className="legend-dot ma"></span>
              MA 7 jours
            </div>
          </div>
        </div>

        <div className="chart-container">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis
                dataKey="date"
                stroke="#4b5563"
                tick={{ fill: '#6b7280', fontSize: 12 }}
              />
              <YAxis
                domain={[-100, 100]}
                ticks={[-100, -50, 0, 50, 100]}
                stroke="#4b5563"
                tick={{ fill: '#6b7280', fontSize: 12 }}
              />
              <Tooltip content={<CustomTooltip />} />
              <ReferenceLine y={0} stroke="#374151" strokeDasharray="3 3" />
              <Line
                type="monotone"
                dataKey="sentiment"
                name="Sentiment"
                stroke="#10b981"
                strokeWidth={2.5}
                dot={{ r: 3, fill: '#10b981' }}
                activeDot={{ r: 5, fill: '#34d399' }}
              />
              <Line
                type="monotone"
                dataKey="ma7"
                name="MA 7 jours"
                stroke="#ef4444"
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Info Cards */}
      <div className="timeline-info">
        <div className="info-card">
          <div className="info-card-header">
            <div className="info-card-icon">
              <Info size={20} />
            </div>
            <h3>Comment lire ce graphique</h3>
          </div>
          <p>
            Le score de sentiment varie de -100 (tres negatif) a +100 (tres positif).
            La ligne verte represente le sentiment quotidien, tandis que la ligne rouge
            pointillee montre la moyenne mobile sur 7 jours pour lisser les fluctuations.
          </p>
        </div>

        <div className="info-card">
          <div className="info-card-header">
            <div className="info-card-icon">
              <Lightbulb size={20} />
            </div>
            <h3>Interpretation</h3>
          </div>
          <p>
            Un sentiment positif persistant peut indiquer une tendance haussiere,
            tandis qu'un sentiment negatif prolonge peut signaler une pression
            baissiere. La divergence entre le prix et le sentiment peut reveler
            des opportunites.
          </p>
        </div>
      </div>

      <Chatbot />
    </div>
  );
}
