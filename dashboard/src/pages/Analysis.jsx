import { useState, useEffect } from 'react';
import {
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ScatterChart,
  Scatter,
  ZAxis,
  ReferenceLine
} from 'recharts';
import { useCrypto } from '../store';
import { cryptoOptions, COLORS } from '../data/mockData';
import { sharedStyles } from '../styles/commonStyles';

// ============================================
// HELPER: getCorrelationLabel
// ============================================
function getCorrelationLabel(corr) {
  const absCorr = Math.abs(corr);
  if (absCorr >= 0.7) return 'Forte';
  if (absCorr >= 0.4) return 'Moyenne';
  if (absCorr >= 0.2) return 'Faible';
  return 'Négligeable';
}

// ============================================
// SOUS-COMPOSANT: OverlayTooltip
// ============================================
const OverlayTooltip = ({ active, payload, label }) => {
  if (!active || !payload) return null;

  return (
    <div style={{
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      padding: '12px',
      border: '1px solid #333',
      borderRadius: '8px'
    }}>
      <p style={{ color: '#fff', marginBottom: '8px', fontWeight: 'bold' }}>
        {label}
      </p>
      {payload.map((entry, index) => (
        <p key={index} style={{ color: entry.color, margin: '4px 0' }}>
          {entry.name}: {entry.name === 'Prix'
            ? `$${entry.value?.toLocaleString() || 0}`
            : entry.value}
        </p>
      ))}
    </div>
  );
};

// ============================================
// SOUS-COMPOSANT: ScatterTooltip
// ============================================
const ScatterTooltip = ({ active, payload }) => {
  if (!active || !payload || !payload[0]) return null;

  const data = payload[0].payload;

  return (
    <div style={{
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      padding: '12px',
      border: '1px solid #333',
      borderRadius: '8px'
    }}>
      <p style={{ color: '#fff', marginBottom: '4px' }}>{data.date}</p>
      <p style={{ color: COLORS.primary, margin: '4px 0' }}>
        Sentiment: {data.sentiment}
      </p>
      <p style={{ color: COLORS.secondary, margin: '4px 0' }}>
        Var. Prix: {data.priceChange}%
      </p>
    </div>
  );
};

