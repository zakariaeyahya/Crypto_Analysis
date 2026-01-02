import { useState } from 'react';
import { Bot } from 'lucide-react';
import Chatbot from './Chatbot';

export default function ChatbotWidget() {
  const [open, setOpen] = useState(false);

  const toggle = () => setOpen((v) => !v);

  const buttonStyle = {
    position: 'fixed',
    right: '20px',
    bottom: '20px',
    width: '48px',
    height: '48px',
    borderRadius: '50%',
    backgroundColor: '#3b82f6',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: '#fff',
    boxShadow: '0 6px 18px rgba(0,0,0,0.25)',
    cursor: 'pointer',
    zIndex: 1100,
  };

  const wrapperStyle = {
    position: 'fixed',
    right: '20px',
    bottom: '20px',
    width: '360px',
    height: '520px',
    borderRadius: '12px',
    zIndex: 1100,
    overflow: 'hidden',
  };

  const closeBtnStyle = {
    position: 'absolute',
    top: '8px',
    right: '8px',
    background: 'rgba(0,0,0,0.4)',
    border: 'none',
    color: '#fff',
    width: '32px',
    height: '32px',
    borderRadius: '6px',
    cursor: 'pointer',
    zIndex: 1110,
  };

  return (
    <>
      {!open && (
        <button aria-label="Open chat" style={buttonStyle} onClick={toggle}>
          <Bot size={20} />
        </button>
      )}

      {open && (
        <div style={wrapperStyle}>
          <button aria-label="Close chat" style={closeBtnStyle} onClick={toggle}>
            ×
          </button>
          <Chatbot styleOverride={{ width: '100%', height: '100%', borderRadius: '12px' }} />
        </div>
      )}
    </>
  );
}
