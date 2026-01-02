import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import * as api from '../api';

const CryptoContext = createContext();

export function CryptoProvider({ children }) {
  // State
  const [cryptos, setCryptos] = useState([]);
  const [sentiment, setSentiment] = useState({ score: 0, label: 'Loading' });
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch initial data
  useEffect(() => {
    async function fetchData() {
      try {
        const [cryptosData, sentimentData, chartResult] = await Promise.all([
          api.getCryptos(),
          api.getGlobalSentiment(),
          api.getCryptoChart('BTC', 7)
        ]);
        setCryptos(cryptosData);
        setSentiment(sentimentData);
        setChartData(chartResult.data || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  // Timeline data fetcher
  const fetchTimeline = useCallback(async (symbol, days = 30) => {
    const result = await api.getSentimentTimeline(symbol, days);
    const data = result.data || [];
    return data.map(item => ({
      date: item.date,
      sentiment: Math.round((item.sentiment_mean || 0) * 100),
      ma7: item.ma7 ? Math.round(item.ma7 * 100) : null
    }));
  }, []);

  // Analysis data fetcher
  const fetchAnalysis = useCallback(async (symbol, days = 30) => {
    const [statsResult, scatterResult] = await Promise.all([
      api.getAnalysisStats(symbol),
      api.getScatterData(symbol, days)
    ]);

    // Format stats for the Analysis page
    const stats = {
      correlation: statsResult.correlation?.pearson_r || 0,
      pValue: statsResult.correlation?.p_value || 0,
      correlationLabel: statsResult.correlationLabel || 'N/A',
      nObservations: scatterResult.data?.length || 0
    };

    // Format scatter data (backend already returns sentiment in -100 to +100)
    const scatterData = (scatterResult.data || []).map(item => ({
      date: item.date,
      sentiment: item.sentiment || 0,
      priceChange: item.priceChange || 0
    }));

    return { stats, scatterData };
  }, []);

  // Events data fetcher
  const fetchEvents = useCallback(async (crypto, sentiment = 'All', limit = 50) => {
    const [events, stats] = await Promise.all([
      api.getEvents(crypto, sentiment, limit),
      api.getEventsStats(crypto)
    ]);
    return {
      events: events.map((e, i) => ({
        id: e.id || i,
        date: e.date,
        crypto: e.crypto,
        title: e.text?.substring(0, 100) || 'No title',
        description: e.text || '',
        type: e.sentiment || 'neutral'
      })),
      stats
    };
  }, []);

  const value = {
    // Data
    cryptos,
    sentiment,
    chartData,
    loading,
    error,
    // Fetchers
    fetchTimeline,
    fetchAnalysis,
    fetchEvents,
    // Refresh
    refresh: () => window.location.reload()
  };

  return (
    <CryptoContext.Provider value={value}>
      {children}
    </CryptoContext.Provider>
  );
}

export function useCrypto() {
  const context = useContext(CryptoContext);
  if (!context) throw new Error('useCrypto must be used within CryptoProvider');
  return context;
}
