import { useState } from 'react';
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
import {
  cryptoOptions,
  generateAnalysisData,
  calculateAnalysisStats,
  getCorrelationLabel,
  COLORS
} from '../data/mockData';
import { sharedStyles } from '../styles/commonStyles';

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
            ? `$${entry.value.toLocaleString()}` 
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
  // ============================================
  // STATE
  // ============================================
  const [selectedCrypto, setSelectedCrypto] = useState('BTC');

  // ============================================
  // DONNÉES DÉRIVÉES
  // ============================================
  const data = generateAnalysisData(selectedCrypto);
  const scatterData = data.map((item, index) => ({ ...item, index }));
  const stats = calculateAnalysisStats(data);

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
        {/* Sentiment Moyen */}
        <div style={sharedStyles.card}>
          <p style={{ color: '#888', fontSize: '0.875rem', marginBottom: '8px' }}>
            Sentiment Moyen
          </p>
          <p style={{
            fontSize: '2rem',
            fontWeight: 'bold',
            color: stats.avgSentiment >= 0 ? COLORS.primary : COLORS.secondary,
            marginBottom: '4px'
          }}>
            {stats.avgSentiment}
          </p>
          <p style={{ color: '#666', fontSize: '0.75rem' }}>
            sur 30 jours
          </p>
        </div>

        {/* Volatilité Sentiment */}
        <div style={sharedStyles.card}>
          <p style={{ color: '#888', fontSize: '0.875rem', marginBottom: '8px' }}>
            Volatilité Sentiment
          </p>
          <p style={{
            fontSize: '2rem',
            fontWeight: 'bold',
            color: '#fff',
            marginBottom: '4px'
          }}>
            {stats.sentimentVolatility}
          </p>
          <p style={{ color: '#666', fontSize: '0.75rem' }}>
            écart-type
          </p>
        </div>

        {/* Volatilité Prix */}
        <div style={sharedStyles.card}>
          <p style={{ color: '#888', fontSize: '0.875rem', marginBottom: '8px' }}>
            Volatilité Prix
          </p>
          <p style={{
            fontSize: '2rem',
            fontWeight: 'bold',
            color: '#fff',
            marginBottom: '4px'
          }}>
            {stats.priceVolatility}%
          </p>
          <p style={{ color: '#666', fontSize: '0.75rem' }}>
            écart-type
          </p>
        </div>

        {/* Corrélation */}
        <div style={sharedStyles.card}>
          <p style={{ color: '#888', fontSize: '0.875rem', marginBottom: '8px' }}>
            Corrélation
          </p>
          <p style={{
            fontSize: '2rem',
            fontWeight: 'bold',
            color: stats.correlation >= 0 ? COLORS.primary : COLORS.secondary,
            marginBottom: '4px'
          }}>
            {stats.correlation}
          </p>
          <p style={{ color: '#666', fontSize: '0.75rem' }}>
            {getCorrelationLabel(stats.correlation)}
          </p>
        </div>
      </section>

      {/* CHARTS GRID */}
      <section style={{ ...sharedStyles.gridAutoFit('400px'), marginBottom: '32px' }}>
        {/* Overlay Chart */}
        <div style={sharedStyles.card}>
          <h2 style={{ fontSize: '1.25rem', marginBottom: '8px', color: '#fff' }}>
            Sentiment vs Prix
          </h2>
          <p style={{ color: '#888', fontSize: '0.875rem', marginBottom: '20px' }}>
            Évolution sur 30 jours avec double axe Y
          </p>

          <ResponsiveContainer width="100%" height={350}>
            <ComposedChart
              data={data}
              margin={{ top: 20, right: 60, left: 20, bottom: 20 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis 
                dataKey="date" 
                stroke="#888"
                style={{ fontSize: '0.75rem' }}
              />
              <YAxis 
                yAxisId="sentiment"
                orientation="left"
                domain={[-100, 100]}
                stroke="#888"
                label={{ value: 'Sentiment', angle: -90, position: 'insideLeft', fill: '#888' }}
              />
              <YAxis 
                yAxisId="price"
                orientation="right"
                stroke="#888"
                label={{ value: 'Prix ($)', angle: 90, position: 'insideRight', fill: '#888' }}
              />
              <Tooltip content={<OverlayTooltip />} />
              <Legend />
              <ReferenceLine 
                y={0} 
                yAxisId="sentiment" 
                stroke="#666" 
                strokeDasharray="3 3" 
              />
              <Area
                yAxisId="sentiment"
                type="monotone"
                dataKey="sentiment"
                fill={COLORS.primary}
                fillOpacity={0.2}
                stroke={COLORS.primary}
                strokeWidth={2}
                name="Sentiment"
              />
              <Line
                yAxisId="price"
                type="monotone"
                dataKey="price"
                stroke={COLORS.secondary}
                strokeWidth={2}
                dot={false}
                name="Prix"
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        {/* Scatter Plot */}
        <div style={sharedStyles.card}>
          <h2 style={{ fontSize: '1.25rem', marginBottom: '8px', color: '#fff' }}>
            Dispersion Sentiment/Prix
          </h2>
          <p style={{ color: '#888', fontSize: '0.875rem', marginBottom: '20px' }}>
            Chaque point = 1 jour
          </p>

          <ResponsiveContainer width="100%" height={350}>
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
          La corrélation de <strong style={{ color: COLORS.primary }}>{stats.correlation}</strong> entre 
          le sentiment et les variations de prix indique une relation{' '}
          <strong>{getCorrelationLabel(stats.correlation).toLowerCase()}</strong>.
          {stats.correlation > 0.5 && 
            ' Les mouvements de sentiment tendent à précéder ou accompagner les variations de prix de manière significative.'
          }
          {stats.correlation > 0 && stats.correlation <= 0.5 && 
            ' Il existe une tendance modérée entre le sentiment et les mouvements de prix.'
          }
          {stats.correlation >= -0.5 && stats.correlation <= 0 && 
            ' La relation entre sentiment et prix est faible ou neutre.'
          }
          {stats.correlation < -0.5 && 
            ' Une corrélation négative suggère que le sentiment et les prix évoluent de manière inverse.'
          }
        </p>
      </div>
    </div>
  );
}