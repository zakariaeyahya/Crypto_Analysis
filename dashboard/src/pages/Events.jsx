import { useState, useEffect } from 'react';
import { MessageSquare, X, ChevronDown, ChevronUp, Calendar, Filter } from 'lucide-react';
import { useCrypto } from '../store';
import { cryptoFilters, typeLabels, formatDate } from '../data/mockData';
import Chatbot from '../components/Chatbot';
import '../styles/events.css';

// Event Card Component
const EventCard = ({ event, isExpanded, onToggle }) => {
  const sentimentClass = event.type || 'neutral';

  return (
    <div className={`event-card ${sentimentClass}`} onClick={onToggle}>
      <div className="event-card-header">
        <div className="event-meta">
          <span className="event-date">
            {formatDate ? formatDate(event.date) : event.date}
          </span>
          <span className={`event-type-badge ${sentimentClass}`}>
            {typeLabels?.[event.type] || event.type}
          </span>
          <span className="event-crypto-badge">{event.crypto}</span>
        </div>
        <span className="event-expand-icon">
          {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
        </span>
      </div>
      <h3 className="event-title">{event.title}</h3>
      {isExpanded && (
        <div className="event-details">
          <p className="event-description">{event.description}</p>
        </div>
      )}
    </div>
  );
};

// Event Modal Component
const EventModal = ({ event, onClose }) => {
  if (!event) return null;
  const sentimentClass = event.type || 'neutral';

  return (
    <div className="event-modal-overlay" onClick={onClose}>
      <div className={`event-modal ${sentimentClass}`} onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="event-meta">
            <span className="event-date">
              {formatDate ? formatDate(event.date) : event.date}
            </span>
            <span className={`event-type-badge ${sentimentClass}`}>
              {typeLabels?.[event.type] || event.type}
            </span>
            <span className="event-crypto-badge">{event.crypto}</span>
          </div>
          <button className="modal-close" onClick={onClose}>
            <X size={18} />
          </button>
        </div>
        <h2 className="modal-title">{event.title}</h2>
        <p className="modal-description">{event.description}</p>
        <div className="modal-footer">
          Impact: <strong style={{ color: sentimentClass === 'positive' ? '#10b981' : sentimentClass === 'negative' ? '#ef4444' : '#6b7280' }}>
            {typeLabels?.[event.type] || event.type}
          </strong>
        </div>
      </div>
    </div>
  );
};

export default function Events() {
  const { fetchEvents } = useCrypto();
  const [filter, setFilter] = useState('All');
  const [sentimentFilter, setSentimentFilter] = useState('All');
  const [expandedId, setExpandedId] = useState(null);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [viewMode, setViewMode] = useState('expand');
  const [events, setEvents] = useState([]);
  const [stats, setStats] = useState({ total: 0, positive: 0, negative: 0, neutral: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const sentimentOptions = [
    { value: 'All', label: 'Tous' },
    { value: 'positive', label: 'Positif' },
    { value: 'negative', label: 'Negatif' },
    { value: 'neutral', label: 'Neutre' }
  ];

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      setError(null);
      try {
        const result = await fetchEvents(filter, sentimentFilter, 50);
        setEvents(result.events);
        setStats(result.stats);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [filter, sentimentFilter, fetchEvents]);

  const handleEventClick = (event) => {
    if (viewMode === 'modal') {
      setSelectedEvent(event);
    } else {
      setExpandedId(expandedId === event.id ? null : event.id);
    }
  };

  if (loading) {
    return (
      <div className="events-page">
        <div className="events-loading">
          <div className="loading-spinner"></div>
          <p style={{ color: '#64748b' }}>Chargement des evenements...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="events-page">
        <div className="events-error">
          <p style={{ color: '#ef4444' }}>Erreur: {error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="events-page">
      {/* Header */}
      <header className="events-header">
        <div className="events-title-section">
          <h1>Evenements Crypto</h1>
          <p>Posts et actualites des reseaux sociaux</p>
        </div>
      </header>

      {/* Filters */}
      <div className="events-filters">
        <div className="filter-group">
          <label>Crypto:</label>
          <select
            className="filter-select"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            {cryptoFilters.map((crypto) => (
              <option key={crypto.value} value={crypto.value}>
                {crypto.label}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>Sentiment:</label>
          <select
            className="filter-select"
            value={sentimentFilter}
            onChange={(e) => setSentimentFilter(e.target.value)}
          >
            {sentimentOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        <div className="view-toggle">
          <button
            className={`view-btn ${viewMode === 'expand' ? 'active' : ''}`}
            onClick={() => setViewMode('expand')}
          >
            Expand
          </button>
          <button
            className={`view-btn ${viewMode === 'modal' ? 'active' : ''}`}
            onClick={() => setViewMode('modal')}
          >
            Modal
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="events-stats">
        <div className="stat-badge total">
          <span className="label">Total</span>
          <span className="value">{stats.total || events.length}</span>
        </div>
        <div className="stat-badge positive">
          <span className="label">Positifs</span>
          <span className="value">{stats.positive || 0}</span>
        </div>
        <div className="stat-badge negative">
          <span className="label">Negatifs</span>
          <span className="value">{stats.negative || 0}</span>
        </div>
        <div className="stat-badge neutral">
          <span className="label">Neutres</span>
          <span className="value">{stats.neutral || 0}</span>
        </div>
      </div>

      {/* Timeline */}
      <div className="events-timeline">
        <div className="timeline-line" />
        {events.length > 0 ? (
          events.map((event) => (
            <div key={event.id} className="event-item">
              <div className={`event-dot ${event.type || 'neutral'}`} />
              <EventCard
                event={event}
                isExpanded={expandedId === event.id}
                onToggle={() => handleEventClick(event)}
              />
            </div>
          ))
        ) : (
          <div className="events-empty">
            <div className="events-empty-icon">
              <MessageSquare size={32} />
            </div>
            <p>Aucun evenement trouve</p>
          </div>
        )}
      </div>

      {/* Modal */}
      {viewMode === 'modal' && selectedEvent && (
        <EventModal event={selectedEvent} onClose={() => setSelectedEvent(null)} />
      )}

      <Chatbot />
    </div>
  );
}
