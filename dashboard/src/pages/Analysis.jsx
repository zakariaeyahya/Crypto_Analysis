import { useState, useEffect } from 'react';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ZAxis,
  ReferenceLine
} from 'recharts';
import {
  TrendingUp,
  Activity,
  BarChart3,
  Target,
  Lightbulb,
  Loader2
} from 'lucide-react';
import { useCrypto } from '../store';
import { cryptoOptions } from '../data/mockData';
import Chatbot from '../components/Chatbot';
import '../styles/analysis.css';

// Helper function
function getCorrelationLabel(corr) {
  const absCorr = Math.abs(corr);
  if (absCorr >= 0.7) return 'Forte';
  if (absCorr >= 0.4) return 'Moyenne';
  if (absCorr >= 0.2) return 'Faible';
  return 'Negligeable';
}

// Custom Tooltip
const ScatterTooltip = ({ active, payload }) => {
  if (!active || !payload || !payload[0]) return null;
  const data = payload[0].payload;

  return (
    <div style={{
      background: 'rgba(15, 15, 25, 0.95)',
      backdropFilter: 'blur(10px)',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      borderRadius: '12px',
      padding: '14px 18px',
      boxShadow: '0 10px 40px rgba(0, 0, 0, 0.4)'
    }}>
      <p style={{ color: '#fff', fontWeight: '600', marginBottom: '8px' }}>{data.date}</p>
      <p style={{ color: '#818cf8', margin: '4px 0', fontSize: '0.9rem' }}>
        Sentiment: <strong>{data.sentiment}</strong>
      </p>
      <p style={{ color: '#10b981', margin: '4px 0', fontSize: '0.9rem' }}>
        Var. Prix: <strong>{data.priceChange}%</strong>
      </p>
    </div>
  );
};

