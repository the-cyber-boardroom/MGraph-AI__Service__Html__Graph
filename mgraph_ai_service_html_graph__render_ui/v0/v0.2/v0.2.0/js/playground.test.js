/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Test Suite - Playground Extended Tests
   v0.2.0 - Additional tests to improve coverage from 38%

   Focuses on methods not covered by existing tests:
   - renderWithCurrentRenderer and all render methods
   - handleRenderError
   - enablePanning
   - showDotFallback
   - fetchDotFromApi
   - loadFromUrl with various params
   ═══════════════════════════════════════════════════════════════════════════════ */

QUnit.module('Playground Extended', function(hooks) {

    let originalConsoleLog;
    let originalConsoleError;
    let originalApiClient;
    let playgroundInstance = null;

    hooks.before(async function(assert) {
        originalConsoleLog = console.log;
        originalConsoleError = console.error;

        await TestUtils.loadScript(TestPaths.apiClient);
        await TestUtils.loadScript(TestPaths.playgroundJs);
        assert.ok(typeof Playground === 'function', 'Playground class should be available');
    });

    hooks.beforeEach(function() {
        originalApiClient = window.apiClient;
        console.log = () => {};
        console.error = () => {};
    });

    hooks.afterEach(function() {
        console.log = originalConsoleLog;
        console.error = originalConsoleError;
        window.apiClient = originalApiClient;

        if (playgroundInstance && playgroundInstance.autoRenderTimer) {
            clearTimeout(playgroundInstance.autoRenderTimer);
        }
        playgroundInstance = null;
        TestUtils.cleanup();
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // renderWithCurrentRenderer Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('renderWithCurrentRenderer does nothing without currentDot', async function(assert) {
        playgroundInstance = new Playground();
        playgroundInstance.currentDot = null;

        let renderCalled = false;
        playgroundInstance.renderWithDot = async () => { renderCalled = true; };

        await playgroundInstance.renderWithCurrentRenderer();

        assert.ok(!renderCalled, 'should not render without DOT');
    });

    QUnit.test('renderWithCurrentRenderer calls renderWithDot for dot renderer', async function(assert) {
        playgroundInstance = new Playground();
        playgroundInstance.currentDot = 'digraph { a -> b }';
        playgroundInstance.graphCanvas = { getCurrentRenderer: () => 'dot' };
        playgroundInstance.statsToolbar = { setTiming: () => {} };

        let renderDotCalled = false;
        playgroundInstance.renderWithDot = async () => { renderDotCalled = true; };

        await playgroundInstance.renderWithCurrentRenderer();

        assert.ok(renderDotCalled, 'renderWithDot should be called');
    });

    QUnit.test('renderWithCurrentRenderer calls renderWithVisJs for visjs renderer', async function(assert) {
        playgroundInstance = new Playground();
        playgroundInstance.currentDot = 'digraph { a -> b }';
        playgroundInstance.graphCanvas = { getCurrentRenderer: () => 'visjs' };
        playgroundInstance.statsToolbar = { setTiming: () => {} };

        let renderVisJsCalled = false;
        playgroundInstance.renderWithVisJs = async () => { renderVisJsCalled = true; };

        await playgroundInstance.renderWithCurrentRenderer();

        assert.ok(renderVisJsCalled, 'renderWithVisJs should be called');
    });

    QUnit.test('renderWithCurrentRenderer calls renderWithD3 for d3 renderer', async function(assert) {
        playgroundInstance = new Playground();
        playgroundInstance.currentDot = 'digraph { a -> b }';
        playgroundInstance.graphCanvas = { getCurrentRenderer: () => 'd3' };
        playgroundInstance.statsToolbar = { setTiming: () => {} };

        let renderD3Called = false;
        playgroundInstance.renderWithD3 = async () => { renderD3Called = true; };

        await playgroundInstance.renderWithCurrentRenderer();

        assert.ok(renderD3Called, 'renderWithD3 should be called');
    });

    QUnit.test('renderWithCurrentRenderer calls renderWithCytoscape for cytoscape renderer', async function(assert) {
        playgroundInstance = new Playground();
        playgroundInstance.currentDot = 'digraph { a -> b }';
        playgroundInstance.graphCanvas = { getCurrentRenderer: () => 'cytoscape' };
        playgroundInstance.statsToolbar = { setTiming: () => {} };

        let renderCytoscapeCalled = false;
        playgroundInstance.renderWithCytoscape = async () => { renderCytoscapeCalled = true; };

        await playgroundInstance.renderWithCurrentRenderer();

        assert.ok(renderCytoscapeCalled, 'renderWithCytoscape should be called');
    });

    QUnit.test('renderWithCurrentRenderer calls renderWithMermaid for mermaid renderer', async function(assert) {
        playgroundInstance = new Playground();
        playgroundInstance.currentDot = 'digraph { a -> b }';
        playgroundInstance.graphCanvas = { getCurrentRenderer: () => 'mermaid' };
        playgroundInstance.statsToolbar = { setTiming: () => {} };

        let renderMermaidCalled = false;
        playgroundInstance.renderWithMermaid = async () => { renderMermaidCalled = true; };

        await playgroundInstance.renderWithCurrentRenderer();

        assert.ok(renderMermaidCalled, 'renderWithMermaid should be called');
    });

    QUnit.test('renderWithCurrentRenderer handles unknown renderer', async function(assert) {
        playgroundInstance = new Playground();
        playgroundInstance.currentDot = 'digraph { a -> b }';
        playgroundInstance.graphCanvas = { getCurrentRenderer: () => 'unknown' };

        let errorHandled = false;
        playgroundInstance.handleRenderError = () => { errorHandled = true; };

        await playgroundInstance.renderWithCurrentRenderer();

        assert.ok(errorHandled, 'should handle unknown renderer error');
    });

    QUnit.test('renderWithCurrentRenderer sets timing on success', async function(assert) {
        playgroundInstance = new Playground();
        playgroundInstance.currentDot = 'digraph { a -> b }';
        playgroundInstance.currentApiMs = 100;
        playgroundInstance.currentServerMs = 50;
        playgroundInstance.currentDotSize = 200;
        playgroundInstance.graphCanvas = { getCurrentRenderer: () => 'dot' };

        let timingSet = null;
        playgroundInstance.statsToolbar = { setTiming: (t) => { timingSet = t; } };
        playgroundInstance.renderWithDot = async () => {};

        await playgroundInstance.renderWithCurrentRenderer();

        assert.ok(timingSet, 'timing should be set');
        assert.strictEqual(timingSet.api_ms, 100, 'api_ms should be set');
        assert.strictEqual(timingSet.server_ms, 50, 'server_ms should be set');
        assert.strictEqual(timingSet.dot_size, 200, 'dot_size should be set');
        assert.ok(timingSet.render_ms >= 0, 'render_ms should be set');
    });

    QUnit.test('renderWithCurrentRenderer calls handleRenderError on exception', async function(assert) {
        playgroundInstance = new Playground();
        playgroundInstance.currentDot = 'digraph { a -> b }';
        playgroundInstance.graphCanvas = { getCurrentRenderer: () => 'dot' };

        playgroundInstance.renderWithDot = async () => { throw new Error('Test error'); };

        let errorRenderer = null;
        let errorObj = null;
        playgroundInstance.handleRenderError = (r, e) => { errorRenderer = r; errorObj = e; };

        await playgroundInstance.renderWithCurrentRenderer();

        assert.strictEqual(errorRenderer, 'dot', 'error renderer should be passed');
        assert.ok(errorObj.message.includes('Test error'), 'error should be passed');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // Individual Render Method Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('renderWithDot throws when dotRenderer is null', async function(assert) {
        playgroundInstance = new Playground();
        playgroundInstance.dotRenderer = null;

        try {
            await playgroundInstance.renderWithDot();
            assert.ok(false, 'should throw');
        } catch (e) {
            assert.ok(e.message.includes('DOT renderer'), 'should mention DOT renderer');
        }
    });

    QUnit.test('renderWithDot calls dotRenderer.renderDot', async function(assert) {
        playgroundInstance = new Playground();
        playgroundInstance.currentDot = 'digraph { a }';
        playgroundInstance.graphCanvas = { canvasArea: document.createElement('div') };

        let dotPassed = null;
        playgroundInstance.dotRenderer = {
            renderDot: async (dot) => { dotPassed = dot; }
        };
        playgroundInstance.enablePanning = () => {};

        await playgroundInstance.renderWithDot();

        assert.strictEqual(dotPassed, 'digraph { a }', 'DOT should be passed');
    });

    QUnit.test('renderWithDot calls enablePanning', async function(assert) {
        playgroundInstance = new Playground();
        playgroundInstance.currentDot = 'digraph { a }';
        playgroundInstance.dotRenderer = { renderDot: async () => {} };
        playgroundInstance.graphCanvas = { canvasArea: document.createElement('div') };

        let panningEnabled = false;
        playgroundInstance.enablePanning = () => { panningEnabled = true; };

        await playgroundInstance.renderWithDot();

        assert.ok(panningEnabled, 'enablePanning should be called');
    });

    QUnit.test('renderWithVisJs throws when visRenderer is null', async function(assert) {
        playgroundInstance = new Playground();
        playgroundInstance.visRenderer = null;

        try {
            await playgroundInstance.renderWithVisJs();
            assert.ok(false, 'should throw');
        } catch (e) {
            assert.ok(e.message.includes('vis.js'), 'should mention vis.js');
        }
    });

    QUnit.test('renderWithD3 throws when d3Renderer is null', async function(assert) {
        playgroundInstance = new Playground();
        playgroundInstance.d3Renderer = null;

        try {
            await playgroundInstance.renderWithD3();
            assert.ok(false, 'should throw');
        } catch (e) {
            assert.ok(e.message.includes('D3'), 'should mention D3');
        }
    });

    QUnit.test('renderWithCytoscape throws when cytoscapeRenderer is null', async function(assert) {
        playgroundInstance = new Playground();
        playgroundInstance.cytoscapeRenderer = null;

        try {
            await playgroundInstance.renderWithCytoscape();
            assert.ok(false, 'should throw');
        } catch (e) {
            assert.ok(e.message.includes('Cytoscape'), 'should mention Cytoscape');
        }
    });

    QUnit.test('renderWithMermaid throws when mermaidRenderer is null', async function(assert) {
        playgroundInstance = new Playground();
        playgroundInstance.mermaidRenderer = null;

        try {
            await playgroundInstance.renderWithMermaid();
            assert.ok(false, 'should throw');
        } catch (e) {
            assert.ok(e.message.includes('Mermaid'), 'should mention Mermaid');
        }
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // handleRenderError Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('handleRenderError detects memory errors', async function(assert) {
        playgroundInstance = new Playground();
        playgroundInstance.currentStats = { total_nodes: 10000 };

        let showDotFallbackCalled = false;
        playgroundInstance.showDotFallback = () => { showDotFallbackCalled = true; };
        playgroundInstance.statsToolbar = { showError: () => {} };

        playgroundInstance.handleRenderError('dot', new Error('out of memory'));

        assert.ok(showDotFallbackCalled, 'showDotFallback should be called for memory error');
    });

    QUnit.test('handleRenderError detects WASM errors', async function(assert) {
        playgroundInstance = new Playground();
        playgroundInstance.currentStats = { total_nodes: 5000 };

        let showDotFallbackCalled = false;
        playgroundInstance.showDotFallback = () => { showDotFallbackCalled = true; };
        playgroundInstance.statsToolbar = { showError: () => {} };

        playgroundInstance.handleRenderError('dot', new Error('WASM RuntimeError'));

        assert.ok(showDotFallbackCalled, 'showDotFallback should be called for WASM error');
    });

    QUnit.test('handleRenderError detects allocation errors', async function(assert) {
        playgroundInstance = new Playground();
        playgroundInstance.currentStats = { total_nodes: 5000 };

        let showDotFallbackCalled = false;
        playgroundInstance.showDotFallback = () => { showDotFallbackCalled = true; };
        playgroundInstance.statsToolbar = { showError: () => {} };

        playgroundInstance.handleRenderError('dot', new Error('allocation failed'));

        assert.ok(showDotFallbackCalled, 'showDotFallback should be called for allocation error');
    });

    QUnit.test('handleRenderError detects out of bounds errors', async function(assert) {
        playgroundInstance = new Playground();
        playgroundInstance.currentStats = { total_nodes: 5000 };

        let showDotFallbackCalled = false;
        playgroundInstance.showDotFallback = () => { showDotFallbackCalled = true; };
        playgroundInstance.statsToolbar = { showError: () => {} };

        playgroundInstance.handleRenderError('dot', new Error('index out of bounds'));

        assert.ok(showDotFallbackCalled, 'showDotFallback should be called for out of bounds error');
    });

    QUnit.test('handleRenderError shows generic error for non-memory errors', async function(assert) {
        playgroundInstance = new Playground();

        let showErrorCalled = false;
        let showDotFallbackCalled = false;
        playgroundInstance.statsToolbar = { showError: () => { showErrorCalled = true; } };
        playgroundInstance.graphCanvas = { showError: () => {} };
        playgroundInstance.showDotFallback = () => { showDotFallbackCalled = true; };

        playgroundInstance.handleRenderError('dot', new Error('syntax error'));

        assert.ok(showErrorCalled, 'showError should be called');
        assert.ok(!showDotFallbackCalled, 'showDotFallback should not be called');
    });

    QUnit.test('handleRenderError shows error in graphCanvas for non-memory errors', async function(assert) {
        playgroundInstance = new Playground();

        let canvasErrorRenderer = null;
        playgroundInstance.statsToolbar = { showError: () => {} };
        playgroundInstance.graphCanvas = { showError: (r) => { canvasErrorRenderer = r; } };

        playgroundInstance.handleRenderError('visjs', new Error('parse error'));

        assert.ok(canvasErrorRenderer.includes('visjs'), 'should show renderer in canvas error');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // enablePanning Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('enablePanning does nothing without canvasArea', async function(assert) {
        playgroundInstance = new Playground();
        playgroundInstance.graphCanvas = null;

        playgroundInstance.enablePanning();

        assert.ok(true, 'should not throw');
    });

    QUnit.test('enablePanning does nothing without SVG', async function(assert) {
        playgroundInstance = new Playground();
        const canvasArea = document.createElement('div');
        playgroundInstance.graphCanvas = { canvasArea: canvasArea };

        playgroundInstance.enablePanning();

        assert.ok(true, 'should not throw');
    });

    QUnit.test('enablePanning sets up mouse event handlers', async function(assert) {
        playgroundInstance = new Playground();
        const canvasArea = document.createElement('div');
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        canvasArea.appendChild(svg);
        playgroundInstance.graphCanvas = { canvasArea: canvasArea };

        playgroundInstance.enablePanning();

        assert.ok(canvasArea.onmousedown, 'should set onmousedown');
        assert.ok(canvasArea.onmousemove, 'should set onmousemove');
        assert.ok(canvasArea.onmouseup, 'should set onmouseup');
        assert.ok(canvasArea.onmouseleave, 'should set onmouseleave');
    });

    QUnit.test('enablePanning sets overflow and cursor styles', async function(assert) {
        playgroundInstance = new Playground();
        const canvasArea = document.createElement('div');
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        canvasArea.appendChild(svg);
        playgroundInstance.graphCanvas = { canvasArea: canvasArea };

        playgroundInstance.enablePanning();

        assert.strictEqual(canvasArea.style.overflow, 'auto', 'should set overflow');
        assert.strictEqual(canvasArea.style.cursor, 'grab', 'should set cursor');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // showDotFallback Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('showDotFallback renders DOT code', async function(assert) {
        playgroundInstance = new Playground();
        const canvasArea = document.createElement('div');
        playgroundInstance.graphCanvas = { canvasArea: canvasArea };

        playgroundInstance.showDotFallback('digraph { a -> b }', { total_nodes: 100 });

        assert.ok(canvasArea.innerHTML.includes('digraph'), 'should include DOT code');
    });

    QUnit.test('showDotFallback truncates large DOT', async function(assert) {
        playgroundInstance = new Playground();
        const canvasArea = document.createElement('div');
        playgroundInstance.graphCanvas = { canvasArea: canvasArea };

        const largeDot = 'x'.repeat(10000);
        playgroundInstance.showDotFallback(largeDot, { total_nodes: 1000 });

        assert.ok(canvasArea.innerHTML.includes('truncated'), 'should mention truncation');
    });

    QUnit.test('showDotFallback shows error message when provided', async function(assert) {
        playgroundInstance = new Playground();
        const canvasArea = document.createElement('div');
        playgroundInstance.graphCanvas = { canvasArea: canvasArea };

        playgroundInstance.showDotFallback('digraph {}', { total_nodes: 100 }, 'Memory error');

        assert.ok(canvasArea.innerHTML.includes('Memory error'), 'should include error message');
    });

    QUnit.test('showDotFallback shows node count', async function(assert) {
        playgroundInstance = new Playground();
        const canvasArea = document.createElement('div');
        playgroundInstance.graphCanvas = { canvasArea: canvasArea };

        playgroundInstance.showDotFallback('digraph {}', { total_nodes: 5000 });

        assert.ok(canvasArea.innerHTML.includes('5,000'), 'should show formatted node count');
    });

    QUnit.test('showDotFallback handles null stats', async function(assert) {
        playgroundInstance = new Playground();
        const canvasArea = document.createElement('div');
        playgroundInstance.graphCanvas = { canvasArea: canvasArea };

        playgroundInstance.showDotFallback('digraph {}', null);

        assert.ok(canvasArea.innerHTML.includes('?'), 'should show ? for unknown count');
    });

    QUnit.test('showDotFallback escapes HTML in error message', async function(assert) {
        playgroundInstance = new Playground();
        const canvasArea = document.createElement('div');
        playgroundInstance.graphCanvas = { canvasArea: canvasArea };

        playgroundInstance.showDotFallback('digraph {}', {}, '<script>alert("xss")</script>');

        assert.ok(!canvasArea.innerHTML.includes('<script>'), 'should escape script tags');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // fetchDotFromApi Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('fetchDotFromApi calls apiClient.htmlToDot', async function(assert) {
        playgroundInstance = new Playground();
        playgroundInstance.statsToolbar = { setStats: () => {}, setTiming: () => {} };

        let calledWith = null;
        window.apiClient = {
            htmlToDot: async (req) => {
                calledWith = req;
                return { dot: 'digraph {}', stats: {}, processing_ms: 10 };
            }
        };

        await playgroundInstance.fetchDotFromApi('<div></div>', { preset: 'minimal' });

        assert.ok(calledWith, 'htmlToDot should be called');
        assert.strictEqual(calledWith.html, '<div></div>', 'should pass HTML');
        assert.strictEqual(calledWith.preset, 'minimal', 'should pass preset');
    });

    QUnit.test('fetchDotFromApi stores currentDot', async function(assert) {
        playgroundInstance = new Playground();
        playgroundInstance.statsToolbar = { setStats: () => {}, setTiming: () => {} };

        window.apiClient = {
            htmlToDot: async () => ({ dot: 'digraph { test }', stats: {}, processing_ms: 10 })
        };

        await playgroundInstance.fetchDotFromApi('<div></div>', {});

        assert.strictEqual(playgroundInstance.currentDot, 'digraph { test }', 'should store DOT');
    });

    QUnit.test('fetchDotFromApi stores currentStats', async function(assert) {
        playgroundInstance = new Playground();
        playgroundInstance.statsToolbar = { setStats: () => {}, setTiming: () => {} };

        const stats = { total_nodes: 50, total_edges: 40 };
        window.apiClient = {
            htmlToDot: async () => ({ dot: '', stats: stats, processing_ms: 10 })
        };

        await playgroundInstance.fetchDotFromApi('<div></div>', {});

        assert.deepEqual(playgroundInstance.currentStats, stats, 'should store stats');
    });

    QUnit.test('fetchDotFromApi calls setStats', async function(assert) {
        playgroundInstance = new Playground();

        let statsSet = null;
        playgroundInstance.statsToolbar = {
            setStats: (s) => { statsSet = s; },
            setTiming: () => {}
        };

        const stats = { total_nodes: 25 };
        window.apiClient = {
            htmlToDot: async () => ({ dot: '', stats: stats, processing_ms: 10 })
        };

        await playgroundInstance.fetchDotFromApi('<div></div>', {});

        assert.deepEqual(statsSet, stats, 'setStats should be called with stats');
    });

    QUnit.test('fetchDotFromApi sets timing values', async function(assert) {
        playgroundInstance = new Playground();

        let timingSet = null;
        playgroundInstance.statsToolbar = {
            setStats: () => {},
            setTiming: (t) => { timingSet = t; }
        };

        window.apiClient = {
            htmlToDot: async () => ({
                dot: 'abc',
                stats: {},
                processing_ms: 42,
                dot_size_bytes: 100
            })
        };

        await playgroundInstance.fetchDotFromApi('<div></div>', {});

        assert.ok(timingSet, 'setTiming should be called');
        assert.strictEqual(timingSet.server_ms, 42, 'should set server_ms');
        assert.strictEqual(timingSet.dot_size, 100, 'should set dot_size');
    });

    QUnit.test('fetchDotFromApi uses dot.length when dot_size_bytes missing', async function(assert) {
        playgroundInstance = new Playground();

        let timingSet = null;
        playgroundInstance.statsToolbar = {
            setStats: () => {},
            setTiming: (t) => { timingSet = t; }
        };

        window.apiClient = {
            htmlToDot: async () => ({
                dot: 'digraph { a -> b }',
                stats: {},
                processing_ms: 10
                // no dot_size_bytes
            })
        };

        await playgroundInstance.fetchDotFromApi('<div></div>', {});

        assert.strictEqual(timingSet.dot_size, 'digraph { a -> b }'.length, 'should use dot length');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // loadFromUrl Extended Tests
    // ═══════════════════════════════════════════════════════════════════════════

    //todo fix test which fails with: "Promise rejected during "loadFromUrl handles sample param": Cannot redefine property: location
    QUnit.skip('[bug] loadFromUrl handles sample param', async function(assert) {
        playgroundInstance = new Playground();

        // Mock URL with sample param
        const originalSearch = window.location.search;
        Object.defineProperty(window, 'location', {
            value: { search: '?sample=nested' },
            writable: true
        });

        let loadedSample = null;
        playgroundInstance.htmlInput = {
            loadSample: (s) => { loadedSample = s; }
        };

        playgroundInstance.loadFromUrl();

        // Restore
        Object.defineProperty(window, 'location', {
            value: { search: originalSearch },
            writable: true
        });

        assert.strictEqual(loadedSample, 'nested', 'should load sample from URL');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // Keyboard Shortcut Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('setupEventListeners handles Ctrl+Enter', async function(assert) {
        playgroundInstance = new Playground();

        let renderCalled = false;
        playgroundInstance.renderGraph = async () => { renderCalled = true; };

        playgroundInstance.setupEventListeners();

        // Simulate Ctrl+Enter
        const event = new KeyboardEvent('keydown', {
            key: 'Enter',
            ctrlKey: true,
            bubbles: true
        });
        document.dispatchEvent(event);

        await TestUtils.nextFrame();

        assert.ok(renderCalled, 'Ctrl+Enter should trigger render');
    });

    QUnit.test('setupEventListeners handles Meta+Enter (Mac)', async function(assert) {
        playgroundInstance = new Playground();

        let renderCalled = false;
        playgroundInstance.renderGraph = async () => { renderCalled = true; };

        playgroundInstance.setupEventListeners();

        // Simulate Meta+Enter (Mac Cmd key)
        const event = new KeyboardEvent('keydown', {
            key: 'Enter',
            metaKey: true,
            bubbles: true
        });
        document.dispatchEvent(event);

        await TestUtils.nextFrame();

        assert.ok(renderCalled, 'Meta+Enter should trigger render');
    });

});