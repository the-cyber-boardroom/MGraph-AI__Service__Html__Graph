/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - API Client
   v0.2.2 - Surgical Override: Add native export format methods
   
   Adds to ApiClient from v0.2.0:
   - htmlToVisJs(), htmlToD3(), htmlToCytoscape(), htmlToMermaid()
   - urlToVisJs(), urlToD3(), urlToCytoscape(), urlToMermaid()
   ═══════════════════════════════════════════════════════════════════════════════ */

// ═══════════════════════════════════════════════════════════════════════════════
// NEW: Native Format Methods for HTML
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Convert HTML to vis.js native format
 * @param {object} request - Request with html and options
 * @returns {Promise<{nodes: array, edges: array, stats: object, duration: number}>}
 */
ApiClient.prototype.htmlToVisJs = async function(request) {
    return this.post('/graph/from/html/to/visjs', request);
};

/**
 * Convert HTML to D3.js native format
 * @param {object} request - Request with html and options
 * @returns {Promise<{nodes: array, links: array, stats: object, duration: number}>}
 */
ApiClient.prototype.htmlToD3 = async function(request) {
    return this.post('/graph/from/html/to/d3', request);
};

/**
 * Convert HTML to Cytoscape.js native format
 * @param {object} request - Request with html and options
 * @returns {Promise<{elements: object, stats: object, duration: number}>}
 */
ApiClient.prototype.htmlToCytoscape = async function(request) {
    return this.post('/graph/from/html/to/cytoscape', request);
};

/**
 * Convert HTML to Mermaid format
 * @param {object} request - Request with html and options
 * @returns {Promise<{mermaid: string, stats: object, duration: number}>}
 */
ApiClient.prototype.htmlToMermaid = async function(request) {
    return this.post('/graph/from/html/to/mermaid', request);
};

// ═══════════════════════════════════════════════════════════════════════════════
// NEW: Native Format Methods for URL
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Fetch URL and convert to vis.js format
 */
ApiClient.prototype.urlToVisJs = async function(request) {
    return this.post('/graph/from/url/to/visjs', request);
};

/**
 * Fetch URL and convert to D3.js format
 */
ApiClient.prototype.urlToD3 = async function(request) {
    return this.post('/graph/from/url/to/d3', request);
};

/**
 * Fetch URL and convert to Cytoscape.js format
 */
ApiClient.prototype.urlToCytoscape = async function(request) {
    return this.post('/graph/from/url/to/cytoscape', request);
};

/**
 * Fetch URL and convert to Mermaid format
 */
ApiClient.prototype.urlToMermaid = async function(request) {
    return this.post('/graph/from/url/to/mermaid', request);
};
