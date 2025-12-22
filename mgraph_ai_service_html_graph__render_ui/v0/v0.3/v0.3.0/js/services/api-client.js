/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - API Client
   v0.3.0 - Consolidated from v0.2.0 → v0.2.3 → v0.2.5 → v0.2.9 → v0.2.10
   
   Merged features:
   - Base API client with POST/GET methods (v0.2.0)
   - Native format endpoints: visjs, d3, cytoscape, mermaid (v0.2.3)
   - Transformation support with dynamic endpoints (v0.2.5)
   - Tree format endpoints: tree, tree_text (v0.2.9)
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
    // Transformation Methods (from v0.2.5)
    // ═══════════════════════════════════════════════════════════════════════════════

    /**
     * Get list of available graph transformations
     * @returns {Promise<Array<{name: string, label: string, description: string}>>}
     */
    async getTransformations() {
        return this.get('/graph/transformations');
    }

    // ═══════════════════════════════════════════════════════════════════════════════
    // DOT Format Methods
    // ═══════════════════════════════════════════════════════════════════════════════

    /**
     * Convert HTML to DOT format with transformation
     * @param {object} request - Request with html and options
     * @param {string} transformation - Transformation name (default: 'default')
     * @returns {Promise<{dot: string, stats: object, duration: number}>}
     */
    async htmlToDot(request, transformation = 'default') {
        return this.post(`/graph/from/html/to/dot/${transformation}`, request);
    }

    /**
     * Fetch URL and convert to DOT format
     */
    async urlToDot(request, transformation = 'default') {
        return this.post(`/graph/from/url/to/dot/${transformation}`, request);
    }

    // ═══════════════════════════════════════════════════════════════════════════════
    // vis.js Format Methods (from v0.2.3 + v0.2.5)
    // ═══════════════════════════════════════════════════════════════════════════════

    /**
     * Convert HTML to vis.js native format
     * @param {object} request - Request with html and options
     * @param {string} transformation - Transformation name (default: 'default')
     * @returns {Promise<{nodes: array, edges: array, stats: object, duration: number}>}
     */
    async htmlToVisJs(request, transformation = 'default') {
        return this.post(`/graph/from/html/to/visjs/${transformation}`, request);
    }

    /**
     * Fetch URL and convert to vis.js format
     */
    async urlToVisJs(request, transformation = 'default') {
        return this.post(`/graph/from/url/to/visjs/${transformation}`, request);
    }

    // ═══════════════════════════════════════════════════════════════════════════════
    // D3.js Format Methods (from v0.2.3 + v0.2.5)
    // ═══════════════════════════════════════════════════════════════════════════════

    /**
     * Convert HTML to D3.js native format
     * @param {object} request - Request with html and options
     * @param {string} transformation - Transformation name (default: 'default')
     * @returns {Promise<{nodes: array, links: array, stats: object, duration: number}>}
     */
    async htmlToD3(request, transformation = 'default') {
        return this.post(`/graph/from/html/to/d3/${transformation}`, request);
    }

    /**
     * Fetch URL and convert to D3.js format
     */
    async urlToD3(request, transformation = 'default') {
        return this.post(`/graph/from/url/to/d3/${transformation}`, request);
    }

    // ═══════════════════════════════════════════════════════════════════════════════
    // Cytoscape.js Format Methods (from v0.2.3 + v0.2.5)
    // ═══════════════════════════════════════════════════════════════════════════════

    /**
     * Convert HTML to Cytoscape.js native format
     * @param {object} request - Request with html and options
     * @param {string} transformation - Transformation name (default: 'default')
     * @returns {Promise<{elements: object, stats: object, duration: number}>}
     */
    async htmlToCytoscape(request, transformation = 'default') {
        return this.post(`/graph/from/html/to/cytoscape/${transformation}`, request);
    }

    /**
     * Fetch URL and convert to Cytoscape.js format
     */
    async urlToCytoscape(request, transformation = 'default') {
        return this.post(`/graph/from/url/to/cytoscape/${transformation}`, request);
    }

    // ═══════════════════════════════════════════════════════════════════════════════
    // Mermaid Format Methods (from v0.2.3 + v0.2.5)
    // ═══════════════════════════════════════════════════════════════════════════════

    /**
     * Convert HTML to Mermaid format
     * @param {object} request - Request with html and options
     * @param {string} transformation - Transformation name (default: 'default')
     * @returns {Promise<{mermaid: string, stats: object, duration: number}>}
     */
    async htmlToMermaid(request, transformation = 'default') {
        return this.post(`/graph/from/html/to/mermaid/${transformation}`, request);
    }

    /**
     * Fetch URL and convert to Mermaid format
     */
    async urlToMermaid(request, transformation = 'default') {
        return this.post(`/graph/from/url/to/mermaid/${transformation}`, request);
    }

    // ═══════════════════════════════════════════════════════════════════════════════
    // Tree Format Methods (from v0.2.9)
    // ═══════════════════════════════════════════════════════════════════════════════

    /**
     * Convert HTML to Tree (JSON hierarchical structure)
     * @param {object} request - Graph request with html, preset, show_* flags
     * @param {string} transformation - Transformation name (default: 'default')
     * @returns {Promise<{tree: object, rootId: string, stats: object, duration: number}>}
     */
    async htmlToTree(request, transformation = 'default') {
        const endpoint = `/graph/from/html/to/tree/${transformation}`;
        
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request)
        });

        if (!response.ok) {
            const error = await response.text();
            throw new Error(`Tree conversion failed: ${error}`);
        }

        return response.json();
    }

    /**
     * Convert HTML to Tree Text (formatted string representation)
     * @param {object} request - Graph request with html, preset, show_* flags
     * @param {string} transformation - Transformation name (default: 'default')
     * @returns {Promise<{tree_text: string, tree_text_size: number, rootId: string, stats: object, duration: number}>}
     */
    async htmlToTreeText(request, transformation = 'default') {
        const endpoint = `/graph/from/html/to/tree_text/${transformation}`;
        
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request)
        });

        if (!response.ok) {
            const error = await response.text();
            throw new Error(`Tree text conversion failed: ${error}`);
        }

        return response.json();
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

window.apiClient = apiClient;
