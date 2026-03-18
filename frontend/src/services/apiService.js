/**
 * API Service - Handles all backend communication
 * Moved from api/gateway.js with improved error handling
 */

import axios from 'axios';
import { DEFAULT_API_URL, API_TIMEOUT } from '../constants';

const API_URL = import.meta.env.VITE_API_URL || DEFAULT_API_URL;

// Create axios instance with default config
const apiClient = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: API_TIMEOUT,
});

// Request interceptor - log requests
apiClient.interceptors.request.use(
    (config) => {
        console.log(`[API] ${config.method.toUpperCase()} ${config.url}`);
        return config;
    },
    (error) => {
        console.error('[API] Request Error:', error);
        return Promise.reject(error);
    }
);

// Response interceptor - log responses and handle errors
apiClient.interceptors.response.use(
    (response) => {
        console.log(`[API] ${response.status} ${response.config.url}`);
        return response;
    },
    (error) => {
        if (error.response) {
            console.error(`[API] Error ${error.response.status}:`, error.response.data);
        } else if (error.request) {
            console.error('[API] No Response:', error.request);
        } else {
            console.error('[API] Error:', error.message);
        }
        return Promise.reject(error);
    }
);

/**
 * API Service object with all backend endpoints
 */
const apiService = {
    /**
     * Health check - verify backend is running
     */
    async health() {
        try {
            const response = await apiClient.get('/health');
            return { success: true, data: response.data };
        } catch (error) {
            return { success: false, error };
        }
    },

    /**
     * Ingest a PDF document
     * @param {File} file - PDF file to upload
     * @returns {Promise} Response with doc_id and metadata
     */
    async ingestDocument(file) {
        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await apiClient.post('/ingest', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            return {
                success: true,
                data: response.data,
            };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.detail || error.message,
            };
        }
    },

    /**
     * Generate explanation for text
     * @param {string} query - Question/prompt
     * @param {string} docId - Document ID
     * @param {string} highlightedText - Selected text (optional)
     * @returns {Promise} Explanation with citations
     */
    async explainText(query, docId, highlightedText = '') {
        try {
            const response = await apiClient.post('/explain', {
                query,
                doc_id: docId,
                highlighted_text: highlightedText,
            });
            return { success: true, data: response.data };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.detail || error.message,
            };
        }
    },

    /**
     * Generate exam questions
     * @param {string[]} docIds - Document IDs to analyze
     * @param {string} subject - Subject (optional)
     * @returns {Promise} Generated questions
     */
    async generateQuestions(docIds, subject = null) {
        try {
            const response = await apiClient.post('/predict', {
                doc_ids: docIds,
                subject,
            });
            return { success: true, data: response.data };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.detail || error.message,
            };
        }
    },

    /**
     * Execute Python code
     * @param {string} code - Python code to execute
     * @param {object} context - Context variables (optional)
     * @returns {Promise} Execution output
     */
    async executeCode(code, context = {}) {
        try {
            const response = await apiClient.post('/execute', {
                code,
                context,
            });
            return { success: true, data: response.data };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.detail || error.message,
            };
        }
    },

    /**
     * Analyze documents
     * @param {string[]} docIds - Document IDs
     * @param {string} groupBy - Grouping strategy (topic, difficulty, type)
     * @returns {Promise} Analysis results
     */
    async analyzeDocuments(docIds, groupBy = 'topic') {
        try {
            const response = await apiClient.post('/analyze', {
                doc_ids: docIds,
                group_by: groupBy,
            });
            return { success: true, data: response.data };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.detail || error.message,
            };
        }
    },
};

export default apiService;
