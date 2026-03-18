import React from 'react';
import './TabBar.css';

/**
 * TabBar component
 * Navigation bar for switching between panels
 */
function TabBar({ activeTab, onTabChange }) {
    const tabs = [
        { id: 'chat', label: '💬 Chat', icon: '💬' },
        { id: 'ingest', label: '📤 Ingest', icon: '📤' },
        { id: 'predict', label: '❓ Predict', icon: '❓' },
        { id: 'execute', label: '⚙️ Execute', icon: '⚙️' },
    ];

    return (
        <div className="tab-bar">
            {tabs.map((tab) => (
                <button
                    key={tab.id}
                    className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
                    onClick={() => onTabChange(tab.id)}
                    title={tab.label}
                >
                    <span className="tab-icon">{tab.icon}</span>
                    <span className="tab-label">{tab.label}</span>
                </button>
            ))}
        </div>
    );
}

export default TabBar;
