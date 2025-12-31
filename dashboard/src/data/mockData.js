// ============================================
// MOCK DATA - Crypto Dashboard
// ============================================

// Color palette
export const COLORS = {
  positive: '#10B981',
  negative: '#EF4444',
  neutral: '#6B7280',
  background: '#1F2937',
  backgroundDark: '#111827',
  border: '#374151',
  textPrimary: '#FFFFFF',
  textSecondary: '#9CA3AF',
  textMuted: '#6B7280',
};

// Crypto options for selectors
export const cryptoOptions = [
  { value: 'BTC', label: 'Bitcoin (BTC)', symbol: 'BTC' },
  { value: 'ETH', label: 'Ethereum (ETH)', symbol: 'ETH' },
  { value: 'SOL', label: 'Solana (SOL)', symbol: 'SOL' },
];

// Crypto filters (with All option)
export const cryptoFilters = [
  { value: 'All', label: 'All Cryptos' },
  ...cryptoOptions,
];

// ============================================
// OVERVIEW PAGE DATA
// ============================================

export const overviewCryptoData = [
  { title: 'Bitcoin (BTC)', value: '$43,250.00', change: 2.45 },
  { title: 'Ethereum (ETH)', value: '$2,280.50', change: -1.32 },
  { title: 'Solana (SOL)', value: '$98.75', change: 5.67 },
  { title: 'BNB', value: '$312.40', change: 0.89 },
];

export const overviewChartData = [
  { date: '24 Dec', value: 42100 },
  { date: '25 Dec', value: 41800 },
  { date: '26 Dec', value: 42500 },
  { date: '27 Dec', value: 43100 },
  { date: '28 Dec', value: 42800 },
  { date: '29 Dec', value: 43500 },
  { date: '30 Dec', value: 43250 },
];

export const overviewSentiment = 35;

// ============================================
// TIMELINE PAGE DATA GENERATOR
// ============================================

export const timelineConfig = {
  baseValues: { BTC: 25, ETH: 10, SOL: -5 },
  volatility: { BTC: 30, ETH: 40, SOL: 50 },
};

export const generateTimelineData = (crypto) => {
  const base = timelineConfig.baseValues[crypto];
  const vol = timelineConfig.volatility[crypto];
  const data = [];
  const today = new Date();

  for (let i = 29; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    const randomFactor = Math.sin(i * 0.5) * vol + (Math.random() - 0.5) * 20;
    const sentiment = Math.max(-100, Math.min(100, base + randomFactor));

    data.push({
      date: date.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' }),
      sentiment: Math.round(sentiment),
    });
  }

  // Calculate 7-day moving average
  return data.map((item, index) => {
    if (index < 6) return { ...item, ma7: null };
    const sum = data.slice(index - 6, index + 1).reduce((acc, d) => acc + d.sentiment, 0);
    return { ...item, ma7: Math.round(sum / 7) };
  });
};

// ============================================
// ANALYSIS PAGE DATA GENERATOR
// ============================================

export const analysisConfig = {
  basePrice: { BTC: 43000, ETH: 2300, SOL: 95 },
  baseSentiment: { BTC: 30, ETH: 15, SOL: -10 },
  priceVolatility: { BTC: 0.03, ETH: 0.045, SOL: 0.08 },
  sentimentVolatility: { BTC: 25, ETH: 35, SOL: 45 },
};

