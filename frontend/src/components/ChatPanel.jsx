import React, { useState, useRef, useEffect } from 'react';
import './ChatPanel.css';

/**
 * ChatPanel component
 * Displays chat history and allows user to ask questions
 */
function ChatPanel({ chatHistory, isLoading, onExplain }) {
    const [userInput, setUserInput] = useState('');
    const messagesEndRef = useRef(null);

    // Auto-scroll to bottom when new messages arrive
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [chatHistory]);

    const handleSendMessage = () => {
        if (!userInput.trim()) return;

        const message = userInput;
        setUserInput('');
        onExplain(message);
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    return (
        <div className="chat-panel">
            <div className="chat-messages">
                {chatHistory.length === 0 ? (
                    <div className="chat-welcome">
                        <h3>👋 Welcome to Teleios</h3>
                        <p>Upload a document to get started, then ask questions about it.</p>
                        <ul className="quick-tips">
                            <li>Highlight text in the PDF to get explanations</li>
                            <li>Ask follow-up questions in natural language</li>
                            <li>Generate practice exam questions</li>
                            <li>Execute Python code for analysis</li>
                        </ul>
                    </div>
                ) : (
                    chatHistory.map((msg, idx) => (
                        <div key={idx} className={`message message-${msg.role}`}>
                            <div className="message-header">
                                <span className="message-role">
                                    {msg.role === 'user' && '👤 You'}
                                    {msg.role === 'assistant' && '🤖 Assistant'}
                                    {msg.role === 'system' && '⚙️ System'}
                                    {msg.role === 'error' && '❌ Error'}
                                </span>
                                {msg.timestamp && (
                                    <span className="message-time">
                                        {new Date(msg.timestamp).toLocaleTimeString()}
                                    </span>
                                )}
                            </div>
                            <div className="message-content">{msg.content}</div>
                            {msg.citations && msg.citations.length > 0 && (
                                <div className="message-citations">
                                    <span className="citations-label">📚 Sources:</span>
                                    {msg.citations.map((citation, cidx) => (
                                        <div key={cidx} className="citation">
                                            <strong>{citation.source}:</strong> {citation.excerpt}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    ))
                )}
                <div ref={messagesEndRef} />
            </div>

            <div className="chat-input-area">
                <textarea
                    className="chat-input"
                    value={userInput}
                    onChange={(e) => setUserInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask a question about the document... (Shift+Enter for new line)"
                    disabled={isLoading}
                    rows="3"
                />
                <button
                    className="chat-send-btn"
                    onClick={handleSendMessage}
                    disabled={isLoading || !userInput.trim()}
                >
                    {isLoading ? '⏳ Sending...' : '📤 Send'}
                </button>
            </div>
        </div>
    );
}

export default ChatPanel;
