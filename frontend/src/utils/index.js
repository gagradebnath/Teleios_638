/**
 * Utility functions for the application
 */

/**
 * Format a date to readable string
 * @param {Date|string} date - Date to format
 * @returns {string} Formatted date or time
 */
export const formatDate = (date) => {
    try {
        const d = new Date(date);
        const now = new Date();
        const diffMs = now - d;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;

        return d.toLocaleDateString();
    } catch {
        return 'Unknown date';
    }
};

/**
 * Truncate text to specified length
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} Truncated text
 */
export const truncateText = (text, maxLength = 100) => {
    if (!text) return '';
    return text.length > maxLength ? text.slice(0, maxLength) + '...' : text;
};

/**
 * Validate file is a PDF
 * @param {File} file - File to validate
 * @returns {boolean} True if valid PDF
 */
export const isValidPDF = (file) => {
    if (!file) return false;
    return file.type === 'application/pdf' || file.name.endsWith('.pdf');
};

/**
 * Format file size to readable format
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted file size
 */
export const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
};

/**
 * Generate unique ID
 * @returns {string} Unique ID
 */
export const generateId = () => {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Parse error message from various error types
 * @param {Error|string|object} error - Error object or message
 * @returns {string} Error message
 */
export const getErrorMessage = (error) => {
    if (typeof error === 'string') return error;
    if (error?.response?.data?.detail) return error.response.data.detail;
    if (error?.response?.data?.message) return error.response.data.message;
    if (error?.message) return error.message;
    return 'An unknown error occurred';
};

/**
 * Safely parse JSON
 * @param {string} json - JSON string
 * @param {*} fallback - Fallback value
 * @returns {*} Parsed JSON or fallback
 */
export const safeParseJSON = (json, fallback = null) => {
    try {
        return JSON.parse(json);
    } catch {
        return fallback;
    }
};

/**
 * Debounce function
 * @param {function} fn - Function to debounce
 * @param {number} ms - Debounce delay in milliseconds
 * @returns {function} Debounced function
 */
export const debounce = (fn, ms = 300) => {
    let timeoutId;
    return (...args) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => fn(...args), ms);
    };
};

/**
 * Group array items by a key
 * @param {array} items - Items to group
 * @param {function|string} keyFn - Function or key to group by
 * @returns {object} Grouped items
 */
export const groupBy = (items, keyFn) => {
    return items.reduce((acc, item) => {
        const key = typeof keyFn === 'function' ? keyFn(item) : item[keyFn];
        if (!acc[key]) acc[key] = [];
        acc[key].push(item);
        return acc;
    }, {});
};