export const generateAnalysisData = (crypto) => {
  const config = analysisConfig;
  const price = config.basePrice[crypto];
  const sentiment = config.baseSentiment[crypto];
  const priceVol = config.priceVolatility[crypto];
  const sentVol = config.sentimentVolatility[crypto];

  const data = [];
  const today = new Date();
  let currentPrice = price;

  for (let i = 29; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);

    const trend = Math.sin(i * 0.3) * 0.5 + (Math.random() - 0.5);
    const sentimentValue = Math.max(-100, Math.min(100, sentiment + trend * sentVol + (Math.random() - 0.5) * 20));
    const priceChange = (sentimentValue / 100) * priceVol + (Math.random() - 0.5) * priceVol * 0.5;
    currentPrice = currentPrice * (1 + priceChange * 0.1);

    const prevPrice = i === 29 ? currentPrice : data[data.length - 1]?.price || currentPrice;
    const priceChangePercent = ((currentPrice - prevPrice) / prevPrice) * 100;

    data.push({
      date: date.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' }),
      sentiment: Math.round(sentimentValue),
      price: Math.round(currentPrice * 100) / 100,
      priceChange: Math.round(priceChangePercent * 100) / 100,
    });
  }

  return data;
};

export const calculateAnalysisStats = (data) => {
  const sentiments = data.map((d) => d.sentiment);
  const priceChanges = data.map((d) => d.priceChange);

  const avgSentiment = sentiments.reduce((a, b) => a + b, 0) / sentiments.length;
  const sentimentVariance = sentiments.reduce((sum, s) => sum + Math.pow(s - avgSentiment, 2), 0) / sentiments.length;
  const sentimentVolatility = Math.sqrt(sentimentVariance);

  const avgPriceChange = priceChanges.reduce((a, b) => a + b, 0) / priceChanges.length;
  const priceVariance = priceChanges.reduce((sum, p) => sum + Math.pow(p - avgPriceChange, 2), 0) / priceChanges.length;
  const priceVolatility = Math.sqrt(priceVariance);

  // Pearson correlation
  const n = sentiments.length;
  const sumXY = sentiments.reduce((sum, s, i) => sum + s * priceChanges[i], 0);
  const sumX = sentiments.reduce((a, b) => a + b, 0);
  const sumY = priceChanges.reduce((a, b) => a + b, 0);
  const sumX2 = sentiments.reduce((sum, s) => sum + s * s, 0);
  const sumY2 = priceChanges.reduce((sum, p) => sum + p * p, 0);
  const numerator = n * sumXY - sumX * sumY;
  const denominator = Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY));
  const correlation = denominator !== 0 ? numerator / denominator : 0;

  return {
    avgSentiment: Math.round(avgSentiment),
    sentimentVolatility: Math.round(sentimentVolatility * 10) / 10,
    avgPriceChange: Math.round(avgPriceChange * 100) / 100,
    priceVolatility: Math.round(priceVolatility * 100) / 100,
    correlation: Math.round(correlation * 100) / 100,
  };
};

// ============================================
// EVENTS PAGE DATA
// ============================================

