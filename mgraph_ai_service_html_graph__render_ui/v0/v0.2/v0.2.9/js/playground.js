/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Playground Surgical Override
   v0.2.9 - Add tree and tree_text engine support
   
   Patches Playground to:
   - Include 'tree' and 'tree_text' in available engines
   - Route to TreeRenderer and TreeTextRenderer
   ═══════════════════════════════════════════════════════════════════════════════ */

(function() {
    'use strict';

    const patchPlayground = () => {
        if (typeof Playground === 'undefined') {
            setTimeout(patchPlayground, 50);
            return;
        }

        // Store original method
        const originalRenderGraph = Playground.prototype.renderGraph;

        /**
         * Patch renderGraph to intercept tree engines before the switch statement
         */
        Playground.prototype.renderGraph = async function() {
            const renderer = this.graphCanvas?.getCurrentRenderer() || 'dot';

            // Intercept tree engines - handle separately
            if (renderer === 'tree' || renderer === 'tree_text') {
                return this.renderTreeEngine(renderer);
            }

            // Delegate to original for all other engines
            return originalRenderGraph.call(this);
        };

        /**
         * NEW: Render using tree or tree_text engine
         * Mirrors the structure of the original renderGraph but for tree engines
         */
        Playground.prototype.renderTreeEngine = async function(renderer) {
            if (this.isRendering) return;

            const html = this.htmlInput ? this.htmlInput.getHtml() : this.currentHtml;

            if (!html || !html.trim()) {
                this.statsToolbar?.showError(
                    'No HTML to render',
                    'Please enter some HTML or fetch from a URL first.',
                    ''
                );
                return;
            }

            this.isRendering = true;
            this.statsToolbar?.setRenderingState(true);
            this.statsToolbar?.hideError();
            this.statsToolbar?.clearStats();
            this.graphCanvas?.showLoading();

            const transformation = this.currentTransformation || 'default';
            const request = this.buildRequest();

            try {
                const apiStartTime = performance.now();

                // Call tree API
                let response;
                if (renderer === 'tree') {
                    response = await window.apiClient.htmlToTree(request, transformation);
                } else {
                    response = await window.apiClient.htmlToTreeText(request, transformation);
                }

                const apiEndTime = performance.now();
                this.currentApiMs = Math.round(apiEndTime - apiStartTime);

                // Update stats
                if (response.stats) {
                    this.currentStats = response.stats;
                    this.statsToolbar?.setStats(response.stats);
                }

                // Render using tree renderer
                const renderStartTime = performance.now();
                await this.renderTreeFormat(renderer, response);
                const renderEndTime = performance.now();

                // Update timing
                this.statsToolbar?.setTiming({
                    api_ms: this.currentApiMs,
                    server_ms: Math.round((response.duration || 0) * 1000),
                    dot_size: response.tree_text_size || 0,
                    render_ms: Math.round(renderEndTime - renderStartTime)
                });

                // Update max stats if in maximize mode
                if (this.updateMaxStats) {
                    this.updateMaxStats();
                }

            } catch (error) {
                console.error('[v0.2.9] Tree render error:', error);
                this.statsToolbar?.showError(
                    'API Error',
                    error.message || 'Failed to call the API.',
                    'Check that the server is running and try again.'
                );
                this.graphCanvas?.showError('API request failed', error.message);
            } finally {
                this.isRendering = false;
                this.statsToolbar?.setRenderingState(false);
            }
        };

        /**
         * NEW: Render tree format to canvas
         */
        Playground.prototype.renderTreeFormat = async function(renderer, response) {
            // Try different ways to get the canvas area
            const canvasArea = this.graphCanvas?.canvasArea
                            || this.graphCanvas?.shadowRoot?.querySelector('.canvas-area')
                            || this.graphCanvas?.querySelector('.canvas-area');

            if (!canvasArea) {
                console.error('[v0.2.9] GraphCanvas structure:', this.graphCanvas);
                throw new Error('No canvas area available');
            }

            // Get or create the appropriate renderer element
            let rendererEl;
            if (renderer === 'tree') {
                rendererEl = document.querySelector('tree-renderer');
            } else {
                rendererEl = document.querySelector('tree-text-renderer');
            }

            if (!rendererEl) {
                throw new Error(`Renderer element not found: ${renderer}`);
            }

            // Set target and render
            rendererEl.setTargetCanvas(canvasArea);
            await rendererEl.render(response);
        };

        /**
         * NEW: Format engine name for display
         */
        const originalFormatEngineName = Playground.prototype.formatEngineName;
        Playground.prototype.formatEngineName = function(engine) {
            if (engine === 'tree') return 'Tree (JSON)';
            if (engine === 'tree_text') return 'Tree (Text)';

            if (originalFormatEngineName) {
                return originalFormatEngineName.call(this, engine);
            }

            var names = {
                'dot': 'DOT (Graphviz)',
                'visjs': 'VisJS',
                'd3': 'D3 Force',
                'cytoscape': 'Cytoscape',
                'mermaid': 'Mermaid'
            };
            return names[engine] || engine;
        };

        /**
         * Patch initMaximizeMode to add tree renderers to the dropdown
         */
        const originalInitMaximizeMode = Playground.prototype.initMaximizeMode;
        Playground.prototype.initMaximizeMode = function() {
            // Call original first
            originalInitMaximizeMode.call(this);

            // Add tree options to the maximize renderer select
            const maxSelect = document.getElementById('max-renderer-select');
            if (maxSelect && !maxSelect.querySelector('option[value="tree"]')) {
                const treeOption = document.createElement('option');
                treeOption.value = 'tree';
                treeOption.textContent = 'Tree (JSON)';
                maxSelect.appendChild(treeOption);

                const treeTextOption = document.createElement('option');
                treeTextOption.value = 'tree_text';
                treeTextOption.textContent = 'Tree (Text)';
                maxSelect.appendChild(treeTextOption);
            }
        };

        /**
         * Patch cycleEngine to include tree engines
         */
        const originalCycleEngine = Playground.prototype.cycleEngine;
        Playground.prototype.cycleEngine = function(direction) {
            var engines = ['dot', 'visjs', 'd3', 'cytoscape', 'mermaid', 'tree', 'tree_text'];
            var currentEngine = this.getCurrentEngine();
            var currentIndex = engines.indexOf(currentEngine);
            if (currentIndex === -1) currentIndex = 0;

            var newIndex = (currentIndex + direction + engines.length) % engines.length;
            var newEngine = engines[newIndex];

            this.setEngine(newEngine);
            this.renderGraph();
            this.showToast('Engine: ' + this.formatEngineName(newEngine));
        };
        console.log('[v0.2.9] Playground patched: tree engine support');
    };

    patchPlayground();
})();