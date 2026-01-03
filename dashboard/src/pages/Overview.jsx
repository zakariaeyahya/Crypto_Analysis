import { useCrypto } from '../store';
import MetricCard from '../components/MetricCard';
import SentimentGauge from '../components/SentimentGauge';
import CryptoChart from '../components/CryptoChart';
import { COLORS } from '../data/mockData';
import { sharedStyles } from '../styles/commonStyles';
import Chatbot from '../components/ChatBot';

// ============================================
// MAIN COMPONENT: Overview
// ============================================
export default function Overview() {
  const { cryptos, chartData, sentiment, loading, error } = useCrypto();

  if (loading) {
    return (
      <div style={{ ...sharedStyles.pageContainer, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <div style={{ color: '#888', fontSize: '1.25rem' }}>Loading...</div>
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

  return (
    <div style={sharedStyles.pageContainer}>
      {/* PAGE TITLE */}
      <h1 style={sharedStyles.pageTitle}>
        Dashboard Overview
      </h1>

      {/* METRICS GRID */}
      <section style={{
        ...sharedStyles.gridAutoFit('220px'),
        marginBottom: '32px'
      }}>
        {cryptos.map((crypto, index) => (
          <MetricCard
            key={index}
            title={`${crypto.name} (${crypto.symbol})`}
            value={`$${crypto.price.toLocaleString()}`}
            change={crypto.change24h}
          />
        ))}
      </section>

      {/* BOTTOM SECTION - Chart + Gauge */}
      <section style={{
        ...sharedStyles.gridAutoFit('300px'),
        alignItems: 'start'
      }}>
        {/* CHART CONTAINER */}
        <div style={{ minWidth: 0 }}>
          <CryptoChart
            data={chartData}
            title="Bitcoin (7 Days)"
            dataKey="value"
            color={COLORS.positive}
          />
        </div>

        {/* GAUGE CONTAINER */}
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center'
        }}>
          <SentimentGauge
            value={Math.round(sentiment.score * 100)}
            label={sentiment.label || "Market Sentiment"}
          />
        </div>
      </section>
      <Chatbot />
    </div>
  );
}
