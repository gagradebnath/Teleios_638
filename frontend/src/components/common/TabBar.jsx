import React from 'react';
import '../../../styles/components/TabBar.css';

/**
 * TabBar Component
 * Provides navigation between different panels (Chat, Ingest, Predict, Execute)
 * 
 * Props:
 *   - activeTab (string): Currently active tab ID
 *   - onTabChange (function): Callback when tab is clicked
 */
function TabBar({ activeTab, onTabChange }) {
    const tabs = [
        { id: 'chat', label: '💬 Chat', title: 'Ask questions and get explanations' },
        { id: 'ingest', label: '📤 Ingest', title: 'Upload and process documents' },
        { id: 'predict', label: '❓ Predict', title: 'Generate exam questions' },
        { id: 'execute', label: '⚙️ Execute', title: 'Run analysis scripts' },
    ];

    return (
        <div className="tab-bar" role="tablist" aria-label="Main Navigation">
            {tabs.map((tab) => (
                <button
                    key={tab.id}
                    role="tab"
                    aria-selected={activeTab === tab.id}
                    aria-label={tab.label}
                    className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
                    onClick={() => onTabChange(tab.id)}
                    title={tab.title}
                >
                    <span className="tab-label">{tab.label}</span>
                </button>
            ))}
        </div>
    );
}

export default TabBar;
