/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - API Client Extensions
   v0.2.11 - Surgical patch for Cache Entity and Flow APIs
   
   Extends the base ApiClient from v0.2.0 with:
   - Entity listing API
   - HTML load/store by cache_id
   - Flow timeline APIs
   ═══════════════════════════════════════════════════════════════════════════════ */

// ═══════════════════════════════════════════════════════════════════════════════
// Cache Entity API
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * List all entities in a namespace
 * @param {string} namespace - Cache namespace (e.g., 'html-cache')
 * @param {boolean} includeDataFiles - Include data_files array per entity
 * @returns {Promise<{success: boolean, namespace: string, count: number, entities: array}>}
 */
ApiClient.prototype.listEntities = async function(namespace, includeDataFiles = false) {
    const query = includeDataFiles ? '?include_data_files=true' : '';
    return this.get(`/cache-entity/${namespace}/entities${query}`);
};

/**
 * Get entity metadata by cache_id
 * @param {string} namespace - Cache namespace
 * @param {string} cacheId - Entity cache_id
 * @returns {Promise<object>}
 */
ApiClient.prototype.getEntityMetadata = async function(namespace, cacheId) {
    return this.get(`/cache-entity/${namespace}/entity/${cacheId}/metadata`);
};

/**
 * Check if entity exists
 * @param {string} namespace - Cache namespace
 * @param {string} cacheId - Entity cache_id
 * @returns {Promise<{exists: boolean}>}
 */
ApiClient.prototype.entityExists = async function(namespace, cacheId) {
    return this.get(`/cache-entity/${namespace}/entity/${cacheId}/exists`);
};

// ═══════════════════════════════════════════════════════════════════════════════
// HTML Domain API (FLeT)
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Load HTML by cache_id
 * @param {string} namespace - Cache namespace
 * @param {string} cacheId - Entity cache_id
 * @returns {Promise<{success: boolean, found: boolean, html: string, cache_id: string, ...}>}
 */
ApiClient.prototype.loadHtmlById = async function(namespace, cacheId) {
    return this.post(`/flet-html-domain/html/load/${namespace}/id`, {
        cache_id: cacheId
    });
};

/**
 * Load HTML by cache_key
 * @param {string} namespace - Cache namespace
 * @param {string} cacheKey - Cache key path (e.g., 'site/abc.com')
 * @returns {Promise<{success: boolean, found: boolean, html: string, ...}>}
 */
ApiClient.prototype.loadHtmlByKey = async function(namespace, cacheKey) {
    return this.post(`/flet-html-domain/html/load/${namespace}/key/${cacheKey}`, {});
};

/**
 * Store HTML with a cache_key
 * @param {string} namespace - Cache namespace
 * @param {string} cacheKey - Cache key path
 * @param {string} html - HTML content
 * @returns {Promise<{success: boolean, cache_id: string, ...}>}
 */
ApiClient.prototype.storeHtmlByKey = async function(namespace, cacheKey, html) {
    return this.post(`/flet-html-domain/html/store/${namespace}/key/${cacheKey}`, {
        html: html
    });
};

/**
 * Store raw HTML
 * @param {string} namespace - Cache namespace
 * @param {string} html - HTML content
 * @param {string} cacheKey - Optional cache key
 * @returns {Promise<{success: boolean, cache_id: string, ...}>}
 */
ApiClient.prototype.storeHtmlRaw = async function(namespace, html, cacheKey = null) {
    const payload = { html };
    if (cacheKey) payload.cache_key = cacheKey;
    return this.post(`/flet-html-domain/html/store/${namespace}/raw`, payload);
};

// ═══════════════════════════════════════════════════════════════════════════════
// Cache Data API (Direct data file access)
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Get string data file
 * @param {string} namespace - Cache namespace
 * @param {string} cacheId - Entity cache_id
 * @param {string} dataKey - Data key path (e.g., 'html')
 * @param {string} fileId - File ID (e.g., 'raw')
 * @returns {Promise<string>}
 */
ApiClient.prototype.getStringData = async function(namespace, cacheId, dataKey, fileId) {
    return this.get(`/cache-data/${namespace}/data/${cacheId}/string/${dataKey}/${fileId}`);
};

/**
 * Get JSON data file
 * @param {string} namespace - Cache namespace
 * @param {string} cacheId - Entity cache_id
 * @param {string} dataKey - Data key path (e.g., 'flows/html-to-cache')
 * @param {string} fileId - File ID (e.g., 'flow-data')
 * @returns {Promise<object>}
 */
ApiClient.prototype.getJsonData = async function(namespace, cacheId, dataKey, fileId) {
    return this.get(`/cache-data/${namespace}/data/${cacheId}/json/${dataKey}/${fileId}`);
};

// ═══════════════════════════════════════════════════════════════════════════════
// FLeT Flows API
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * List all flows for a cache entity
 * @param {string} namespace - Cache namespace
 * @param {string} cacheId - Entity cache_id
 * @returns {Promise<{success: boolean, flets: string[]}>}
 */
ApiClient.prototype.listFlows = async function(namespace, cacheId) {
    return this.get(`/flet-flows/flows/${namespace}/${cacheId}`);
};

/**
 * Get flow details
 * @param {string} namespace - Cache namespace
 * @param {string} cacheId - Entity cache_id
 * @param {string} fletName - FLeT name (e.g., 'html-to-cache')
 * @returns {Promise<object>}
 */
ApiClient.prototype.getFlow = async function(namespace, cacheId, fletName) {
    return this.get(`/flet-flows/flows/${namespace}/${cacheId}/${fletName}`);
};

/**
 * Get flow task durations
 * @param {string} namespace - Cache namespace
 * @param {string} cacheId - Entity cache_id
 * @param {string} fletName - FLeT name
 * @returns {Promise<{durations: object, total_duration: number}>}
 */
ApiClient.prototype.getFlowDurations = async function(namespace, cacheId, fletName) {
    return this.get(`/flet-flows/flows/${namespace}/${cacheId}/${fletName}/durations`);
};

/**
 * Get flow execution logs
 * @param {string} namespace - Cache namespace
 * @param {string} cacheId - Entity cache_id
 * @param {string} fletName - FLeT name
 * @returns {Promise<{logs: array}>}
 */
ApiClient.prototype.getFlowLogs = async function(namespace, cacheId, fletName) {
    return this.get(`/flet-flows/flows/${namespace}/${cacheId}/${fletName}/logs`);
};

/**
 * Get flow tasks
 * @param {string} namespace - Cache namespace
 * @param {string} cacheId - Entity cache_id
 * @param {string} fletName - FLeT name
 * @returns {Promise<{tasks: array}>}
 */
ApiClient.prototype.getFlowTasks = async function(namespace, cacheId, fletName) {
    return this.get(`/flet-flows/flows/${namespace}/${cacheId}/${fletName}/tasks`);
};

// ═══════════════════════════════════════════════════════════════════════════════
// Legacy Compatibility (if old code calls these)
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * @deprecated Use listEntities() instead
 */
ApiClient.prototype.listFolders = async function(namespace, pathPrefix = '') {
    console.warn('[ApiClient] listFolders is deprecated, use listEntities()');
    // Return empty to avoid breaking existing code
    return { success: true, entities: [] };
};
