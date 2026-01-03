import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, Loader, Sparkles, Trash2, ThumbsUp, ThumbsDown } from 'lucide-react';
import { sendChatMessage, getChatSuggestions, clearChatSession, sendFeedback } from '../api';

// Generer un ID de session unique
const generateSessionId = () => {
  return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
};

export default function Chatbot({ styleOverride = {} }) {
  const [open, setOpen] = useState(false);
  const [sessionId] = useState(() => generateSessionId());
  const [messages, setMessages] = useState([
    {
      id: '1',
      content: "Bonjour! Je suis votre assistant IA specialise dans l'analyse de cryptomonnaies. Posez-moi vos questions sur Bitcoin, Ethereum ou Solana!",
      role: 'assistant',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const [feedbackGiven, setFeedbackGiven] = useState({});  // Track feedback per message
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, open]);

  // Load suggestions on mount
  useEffect(() => {
    const loadSuggestions = async () => {
      try {
        const data = await getChatSuggestions();
        if (data.suggestions) {
          setSuggestions(data.suggestions.slice(0, 4));
        }
      } catch (error) {
        setSuggestions([
          "Quel est le sentiment actuel de Bitcoin?",
          "Compare le sentiment de ETH et SOL",
          "Quelle crypto a le meilleur sentiment?",
          "Resume l'analyse de Solana"
        ]);
      }
    };
    loadSuggestions();
  }, []);

  const handleSend = async (messageText = null) => {
    const textToSend = messageText || input.trim();
    if (!textToSend || isTyping) return;

    const userMessage = {
      id: Date.now().toString(),
      content: textToSend,
      role: 'user',
      timestamp: new Date()
    };
    setMessages((p) => [...p, userMessage]);
    setInput('');
    setIsTyping(true);
    setShowSuggestions(false);

    try {
      // Envoyer avec session_id pour la memoire conversationnelle
      const response = await sendChatMessage(textToSend, null, sessionId);

      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        content: response.response || response.answer || "Desole, je n'ai pas pu generer une reponse.",
        role: 'assistant',
        timestamp: new Date(),
        hasHistory: response.metadata?.has_history,
        relatedQuestion: textToSend  // Store the question for feedback
      };

      setMessages((p) => [...p, assistantMessage]);
    } catch (error) {
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        content: "Desole, une erreur s'est produite. Verifiez que le serveur backend est lance.",
        role: 'assistant',
        timestamp: new Date(),
        isError: true
      };
      setMessages((p) => [...p, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleClearChat = async () => {
    try {
      await clearChatSession(sessionId);
    } catch (error) {
      console.error('Failed to clear session:', error);
    }
    // Reset local state
    setMessages([
      {
        id: Date.now().toString(),
        content: "Conversation effacee. Comment puis-je vous aider?",
        role: 'assistant',
        timestamp: new Date(),
      },
    ]);
    setShowSuggestions(true);
  };

  const handleSuggestionClick = (suggestion) => {
    handleSend(suggestion);
  };

  const handleFeedback = async (messageId, feedbackType, question, answer) => {
    // Don't allow feedback twice
    if (feedbackGiven[messageId]) return;

    try {
      await sendFeedback(messageId, question, answer, feedbackType, sessionId);
      setFeedbackGiven(prev => ({ ...prev, [messageId]: feedbackType }));
    } catch (error) {
      console.error('Failed to send feedback:', error);
    }
  };

  // Styles
  const floatBtn = {
    position: 'fixed',
    right: '20px',
    bottom: '20px',
    width: '56px',
    height: '56px',
    borderRadius: '50%',
    background: 'linear-gradient(135deg, #667eea, #764ba2)',
    color: '#fff',
    border: 'none',
    boxShadow: '0 6px 20px rgba(102, 126, 234, 0.4)',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 2000,
    transition: 'transform 0.2s, box-shadow 0.2s',
  };

  const panel = {
    position: 'fixed',
    right: '20px',
    bottom: '88px',
    width: '380px',
    height: '500px',
    borderRadius: '16px',
    background: 'rgba(15, 15, 20, 0.95)',
    backdropFilter: 'blur(20px)',
    boxShadow: '0 12px 40px rgba(0, 0, 0, 0.5)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    color: '#fff',
    zIndex: 2000,
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
  };

  const header = {
    padding: '14px 16px',
    borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    background: 'rgba(102, 126, 234, 0.1)'
  };

  const messagesStyle = {
    flex: 1,
    overflowY: 'auto',
    padding: '16px',
    display: 'flex',
    flexDirection: 'column',
    gap: '12px'
  };

  const inputRow = {
    padding: '12px',
    borderTop: '1px solid rgba(255, 255, 255, 0.1)',
    display: 'flex',
    gap: '10px',
    background: 'rgba(0, 0, 0, 0.2)'
  };

  const inputStyle = {
    flex: 1,
    padding: '10px 14px',
    borderRadius: '10px',
    border: '1px solid rgba(255, 255, 255, 0.15)',
    background: 'rgba(255, 255, 255, 0.05)',
    color: '#fff',
    fontSize: '14px',
    outline: 'none'
  };

  const sendBtn = {
    padding: '10px 14px',
    borderRadius: '10px',
    background: 'linear-gradient(135deg, #667eea, #764ba2)',
    color: '#fff',
    border: 'none',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  };

  const suggestionBtn = {
    padding: '8px 12px',
    borderRadius: '8px',
    border: '1px solid rgba(102, 126, 234, 0.4)',
    background: 'rgba(102, 126, 234, 0.1)',
    color: '#a5b4fc',
    fontSize: '12px',
    cursor: 'pointer',
    textAlign: 'left',
    transition: 'all 0.2s'
  };

  const iconBtn = {
    background: 'rgba(255, 255, 255, 0.1)',
    border: 'none',
    color: '#9ca3af',
    cursor: 'pointer',
    width: '28px',
    height: '28px',
    borderRadius: '6px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: 'all 0.2s'
  };

  return (
    <>
      {open && (
        <div style={panel} role="dialog" aria-label="Chatbot panel">
          <div style={header}>
            <div style={{
              width: '36px',
              height: '36px',
              borderRadius: '10px',
              background: 'linear-gradient(135deg, #667eea, #764ba2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Bot size={20} color="#fff" />
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 600, fontSize: '15px' }}>Assistant IA Crypto</div>
              <div style={{ fontSize: '12px', color: '#10b981', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#10b981' }}></span>
                En ligne - Memoire active
              </div>
            </div>
            {/* Clear chat button */}
            <button
              aria-label="Effacer conversation"
              title="Effacer conversation"
              onClick={handleClearChat}
              style={iconBtn}
              onMouseOver={(e) => { e.currentTarget.style.background = 'rgba(239, 68, 68, 0.3)'; e.currentTarget.style.color = '#ef4444'; }}
              onMouseOut={(e) => { e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)'; e.currentTarget.style.color = '#9ca3af'; }}
            >
              <Trash2 size={14} />
            </button>
            {/* Close button */}
            <button
              aria-label="Fermer chat"
              onClick={() => setOpen(false)}
              style={iconBtn}
            >
              x
            </button>
          </div>

          <div style={messagesStyle}>
            {messages.map((m) => (
              <div key={m.id}>
                <div style={{ display: 'flex', justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start' }}>
                  <div style={{
                    maxWidth: '85%',
                    padding: '10px 14px',
                    borderRadius: m.role === 'user' ? '14px 14px 4px 14px' : '14px 14px 14px 4px',
                    background: m.role === 'user'
                      ? 'linear-gradient(135deg, #667eea, #764ba2)'
                      : m.isError ? 'rgba(239, 68, 68, 0.2)' : 'rgba(255, 255, 255, 0.08)',
                    color: '#fff',
                    fontSize: '14px',
                    lineHeight: '1.5'
                  }}>
                    {m.content}
                  </div>
                </div>
                {/* Feedback buttons for assistant messages (not the welcome message) */}
                {m.role === 'assistant' && m.relatedQuestion && (
                  <div style={{
                    display: 'flex',
                    gap: '8px',
                    marginTop: '6px',
                    marginLeft: '4px'
                  }}>
                    <button
                      onClick={() => handleFeedback(m.id, 'positive', m.relatedQuestion, m.content)}
                      disabled={!!feedbackGiven[m.id]}
                      style={{
                        background: feedbackGiven[m.id] === 'positive'
                          ? 'rgba(16, 185, 129, 0.3)'
                          : 'rgba(255, 255, 255, 0.05)',
                        border: feedbackGiven[m.id] === 'positive'
                          ? '1px solid rgba(16, 185, 129, 0.5)'
                          : '1px solid rgba(255, 255, 255, 0.1)',
                        borderRadius: '6px',
                        padding: '4px 8px',
                        cursor: feedbackGiven[m.id] ? 'default' : 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                        color: feedbackGiven[m.id] === 'positive' ? '#10b981' : '#9ca3af',
                        fontSize: '12px',
                        opacity: feedbackGiven[m.id] && feedbackGiven[m.id] !== 'positive' ? 0.4 : 1,
                        transition: 'all 0.2s'
                      }}
                      title="Bonne reponse"
                    >
                      <ThumbsUp size={12} />
                    </button>
                    <button
                      onClick={() => handleFeedback(m.id, 'negative', m.relatedQuestion, m.content)}
                      disabled={!!feedbackGiven[m.id]}
                      style={{
                        background: feedbackGiven[m.id] === 'negative'
                          ? 'rgba(239, 68, 68, 0.3)'
                          : 'rgba(255, 255, 255, 0.05)',
                        border: feedbackGiven[m.id] === 'negative'
                          ? '1px solid rgba(239, 68, 68, 0.5)'
                          : '1px solid rgba(255, 255, 255, 0.1)',
                        borderRadius: '6px',
                        padding: '4px 8px',
                        cursor: feedbackGiven[m.id] ? 'default' : 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                        color: feedbackGiven[m.id] === 'negative' ? '#ef4444' : '#9ca3af',
                        fontSize: '12px',
                        opacity: feedbackGiven[m.id] && feedbackGiven[m.id] !== 'negative' ? 0.4 : 1,
                        transition: 'all 0.2s'
                      }}
                      title="Mauvaise reponse"
                    >
                      <ThumbsDown size={12} />
                    </button>
                  </div>
                )}
              </div>
            ))}

            {/* Typing indicator */}
            {isTyping && (
              <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                <div style={{
                  padding: '10px 14px',
                  borderRadius: '14px 14px 14px 4px',
                  background: 'rgba(255, 255, 255, 0.08)',
                  color: '#9ca3af',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  fontSize: '14px'
                }}>
                  <Loader size={14} style={{ animation: 'spin 1s linear infinite' }} />
                  Analyse en cours...
                </div>
              </div>
            )}

            {/* Suggestions */}
            {showSuggestions && suggestions.length > 0 && messages.length <= 1 && (
              <div style={{ marginTop: '8px' }}>
                <div style={{
                  fontSize: '12px',
                  color: '#9ca3af',
                  marginBottom: '8px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}>
                  <Sparkles size={12} />
                  Questions suggerees
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  {suggestions.map((suggestion, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSuggestionClick(suggestion)}
                      style={suggestionBtn}
                      onMouseOver={(e) => {
                        e.target.style.background = 'rgba(102, 126, 234, 0.25)';
                        e.target.style.borderColor = 'rgba(102, 126, 234, 0.6)';
                      }}
                      onMouseOut={(e) => {
                        e.target.style.background = 'rgba(102, 126, 234, 0.1)';
                        e.target.style.borderColor = 'rgba(102, 126, 234, 0.4)';
                      }}
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          <div style={inputRow}>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Posez une question sur les cryptos..."
              style={inputStyle}
              disabled={isTyping}
            />
            <button
              onClick={() => handleSend()}
              style={{
                ...sendBtn,
                opacity: isTyping ? 0.5 : 1,
                cursor: isTyping ? 'not-allowed' : 'pointer'
              }}
              disabled={isTyping}
            >
              <Send size={18} />
            </button>
          </div>
        </div>
      )}

      <button
        aria-expanded={open}
        aria-label={open ? 'Fermer chat' : 'Ouvrir chat'}
        onClick={() => setOpen((v) => !v)}
        style={{ ...floatBtn, ...styleOverride }}
        onMouseOver={(e) => {
          e.currentTarget.style.transform = 'scale(1.05)';
          e.currentTarget.style.boxShadow = '0 8px 25px rgba(102, 126, 234, 0.5)';
        }}
        onMouseOut={(e) => {
          e.currentTarget.style.transform = 'scale(1)';
          e.currentTarget.style.boxShadow = '0 6px 20px rgba(102, 126, 234, 0.4)';
        }}
      >
        <Bot size={24} />
      </button>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </>
  );
}
