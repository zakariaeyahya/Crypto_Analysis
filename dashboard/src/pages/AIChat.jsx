import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader } from 'lucide-react';
import { useCrypto } from '../store';

const AIChat = () => {
  const [messages, setMessages] = useState([
    {
      id: '1',
      content: "Bonjour! 👋 Je suis votre assistant IA spécialisé dans l'analyse de cryptomonnaies. Je peux vous aider avec:\n\n• Analyse des tendances de prix\n• Sentiment du marché\n• Informations sur BTC, ETH, SOL\n• Prédictions basées sur les données\n\nComment puis-je vous assister?",
      role: 'assistant',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const { cryptos } = useCrypto();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Base de connaissances pour les réponses AI
  const knowledgeBase = {
    btc: 'Bitcoin (BTC) est la première cryptomonnaie décentralisée. C\'est actuellement le leader du marché avec la plus grande capitalisation.',
    eth: 'Ethereum (ETH) est une plateforme blockchain qui permet les contrats intelligents et les applications décentralisées (DApps).',
    sol: 'Solana (SOL) est une blockchain haute performance connue pour ses faibles frais de transaction et sa vitesse.',
    price: 'Pour obtenir les prix actuels, consultez la page Vue d\'ensemble du tableau de bord.',
    sentiment: 'L\'analyse du sentiment examine les émotions des investisseurs sur les réseaux sociaux pour prédire les mouvements du marché.',
    crypto: 'Une cryptomonnaie est une forme d\'argent numérique décentralisée utilisant la technologie blockchain.',
    market: 'Le marché des cryptomonnaies fonctionne 24/7 et est très volatil. Il est influencé par l\'actualité, les réglementations et le sentiment.',
  };

  // Fonction pour générer une réponse AI intelligente
  const generateAIResponse = (userMessage) => {
    const lowerInput = userMessage.toLowerCase();

    // Réponses contextuelles
    if (lowerInput.includes('bonjour') || lowerInput.includes('salut') || lowerInput.includes('coucou')) {
      return "Bonjour! 👋 Comment puis-je vous aider avec l'analyse des cryptomonnaies aujourd'hui?";
    }

    if (lowerInput.includes('bitcoin') || lowerInput.includes('btc')) {
      return `📊 ${knowledgeBase.btc}\n\nPrix actuel: Consultez la page Vue d'ensemble pour les données en temps réel.`;
    }

    if (lowerInput.includes('ethereum') || lowerInput.includes('eth')) {
      return `📊 ${knowledgeBase.eth}\n\nEthernet domine le marché des contrats intelligents.`;
    }

    if (lowerInput.includes('solana') || lowerInput.includes('sol')) {
      return `📊 ${knowledgeBase.sol}\n\nSolana est un excellent choix pour les transactions rapides et bon marché.`;
    }

    if (
      lowerInput.includes('prix') ||
      lowerInput.includes('price') ||
      lowerInput.includes('valeur')
    ) {
      return `💰 ${knowledgeBase.price}\n\nVous pouvez voir les graphiques de prix détaillés dans la section Analyse du tableau de bord.`;
    }

    if (
      lowerInput.includes('sentiment') ||
      lowerInput.includes('analyse') ||
      lowerInput.includes('prédiction')
    ) {
      return `📈 ${knowledgeBase.sentiment}\n\nNotre tableau de bord utilise le sentiment Reddit et les données d'analyse pour fournir des insights.`;
    }

    if (
      lowerInput.includes('qu\'est-ce') ||
      lowerInput.includes('c\'est quoi') ||
      lowerInput.includes('what is')
    ) {
      return `🔍 Les cryptomonnaies sont des actifs numériques décentralisés. ${knowledgeBase.crypto}\n\nPour en savoir plus, consultez notre page d'analyse!`;
    }

    if (
      lowerInput.includes('comment') ||
      lowerInput.includes('how') ||
      lowerInput.includes('marché')
    ) {
      return `📊 ${knowledgeBase.market}\n\nNous analysons continuellement les tendances pour vous fournir les meilleures insights.`;
    }

    if (
      lowerInput.includes('conseil') ||
      lowerInput.includes('recommendation') ||
      lowerInput.includes('acheter')
    ) {
      return "⚠️ Je fournis des analyses et des informations, mais je ne peux pas donner de conseils d'investissement personnalisés. Consultez toujours un professionnel avant d'investir.";
    }

    if (lowerInput.includes('aide') || lowerInput.includes('help')) {
      return "🆘 Je peux vous aider avec:\n\n• Questions sur BTC, ETH, SOL\n• Explications sur le sentiment du marché\n• Informations sur la blockchain\n• Tendances des cryptomonnaies\n\nQue voulez-vous savoir?";
    }

    // Réponse par défaut intelligente
    return `Je comprends votre question sur "${userMessage.substring(0, 30)}..."\n\nPour de meilleures réponses, vous pouvez me demander:\n• Des informations sur des cryptomonnaies spécifiques\n• Des explications sur le sentiment du marché\n• Comment interpréter les graphiques du tableau de bord\n\nQu'aimerais-je approfondir?`;
  };

  const handleSend = async () => {
    if (!input.trim() || isTyping) return;

    const userMessage = {
      id: Date.now().toString(),
      content: input.trim(),
      role: 'user',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);

    // Simulation du délai de réponse
    await new Promise((resolve) => setTimeout(resolve, 800));

    const aiResponse = {
      id: (Date.now() + 1).toString(),
      content: generateAIResponse(input.trim()),
      role: 'assistant',
      timestamp: new Date(),
    };

    setIsTyping(false);
    setMessages((prev) => [...prev, aiResponse]);
  };

  const containerStyle = {
    display: 'flex',
    flexDirection: 'column',
    height: 'calc(100vh - 80px)',
    backgroundColor: '#0f172a',
    color: '#e2e8f0',
    fontFamily: 'system-ui, -apple-system, sans-serif',
  };

  const headerStyle = {
    borderBottom: '1px solid #1e293b',
    padding: '20px',
    backgroundColor: '#1e293b',
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  };

  const messagesContainerStyle = {
    flex: 1,
    overflowY: 'auto',
    padding: '20px',
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  };

  const messageStyle = (role) => ({
    display: 'flex',
    justifyContent: role === 'user' ? 'flex-end' : 'flex-start',
    marginBottom: '8px',
  });

  const messageBubbleStyle = (role) => ({
    maxWidth: '70%',
    padding: '12px 16px',
    borderRadius: '12px',
    backgroundColor: role === 'user' ? '#3b82f6' : '#1e293b',
    border: role === 'user' ? 'none' : '1px solid #334155',
    color: role === 'user' ? '#fff' : '#e2e8f0',
    wordWrap: 'break-word',
    whiteSpace: 'pre-wrap',
    lineHeight: '1.5',
    fontSize: '14px',
  });

  const inputContainerStyle = {
    borderTop: '1px solid #1e293b',
    padding: '16px 20px',
    backgroundColor: '#1e293b',
    display: 'flex',
    gap: '12px',
    alignItems: 'flex-end',
  };

  const inputStyle = {
    flex: 1,
    backgroundColor: '#0f172a',
    border: '1px solid #334155',
    borderRadius: '8px',
    color: '#e2e8f0',
    padding: '10px 14px',
    fontSize: '14px',
    outline: 'none',
    fontFamily: 'inherit',
  };

  const buttonStyle = {
    backgroundColor: '#3b82f6',
    border: 'none',
    borderRadius: '8px',
    color: '#fff',
    padding: '10px 16px',
    cursor: isTyping ? 'not-allowed' : 'pointer',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    opacity: isTyping ? 0.6 : 1,
    transition: 'background-color 0.2s',
    fontSize: '14px',
    fontWeight: 'bold',
  };

  const typingIndicatorStyle = {
    display: 'flex',
    gap: '4px',
    alignItems: 'center',
    color: '#64748b',
    fontSize: '12px',
  };

  return (
    <div style={containerStyle}>
      {/* Header */}
      <div style={headerStyle}>
        <Bot size={24} color="#3b82f6" />
        <div>
          <h1 style={{ margin: 0, fontSize: '18px', fontWeight: 'bold' }}>
            Assistant IA Crypto
          </h1>
          <p style={{ margin: '4px 0 0 0', fontSize: '12px', color: '#94a3b8' }}>
            En ligne 🟢
          </p>
        </div>
      </div>

      {/* Messages */}
      <div style={messagesContainerStyle}>
        {messages.map((message) => (
          <div key={message.id}>
            <div style={messageStyle(message.role)}>
              <div style={messageBubbleStyle(message.role)}>
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                  {message.role === 'assistant' && (
                    <Bot size={16} style={{ marginTop: '2px', flexShrink: 0 }} />
                  )}
                  <span>{message.content}</span>
                </div>
              </div>
            </div>
            <div
              style={{
                textAlign: message.role === 'user' ? 'right' : 'left',
                fontSize: '11px',
                color: '#64748b',
                paddingRight: message.role === 'user' ? '10%' : '0',
                paddingLeft: message.role === 'assistant' ? '10%' : '0',
              }}
            >
              {message.timestamp?.toLocaleTimeString('fr-FR', {
                hour: '2-digit',
                minute: '2-digit',
              })}
            </div>
          </div>
        ))}

        {isTyping && (
          <div style={{ ...messageStyle('assistant'), marginTop: '8px' }}>
            <div style={messageBubbleStyle('assistant')}>
              <div style={typingIndicatorStyle}>
                <Loader size={14} style={{ animation: 'spin 1s linear infinite' }} />
                <span>L'assistant est en train de répondre...</span>
              </div>
              <style>{`
                @keyframes spin {
                  from { transform: rotate(0deg); }
                  to { transform: rotate(360deg); }
                }
              `}</style>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div style={inputContainerStyle}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Posez une question sur les crypto..."
          style={inputStyle}
          disabled={isTyping}
        />
        <button style={buttonStyle} onClick={handleSend} disabled={isTyping}>
          <Send size={18} />
          <span style={{ display: 'none' }}>Envoyer</span>
        </button>
      </div>
    </div>
  );
};

export default AIChat;