export default function Analysis() {
  const { fetchAnalysis } = useCrypto();
  const [selectedCrypto, setSelectedCrypto] = useState('BTC');
  const [stats, setStats] = useState(null);
  const [scatterData, setScatterData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      setError(null);
      try {
        const result = await fetchAnalysis(selectedCrypto, 30);
        setStats(result.stats);
        setScatterData(result.scatterData);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [selectedCrypto, fetchAnalysis]);

  if (loading) {
    return (
      <div className="analysis-page">
        <div className="analysis-loading">
          <div className="loading-spinner"></div>
          <p>Chargement de l'analyse...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analysis-page">
        <div className="analysis-error">
          <p>Erreur: {error}</p>
        </div>
      </div>
    );
  }

  const correlation = stats?.correlation || 0;
  const correlationLabel = stats?.correlationLabel || getCorrelationLabel(correlation);
  const correlationPercent = ((correlation + 1) / 2) * 100;

  return (
    <div className="analysis-page">
      {/* Header */}
      <header className="analysis-header">
        <div className="analysis-title-section">
          <h1>Analyse de Correlation</h1>
          <p>Relation entre sentiment social et variations de prix</p>
        </div>
        <div className="crypto-selector">
          <label>Crypto:</label>
          <select
            className="crypto-select"
            value={selectedCrypto}
            onChange={(e) => setSelectedCrypto(e.target.value)}
          >
            {cryptoOptions.map((crypto) => (
              <option key={crypto.value} value={crypto.value}>
                {crypto.label}
              </option>
            ))}
          </select>
        </div>
      </header>

      {/* Stats Grid */}
      <section className="stats-grid">
        <div className="stat-card" style={{ '--accent-color': correlation >= 0 ? '#10b981' : '#ef4444' }}>
          <div className="stat-card-header">
            <div className="stat-icon">
              <TrendingUp size={20} />
            </div>
            <span className="stat-label">Correlation Pearson</span>
          </div>
          <div className={`stat-value ${correlation >= 0 ? 'positive' : 'negative'}`}>
            {typeof correlation === 'number' ? correlation.toFixed(3) : 'N/A'}
          </div>
          <span className="stat-sublabel">{correlationLabel}</span>
        </div>

        <div className="stat-card" style={{ '--accent-color': '#6366f1' }}>
          <div className="stat-card-header">
            <div className="stat-icon">
              <Target size={20} />
            </div>
            <span className="stat-label">P-Value</span>
          </div>
          <div className="stat-value neutral">
            {stats?.pValue?.toFixed(4) || 'N/A'}
          </div>
          <span className="stat-sublabel">Significativite</span>
        </div>

        <div className="stat-card" style={{ '--accent-color': '#8b5cf6' }}>
          <div className="stat-card-header">
            <div className="stat-icon">
              <Activity size={20} />
            </div>
            <span className="stat-label">Observations</span>
          </div>
          <div className="stat-value neutral">
            {stats?.nObservations || 0}
          </div>
          <span className="stat-sublabel">Points de donnees</span>
        </div>

        <div className="stat-card" style={{ '--accent-color': '#ec4899' }}>
          <div className="stat-card-header">
            <div className="stat-icon">
              <BarChart3 size={20} />
            </div>
            <span className="stat-label">Periode</span>
          </div>
          <div className="stat-value neutral">
            {scatterData.length}
          </div>
          <span className="stat-sublabel">Jours analyses</span>
        </div>
      </section>

      {/* Main Content */}
      <div className="analysis-content">
        {/* Chart */}
        <div className="chart-card">
          <div className="chart-header">
            <div className="chart-title">
              <div className="chart-title-icon">
                <BarChart3 size={20} />
              </div>
              <div>
                <h2>Dispersion Sentiment / Prix</h2>
                <span className="chart-subtitle">Chaque point represente un jour</span>
              </div>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={400}>
            <ScatterChart margin={{ top: 20, right: 20, left: 20, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis
                type="number"
                dataKey="sentiment"
                domain={[-100, 100]}
                stroke="#4b5563"
                tick={{ fill: '#6b7280', fontSize: 12 }}
                label={{ value: 'Sentiment', position: 'insideBottom', offset: -10, fill: '#6b7280' }}
              />
              <YAxis
                type="number"
                dataKey="priceChange"
                stroke="#4b5563"
                tick={{ fill: '#6b7280', fontSize: 12 }}
                label={{ value: 'Variation Prix (%)', angle: -90, position: 'insideLeft', fill: '#6b7280' }}
              />
              <ZAxis range={[60, 60]} />
              <Tooltip content={<ScatterTooltip />} />
              <ReferenceLine x={0} stroke="#374151" strokeDasharray="3 3" />
              <ReferenceLine y={0} stroke="#374151" strokeDasharray="3 3" />
              <Scatter
                data={scatterData}
                fill="#6366f1"
                fillOpacity={0.7}
              />
            </ScatterChart>
          </ResponsiveContainer>
        </div>

        {/* Sidebar */}
        <aside className="analysis-sidebar">
          {/* Correlation Visual */}
          <div className="correlation-visual">
            <h3>Force de la Correlation</h3>
            <div className="correlation-bar-container">
              <div
                className="correlation-indicator"
                style={{ left: `${correlationPercent}%` }}
              />
            </div>
            <div className="correlation-labels">
              <span>-1 (Inverse)</span>
              <span>0 (Neutre)</span>
              <span>+1 (Forte)</span>
            </div>
            <div className="correlation-value-display">
              <div className="value" style={{ color: correlation >= 0 ? '#10b981' : '#ef4444' }}>
                {correlation >= 0 ? '+' : ''}{correlation.toFixed(3)}
              </div>
              <div className="label">{correlationLabel}</div>
            </div>
          </div>

          {/* Interpretation */}
          <div className="interpretation-card">
            <div className="interpretation-header">
              <div className="interpretation-icon">
                <Lightbulb size={20} />
              </div>
              <h3>Interpretation</h3>
            </div>
            <div className="interpretation-content">
              <p>
                La correlation de <strong>{correlation.toFixed(3)}</strong> entre
                le sentiment et les variations de prix indique une relation{' '}
                <strong>{correlationLabel.toLowerCase()}</strong>.
                {correlation > 0.5 &&
                  ' Les mouvements de sentiment tendent a preceder ou accompagner les variations de prix de maniere significative.'
                }
                {correlation > 0 && correlation <= 0.5 &&
                  ' Il existe une tendance moderee entre le sentiment et les mouvements de prix.'
                }
                {correlation >= -0.5 && correlation <= 0 &&
                  ' La relation entre sentiment et prix est faible ou neutre.'
                }
                {correlation < -0.5 &&
                  ' Une correlation negative suggere que le sentiment et les prix evoluent de maniere inverse.'
                }
              </p>
            </div>
          </div>
        </aside>
      </div>

      <Chatbot />
    </div>
  );
}
