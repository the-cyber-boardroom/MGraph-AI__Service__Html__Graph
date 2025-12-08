/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Test Suite - Path Configuration
   v0.2.0 - Consolidated from v0.1.x
   
   All paths are local to v0.2.0 (self-contained, no cross-version references)
   Tests are co-located with source files per IFD methodology.
   ═══════════════════════════════════════════════════════════════════════════════ */

const TestPaths = {
    // v0.2.0: All paths are relative to tests/ folder
    BASE_PATH: '/console/v0/v0.2',
    
    // v0.2.0: Legacy version mapping (all point to local)
    VERSIONS: {
        V0_2_0: 'v0.2.0',
        V0_1_1: 'v0.2.1',
        V0_1_2: 'v0.2.2',
        V0_1_3: 'v0.2.3',
        V0_1_4: 'v0.2.4'
    },

    getComponentPath(version, componentPath) {
        return `${this.BASE_PATH}/${version}/${componentPath}`;
    },
    
    // ═══════════════════════════════════════════════════════════════════════════
    // Component Paths (all local)
    // ═══════════════════════════════════════════════════════════════════════════
    
    get configPanel() {
        //return `${this.BASE_PATH}/v0.2.0/components/config-panel/config-panel.js`;
        return this.getComponentPath(this.VERSIONS.V0_2_0, 'components/config-panel/config-panel.js');
    },
    
    get graphCanvas() {
        return this.getComponentPath(this.VERSIONS.V0_2_0, 'components/graph-canvas/graph-canvas.js');
    },
    
    get graphCanvas_v0_1_1() {
        // In v0.2.0, there's only one graph-canvas
        return this.graphCanvas;
    },
    
    get htmlInput() {
        return this.getComponentPath(this.VERSIONS.V0_2_0, 'components/html-input/html-input.js');
    },
    
    get statsPanel() {
        return this.getComponentPath(this.VERSIONS.V0_2_0, 'components/stats-panel/stats-panel.js');
    },
    
    get topNav() {
        return this.getComponentPath(this.VERSIONS.V0_2_0, 'components/top-nav/top-nav.js');
    },
    
    get dotRenderer() {
        return this.getComponentPath(this.VERSIONS.V0_2_0, 'components/dot-renderer/dot-renderer.js');
    },
    
    get statsToolbar() {
        return this.getComponentPath(this.VERSIONS.V0_2_0, 'components/stats-toolbar/stats-toolbar.js');
    },
    
    get urlInput() {
        return this.getComponentPath(this.VERSIONS.V0_2_0, 'components/url-input/url-input.js');
    },
    
    get visRenderer() {
        return this.getComponentPath(this.VERSIONS.V0_2_0, 'components/vis-renderer/vis-renderer.js');
    },
    
    get d3Renderer() {
        return this.getComponentPath(this.VERSIONS.V0_2_0, 'components/d3-renderer/d3-renderer.js');
    },
    
    get cytoscapeRenderer() {
        return this.getComponentPath(this.VERSIONS.V0_2_0, 'components/cytoscape-renderer/cytoscape-renderer.js');
    },
    
    get mermaidRenderer() {
        return this.getComponentPath(this.VERSIONS.V0_2_0, 'components/mermaid-renderer/mermaid-renderer.js');
    },
    
    // ═══════════════════════════════════════════════════════════════════════════
    // Service Paths
    // ═══════════════════════════════════════════════════════════════════════════
    
    get apiClient() {
        return this.getComponentPath(this.VERSIONS.V0_2_0, 'js/services/api-client.js');
    },
    
    get playgroundJs() {
        return this.getComponentPath(this.VERSIONS.V0_2_0, 'js/playground.js');
    },
    
    // ═══════════════════════════════════════════════════════════════════════════
    // CSS Paths
    // ═══════════════════════════════════════════════════════════════════════════
    
    get commonCss() {
        //return `${this.BASE_PATH}/css/common.css`;
        return this.getComponentPath(this.VERSIONS.V0_2_0, 'css/common.css');
    },
    
    get playgroundCss() {
        return this.getComponentPath(this.VERSIONS.V0_2_0, 'css/playground.css');
    },
    
    get playgroundCssOverride() {
        // In v0.2.0, there's only one playground.css (merged)
        return this.playgroundCss;
    },
    
    // ═══════════════════════════════════════════════════════════════════════════
    // Sample Paths
    // ═══════════════════════════════════════════════════════════════════════════
    
    getSamplePath(sampleName) {
        return `${this.BASE_PATH}/samples/${sampleName}.html`;
    },
    
    // ═══════════════════════════════════════════════════════════════════════════
    // Co-located Test Files
    // ═══════════════════════════════════════════════════════════════════════════
    
    get testFiles() {
        return {
            // Services
            apiClient: `${this.BASE_PATH}/js/services/api-client.test.js`,
            
            // Components
            configPanel: `${this.BASE_PATH}/v0.2.0/components/config-panel/config-panel.test.js`,
            htmlInput: `${this.BASE_PATH}/components/html-input/html-input.test.js`,
            dotRenderer: `${this.BASE_PATH}/components/dot-renderer/dot-renderer.test.js`,
            statsToolbar: `${this.BASE_PATH}/components/stats-toolbar/stats-toolbar.test.js`,
            urlInput: `${this.BASE_PATH}/components/url-input/url-input.test.js`,
            graphCanvas: `${this.BASE_PATH}/components/graph-canvas/graph-canvas.test.js`,
            visRenderer: `${this.BASE_PATH}/components/vis-renderer/vis-renderer.test.js`,
            d3Renderer: `${this.BASE_PATH}/components/d3-renderer/d3-renderer.test.js`,
            cytoscapeRenderer: `${this.BASE_PATH}/components/cytoscape-renderer/cytoscape-renderer.test.js`,
            mermaidRenderer: `${this.BASE_PATH}/components/mermaid-renderer/mermaid-renderer.test.js`,
            
            // Orchestrators
            playground: `${this.BASE_PATH}/js/playground.test.js`,
            
            // Integration tests
            playgroundIntegration: `${this.BASE_PATH}/playground.html.test.js`
        };
    }
};

// Freeze to prevent accidental modification
Object.freeze(TestPaths.VERSIONS);

// Export for both browser and Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TestPaths;
}
if (typeof window !== 'undefined') {
    window.TestPaths = TestPaths;
}
