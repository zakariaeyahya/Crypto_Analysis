const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

async function fetchAPI(endpoint) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`);
  if (!response.ok) throw new Error(`API Error: ${response.status}`);
  return response.json();
}

// CRYPTOS
export const getCryptos = () => fetchAPI('/api/cryptos');
export const getCryptoChart = (symbol, days = 7) => fetchAPI(`/api/cryptos/${symbol}/chart?days=${days}`);

// SENTIMENT
export const getGlobalSentiment = () => fetchAPI('/api/sentiment/global');
export const getSentimentTimeline = (symbol, days = 30) => fetchAPI(`/api/sentiment/${symbol}/timeline?days=${days}`);

// ANALYSIS
export const getAnalysisStats = (symbol) => fetchAPI(`/api/analysis/${symbol}/stats`);
export const getScatterData = (symbol, days = 30) => fetchAPI(`/api/analysis/${symbol}/scatter?days=${days}`);

// EVENTS
export const getEvents = (crypto, sentiment = 'All', limit = 50) => {
  const params = new URLSearchParams();
  if (crypto && crypto !== 'All') params.append('crypto', crypto);
  if (sentiment && sentiment !== 'All') params.append('sentiment', sentiment);
  params.append('limit', limit);
  return fetchAPI(`/api/events?${params}`);
};
export const getEventsStats = (crypto) => {
  const query = crypto && crypto !== 'All' ? `?crypto=${crypto}` : '';
  return fetchAPI(`/api/events/stats${query}`);
};
