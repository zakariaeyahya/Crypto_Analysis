import { useState, useEffect } from 'react';
import { useCrypto } from '../store';
import { cryptoFilters, typeLabels, formatDate, COLORS } from '../data/mockData';
import { sharedStyles } from '../styles/commonStyles';
import Chatbot from '../components/ChatBot';

// ============================================
// SUBCOMPONENT: EventCard
// ============================================
const EventCard = ({ event, isExpanded, onToggle }) => {
  const borderColor = COLORS[event.type] || COLORS.neutral;

  return (
    <div
      onClick={onToggle}
      style={{
        ...sharedStyles.card,
        borderLeft: `4px solid ${borderColor}`,
        cursor: 'pointer',
        transition: 'all 0.3s ease'
      }}
    >
      {/* HEADER */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: '12px'
      }}>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          <span style={{ color: '#888', fontSize: '0.875rem' }}>
            {formatDate ? formatDate(event.date) : event.date}
          </span>
          <span style={{
            padding: '2px 8px',
            borderRadius: '4px',
            backgroundColor: `${borderColor}22`,
            color: borderColor,
            fontSize: '0.75rem',
            fontWeight: '600'
          }}>
            {typeLabels?.[event.type] || event.type}
          </span>
          <span style={{
            padding: '2px 8px',
            borderRadius: '4px',
            backgroundColor: '#333',
            color: '#fff',
            fontSize: '0.75rem',
            fontWeight: '600'
          }}>
            {event.crypto}
          </span>
        </div>

        <span style={{
          fontSize: '1.25rem',
          color: '#888',
          fontWeight: 'bold'
        }}>
          {isExpanded ? '−' : '+'}
        </span>
      </div>

      {/* TITLE */}
      <h3 style={{
        fontSize: '1.125rem',
        color: '#fff',
        marginBottom: '8px',
        fontWeight: '600'
      }}>
        {event.title}
      </h3>

      {/* EXPANDED DETAILS */}
      {isExpanded && (
        <div style={{
          marginTop: '16px',
          paddingTop: '16px',
          borderTop: '1px solid #333'
        }}>
          <p style={{
            color: '#ccc',
            lineHeight: '1.6',
            fontSize: '0.9375rem'
          }}>
            {event.description}
          </p>
        </div>
      )}
    </div>
  );
};

// ============================================
// SUBCOMPONENT: EventModal
// ============================================
const EventModal = ({ event, onClose }) => {
  if (!event) return null;

  const borderColor = COLORS[event.type] || COLORS.neutral;

  return (
    <div
      onClick={onClose}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
        padding: '20px'
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          backgroundColor: '#0d0d0d',
          borderRadius: '12px',
          borderTop: `4px solid ${borderColor}`,
          maxWidth: '600px',
          width: '100%',
          maxHeight: '80vh',
          overflow: 'auto',
          padding: '32px',
          position: 'relative'
        }}
      >
        {/* MODAL HEADER */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          marginBottom: '20px'
        }}>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            <span style={{ color: '#888', fontSize: '0.875rem' }}>
              {formatDate ? formatDate(event.date) : event.date}
            </span>
            <span style={{
              padding: '4px 12px',
              borderRadius: '4px',
              backgroundColor: `${borderColor}22`,
              color: borderColor,
              fontSize: '0.875rem',
              fontWeight: '600'
            }}>
              {typeLabels?.[event.type] || event.type}
            </span>
            <span style={{
              padding: '4px 12px',
              borderRadius: '4px',
              backgroundColor: '#333',
              color: '#fff',
              fontSize: '0.875rem',
              fontWeight: '600'
            }}>
              {event.crypto}
            </span>
          </div>

          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              color: '#888',
              fontSize: '1.5rem',
              cursor: 'pointer',
              padding: '0',
              width: '32px',
              height: '32px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              borderRadius: '4px'
            }}
          >
            ×
          </button>
        </div>

        {/* TITLE */}
        <h2 style={{
          fontSize: '1.5rem',
          color: '#fff',
          marginBottom: '20px',
          fontWeight: '700'
        }}>
          {event.title}
        </h2>

        {/* DESCRIPTION */}
        <p style={{
          color: '#ccc',
          lineHeight: '1.8',
          fontSize: '1rem',
          marginBottom: '24px'
        }}>
          {event.description}
        </p>

        {/* FOOTER */}
        <div style={{
          paddingTop: '20px',
          borderTop: '1px solid #333',
          color: '#888',
          fontSize: '0.875rem'
        }}>
          Impact: <span style={{ color: borderColor, fontWeight: '600' }}>
            {typeLabels?.[event.type] || event.type}
          </span>
        </div>
      </div>
    </div>
  );
};

