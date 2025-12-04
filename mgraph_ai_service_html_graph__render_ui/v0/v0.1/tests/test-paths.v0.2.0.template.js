/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Test Suite - Path Configuration
   v0.2.0 TEMPLATE - Use this when consolidating to v0.2.0
   
   INSTRUCTIONS:
   1. Copy entire tests/ folder to v0.2.0/tests/
   2. Replace test-paths.js with this file (rename to test-paths.js)
   3. Run tests - all should pass without modifications
   ═══════════════════════════════════════════════════════════════════════════════ */

const TestPaths = {
    // v0.2.0: All components are local, no cross-version references
    BASE_PATH: '..',
    
    // v0.2.0: All versions point to current directory
    VERSIONS: {
        V0_1_0: '.',  // Now local
        V0_1_1: '.',  // Now local
        V0_1_2: '.',  // Now local
        V0_1_3: '.',  // Now local
        V0_1_4: '.'   // Now local
    },
    
    getComponentPath(version, componentPath) {
        // v0.2.0: version is ignored, all paths are local
        return `${this.BASE_PATH}/${componentPath}`;
    },
    
    // All paths now point to local consolidated structure
    get apiClient() {
        return `${this.BASE_PATH}/js/services/api-client.js`;
    },
    
    get commonCss() {
        return `${this.BASE_PATH}/css/common.css`;
    },
    
    get topNav() {
        return `${this.BASE_PATH}/components/top-nav/top-nav.js`;
    },
    
    get htmlInput() {
        return `${this.BASE_PATH}/components/html-input/html-input.js`;
    },
    
    get configPanel() {
        return `${this.BASE_PATH}/components/config-panel/config-panel.js`;
    },
    
    get statsPanel() {
        return `${this.BASE_PATH}/components/stats-panel/stats-panel.js`;
    },
    
    get graphCanvas_v0_1_1() {
        // In v0.2.0, there's only one graph-canvas
        return `${this.BASE_PATH}/components/graph-canvas/graph-canvas.js`;
    },
    
    get graphCanvas() {
        return `${this.BASE_PATH}/components/graph-canvas/graph-canvas.js`;
    },
    
    get dotRenderer() {
        return `${this.BASE_PATH}/components/dot-renderer/dot-renderer.js`;
    },
    
    get urlInput() {
        return `${this.BASE_PATH}/components/url-input/url-input.js`;
    },
    
    get statsToolbar() {
        return `${this.BASE_PATH}/components/stats-toolbar/stats-toolbar.js`;
    },
    
    get visRenderer() {
        return `${this.BASE_PATH}/components/vis-renderer/vis-renderer.js`;
    },
    
    get d3Renderer() {
        return `${this.BASE_PATH}/components/d3-renderer/d3-renderer.js`;
    },
    
    get cytoscapeRenderer() {
        return `${this.BASE_PATH}/components/cytoscape-renderer/cytoscape-renderer.js`;
    },
    
    get mermaidRenderer() {
        return `${this.BASE_PATH}/components/mermaid-renderer/mermaid-renderer.js`;
    },
    
    get playgroundJs() {
        return `${this.BASE_PATH}/js/playground.js`;
    },
    
    get playgroundCss() {
        return `${this.BASE_PATH}/css/playground.css`;
    },
    
    get playgroundCssOverride() {
        // In v0.2.0, there's only one playground.css
        return `${this.BASE_PATH}/css/playground.css`;
    },
    
    getSamplePath(sampleName) {
        return `${this.BASE_PATH}/samples/${sampleName}.html`;
    }
};

Object.freeze(TestPaths.VERSIONS);
