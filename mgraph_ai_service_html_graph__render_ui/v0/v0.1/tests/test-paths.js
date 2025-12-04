/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Test Suite - Path Configuration
   v0.1.4 - Test Infrastructure
   
   This file defines paths to components for testing.
   
   IMPORTANT: When consolidating to v0.2.0:
   1. Copy this entire tests/ folder to v0.2.0/tests/
   2. Update the BASE_PATH below to '..' (relative to tests folder)
   3. All tests should pass without any other changes
   ═══════════════════════════════════════════════════════════════════════════════ */

const TestPaths = {
    // Base path to version root (relative to tests/ folder)
    // v0.1.x: Points to the v0 folder containing all minor versions
    // v0.2.0: Change to 'v0.2' to point to consolidated v0.2.0 folder
    BASE_PATH: '/console/v0/v0.1',  // this needs to be an absolute path, so that we can run tests from multiple folders
    
    // Version paths for v0.1.x (minor versions share code)
    // When consolidated to v0.2.0, these all become '.'
    VERSIONS: {
        V0_1_0: 'v0.1.0',
        V0_1_1: 'v0.1.1', 
        V0_1_2: 'v0.1.2',
        V0_1_3: 'v0.1.3',
        V0_1_4: 'v0.1.4'
    },
    
    // Component paths (matches playground.html structure)
    getComponentPath(version, componentPath) {
        return `${this.BASE_PATH}/${version}/${componentPath}`;
    },
    
    // Convenience getters for common components
    get apiClient() {
        return this.getComponentPath(this.VERSIONS.V0_1_0, 'js/services/api-client.js');
    },
    
    get commonCss() {
        return this.getComponentPath(this.VERSIONS.V0_1_0, 'css/common.css');
    },
    
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
        return this.getComponentPath(this.VERSIONS.V0_1_1, 'components/graph-canvas/graph-canvas.js');
    },
    
    get graphCanvas() {
        // v0.1.4 overrides v0.1.1's graph-canvas
        return this.getComponentPath(this.VERSIONS.V0_1_4, 'components/graph-canvas/graph-canvas.js');
    },
    
    get dotRenderer() {
        return this.getComponentPath(this.VERSIONS.V0_1_2, 'components/dot-renderer/dot-renderer.js');
    },
    
    get urlInput() {
        return this.getComponentPath(this.VERSIONS.V0_1_3, 'components/url-input/url-input.js');
    },
    
    get statsToolbar() {
        return this.getComponentPath(this.VERSIONS.V0_1_3, 'components/stats-toolbar/stats-toolbar.js');
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
        return this.getComponentPath(this.VERSIONS.V0_1_4, 'js/playground.js');
    },
    
    get playgroundCss() {
        return this.getComponentPath(this.VERSIONS.V0_1_1, 'css/playground.css');
    },
    
    get playgroundCssOverride() {
        return this.getComponentPath(this.VERSIONS.V0_1_4, 'css/playground.css');
    },
    
    // Sample files
    getSamplePath(sampleName) {
        return this.getComponentPath(this.VERSIONS.V0_1_0, `samples/${sampleName}.html`);
    }
};

// Freeze to prevent accidental modification
Object.freeze(TestPaths.VERSIONS);
