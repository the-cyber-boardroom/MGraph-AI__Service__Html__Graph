/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - Test Path Configuration
   v0.2.0 - Consolidated from v0.1.x
   
   All paths are local to v0.2.0 (self-contained)
   ═══════════════════════════════════════════════════════════════════════════════ */

const TestPaths = {
    // Base path for this version
    base: '.',

    // Component paths (all local)
    components: {
        configPanel:       './components/config-panel/config-panel.js',
        graphCanvas:       './components/graph-canvas/graph-canvas.js',
        htmlInput:         './components/html-input/html-input.js',
        statsPanel:        './components/stats-panel/stats-panel.js',
        topNav:            './components/top-nav/top-nav.js',
        dotRenderer:       './components/dot-renderer/dot-renderer.js',
        statsToolbar:      './components/stats-toolbar/stats-toolbar.js',
        urlInput:          './components/url-input/url-input.js',
        visRenderer:       './components/vis-renderer/vis-renderer.js',
        d3Renderer:        './components/d3-renderer/d3-renderer.js',
        cytoscapeRenderer: './components/cytoscape-renderer/cytoscape-renderer.js',
        mermaidRenderer:   './components/mermaid-renderer/mermaid-renderer.js'
    },

    // Service paths (all local)
    services: {
        apiClient: './js/services/api-client.js'
    },

    // CSS paths (all local)
    css: {
        common:     './css/common.css',
        dashboard:  './css/dashboard.css',
        playground: './css/playground.css'
    },

    // Sample paths (all local)
    samples: {
        simple:       './samples/simple.html',
        nested:       './samples/nested.html',
        attributes:   './samples/attributes.html',
        mixedContent: './samples/mixed-content.html',
        bootstrap:    './samples/bootstrap.html'
    },

    // HTML pages (all local)
    pages: {
        index:      './index.html',
        playground: './playground.html',
        notFound:   './404.html'
    }
};

// Export for both browser and Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TestPaths;
}
if (typeof window !== 'undefined') {
    window.TestPaths = TestPaths;
}