// ============================================
// COMPOSANT PRINCIPAL: Analysis
// ============================================
export default function Analysis() {
  const { fetchAnalysis } = useCrypto();

  // ============================================
  // STATE
  // ============================================
  const [selectedCrypto, setSelectedCrypto] = useState('BTC');
  const [stats, setStats] = useState(null);
  const [scatterData, setScatterData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // ============================================
  // FETCH DATA
  // ============================================
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

  // ============================================
  // LOADING / ERROR STATES
  // ============================================
  if (loading) {
    return (
      <div style={{ ...sharedStyles.pageContainer, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <div style={{ color: '#888', fontSize: '1.25rem' }}>Loading analysis...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ ...sharedStyles.pageContainer, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <div style={{ color: '#EF4444', fontSize: '1.25rem' }}>Error: {error}</div>
      </div>
    );
  }

  // ============================================
  // DONNÉES DÉRIVÉES
  // ============================================
  const correlation = stats?.correlation || 0;
  const correlationLabel = stats?.correlationLabel || getCorrelationLabel(correlation);

  // ============================================
  // RENDER
  // ============================================
  return (
    <div style={sharedStyles.pageContainer}>
      {/* TITRE */}
      <h1 style={{ fontSize: '2rem', marginBottom: '24px', color: '#fff' }}>
        Analyse Corrélation
      </h1>

      {/* HEADER - Sélecteur */}
      <div style={{ ...sharedStyles.flexBetween, marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <label style={{ color: '#fff', fontSize: '1rem' }}>Crypto:</label>
          <select
            value={selectedCrypto}
            onChange={(e) => setSelectedCrypto(e.target.value)}
            style={{
              padding: '8px 16px',
              borderRadius: '8px',
              border: '1px solid #333',
              backgroundColor: '#1a1a1a',
              color: '#fff',
              fontSize: '1rem',
              cursor: 'pointer'
            }}
          >
            {cryptoOptions.map((crypto) => (
              <option key={crypto.value} value={crypto.value}>
                {crypto.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* STATS GRID */}
      <section style={{ ...sharedStyles.gridAutoFit('180px'), marginBottom: '32px' }}>
        {/* Corrélation */}
        <div style={sharedStyles.card}>
          <p style={{ color: '#888', fontSize: '0.875rem', marginBottom: '8px' }}>
            Corrélation Pearson
          </p>
          <p style={{
            fontSize: '2rem',
            fontWeight: 'bold',
            color: correlation >= 0 ? COLORS.primary : COLORS.secondary,
            marginBottom: '4px'
          }}>
            {typeof correlation === 'number' ? correlation.toFixed(3) : 'N/A'}
          </p>
          <p style={{ color: '#666', fontSize: '0.75rem' }}>
            {correlationLabel}
          </p>
        </div>

        {/* P-Value */}
        <div style={sharedStyles.card}>
          <p style={{ color: '#888', fontSize: '0.875rem', marginBottom: '8px' }}>
            P-Value
          </p>
          <p style={{
            fontSize: '2rem',
            fontWeight: 'bold',
            color: '#fff',
            marginBottom: '4px'
          }}>
            {stats?.pValue?.toFixed(4) || 'N/A'}
          </p>
          <p style={{ color: '#666', fontSize: '0.75rem' }}>
            significativité
          </p>
        </div>

        {/* Observations */}
        <div style={sharedStyles.card}>
          <p style={{ color: '#888', fontSize: '0.875rem', marginBottom: '8px' }}>
            Observations
          </p>
          <p style={{
            fontSize: '2rem',
            fontWeight: 'bold',
            color: '#fff',
            marginBottom: '4px'
          }}>
            {stats?.nObservations || 0}
          </p>
          <p style={{ color: '#666', fontSize: '0.75rem' }}>
            points de données
          </p>
        </div>

        {/* Scatter Points */}
        <div style={sharedStyles.card}>
          <p style={{ color: '#888', fontSize: '0.875rem', marginBottom: '8px' }}>
            Points Scatter
          </p>
          <p style={{
            fontSize: '2rem',
            fontWeight: 'bold',
            color: '#fff',
            marginBottom: '4px'
          }}>
            {scatterData.length}
          </p>
          <p style={{ color: '#666', fontSize: '0.75rem' }}>
            jours affichés
          </p>
        </div>
      </section>

      {/* SCATTER PLOT */}
      <section style={{ marginBottom: '32px' }}>
        <div style={sharedStyles.card}>
          <h2 style={{ fontSize: '1.25rem', marginBottom: '8px', color: '#fff' }}>
            Dispersion Sentiment/Prix
          </h2>
          <p style={{ color: '#888', fontSize: '0.875rem', marginBottom: '20px' }}>
            Chaque point = 1 jour
          </p>

          <ResponsiveContainer width="100%" height={400}>
            <ScatterChart
              margin={{ top: 20, right: 20, left: 20, bottom: 20 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis
                type="number"
                dataKey="sentiment"
                domain={[-100, 100]}
                stroke="#888"
                label={{ value: 'Sentiment', position: 'insideBottom', offset: -10, fill: '#888' }}
              />
              <YAxis
                type="number"
                dataKey="priceChange"
                stroke="#888"
                label={{ value: 'Variation Prix (%)', angle: -90, position: 'insideLeft', fill: '#888' }}
              />
              <ZAxis range={[50, 50]} />
              <Tooltip content={<ScatterTooltip />} />
              <ReferenceLine x={0} stroke="#666" strokeDasharray="3 3" />
              <ReferenceLine y={0} stroke="#666" strokeDasharray="3 3" />
              <Scatter
                data={scatterData}
                fill="#FFFFFF"
                fillOpacity={0.8}
              />
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* INTERPRETATION CARD */}
      <div style={{
        ...sharedStyles.card,
        borderLeft: `4px solid ${COLORS.accent}`
      }}>
        <h3 style={{ fontSize: '1.25rem', marginBottom: '12px', color: '#fff' }}>
          Interprétation
        </h3>
        <p style={{ color: '#ccc', lineHeight: '1.6' }}>
          La corrélation de <strong style={{ color: COLORS.primary }}>
            {typeof correlation === 'number' ? correlation.toFixed(3) : 'N/A'}
          </strong> entre le sentiment et les variations de prix indique une relation{' '}
          <strong>{correlationLabel.toLowerCase()}</strong>.
          {correlation > 0.5 &&
            ' Les mouvements de sentiment tendent à précéder ou accompagner les variations de prix de manière significative.'
          }
          {correlation > 0 && correlation <= 0.5 &&
            ' Il existe une tendance modérée entre le sentiment et les mouvements de prix.'
          }
          {correlation >= -0.5 && correlation <= 0 &&
            ' La relation entre sentiment et prix est faible ou neutre.'
          }
          {correlation < -0.5 &&
            ' Une corrélation négative suggère que le sentiment et les prix évoluent de manière inverse.'
          }
        </p>
      </div>
    </div>
  );
}
