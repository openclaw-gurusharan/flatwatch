// Chat Guard - AI-powered financial query interface
'use client';

import { useEffect, useState, useRef } from 'react';
import { PageLayout } from '@/components/layout/PageLayout';
import { ProtectedRoute } from '@/lib/ProtectedRoute';
import { chatApi } from '@/lib/api';
import type { ChatMessage } from '@/lib/api';

function ChatContent() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setLoading(false);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = async () => {
    if (!input.trim() || sending) return;

    const userMessage: ChatMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setSending(true);

    try {
      setError(null);
      const response = await chatApi.query(input);
      setMessages(prev => [...prev, response]);
    } catch {
      setError('Failed to get response');
      setMessages(prev => [...prev.slice(0, -1)]);
    } finally {
      setSending(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const suggestedQueries = [
    'Show me all water bills from last month',
    'What is the total maintenance collected?',
    'List all unverified transactions above ₹5000',
    'Who approved the latest expense?',
  ];

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-white">
        <div className="flex items-center gap-2">
          <span className="h-3 w-3 animate-pulse rounded-full bg-[rgb(255,97,26)]" />
          <span className="text-[#999]">Loading...</span>
        </div>
      </div>
    );
  }

  return (
    <PageLayout title="Chat Guard" description="AI-powered financial queries">
      {/* Error message */}
      {error && (
        <div style={{ marginBottom: '24px', borderRadius: '16px', backgroundColor: 'rgb(255,243,224)', padding: '16px', color: 'rgb(255,97,26)' }}>
          {error}
        </div>
      )}

      {/* Welcome message when no messages */}
      {messages.length === 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '32px', alignItems: 'center', textAlign: 'center' }}>
          <div>
            <h2 style={{ fontSize: '24px', fontWeight: 500, color: '#333', marginBottom: '8px' }}>How can I help you today?</h2>
            <p style={{ color: '#999' }}>Ask anything about your society finances</p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', width: '100%' }}>
            {suggestedQueries.map((query, i) => (
              <button
                key={i}
                onClick={() => setInput(query)}
                style={{
                  borderRadius: '16px',
                  border: '1px solid rgb(238,238,238)',
                  backgroundColor: 'white',
                  padding: '16px',
                  textAlign: 'left',
                  fontSize: '14px',
                  color: '#333',
                  transition: 'all 0.2s',
                  cursor: 'pointer'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = 'rgb(255,97,26)';
                  e.currentTarget.style.boxShadow = '0 4px 12px rgba(255,97,26,0.1)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = 'rgb(238,238,238)';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                {query}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Messages */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {messages.map((msg, i) => (
          <div
            key={i}
            style={{ display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start' }}
          >
            <div
              style={{
                maxWidth: '80%',
                borderRadius: '24px',
                padding: '16px 20px',
                backgroundColor: msg.role === 'user' ? 'rgb(255,97,26)' : 'rgb(238,238,238)',
                color: msg.role === 'user' ? 'white' : '#333'
              }}
            >
              <p style={{ whiteSpace: 'pre-wrap', fontSize: '14px', lineHeight: 1.5, margin: 0 }}>{msg.content}</p>
              {msg.sources && msg.sources.length > 0 && (
                <div style={{ marginTop: '8px', paddingTop: '8px', borderTop: '1px solid rgba(0,0,0,0.1)' }}>
                  <p style={{ fontSize: '12px', opacity: 0.7, margin: 0 }}>Sources: {msg.sources.join(', ')}</p>
                </div>
              )}
            </div>
          </div>
        ))}
        {sending && (
          <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
            <div style={{ borderRadius: '24px', backgroundColor: 'rgb(238,238,238)', padding: '16px 20px' }}>
              <div style={{ display: 'flex', gap: '4px' }}>
                <span className="h-2 w-2 animate-bounce rounded-full bg-[#999]" style={{ animationDelay: '0ms' }} />
                <span className="h-2 w-2 animate-bounce rounded-full bg-[#999]" style={{ animationDelay: '150ms' }} />
                <span className="h-2 w-2 animate-bounce rounded-full bg-[#999]" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div style={{
        position: 'sticky',
        bottom: 0,
        backgroundColor: 'white',
        borderTop: '1px solid rgb(238,238,238)',
        padding: '16px 0',
        marginTop: '32px'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'flex-end',
          gap: '12px',
          borderRadius: '999px',
          border: '2px solid rgb(238,238,238)',
          backgroundColor: 'rgb(249,249,249)',
          padding: '8px',
          transition: 'all 0.2s'
        }}>
          <textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about transactions, balances, compliance..."
            disabled={sending}
            rows={1}
            style={{
              flex: 1,
              resize: 'none',
              border: 'none',
              backgroundColor: 'transparent',
              padding: '8px 16px',
              fontSize: '14px',
              color: '#333',
              outline: 'none',
              minHeight: '40px',
              maxHeight: '120px'
            }}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || sending}
            style={{
              width: '36px',
              height: '36px',
              borderRadius: '50%',
              border: 'none',
              backgroundColor: input.trim() && !sending ? 'rgb(255,97,26)' : 'rgb(238,238,238)',
              color: input.trim() && !sending ? 'white' : '#999',
              boxShadow: input.trim() && !sending ? '0 2px 8px rgba(255,97,26,0.3)' : 'none',
              cursor: input.trim() && !sending ? 'pointer' : 'not-allowed',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'all 0.2s'
            }}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          </button>
        </div>
        <p style={{ marginTop: '8px', textAlign: 'center', fontSize: '12px', color: '#999' }}>
          Chat Guard uses AI to answer questions. Verify important information independently.
        </p>
      </div>
    </PageLayout>
  );
}

export default function ChatPage() {
  return (
    <ProtectedRoute>
      <ChatContent />
    </ProtectedRoute>
  );
}
