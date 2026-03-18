import React from 'react';
import '../../../styles/components/Alert.css';

/**
 * Alert Component
 * Displays success, error, warning, or info messages
 * 
 * Props:
 *   - type (string): 'success', 'error', 'warning', 'info'
 *   - message (string): Alert message content
 *   - onClose (function): Callback to dismiss alert
 */
function Alert({ type = 'info', message, onClose }) {
    if (!message) return null;

    return (
        <div className={`alert alert-${type}`} role="alert">
            <div className="alert-icon">
                {type === 'success' && '✓'}
                {type === 'error' && '✕'}
                {type === 'warning' && '⚠'}
                {type === 'info' && 'ℹ'}
            </div>
            <div className="alert-content">
                <p>{message}</p>
            </div>
            {onClose && (
                <button
                    className="alert-close"
                    onClick={onClose}
                    aria-label="Close alert"
                >
                    ✕
                </button>
            )}
        </div>
    );
}

export default Alert;
