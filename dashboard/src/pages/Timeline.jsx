import { useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ReferenceLine
} from 'recharts';
import {
  cryptoOptions,
  generateTimelineData,
  COLORS
} from '../data/mockData';
import { sharedStyles } from '../styles/commonStyles';

// ============================================
// SOUS-COMPOSANT: CustomTooltip
// ============================================
const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload) return null;

  return (
    <div style={{
      backgroundColor: 'rgba(0, 0, 0, 0.9)',
      padding: '12px',
      border: '1px solid #333',
      borderRadius: '8px'
    }}>
      <p style={{
        color: '#fff',
        marginBottom: '8px',
        fontWeight: 'bold',
        fontSize: '0.875rem'
      }}>
        {label}
      </p>
      {payload.map((entry, index) => (
        <p
          key={index}
          style={{
            color: entry.color,
            margin: '4px 0',
            fontSize: '0.875rem'
          }}
        >
          {entry.name}: {entry.value}
        </p>
      ))}
    </div>
  );
};

// ============================================
// COMPOSANT PRINCIPAL: Timeline
// ============================================
export default function Timeline() {
  // ============================================
  // STATE
  // ============================================
  const [selectedCrypto, setSelectedCrypto] = useState('BTC');

  // ============================================
  // DONNÉES DÉRIVÉES
  // ============================================
  const data = generateTimelineData(selectedCrypto);
  
  const currentSentiment = data[data.length - 1].sentiment;
  
  const avgSentiment = Math.round(
    data.reduce((sum, item) => sum + item.sentiment, 0) / data.length
  );

  const selectedCryptoLabel = cryptoOptions.find(
    opt => opt.value === selectedCrypto
  )?.label || selectedCrypto;

  // ============================================
  // RENDER
  // ============================================
  return (
    <div style={sharedStyles.pageContainer}>
      {/* PAGE TITLE */}
      <h1 style={sharedStyles.pageTitle}>
        Sentiment Timeline
      </h1>

      {/* HEADER */}
      <div style={{
        ...sharedStyles.flexBetween,
        marginBottom: '32px',
        flexWrap: 'wrap',
        gap: '16px'
      }}>
        {/* SELECTOR CONTAINER */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px'
        }}>
          <label style={{
            color: '#fff',
            fontSize: '1rem',
            fontWeight: '500'
          }}>
            Crypto:
          </label>
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
              cursor: 'pointer',
              outline: 'none'
            }}
          >
            {cryptoOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* STATS ROW */}
        <div style={{
          display: 'flex',
          gap: '16px',
          flexWrap: 'wrap'
        }}>
          {/* Current Sentiment */}
          <div style={{
            padding: '12px 20px',
            backgroundColor: '#1a1a1a',
            borderRadius: '8px',
            border: '1px solid #333'
          }}>
            <p style={{
              color: '#888',
              fontSize: '0.75rem',
              marginBottom: '4px'
            }}>
              Current
            </p>
            <p style={{
              color: currentSentiment >= 0 ? COLORS.positive : COLORS.negative,
              fontSize: '1.25rem',
              fontWeight: 'bold'
            }}>
              {currentSentiment}
            </p>
          </div>

          {/* Average Sentiment */}
          <div style={{
            padding: '12px 20px',
            backgroundColor: '#1a1a1a',
            borderRadius: '8px',
            border: '1px solid #333'
          }}>
            <p style={{
              color: '#888',
              fontSize: '0.75rem',
              marginBottom: '4px'
            }}>
              Avg (30d)
            </p>
            <p style={{
              color: avgSentiment >= 0 ? COLORS.positive : COLORS.negative,
              fontSize: '1.25rem',
              fontWeight: 'bold'
            }}>
              {avgSentiment}
            </p>
          </div>
        </div>
      </div>

      {/* CHART CARD */}
      <div style={sharedStyles.card}>
        {/* TITLE */}
        <h2 style={{
          fontSize: '1.25rem',
          color: '#fff',
          marginBottom: '8px',
          fontWeight: '600'
        }}>
          Sentiment Evolution - {selectedCryptoLabel}
        </h2>

        {/* SUBTITLE */}
        <p style={{
          color: '#888',
          fontSize: '0.875rem',
          marginBottom: '24px'
        }}>
          Last 30 days (score: -100 to +100)
        </p>

        {/* CHART WRAPPER */}
        <div style={{ height: '400px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={data}
              margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
            >
              {/* GRID */}
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />

              {/* X AXIS */}
              <XAxis
                dataKey="date"
                stroke="#888"
                tick={{ fill: '#888', fontSize: 12 }}
              />

              {/* Y AXIS */}
              <YAxis
                domain={[-100, 100]}
                ticks={[-100, -50, 0, 50, 100]}
                stroke="#888"
                tick={{ fill: '#888', fontSize: 12 }}
              />

              {/* TOOLTIP */}
              <Tooltip content={<CustomTooltip />} />

              {/* LEGEND */}
              <Legend
                wrapperStyle={{ paddingTop: '20px' }}
                iconType="line"
              />

              {/* REFERENCE LINE AT 0 */}
              <ReferenceLine
                y={0}
                stroke="#666"
                strokeDasharray="3 3"
              />

              {/* SENTIMENT LINE */}
              <Line
                type="monotone"
                dataKey="sentiment"
                name="Sentiment"
                stroke={COLORS.positive}
                strokeWidth={2}
                dot={{ r: 3, fill: COLORS.positive }}
                activeDot={{ r: 5 }}
              />

              {/* MA 7 DAYS LINE */}
              <Line
                type="monotone"
                dataKey="ma7"
                name="MA 7 jours"
                stroke={COLORS.negative}
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}