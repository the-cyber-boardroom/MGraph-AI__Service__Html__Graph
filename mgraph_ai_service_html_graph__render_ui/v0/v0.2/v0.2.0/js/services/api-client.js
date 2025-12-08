/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - API Client
   v0.2.0 - Consolidated from v0.1.x
   ═══════════════════════════════════════════════════════════════════════════════ */

/**
 * API Client for HTML Graph Service
 * Handles all communication with the FastAPI backend
 */
class ApiClient {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl || window.location.origin;
        this.defaultTimeout = 30000;
    }

    /**
     * Make a POST request to the API
     * @param {string} endpoint - API endpoint path
     * @param {object} data - Request body data
     * @param {object} options - Additional fetch options
     * @returns {Promise<object>} Response data
     */
    async post(endpoint, data, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const timeout = options.timeout || this.defaultTimeout;

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                body: JSON.stringify(data),
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new ApiError(
                    errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
                    response.status,
                    errorData
                );
            }

            return await response.json();
        } catch (error) {
            clearTimeout(timeoutId);

            if (error.name === 'AbortError') {
                throw new ApiError('Request timed out', 408);
            }

            if (error instanceof ApiError) {
                throw error;
            }

            throw new ApiError(
                error.message || 'Network error',
                0,
                { originalError: error }
            );
        }
    }

    /**
     * Make a GET request to the API
     * @param {string} endpoint - API endpoint path
     * @param {object} options - Additional fetch options
     * @returns {Promise<object>} Response data
     */
    async get(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const timeout = options.timeout || this.defaultTimeout;

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: options.headers || {},
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new ApiError(
                    `HTTP ${response.status}: ${response.statusText}`,
                    response.status
                );
            }

            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            }
            return await response.text();
        } catch (error) {
            clearTimeout(timeoutId);

            if (error.name === 'AbortError') {
                throw new ApiError('Request timed out', 408);
            }

            if (error instanceof ApiError) {
                throw error;
            }

            throw new ApiError(error.message || 'Network error', 0);
        }
    }

    // ═══════════════════════════════════════════════════════════════════════════════
    // Graph API Methods
    // ═══════════════════════════════════════════════════════════════════════════════

    /**
     * Convert HTML to DOT format
     * @param {object} request - Request with html and options
     * @returns {Promise<{dot: string, stats: object}>}
     */
    async htmlToDot(request) {
        return this.post('/graph/from/html/to/dot', request);
    }

    /**
     * Convert HTML to vis.js format (future)
     * @param {object} request - Request with html and options
     * @returns {Promise<{nodes: array, edges: array, stats: object}>}
     */
    async htmlToVisJs(request) {
        return this.post('/graph/from/html/to/visjs', request);
    }

    /**
     * Convert HTML to D3 format (future)
     * @param {object} request - Request with html and options
     * @returns {Promise<{nodes: array, links: array, stats: object}>}
     */
    async htmlToD3(request) {
        return this.post('/graph/from/html/to/d3', request);
    }

    /**
     * Convert HTML to Cytoscape format (future)
     * @param {object} request - Request with html and options
     * @returns {Promise<{elements: object, stats: object}>}
     */
    async htmlToCytoscape(request) {
        return this.post('/graph/from/html/to/cytoscape', request);
    }

    /**
     * Convert HTML to Mermaid format (future)
     * @param {object} request - Request with html and options
     * @returns {Promise<{mermaid: string, stats: object}>}
     */
    async htmlToMermaid(request) {
        return this.post('/graph/from/html/to/mermaid', request);
    }

    // ═══════════════════════════════════════════════════════════════════════════════
    // Health Check
    // ═══════════════════════════════════════════════════════════════════════════════

    /**
     * Check API health status
     * @returns {Promise<boolean>}
     */
    async checkHealth() {
        try {
            await this.get('/info/health', { timeout: 5000 });
            return true;
        } catch {
            return false;
        }
    }
}

/**
 * Custom API Error class
 */
class ApiError extends Error {
    constructor(message, statusCode = 0, data = null) {
        super(message);
        this.name = 'ApiError';
        this.statusCode = statusCode;
        this.data = data;
    }
}

// Export singleton instance
const apiClient = new ApiClient();

// Also export class for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ApiClient, ApiError, apiClient };
}

window.apiClient = apiClient
