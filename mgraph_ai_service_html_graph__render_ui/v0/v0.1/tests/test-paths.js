/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Test Suite - Path Configuration
   v0.1.4 - Test Infrastructure
   
   This file defines paths to SOURCE files for testing.
   Tests are co-located with their source files (IFD pattern).

   Test Location Pattern:
   - Unit tests:        source.js → source.test.js (same folder)
   - Integration tests: page.html → page.html.test.js (same folder)

   CONSOLIDATION TO v0.2.0:
   1. Copy tests/ folder to v0.2.0/tests/
   2. Replace test-paths.js with test-paths.v0.2.0.template.js
   3. All tests should pass without modifications
   ═══════════════════════════════════════════════════════════════════════════════ */

const TestPaths = {
    // Base path to version root (absolute path for cross-folder test execution)
    BASE_PATH: '/console/v0/v0.1',

    // Version paths for v0.1.x (minor versions share code via link-back)
    // When consolidated to v0.2.0, these all become '.'
    VERSIONS: {
        V0_1_0: 'v0.1.0',
        V0_1_1: 'v0.1.1',
        V0_1_2: 'v0.1.2',
        V0_1_3: 'v0.1.3',
        V0_1_4: 'v0.1.4'
    },

    // ═══════════════════════════════════════════════════════════════════════════
    // Path Builder
    // ═══════════════════════════════════════════════════════════════════════════

    getComponentPath(version, componentPath) {
        return `${this.BASE_PATH}/${version}/${componentPath}`;
    },

    // ═══════════════════════════════════════════════════════════════════════════
    // v0.1.0 - Base version (CSS, samples, api-client)
    // ═══════════════════════════════════════════════════════════════════════════

    get apiClient() {
        return this.getComponentPath(this.VERSIONS.V0_1_0, 'js/services/api-client.js');
    },

    get commonCss() {
        return this.getComponentPath(this.VERSIONS.V0_1_0, 'css/common.css');
    },

    getSamplePath(sampleName) {
        return this.getComponentPath(this.VERSIONS.V0_1_0, `samples/${sampleName}.html`);
    },

    // ═══════════════════════════════════════════════════════════════════════════
    // v0.1.1 - Core UI components
    // ═══════════════════════════════════════════════════════════════════════════

    get topNav() {
        return this.getComponentPath(this.VERSIONS.V0_1_1, 'components/top-nav/top-nav.js');
    },

    get htmlInput() {
        return this.getComponentPath(this.VERSIONS.V0_1_1, 'components/html-input/html-input.js');
    },

    get configPanel() {
        return this.getComponentPath(this.VERSIONS.V0_1_1, 'components/config-panel/config-panel.js');
    },

    get statsPanel() {
        return this.getComponentPath(this.VERSIONS.V0_1_1, 'components/stats-panel/stats-panel.js');
    },

    get graphCanvas_v0_1_1() {
        // Original graph-canvas (before v0.1.4 override)
        return this.getComponentPath(this.VERSIONS.V0_1_1, 'components/graph-canvas/graph-canvas.js');
    },

    get playgroundCss() {
        return this.getComponentPath(this.VERSIONS.V0_1_1, 'css/playground.css');
    },

    // ═══════════════════════════════════════════════════════════════════════════
    // v0.1.2 - DOT renderer
    // ═══════════════════════════════════════════════════════════════════════════

    get dotRenderer() {
        return this.getComponentPath(this.VERSIONS.V0_1_2, 'components/dot-renderer/dot-renderer.js');
    },

    // ═══════════════════════════════════════════════════════════════════════════
    // v0.1.3 - Stats toolbar, URL input
    // ═══════════════════════════════════════════════════════════════════════════

    get urlInput() {
        return this.getComponentPath(this.VERSIONS.V0_1_3, 'components/url-input/url-input.js');
    },

    get statsToolbar() {
        return this.getComponentPath(this.VERSIONS.V0_1_3, 'components/stats-toolbar/stats-toolbar.js');
    },

    // ═══════════════════════════════════════════════════════════════════════════
    // v0.1.4 - Multiple renderers, graph-canvas override, playground override
    // ═══════════════════════════════════════════════════════════════════════════

    get graphCanvas() {
        // v0.1.4 overrides v0.1.1's graph-canvas
        return this.getComponentPath(this.VERSIONS.V0_1_4, 'components/graph-canvas/graph-canvas.js');
    },

    get visRenderer() {
        return this.getComponentPath(this.VERSIONS.V0_1_4, 'components/vis-renderer/vis-renderer.js');
    },

    get d3Renderer() {
        return this.getComponentPath(this.VERSIONS.V0_1_4, 'components/d3-renderer/d3-renderer.js');
    },

    get cytoscapeRenderer() {
        return this.getComponentPath(this.VERSIONS.V0_1_4, 'components/cytoscape-renderer/cytoscape-renderer.js');
    },

    get mermaidRenderer() {
        return this.getComponentPath(this.VERSIONS.V0_1_4, 'components/mermaid-renderer/mermaid-renderer.js');
    },

    get playgroundJs() {
        // v0.1.4 overrides playground.js
        return this.getComponentPath(this.VERSIONS.V0_1_4, 'js/playground.js');
    },

    get playgroundCssOverride() {
        // v0.1.4 CSS overrides (surgical)
        return this.getComponentPath(this.VERSIONS.V0_1_4, 'css/playground.css');
    },

    // ═══════════════════════════════════════════════════════════════════════════
    // Co-located Test Files (for reference in index.html)
    // ═══════════════════════════════════════════════════════════════════════════

    get testFiles() {
        return {
            // v0.1.0
            apiClient: `${this.BASE_PATH}/v0.1.0/js/services/api-client.test.js`,

            // v0.1.1
            configPanel: `${this.BASE_PATH}/v0.1.1/components/config-panel/config-panel.test.js`,
            htmlInput: `${this.BASE_PATH}/v0.1.1/components/html-input/html-input.test.js`,

            // v0.1.2
            dotRenderer: `${this.BASE_PATH}/v0.1.2/components/dot-renderer/dot-renderer.test.js`,

            // v0.1.3
            statsToolbar: `${this.BASE_PATH}/v0.1.3/components/stats-toolbar/stats-toolbar.test.js`,
            urlInput: `${this.BASE_PATH}/v0.1.3/components/url-input/url-input.test.js`,

            // v0.1.4
            graphCanvas: `${this.BASE_PATH}/v0.1.4/components/graph-canvas/graph-canvas.test.js`,
            visRenderer: `${this.BASE_PATH}/v0.1.4/components/vis-renderer/vis-renderer.test.js`,
            d3Renderer: `${this.BASE_PATH}/v0.1.4/components/d3-renderer/d3-renderer.test.js`,
            cytoscapeRenderer: `${this.BASE_PATH}/v0.1.4/components/cytoscape-renderer/cytoscape-renderer.test.js`,
            mermaidRenderer: `${this.BASE_PATH}/v0.1.4/components/mermaid-renderer/mermaid-renderer.test.js`,
            playground: `${this.BASE_PATH}/v0.1.4/js/playground.test.js`,

            // Integration tests
            playgroundIntegration: `${this.BASE_PATH}/v0.1.4/playground.html.test.js`,
        };
    }
};

// Freeze to prevent accidental modification
Object.freeze(TestPaths.VERSIONS);