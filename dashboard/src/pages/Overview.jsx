import MetricCard from '../components/MetricCard';
import SentimentGauge from '../components/SentimentGauge';
import CryptoChart from '../components/CryptoChart';
import {
  overviewCryptoData,
  overviewChartData,
  overviewSentiment,
  COLORS
} from '../data/mockData';
import { sharedStyles } from '../styles/commonStyles';

// ============================================
// COMPOSANT PRINCIPAL: Overview
// ============================================
export default function Overview() {
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
        {overviewCryptoData.map((crypto, index) => (
          <MetricCard
            key={index}
            title={crypto.title}
            value={crypto.value}
            change={crypto.change}
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
            data={overviewChartData}
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
            value={overviewSentiment}
            label="Market Sentiment"
          />
        </div>
      </section>
    </div>
  );
}