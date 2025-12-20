/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - API Client Surgical Override
   v0.2.9 - Add tree and tree_text engine support
   
   Adds two new methods to ApiClient:
   - htmlToTree(request, transformation) → { tree, rootId, stats, duration }
   - htmlToTreeText(request, transformation) → { tree_text, tree_text_size, rootId, stats, duration }
   ═══════════════════════════════════════════════════════════════════════════════ */

(function() {
    'use strict';

    // Wait for ApiClient to be available
    const patchApiClient = () => {
        if (typeof ApiClient === 'undefined') {
            setTimeout(patchApiClient, 50);
            return;
        }

        /**
         * Convert HTML to Tree (JSON hierarchical structure)
         * @param {object} request - Graph request with html, preset, show_* flags
         * @param {string} transformation - Transformation name (default: 'default')
         * @returns {Promise<{tree: object, rootId: string, stats: object, duration: number}>}
         */
        ApiClient.prototype.htmlToTree = async function(request, transformation = 'default') {
            const endpoint = `${this.baseUrl}/graph/from/html/to/tree/${transformation}`;
            
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(request)
            });

            if (!response.ok) {
                const error = await response.text();
                throw new Error(`Tree conversion failed: ${error}`);
            }

            return response.json();
        };

        /**
         * Convert HTML to Tree Text (formatted string representation)
         * @param {object} request - Graph request with html, preset, show_* flags
         * @param {string} transformation - Transformation name (default: 'default')
         * @returns {Promise<{tree_text: string, tree_text_size: number, rootId: string, stats: object, duration: number}>}
         */
        ApiClient.prototype.htmlToTreeText = async function(request, transformation = 'default') {
            const endpoint = `${this.baseUrl}/graph/from/html/to/tree_text/${transformation}`;
            
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(request)
            });

            if (!response.ok) {
                const error = await response.text();
                throw new Error(`Tree text conversion failed: ${error}`);
            }

            return response.json();
        };

        console.log('[v0.2.9] ApiClient patched: htmlToTree, htmlToTreeText');
    };

    patchApiClient();
})();
