import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

// Mock des constantes (à remplacer par les imports réels)
const COLORS = {
  positive: '#10b981',
  negative: '#ef4444',
  neutral: '#6b7280',
  text: '#e5e7eb'
};

const cryptoChartStyles = {
  container: {
    background: 'rgba(30, 41, 59, 0.5)',
    backdropFilter: 'blur(20px)',
    borderRadius: '20px',
    padding: '28px',
    border: '1px solid rgba(255, 255, 255, 0.1)'
  },
  title: {
    fontSize: '1.25rem',
    fontWeight: '600',
    color: COLORS.text,
    marginBottom: '24px'
  },
  chartWrapper: {
    height: '320px'
  }
};

const sharedStyles = {
  tooltip: {
    background: 'rgba(15, 23, 42, 0.95)',
    backdropFilter: 'blur(12px)',
    borderRadius: '12px',
    padding: '12px 16px',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    boxShadow: '0 10px 40px rgba(0, 0, 0, 0.3)'
  }
};

// Sous-composant CustomTooltip
const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload || payload.length === 0) {
    return null;
  }

  return (
    <div style={sharedStyles.tooltip}>
      <p style={{ 
        fontWeight: 'bold', 
        color: COLORS.text, 
        marginBottom: '4px',
        fontSize: '0.875rem'
      }}>
        {label}
      </p>
      <p style={{ 
        color: payload[0].color,
        fontSize: '1rem',
        fontWeight: '600',
        margin: 0
      }}>
        ${payload[0].value.toLocaleString()}
      </p>
    </div>
  );
};

// Composant principal CryptoChart
export default function CryptoChart({ 
  data = [], 
  title = 'Chart', 
  dataKey = 'value', 
  color = COLORS.positive 
}) {
  return (
    <div style={cryptoChartStyles.container}>
      <h3 style={cryptoChartStyles.title}>{title}</h3>
      
      <div style={cryptoChartStyles.chartWrapper}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart 
            data={data}
            margin={{ top: 5, right: 20, bottom: 5, left: 0 }}
          >
            <XAxis 
              dataKey="date"
              stroke={COLORS.neutral}
              tick={{ fill: COLORS.neutral, fontSize: 12 }}
              tickLine={{ stroke: COLORS.neutral }}
            />
            
            <YAxis 
              tickFormatter={(value) => value.toLocaleString()}
              stroke={COLORS.neutral}
              tick={{ fill: COLORS.neutral, fontSize: 12 }}
            />
            
            <Tooltip content={<CustomTooltip />} />
            
            <Line 
              type="monotone"
              dataKey={dataKey}
              stroke={color}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 6, fill: color }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

// Exemple d'utilisation avec données de démonstration
function Demo() {
  const mockData = [
    { date: 'Jan 1', value: 45000 },
    { date: 'Jan 2', value: 47500 },
    { date: 'Jan 3', value: 46800 },
    { date: 'Jan 4', value: 49200 },
    { date: 'Jan 5', value: 51000 },
    { date: 'Jan 6', value: 50200 },
    { date: 'Jan 7', value: 52500 }
  ];

  return (
    <div style={{ 
      padding: '40px', 
      background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
      minHeight: '100vh'
    }}>
      <CryptoChart 
        data={mockData}
        title="Bitcoin (7 Days)"
        dataKey="value"
        color={COLORS.positive}
      />
    </div>
  );
}

export { Demo };