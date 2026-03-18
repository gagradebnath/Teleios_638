import React from 'react';
import '../../../styles/components/Badge.css';

/**
 * Badge Component
 * Displays a small label or badge
 * 
 * Props:
 *   - variant (string): 'default', 'primary', 'success', 'error', 'warning'
 *   - children (string): Badge text
 */
function Badge({ variant = 'default', children }) {
    return <span className={`badge badge-${variant}`}>{children}</span>;
}

export default Badge;
