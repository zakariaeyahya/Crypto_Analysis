import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, Loader } from 'lucide-react';

export default function Chatbot({ styleOverride = {} }) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: '1',
      content: "Bonjour! Je suis votre assistant IA spécialisé dans l'analyse de cryptomonnaies. Comment puis-je vous aider ?",
      role: 'assistant',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, open]);

  const knowledgeBase = {
    btc: 'Bitcoin (BTC) est la première cryptomonnaie décentralisée.',
    eth: 'Ethereum (ETH) est une plateforme pour contrats intelligents.',
    sol: 'Solana (SOL) est une blockchain haute performance.',
  };

  const generateAIResponse = (userMessage) => {
    const lower = userMessage.toLowerCase();
    if (lower.includes('btc') || lower.includes('bitcoin')) return knowledgeBase.btc;
    if (lower.includes('eth') || lower.includes('ethereum')) return knowledgeBase.eth;
    if (lower.includes('sol')) return knowledgeBase.sol;
    return "Désolé, je n'ai pas compris. Posez une question plus précise.";
  };

  const handleSend = async () => {
    if (!input.trim() || isTyping) return;
    const userMessage = { id: Date.now().toString(), content: input.trim(), role: 'user', timestamp: new Date() };
    setMessages((p) => [...p, userMessage]);
    setInput('');
    setIsTyping(true);
    await new Promise((r) => setTimeout(r, 700));
    const ai = { id: (Date.now() + 1).toString(), content: generateAIResponse(userMessage.content), role: 'assistant', timestamp: new Date() };
    setIsTyping(false);
    setMessages((p) => [...p, ai]);
  };

  // Styles (inline for simplicity)
  const floatBtn = {
    position: 'fixed',
    right: '20px',
    bottom: '20px',
    width: '56px',
    height: '56px',
    borderRadius: '50%',
    background: 'linear-gradient(135deg,#10B981,#3B82F6)',
    color: '#fff',
    border: 'none',
    boxShadow: '0 6px 18px rgba(16,185,129,0.15)',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 2000,
  };

  const panel = {
    position: 'fixed',
    right: '20px',
    bottom: '88px',
    width: '340px',
    height: '420px',
    borderRadius: '12px',
    background: '#0b0b0d',
    boxShadow: '0 12px 40px rgba(0,0,0,0.6)',
    color: '#fff',
    zIndex: 2000,
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
  };

  const header = { padding: '10px 12px', borderBottom: '1px solid #111', display: 'flex', alignItems: 'center', gap: '8px' };
  const messagesStyle = { flex: 1, overflowY: 'auto', padding: '12px', display: 'flex', flexDirection: 'column', gap: '10px' };
  const inputRow = { padding: '10px', borderTop: '1px solid #111', display: 'flex', gap: '8px' };
  const inputStyle = { flex: 1, padding: '8px 10px', borderRadius: '8px', border: '1px solid #233', background: '#071022', color: '#fff' };
  const sendBtn = { padding: '8px 12px', borderRadius: '8px', background: '#3b82f6', color: '#fff', border: 'none' };

  return (
    <>
      {open && (
        <div style={panel} role="dialog" aria-label="Chatbot panel">
          <div style={header}>
            <Bot size={18} color="#3B82F6" />
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 700 }}>Assistant IA Crypto</div>
              <div style={{ fontSize: 12, color: '#9ca3af' }}>En ligne</div>
            </div>
            <button aria-label="Close chat" onClick={() => setOpen(false)} style={{ background: 'none', border: 'none', color: '#9ca3af', cursor: 'pointer' }}>✕</button>
          </div>

          <div style={messagesStyle}>
            {messages.map((m) => (
              <div key={m.id} style={{ display: 'flex', justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start' }}>
                <div style={{ maxWidth: '75%', padding: '8px 12px', borderRadius: 10, background: m.role === 'user' ? '#2563eb' : '#0f1724', color: '#fff' }}>{m.content}</div>
              </div>
            ))}
            {isTyping && (
              <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                <div style={{ padding: '6px 10px', borderRadius: 8, background: '#0f1724', color: '#9ca3af', display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Loader size={14} /> En train de répondre...
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div style={inputRow}>
            <input value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleSend()} placeholder="Posez une question..." style={inputStyle} />
            <button onClick={handleSend} style={sendBtn} disabled={isTyping}><Send size={16} /></button>
          </div>
        </div>
      )}

      <button aria-expanded={open} aria-label={open ? 'Fermer chat' : 'Ouvrir chat'} onClick={() => setOpen((v) => !v)} style={{ ...floatBtn, ...styleOverride }}>
        <Bot size={22} />
      </button>
    </>
  );
}