// ============================================
// MAIN COMPONENT: Events
// ============================================
export default function Events() {
  const { fetchEvents } = useCrypto();

  // ============================================
  // STATE
  // ============================================
  const [filter, setFilter] = useState('All');
  const [sentimentFilter, setSentimentFilter] = useState('All');
  const [expandedId, setExpandedId] = useState(null);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [viewMode, setViewMode] = useState('expand');
  const [events, setEvents] = useState([]);
  const [stats, setStats] = useState({ total: 0, positive: 0, negative: 0, neutral: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Sentiment filter options
  const sentimentOptions = [
    { value: 'All', label: 'All Sentiments' },
    { value: 'positive', label: 'Positive' },
    { value: 'negative', label: 'Negative' },
    { value: 'neutral', label: 'Neutral' }
  ];

  // ============================================
  // FETCH DATA
  // ============================================
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

  // ============================================
  // HANDLERS
  // ============================================
  const handleEventClick = (event) => {
    if (viewMode === 'modal') {
      setSelectedEvent(event);
    } else {
      setExpandedId(expandedId === event.id ? null : event.id);
    }
  };

  // ============================================
  // LOADING / ERROR STATES
  // ============================================
  if (loading) {
    return (
      <div style={{ ...sharedStyles.pageContainer, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <div style={{ color: '#888', fontSize: '1.25rem' }}>Loading events...</div>
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

  // ============================================
  // RENDER
  // ============================================
  return (
    <div style={sharedStyles.pageContainer}>
      {/* TITRE */}
      <h1 style={{ fontSize: '2rem', marginBottom: '24px', color: '#fff' }}>
        Crypto Events
      </h1>

      {/* HEADER */}
      <div style={{ marginBottom: '32px' }}>
        {/* FILTER ROW */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '16px',
          marginBottom: '20px'
        }}>
          {/* Crypto Filter */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <label style={{ color: '#fff', fontSize: '1rem' }}>
              Crypto:
            </label>
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
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
              {cryptoFilters.map((crypto) => (
                <option key={crypto.value} value={crypto.value}>
                  {crypto.label}
                </option>
              ))}
            </select>
          </div>

          {/* Sentiment Filter */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <label style={{ color: '#fff', fontSize: '1rem' }}>
              Sentiment:
            </label>
            <select
              value={sentimentFilter}
              onChange={(e) => setSentimentFilter(e.target.value)}
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
              {sentimentOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* View Toggle */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <label style={{ color: '#fff', fontSize: '1rem' }}>
              View:
            </label>
            <button
              onClick={() => setViewMode('expand')}
              style={{
                padding: '8px 16px',
                borderRadius: '8px',
                border: '1px solid #333',
                backgroundColor: viewMode === 'expand' ? COLORS.primary : '#1a1a1a',
                color: '#fff',
                fontSize: '0.875rem',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              Expand
            </button>
            <button
              onClick={() => setViewMode('modal')}
              style={{
                padding: '8px 16px',
                borderRadius: '8px',
                border: '1px solid #333',
                backgroundColor: viewMode === 'modal' ? COLORS.primary : '#1a1a1a',
                color: '#fff',
                fontSize: '0.875rem',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              Modal
            </button>
          </div>
        </div>

        {/* STATS ROW */}
        <div style={{
          display: 'flex',
          gap: '16px',
          flexWrap: 'wrap',
          padding: '16px',
          backgroundColor: '#1a1a1a',
          borderRadius: '8px'
        }}>
          <div style={{ color: '#fff' }}>
            Total: <strong>{stats.total || events.length}</strong>
          </div>
          <div style={{ color: COLORS.positive }}>
            Positive: <strong>{stats.positive || 0}</strong>
          </div>
          <div style={{ color: COLORS.negative }}>
            Negative: <strong>{stats.negative || 0}</strong>
          </div>
          <div style={{ color: '#888' }}>
            Neutral: <strong>{stats.neutral || 0}</strong>
          </div>
        </div>
      </div>

      {/* TIMELINE */}
      <div style={{ position: 'relative', paddingLeft: '40px' }}>
        {/* Timeline Line */}
        <div style={{
          position: 'absolute',
          left: '16px',
          top: '0',
          bottom: '0',
          width: '2px',
          background: 'linear-gradient(to bottom, #333, #666, #333)'
        }} />

        {/* Events */}
        {events.length > 0 ? (
          events.map((event) => (
            <div
              key={event.id}
              style={{
                position: 'relative',
                marginBottom: '24px'
              }}
            >
              {/* Timeline Dot */}
              <div style={{
                position: 'absolute',
                left: '-34px',
                top: '24px',
                width: '12px',
                height: '12px',
                borderRadius: '50%',
                backgroundColor: COLORS[event.type] || COLORS.neutral,
                boxShadow: `0 0 0 4px #0d0d0d, 0 0 0 6px ${(COLORS[event.type] || COLORS.neutral)}44`,
                zIndex: 1
              }} />

              {/* Event Card */}
              <EventCard
                event={event}
                isExpanded={expandedId === event.id}
                onToggle={() => handleEventClick(event)}
              />
            </div>
          ))
        ) : (
          <div style={{
            textAlign: 'center',
            padding: '60px 20px',
            color: '#888',
            fontSize: '1.125rem'
          }}>
            No events found.
          </div>
        )}
      </div>

      {/* MODAL */}
      {viewMode === 'modal' && selectedEvent && (
        <EventModal
          event={selectedEvent}
          onClose={() => setSelectedEvent(null)}
        />
      )}
      <Chatbot />
    </div>
  );
}
