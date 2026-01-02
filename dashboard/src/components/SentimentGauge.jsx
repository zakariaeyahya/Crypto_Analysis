import { useState, useEffect } from 'react';

// Mock constants (replace with real imports)
const COLORS = {
  positive: '#10B981',
  negative: '#EF4444',
  neutral: '#6B7280',
  border: '#334155',
  text: '#e5e7eb'
};

const sentimentGaugeStyles = {
  container: {
    background: 'rgba(30, 41, 59, 0.5)',
    backdropFilter: 'blur(20px)',
    borderRadius: '20px',
    padding: '28px',
    border: '1px solid rgba(255, 255, 255, 0.1)'
  },
  label: {
    fontSize: '1.125rem',
    fontWeight: '600',
    color: COLORS.text,
    marginBottom: '24px',
    textAlign: 'center'
  },
  gaugeWrapper: {
    display: 'flex',
    justifyContent: 'center',
    marginBottom: '20px'
  },
  valueContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '8px',
    marginBottom: '24px'
  },
  value: {
    fontSize: '3rem',
    fontWeight: '800',
    letterSpacing: '-0.02em'
  },
  sentimentText: {
    fontSize: '0.875rem',
    fontWeight: '700',
    letterSpacing: '0.1em',
    textTransform: 'uppercase'
  },
  progressBarContainer: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px'
  },
  progressBarBg: {
    position: 'relative',
    height: '8px',
    background: 'rgba(51, 65, 85, 0.5)',
    borderRadius: '4px',
    overflow: 'visible'
  },
  progressBarFill: {
    height: '100%',
    borderRadius: '4px',
    transition: 'width 0.5s ease-out'
  },
  indicator: {
    position: 'absolute',
    top: '-4px',
    width: '4px',
    height: '16px',
    borderRadius: '2px',
    transition: 'left 0.5s ease-out'
  },
  progressLabels: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: '0.75rem',
    fontWeight: '500',
    paddingTop: '4px'
  }
};

// SentimentGauge component
export default function SentimentGauge({ value = 0, label = 'Market Sentiment' }) {
  const [animatedValue, setAnimatedValue] = useState(0);

  useEffect(() => {
    // Progressive animation of the value
    const timeout = setTimeout(() => setAnimatedValue(value), 100);
    return () => clearTimeout(timeout);
  }, [value]);

  // 1. Clamp value
  const clampedValue = Math.max(-100, Math.min(100, animatedValue));

  // 2. Get sentiment state
  const getSentimentState = () => {
    if (clampedValue <= -20) {
      return { text: 'Bearish', color: COLORS.negative };
    }
    if (clampedValue >= 20) {
      return { text: 'Bullish', color: COLORS.positive };
    }
    return { text: 'Neutral', color: COLORS.neutral };
  };

  const sentiment = getSentimentState();

  // 3. Calculate rotation (-90° to +90°)
  const rotation = (clampedValue / 100) * 90;

  // 4. Calculate progress (0% to 100%)
  const progressPercent = ((clampedValue + 100) / 200) * 100;

  // Arc path calculations
  const arcPath = "M 20 100 A 80 80 0 0 1 180 100";
  const arcLength = 251.2; // Approximation de la longueur de l'arc

  return (
    <div style={sentimentGaugeStyles.container}>
      {/* Label */}
      <h3 style={sentimentGaugeStyles.label}>{label}</h3>

      {/* Gauge SVG */}
      <div style={sentimentGaugeStyles.gaugeWrapper}>
        <svg viewBox="0 0 200 120" style={{ width: '100%', maxWidth: '400px', height: 'auto' }}>
          {/* Arc background */}
          <path
            d={arcPath}
            fill="none"
            stroke={COLORS.border}
            strokeWidth="12"
            strokeLinecap="round"
          />

          {/* Gradient definition */}
          <defs>
            <linearGradient id="sentimentGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor={COLORS.negative} />
              <stop offset="40%" stopColor={COLORS.negative} />
              <stop offset="50%" stopColor={COLORS.neutral} />
              <stop offset="60%" stopColor={COLORS.positive} />
              <stop offset="100%" stopColor={COLORS.positive} />
            </linearGradient>
          </defs>

          {/* Arc colored with gradient */}
          <path
            d={arcPath}
            fill="none"
            stroke="url(#sentimentGradient)"
            strokeWidth="12"
            strokeLinecap="round"
            strokeDasharray={arcLength}
            strokeDashoffset={arcLength - (arcLength * progressPercent) / 100}
            style={{ transition: 'stroke-dashoffset 0.5s ease-out' }}
          />

          {/* Needle */}
          <g transform={`rotate(${rotation}, 100, 100)`} style={{ transition: 'transform 0.3s ease' }}>
            <line
              x1="100"
              y1="100"
              x2="100"
              y2="35"
              stroke={sentiment.color}
              strokeWidth="3"
              strokeLinecap="round"
            />
            <circle cx="100" cy="100" r="6" fill={sentiment.color} />
          </g>

          {/* Labels */}
          <text x="15" y="115" fill={COLORS.neutral} fontSize="10" fontWeight="600">-100</text>
          <text x="175" y="115" fill={COLORS.neutral} fontSize="10" fontWeight="600">+100</text>
        </svg>
      </div>

      {/* Value display */}
      <div style={sentimentGaugeStyles.valueContainer}>
        <span style={{ ...sentimentGaugeStyles.value, color: sentiment.color }}>
          {clampedValue > 0 ? '+' : ''}{Math.round(clampedValue)}
        </span>
        <span style={{ ...sentimentGaugeStyles.sentimentText, color: sentiment.color }}>
          {sentiment.text}
        </span>
      </div>

      {/* Progress bar */}
      <div style={sentimentGaugeStyles.progressBarContainer}>
        <div style={sentimentGaugeStyles.progressBarBg}>
          {/* Progress fill */}
          <div
            style={{
              ...sentimentGaugeStyles.progressBarFill,
              width: `${progressPercent}%`,
              background: `linear-gradient(90deg, ${COLORS.negative} 0%, ${COLORS.neutral} 50%, ${COLORS.positive} 100%)`
            }}
          />
          {/* Indicator */}
          <div
            style={{
              ...sentimentGaugeStyles.indicator,
              left: `${progressPercent}%`,
              background: sentiment.color,
              boxShadow: `0 0 12px ${sentiment.color}80`
            }}
          />
        </div>

        {/* Labels */}
        <div style={sentimentGaugeStyles.progressLabels}>
          <span style={{ color: COLORS.negative }}>Bearish</span>
          <span style={{ color: COLORS.neutral }}>Neutral</span>
          <span style={{ color: COLORS.positive }}>Bullish</span>
        </div>
      </div>
    </div>
  );
}

