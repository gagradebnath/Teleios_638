import React from 'react';
import '../../../styles/components/LoadingSpinner.css';

/**
 * LoadingSpinner Component
 * Displays a loading indicator
 * 
 * Props:
 *   - message (string): Optional loading message
 *   - size (string): Size variant (small, medium, large)
 */
function LoadingSpinner({ message = 'Loading...', size = 'medium' }) {
    return (
        <div className={`loading-spinner ${size}`} role="status" aria-live="polite">
            <div className="spinner" />
            {message && <p className="loading-message">{message}</p>}
        </div>
    );
}

export default LoadingSpinner;
