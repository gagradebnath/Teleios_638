/**
 * Application constants and configuration
 */

export const PANEL_TYPES = {
    CHAT: 'chat',
    INGEST: 'ingest',
    PREDICT: 'predict',
    EXECUTE: 'execute',
};

export const PANEL_LABELS = {
    [PANEL_TYPES.CHAT]: '💬 Chat',
    [PANEL_TYPES.INGEST]: '📤 Ingest',
    [PANEL_TYPES.PREDICT]: '❓ Predict',
    [PANEL_TYPES.EXECUTE]: '⚙️ Execute',
};

export const DIFFICULTY_LEVELS = {
    EASY: 'easy',
    MEDIUM: 'medium',
    HARD: 'hard',
};

export const MESSAGE_ROLES = {
    USER: 'user',
    ASSISTANT: 'assistant',
    SYSTEM: 'system',
    ERROR: 'error',
};

export const API_TIMEOUT = 30000; // milliseconds

export const DEFAULT_API_URL = 'http://localhost:8005';

export const BLOCK_TYPES = {
    TEXT: 'text',
    EQUATION: 'equation',
    FIGURE: 'figure',
    TABLE: 'table',
};

export const ERRORS = {
    NO_DOCUMENT: 'Please ingest a document first.',
    INVALID_FILE: 'Please select a valid PDF file.',
    UPLOAD_FAILED: 'Failed to upload document',
    EXPLANATION_FAILED: 'Failed to generate explanation',
    PREDICTION_FAILED: 'Failed to predict questions',
    EXECUTION_FAILED: 'Failed to execute code',
    ANALYSIS_FAILED: 'Failed to analyze document',
};