// Interactive demo
function Demo() {
  const [sentimentValue, setSentimentValue] = useState(35);

  const presets = [
    { label: 'Extreme Bearish', value: -85 },
    { label: 'Bearish', value: -45 },
    { label: 'Neutral', value: 0 },
    { label: 'Bullish', value: 55 },
    { label: 'Extreme Bullish', value: 92 }
  ];

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
      padding: '60px 40px'
    }}>
      <h1 style={{
        background: 'linear-gradient(135deg, #10B981 0%, #3B82F6 100%)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        backgroundClip: 'text',
        fontWeight: '800',
        fontSize: '2.5rem',
        marginBottom: '40px',
        textAlign: 'center'
      }}>
        Market Sentiment Gauge
      </h1>

      <div style={{
        maxWidth: '600px',
        margin: '0 auto',
        marginBottom: '40px'
      }}>
        <SentimentGauge value={sentimentValue} label="Market Sentiment" />
      </div>

      {/* Controls */}
      <div style={{
        maxWidth: '800px',
        margin: '0 auto',
        background: 'rgba(30, 41, 59, 0.5)',
        backdropFilter: 'blur(20px)',
        borderRadius: '20px',
        padding: '32px',
        border: '1px solid rgba(255, 255, 255, 0.1)'
      }}>
        <h3 style={{
          color: '#e5e7eb',
          fontSize: '1.125rem',
          marginBottom: '20px',
          fontWeight: '600'
        }}>
          🎚️ Adjust Sentiment Value
        </h3>

        {/* Slider */}
        <div style={{ marginBottom: '24px' }}>
          <input
            type="range"
            min="-100"
            max="100"
            value={sentimentValue}
            onChange={(e) => setSentimentValue(Number(e.target.value))}
            style={{
              width: '100%',
              height: '8px',
              borderRadius: '4px',
              outline: 'none',
              cursor: 'pointer'
            }}
          />
        </div>

        {/* Preset buttons */}
        <div style={{
          display: 'flex',
          gap: '12px',
          flexWrap: 'wrap',
          justifyContent: 'center'
        }}>
          {presets.map((preset) => (
            <button
              key={preset.value}
              onClick={() => setSentimentValue(preset.value)}
              style={{
                padding: '10px 20px',
                borderRadius: '10px',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                background: sentimentValue === preset.value
                  ? 'rgba(59, 130, 246, 0.2)'
                  : 'rgba(30, 41, 59, 0.5)',
                color: '#e5e7eb',
                fontSize: '0.875rem',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'all 0.2s',
                backdropFilter: 'blur(10px)'
              }}
            >
              {preset.label} ({preset.value})
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export { Demo };