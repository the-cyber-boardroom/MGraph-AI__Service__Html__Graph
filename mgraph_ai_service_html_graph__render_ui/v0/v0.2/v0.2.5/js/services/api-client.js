/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - API Client
   v0.2.5 - Surgical Override: Add transformation support
   
   Adds to ApiClient:
   - getTransformations(): Fetch available transformations from server
   - Updated export methods to include transformation parameter
   ═══════════════════════════════════════════════════════════════════════════════ */

// ═══════════════════════════════════════════════════════════════════════════════
// NEW: Get available transformations
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Get list of available graph transformations
 * @returns {Promise<Array<{name: string, label: string, description: string}>>}
 */
ApiClient.prototype.getTransformations = async function() {
    return this.get('/graph/transformations');
};

// ═══════════════════════════════════════════════════════════════════════════════
// OVERRIDE: Export methods with transformation parameter
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Convert HTML to vis.js format with transformation
 */
ApiClient.prototype.htmlToVisJs = async function(request, transformation = 'default') {
    return this.post(`/graph/from/html/to/visjs/${transformation}`, request);
};

/**
 * Convert HTML to D3 format with transformation
 */
ApiClient.prototype.htmlToD3 = async function(request, transformation = 'default') {
    return this.post(`/graph/from/html/to/d3/${transformation}`, request);
};

/**
 * Convert HTML to Cytoscape format with transformation
 */
ApiClient.prototype.htmlToCytoscape = async function(request, transformation = 'default') {
    return this.post(`/graph/from/html/to/cytoscape/${transformation}`, request);
};

/**
 * Convert HTML to Mermaid format with transformation
 */
ApiClient.prototype.htmlToMermaid = async function(request, transformation = 'default') {
    return this.post(`/graph/from/html/to/mermaid/${transformation}`, request);
};

/**
 * Convert HTML to DOT format with transformation
 */
ApiClient.prototype.htmlToDot = async function(request, transformation = 'default') {
    return this.post(`/graph/from/html/to/dot/${transformation}`, request);
};

// ═══════════════════════════════════════════════════════════════════════════════
// OVERRIDE: URL methods with transformation parameter
// ═══════════════════════════════════════════════════════════════════════════════

ApiClient.prototype.urlToVisJs = async function(request, transformation = 'default') {
    return this.post(`/graph/from/url/to/visjs/${transformation}`, request);
};

ApiClient.prototype.urlToD3 = async function(request, transformation = 'default') {
    return this.post(`/graph/from/url/to/d3/${transformation}`, request);
};

ApiClient.prototype.urlToCytoscape = async function(request, transformation = 'default') {
    return this.post(`/graph/from/url/to/cytoscape/${transformation}`, request);
};

ApiClient.prototype.urlToMermaid = async function(request, transformation = 'default') {
    return this.post(`/graph/from/url/to/mermaid/${transformation}`, request);
};

ApiClient.prototype.urlToDot = async function(request, transformation = 'default') {
    return this.post(`/graph/from/url/to/dot/${transformation}`, request);
};

console.log('ApiClient v0.2.5 surgical override loaded (transformation support)');