export const eventsData = [
  {
    id: 1,
    date: '2024-12-30',
    crypto: 'BTC',
    title: 'Bitcoin ETF Record Inflows',
    description: 'BlackRock Bitcoin ETF sees record $1.2B daily inflows, pushing total AUM past $50B. Institutional adoption continues to accelerate as major pension funds announce BTC allocations.',
    type: 'positive',
  },
  {
    id: 2,
    date: '2024-12-29',
    crypto: 'ETH',
    title: 'Ethereum Dencun Upgrade Success',
    description: 'The Dencun upgrade successfully deployed, reducing L2 transaction costs by 90%. Arbitrum and Optimism report surge in user activity following the blob implementation.',
    type: 'positive',
  },
  {
    id: 3,
    date: '2024-12-28',
    crypto: 'SOL',
    title: 'Solana Network Outage',
    description: 'Solana experienced a 5-hour network outage due to congestion from memecoin activity. Validators coordinated restart, raising concerns about network stability.',
    type: 'negative',
  },
  {
    id: 4,
    date: '2024-12-27',
    crypto: 'BTC',
    title: 'MicroStrategy Buys More Bitcoin',
    description: 'MicroStrategy announces additional $500M Bitcoin purchase, bringing total holdings to 190,000 BTC. Stock price rallies 8% on the news.',
    type: 'positive',
  },
  {
    id: 5,
    date: '2024-12-26',
    crypto: 'ETH',
    title: 'SEC Delays ETH ETF Decision',
    description: 'SEC postpones decision on spot Ethereum ETF applications to Q2 2025. Market reacts with mild 3% pullback as investors adjust expectations.',
    type: 'negative',
  },
  {
    id: 6,
    date: '2024-12-25',
    crypto: 'SOL',
    title: 'Solana DeFi TVL Milestone',
    description: 'Solana DeFi total value locked surpasses $5B for the first time, driven by Jupiter DEX and Marinade Finance growth.',
    type: 'positive',
  },
  {
    id: 7,
    date: '2024-12-24',
    crypto: 'BTC',
    title: 'Bitcoin Mining Difficulty Adjustment',
    description: 'Bitcoin mining difficulty increases 4.2% to new all-time high. Hashrate remains stable as miners adapt to post-halving economics.',
    type: 'neutral',
  },
  {
    id: 8,
    date: '2024-12-23',
    crypto: 'ETH',
    title: 'Vitalik Proposes New EIP',
    description: 'Vitalik Buterin proposes EIP-7702 for account abstraction improvements. Community reception mixed as developers debate implementation complexity.',
    type: 'neutral',
  },
  {
    id: 9,
    date: '2024-12-22',
    crypto: 'SOL',
    title: 'Major Exchange Listing',
    description: 'Robinhood adds SOL staking with 5.2% APY, opening Solana to millions of retail investors. Trading volume spikes 40% following announcement.',
    type: 'positive',
  },
  {
    id: 10,
    date: '2024-12-21',
    crypto: 'BTC',
    title: 'El Salvador Bitcoin Bonds',
    description: 'El Salvador successfully issues $1B in Bitcoin-backed bonds with 3x oversubscription. Proceeds to fund Bitcoin City infrastructure.',
    type: 'positive',
  },
  {
    id: 11,
    date: '2024-12-20',
    crypto: 'ETH',
    title: 'Ethereum Foundation Treasury Move',
    description: 'Ethereum Foundation transfers 15,000 ETH to exchanges, sparking sell pressure concerns. Foundation clarifies routine operations for grants funding.',
    type: 'negative',
  },
  {
    id: 12,
    date: '2024-12-19',
    crypto: 'SOL',
    title: 'Firedancer Client Beta Launch',
    description: 'Jump Crypto releases Firedancer validator client beta. Early tests show 10x throughput improvement potential for Solana network.',
    type: 'positive',
  },
  {
    id: 13,
    date: '2024-12-18',
    crypto: 'BTC',
    title: 'Federal Reserve Rate Decision',
    description: 'Fed maintains rates, signals potential cuts in 2025. Bitcoin holds steady as macro outlook improves for risk assets.',
    type: 'neutral',
  },
  {
    id: 14,
    date: '2024-12-17',
    crypto: 'ETH',
    title: 'Layer 2 Total Users Milestone',
    description: 'Ethereum L2 ecosystem crosses 10 million monthly active addresses. Base leads growth with 3M users, followed by Arbitrum at 2.5M.',
    type: 'positive',
  },
  {
    id: 15,
    date: '2024-12-16',
    crypto: 'SOL',
    title: 'Phantom Wallet Security Alert',
    description: 'Phantom issues security advisory for potential vulnerability. No funds affected, patch deployed within hours. Users urged to update.',
    type: 'negative',
  },
];

export const typeLabels = {
  positive: 'Positive',
  negative: 'Negative',
  neutral: 'Neutral',
};

// ============================================
// UTILITY FUNCTIONS
// ============================================

export const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  });
};

export const getCorrelationLabel = (corr) => {
  const absCorr = Math.abs(corr);
  if (absCorr >= 0.7) return 'Forte';
  if (absCorr >= 0.4) return 'Moyenne';
  if (absCorr >= 0.2) return 'Faible';
  return 'Negligeable';
};
