/**
 * Gateway API client for Teleios backend
 * Handles all HTTP requests to FastAPI backend
 */

import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8005';

const client = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 30000,
});

// Add request interceptor for logging
client.interceptors.request.use(
    (config) => {
        console.log(`[Gateway] ${config.method.toUpperCase()} ${config.url}`);
        return config;
    },
    (error) => {
        console.error('[Gateway] Request error:', error);
        return Promise.reject(error);
    }
);

// Add response interceptor for error handling
client.interceptors.response.use(
    (response) => {
        console.log(`[Gateway] Response from ${response.config.url}:`, response.status);
        return response;
    },
    (error) => {
        if (error.response) {
            console.error(`[Gateway] Error ${error.response.status}:`, error.response.data);
        } else if (error.request) {
            console.error('[Gateway] No response:', error.request);
        } else {
            console.error('[Gateway] Error:', error.message);
        }
        return Promise.reject(error);
    }
);

export const gateway = {
    /**
     * Health check endpoint
     * GET /health
     */
    async health() {
        const response = await client.get('/health');
        return response.data;
    },

    /**
     * Ingest a PDF document
     * POST /ingest
     * @param {File} file - PDF file to ingest
     */
    async ingestDocument(file) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await client.post('/ingest', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            return { success: true, data: response.data };
        } catch (error) {
            return { success: false, error: error.response?.data || error.message };
        }
    },

    /**
     * Explain a highlighted text passage
     * POST /explain
     * @param {string} query - Question or request for explanation
     * @param {string} doc_id - Document ID to search in
     * @param {string} highlighted_text - Text passage to explain
     */
    async explainText(query, doc_id, highlighted_text) {
        const response = await client.post('/explain', {
            query,
            doc_id,
            highlighted_text,
        });
        return response.data;
    },

    /**
     * Generate exam questions and predictions
     * POST /predict
     * @param {string[]} doc_ids - Document IDs to analyze
     * @param {string} difficulty - Optional difficulty level (easy, medium, hard)
     */
    async predictQuestions(doc_ids, difficulty = 'medium') {
        const response = await client.post('/predict', {
            doc_ids,
            difficulty,
        });
        return response.data;
    },

    /**
     * Execute Python code in sandboxed environment
     * POST /execute
     * @param {string} code - Python code to execute
     * @param {Object} context - Optional context variables
     * @param {string} doc_id - Optional document context
     */
    async executeCode(code, context = {}, doc_id = null) {
        const response = await client.post('/execute', {
            code,
            context,
            doc_id,
        });
        return response.data;
    },

    /**
     * Analyze documents and group questions by topic
     * POST /analyze
     * @param {string[]} doc_ids - Document IDs to analyze
     * @param {string} group_by - Grouping strategy (topic, difficulty, type)
     */
    async analyzeDocuments(doc_ids, group_by = 'topic') {
        const response = await client.post('/analyze', {
            doc_ids,
            group_by,
        });
        return response.data;
    },

    // ═══════════════════════════════════════════════════════════════════════════
    // COURSES
    // ═══════════════════════════════════════════════════════════════════════════

    /**
     * Create a new course
     * POST /courses
     * @param {Object} courseData - {name, code?, description?, color?}
     */
    async createCourse(courseData) {
        const response = await client.post('/courses', courseData);
        return response.data;
    },

    /**
     * List all courses
     * GET /courses
     */
    async listCourses() {
        const response = await client.get('/courses');
        return response.data.courses;
    },

    /**
     * Get a single course
     * GET /courses/{courseId}
     */
    async getCourse(courseId) {
        const response = await client.get(`/courses/${courseId}`);
        return response.data;
    },

    /**
     * Get course statistics
     * GET /courses/{courseId}/stats
     */
    async getCourseStats(courseId) {
        const response = await client.get(`/courses/${courseId}/stats`);
        return response.data;
    },

    // ═══════════════════════════════════════════════════════════════════════════
    // FILE SYSTEM
    // ═══════════════════════════════════════════════════════════════════════════

    /**
     * Create a new folder
     * POST /file-system/folders
     * @param {Object} folderData - {name, parent_id?, course_id?}
     */
    async createFolder(folderData) {
        const response = await client.post('/file-system/folders', folderData);
        return response.data;
    },

    /**
     * List file system nodes
     * GET /file-system/nodes
     * @param {Object} filters - {parent_id?, course_id?}
     */
    async listFileSystemNodes(filters = {}) {
        const params = new URLSearchParams();
        if (filters.parent_id) params.append('parent_id', filters.parent_id);
        if (filters.course_id) params.append('course_id', filters.course_id);
        
        const url = params.toString() ? `/file-system/nodes?${params.toString()}` : '/file-system/nodes';
        const response = await client.get(url);
        return response.data.nodes;
    },

    /**
     * Get a single file/folder node
     * GET /file-system/nodes/{nodeId}
     */
    async getFileSystemNode(nodeId) {
        const response = await client.get(`/file-system/nodes/${nodeId}`);
        return response.data;
    },

    /**
     * Delete a file or folder
     * DELETE /file-system/nodes/{nodeId}
     */
    async deleteFileSystemNode(nodeId) {
        const response = await client.delete(`/file-system/nodes/${nodeId}`);
        return response.data;
    },

    /**
     * Get breadcrumb path for a node
     * GET /file-system/nodes/{nodeId}/path
     */
    async getNodePath(nodeId) {
        const response = await client.get(`/file-system/nodes/${nodeId}/path`);
        return response.data.path;
    },

    // ═══════════════════════════════════════════════════════════════════════════
    // DOCUMENTS
    // ═══════════════════════════════════════════════════════════════════════════

    /**
     * List documents
     * GET /documents
     * @param {string} courseId - Optional course filter
     */
    async listDocuments(courseId = null) {
        const params = courseId ? `?course_id=${courseId}` : '';
        const response = await client.get(`/documents${params}`);
        return response.data.documents;
    },

    /**
     * Get a single document
     * GET /documents/{docId}
     */
    async getDocument(docId) {
        const response = await client.get(`/documents/${docId}`);
        return response.data;
    },

    /**
     * Get document pages
     * GET /documents/{docId}/pages
     */
    async getDocumentPages(docId) {
        const response = await client.get(`/documents/${docId}/pages`);
        return response.data.pages;
    },

    /**
     * Get document blocks
     * GET /documents/{docId}/blocks
     * @param {number} page - Optional page filter
     */
    async getDocumentBlocks(docId, page = null) {
        const params = page !== null ? `?page=${page}` : '';
        const response = await client.get(`/documents/${docId}/blocks${params}`);
        return response.data.blocks;
    },
};

export default gateway;
