/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Shared Utility Helpers
   v0.2.1 - Extracted from duplicated code across components
   
   Functions extracted from:
   - stats-toolbar: escapeHtml, formatNumber, formatBytes
   - url-input: formatBytes, isValidUrl
   - graph-canvas: escapeHtml
   - playground: escapeHtml, formatBytes
   - mermaid-renderer: escapeHtml
   ═══════════════════════════════════════════════════════════════════════════════ */

const Helpers = {
    
    /**
     * Escape HTML entities to prevent XSS
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeHtml(text) {
        if (text == null) return '';
        const div = document.createElement('div');
        div.textContent = String(text);
        return div.innerHTML;
    },
    
    /**
     * Format number with K/M suffixes for display
     * @param {number} num - Number to format
     * @returns {string} Formatted string (e.g., "1.5K", "2.3M")
     */
    formatNumber(num) {
        if (num == null || isNaN(num)) return '0';
        num = Number(num);
        if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
        if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
        return num.toString();
    },
    
    /**
     * Format bytes to human-readable string
     * @param {number} bytes - Number of bytes
     * @returns {string} Formatted string (e.g., "1.5 KB", "2.3 MB")
     */
    formatBytes(bytes) {
        if (bytes == null || isNaN(bytes)) return '0 B';
        bytes = Number(bytes);
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    },
    
    /**
     * Validate URL format (http/https only)
     * @param {string} urlString - URL to validate
     * @returns {boolean} True if valid http/https URL
     */
    isValidUrl(urlString) {
        if (!urlString) return false;
        try {
            const url = new URL(urlString);
            return url.protocol === 'http:' || url.protocol === 'https:';
        } catch {
            return false;
        }
    },
    
    /**
     * Debounce a function
     * @param {Function} func - Function to debounce
     * @param {number} wait - Wait time in ms
     * @returns {Function} Debounced function
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func.apply(this, args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    /**
     * Wait for next animation frame
     * @returns {Promise<void>}
     */
    nextFrame() {
        return new Promise(resolve => requestAnimationFrame(resolve));
    },
    
    /**
     * Wait for specified milliseconds
     * @param {number} ms - Milliseconds to wait
     * @returns {Promise<void>}
     */
    wait(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
};

// Freeze to prevent accidental modification
Object.freeze(Helpers);

// Export for both browser and Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Helpers;
}
if (typeof window !== 'undefined') {
    window.Helpers = Helpers;
}
