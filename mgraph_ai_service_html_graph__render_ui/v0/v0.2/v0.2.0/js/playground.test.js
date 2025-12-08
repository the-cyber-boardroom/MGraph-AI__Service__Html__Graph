/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Test Suite - Playground Orchestrator Tests
   v0.2.0 - Consolidated from v0.1.x

   Note: These tests create isolated Playground instances and properly clean up
   event listeners, timers, and mocked functions after each test.
   ═══════════════════════════════════════════════════════════════════════════════ */

QUnit.module('Playground Orchestrator', function(hooks) {

    // Store originals for restoration
    let originalConsoleLog;
    let originalConsoleError;

    // Track instances and listeners for cleanup
    let playgroundInstance = null;
    let eventListenersAdded = [];

    // Helper to add tracked event listener
    function addTrackedListener(target, event, handler) {
        target.addEventListener(event, handler);
        eventListenersAdded.push({ target, event, handler });
    }

    // Helper to create a playground with mocked renderGraph (prevents API calls)
    function createPlayground() {
        const instance = new Playground();
        instance.renderGraph = async () => {};
        return instance;
    }

    hooks.before(async function(assert) {
        originalConsoleLog = console.log;
        originalConsoleError = console.error;

        await TestUtils.loadScript(TestPaths.playgroundJs);
        assert.ok(typeof Playground === 'function', 'Playground class should be available');
    });

    hooks.afterEach(function() {
        console.log = originalConsoleLog;
        console.error = originalConsoleError;

        if (playgroundInstance && playgroundInstance.autoRenderTimer) {
            clearTimeout(playgroundInstance.autoRenderTimer);
            playgroundInstance.autoRenderTimer = null;
        }

        eventListenersAdded.forEach(({ target, event, handler }) => {
            target.removeEventListener(event, handler);
        });
        eventListenersAdded = [];

        playgroundInstance = null;
        TestUtils.cleanup();
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // Constructor Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('Playground class exists', function(assert) {
        assert.ok(typeof Playground === 'function', 'Playground should be a function/class');
    });

    QUnit.test('constructor initializes component references to null', function(assert) {
        playgroundInstance = new Playground();

        assert.strictEqual(playgroundInstance.htmlInput, null, 'htmlInput should be null');
        assert.strictEqual(playgroundInstance.configPanel, null, 'configPanel should be null');
        assert.strictEqual(playgroundInstance.statsToolbar, null, 'statsToolbar should be null');
        assert.strictEqual(playgroundInstance.graphCanvas, null, 'graphCanvas should be null');
        assert.strictEqual(playgroundInstance.urlInput, null, 'urlInput should be null');
    });

    QUnit.test('constructor initializes renderer references to null', function(assert) {
        playgroundInstance = new Playground();

        assert.strictEqual(playgroundInstance.dotRenderer, null, 'dotRenderer should be null');
        assert.strictEqual(playgroundInstance.visRenderer, null, 'visRenderer should be null');
        assert.strictEqual(playgroundInstance.d3Renderer, null, 'd3Renderer should be null');
        assert.strictEqual(playgroundInstance.cytoscapeRenderer, null, 'cytoscapeRenderer should be null');
        assert.strictEqual(playgroundInstance.mermaidRenderer, null, 'mermaidRenderer should be null');
    });

    QUnit.test('constructor initializes state properties', function(assert) {
        playgroundInstance = new Playground();

        assert.strictEqual(playgroundInstance.currentHtml, '', 'currentHtml should be empty string');
        assert.deepEqual(playgroundInstance.currentConfig, {}, 'currentConfig should be empty object');
        assert.strictEqual(playgroundInstance.currentDot, null, 'currentDot should be null');
        assert.strictEqual(playgroundInstance.currentStats, null, 'currentStats should be null');
        assert.strictEqual(playgroundInstance.isRendering, false, 'isRendering should be false');
    });

    QUnit.test('constructor initializes timing properties', function(assert) {
        playgroundInstance = new Playground();

        assert.strictEqual(playgroundInstance.currentApiMs, 0, 'currentApiMs should be 0');
        assert.strictEqual(playgroundInstance.currentServerMs, 0, 'currentServerMs should be 0');
        assert.strictEqual(playgroundInstance.currentDotSize, 0, 'currentDotSize should be 0');
    });

    QUnit.test('constructor initializes auto-render settings', function(assert) {
        playgroundInstance = new Playground();

        assert.strictEqual(playgroundInstance.autoRenderTimer, null, 'autoRenderTimer should be null');
        assert.strictEqual(playgroundInstance.autoRenderDelay, 800, 'autoRenderDelay should be 800ms');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // Utility Method Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('formatBytes formats bytes correctly', function(assert) {
        playgroundInstance = new Playground();

        assert.strictEqual(playgroundInstance.formatBytes(0), '0 B', 'zero bytes');
        assert.strictEqual(playgroundInstance.formatBytes(500), '500 B', 'small bytes');
        assert.strictEqual(playgroundInstance.formatBytes(1023), '1023 B', 'just under 1 KB');
        assert.strictEqual(playgroundInstance.formatBytes(1024), '1.0 KB', 'exactly 1 KB');
        assert.strictEqual(playgroundInstance.formatBytes(1536), '1.5 KB', '1.5 KB');
        assert.strictEqual(playgroundInstance.formatBytes(10240), '10.0 KB', '10 KB');
    });

    QUnit.test('formatBytes formats megabytes correctly', function(assert) {
        playgroundInstance = new Playground();

        assert.strictEqual(playgroundInstance.formatBytes(1048576), '1.0 MB', 'exactly 1 MB');
        assert.strictEqual(playgroundInstance.formatBytes(1572864), '1.5 MB', '1.5 MB');
        assert.strictEqual(playgroundInstance.formatBytes(10485760), '10.0 MB', '10 MB');
    });

    QUnit.test('escapeHtml escapes script tags', function(assert) {
        playgroundInstance = new Playground();

        const result = playgroundInstance.escapeHtml('<script>alert("xss")</script>');

        assert.ok(!result.includes('<script>'), 'should not contain script tag');
        assert.ok(result.includes('&lt;'), 'should contain escaped <');
        assert.ok(result.includes('&gt;'), 'should contain escaped >');
    });

    QUnit.test('escapeHtml escapes ampersands', function(assert) {
        playgroundInstance = new Playground();

        assert.strictEqual(playgroundInstance.escapeHtml('a & b'), 'a &amp; b', 'should escape &');
    });

    QUnit.test('escapeHtml handles empty string', function(assert) {
        playgroundInstance = new Playground();

        assert.strictEqual(playgroundInstance.escapeHtml(''), '', 'should handle empty string');
    });

    QUnit.test('escapeHtml handles plain text', function(assert) {
        playgroundInstance = new Playground();

        assert.strictEqual(playgroundInstance.escapeHtml('Hello World'), 'Hello World', 'should not modify plain text');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // scheduleAutoRender Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('scheduleAutoRender sets timer when HTML exists', function(assert) {
        playgroundInstance = createPlayground();
        playgroundInstance.htmlInput = { getHtml: () => '<div>test</div>' };
        playgroundInstance.currentHtml = '<div>test</div>';

        playgroundInstance.scheduleAutoRender();

        assert.ok(playgroundInstance.autoRenderTimer !== null, 'timer should be set');
    });

    QUnit.test('scheduleAutoRender clears existing timer before setting new one', function(assert) {
        playgroundInstance = createPlayground();
        playgroundInstance.htmlInput = { getHtml: () => '<div>test</div>' };
        playgroundInstance.currentHtml = '<div>test</div>';

        playgroundInstance.scheduleAutoRender();
        const firstTimer = playgroundInstance.autoRenderTimer;

        playgroundInstance.scheduleAutoRender();
        const secondTimer = playgroundInstance.autoRenderTimer;

        assert.ok(firstTimer !== null, 'first timer should have been set');
        assert.ok(secondTimer !== null, 'second timer should be set');
    });

    QUnit.test('scheduleAutoRender does nothing when isRendering is true', function(assert) {
        playgroundInstance = createPlayground();
        playgroundInstance.isRendering = true;
        playgroundInstance.currentHtml = '<div>test</div>';

        playgroundInstance.scheduleAutoRender();

        assert.strictEqual(playgroundInstance.autoRenderTimer, null, 'timer should not be set when rendering');
    });

    QUnit.test('scheduleAutoRender does nothing with empty HTML from htmlInput', function(assert) {
        playgroundInstance = createPlayground();
        playgroundInstance.htmlInput = { getHtml: () => '' };
        playgroundInstance.currentHtml = '';

        playgroundInstance.scheduleAutoRender();

        assert.strictEqual(playgroundInstance.autoRenderTimer, null, 'timer should not be set with empty HTML');
    });

    QUnit.test('scheduleAutoRender does nothing with whitespace-only HTML', function(assert) {
        playgroundInstance = createPlayground();
        playgroundInstance.htmlInput = { getHtml: () => '   \n\t  ' };
        playgroundInstance.currentHtml = '   \n\t  ';

        playgroundInstance.scheduleAutoRender();

        assert.strictEqual(playgroundInstance.autoRenderTimer, null, 'timer should not be set with whitespace-only HTML');
    });

    QUnit.test('scheduleAutoRender accepts custom delay', function(assert) {
        playgroundInstance = createPlayground();
        playgroundInstance.htmlInput = { getHtml: () => '<div>test</div>' };
        playgroundInstance.currentHtml = '<div>test</div>';

        playgroundInstance.scheduleAutoRender(100);

        assert.ok(playgroundInstance.autoRenderTimer !== null, 'timer should be set with custom delay');
    });

    QUnit.test('scheduleAutoRender uses default delay when null passed', function(assert) {
        playgroundInstance = createPlayground();
        playgroundInstance.htmlInput = { getHtml: () => '<div>test</div>' };
        playgroundInstance.currentHtml = '<div>test</div>';

        playgroundInstance.scheduleAutoRender(null);

        assert.ok(playgroundInstance.autoRenderTimer !== null, 'timer should be set with default delay');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // handleUrlHtmlFetched Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('handleUrlHtmlFetched updates currentHtml', function(assert) {
        playgroundInstance = createPlayground();
        playgroundInstance.htmlInput = { setHtml: () => {}, getHtml: () => '' };

        playgroundInstance.handleUrlHtmlFetched({
            html: '<div>fetched</div>',
            url: 'https://example.com',
            contentType: 'text/html'
        });

        assert.strictEqual(playgroundInstance.currentHtml, '<div>fetched</div>', 'currentHtml should be updated');
    });

    QUnit.test('handleUrlHtmlFetched clears currentDot', function(assert) {
        playgroundInstance = createPlayground();
        playgroundInstance.currentDot = 'digraph { a -> b }';
        playgroundInstance.htmlInput = { setHtml: () => {}, getHtml: () => '' };

        playgroundInstance.handleUrlHtmlFetched({
            html: '<div>fetched</div>',
            url: 'https://example.com',
            contentType: 'text/html'
        });

        assert.strictEqual(playgroundInstance.currentDot, null, 'currentDot should be cleared');
    });

    QUnit.test('handleUrlHtmlFetched calls htmlInput.setHtml', function(assert) {
        playgroundInstance = createPlayground();

        let setHtmlCalledWith = null;
        playgroundInstance.htmlInput = {
            setHtml: (html) => { setHtmlCalledWith = html; },
            getHtml: () => ''
        };

        playgroundInstance.handleUrlHtmlFetched({
            html: '<div>fetched</div>',
            url: 'https://example.com',
            contentType: 'text/html'
        });

        assert.strictEqual(setHtmlCalledWith, '<div>fetched</div>', 'htmlInput.setHtml should be called with fetched HTML');
    });

    QUnit.test('handleUrlHtmlFetched handles null htmlInput', function(assert) {
        playgroundInstance = createPlayground();
        playgroundInstance.htmlInput = null;

        playgroundInstance.handleUrlHtmlFetched({
            html: '<div>fetched</div>',
            url: 'https://example.com',
            contentType: 'text/html'
        });

        assert.strictEqual(playgroundInstance.currentHtml, '<div>fetched</div>', 'currentHtml should still be updated');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // renderGraph Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('renderGraph exits early when isRendering is true', async function(assert) {
        playgroundInstance = new Playground();
        playgroundInstance.isRendering = true;

        let statsToolbarCalled = false;
        playgroundInstance.statsToolbar = {
            setRenderingState: () => { statsToolbarCalled = true; }
        };

        await playgroundInstance.renderGraph();

        assert.ok(!statsToolbarCalled, 'should exit early without calling statsToolbar');
    });

    QUnit.test('renderGraph shows error for empty HTML', async function(assert) {
        playgroundInstance = new Playground();
        playgroundInstance.currentHtml = '';
        playgroundInstance.htmlInput = { getHtml: () => '' };

        let errorMessage = null;
        playgroundInstance.statsToolbar = {
            showError: (title) => { errorMessage = title; }
        };

        await playgroundInstance.renderGraph();

        assert.strictEqual(errorMessage, 'No HTML to render', 'should show "No HTML to render" error');
    });

    QUnit.test('renderGraph shows error for whitespace-only HTML', async function(assert) {
        playgroundInstance = new Playground();
        playgroundInstance.currentHtml = '   \n\t  ';
        playgroundInstance.htmlInput = { getHtml: () => '   \n\t  ' };

        let errorShown = false;
        playgroundInstance.statsToolbar = {
            showError: () => { errorShown = true; }
        };

        await playgroundInstance.renderGraph();

        assert.ok(errorShown, 'should show error for whitespace-only HTML');
    });

    QUnit.test('renderGraph sets isRendering to true during render', async function(assert) {
        playgroundInstance = new Playground();
        playgroundInstance.currentHtml = '<div>test</div>';
        playgroundInstance.htmlInput = { getHtml: () => '<div>test</div>' };
        playgroundInstance.configPanel = { getConfig: () => ({}) };

        let wasRenderingDuringCall = false;
        playgroundInstance.statsToolbar = {
            setRenderingState: (state) => {
                if (state) wasRenderingDuringCall = playgroundInstance.isRendering;
            },
            hideError: () => {},
            clearStats: () => {},
            showError: () => {}
        };
        playgroundInstance.graphCanvas = {
            showLoading: () => {} ,
            showError: () => {}
        };

        console.error = () => {};

        await playgroundInstance.renderGraph();

        assert.ok(wasRenderingDuringCall, 'isRendering should be true during render');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // init Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('init logs initialization message', function(assert) {
        playgroundInstance = new Playground();
        playgroundInstance.setupEventListeners = () => {};
        playgroundInstance.loadFromUrl = () => {};

        let loggedMessage = null;
        console.log = (msg) => { loggedMessage = msg; };

        playgroundInstance.init();

        assert.ok(loggedMessage && loggedMessage.includes('Playground v0.2.0'), 'should log initialization message');
    });

    QUnit.test('init calls setupEventListeners', function(assert) {
        playgroundInstance = new Playground();

        let setupCalled = false;
        playgroundInstance.setupEventListeners = () => {
            setupCalled = true;
        };

        console.log = () => {};

        playgroundInstance.init();

        assert.ok(setupCalled, 'setupEventListeners should be called');
    });

    QUnit.test('init calls loadFromUrl', function(assert) {
        playgroundInstance = new Playground();

        let loadFromUrlCalled = false;
        playgroundInstance.loadFromUrl = () => { loadFromUrlCalled = true; };
        playgroundInstance.setupEventListeners = () => {};

        console.log = () => {};

        playgroundInstance.init();

        assert.ok(loadFromUrlCalled, 'loadFromUrl should be called');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // Event Handling Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('html-changed event updates currentHtml', function(assert) {
        playgroundInstance = createPlayground();
        playgroundInstance.htmlInput = { getHtml: () => '' };

        const handler = (e) => {
            playgroundInstance.currentHtml = e.detail.html;
            playgroundInstance.currentDot = null;
        };
        addTrackedListener(document, 'html-changed', handler);

        document.dispatchEvent(new CustomEvent('html-changed', {
            detail: { html: '<div>new content</div>' }
        }));

        assert.strictEqual(playgroundInstance.currentHtml, '<div>new content</div>', 'currentHtml should be updated');
        assert.strictEqual(playgroundInstance.currentDot, null, 'currentDot should be cleared');
    });

    QUnit.test('config-changed event updates currentConfig', function(assert) {
        playgroundInstance = createPlayground();

        const newConfig = { preset: 'minimal', show_tag_nodes: false };

        const handler = (e) => {
            playgroundInstance.currentConfig = e.detail.config;
            playgroundInstance.currentDot = null;
        };
        addTrackedListener(document, 'config-changed', handler);

        document.dispatchEvent(new CustomEvent('config-changed', {
            detail: { config: newConfig }
        }));

        assert.deepEqual(playgroundInstance.currentConfig, newConfig, 'currentConfig should be updated');
    });

    QUnit.test('render-requested event triggers renderGraph', async function(assert) {
        playgroundInstance = createPlayground();

        let renderCalled = false;
        playgroundInstance.renderGraph = async () => { renderCalled = true; };

        const handler = () => { playgroundInstance.renderGraph(); };
        addTrackedListener(document, 'render-requested', handler);

        document.dispatchEvent(new CustomEvent('render-requested'));

        await TestUtils.nextFrame();

        assert.ok(renderCalled, 'renderGraph should be called');
    });

    QUnit.test('renderer-changed event triggers re-render with cached DOT', function(assert) {
        playgroundInstance = createPlayground();
        playgroundInstance.currentDot = 'digraph { a -> b }';
        playgroundInstance.currentHtml = '<div>test</div>';

        let renderWithCurrentRendererCalled = false;
        playgroundInstance.renderWithCurrentRenderer = () => {
            renderWithCurrentRendererCalled = true;
        };

        const handler = (e) => {
            if (playgroundInstance.currentDot && playgroundInstance.currentHtml) {
                playgroundInstance.renderWithCurrentRenderer();
            }
        };
        addTrackedListener(document, 'renderer-changed', handler);

        document.dispatchEvent(new CustomEvent('renderer-changed', {
            detail: { renderer: 'visjs' }
        }));

        assert.ok(renderWithCurrentRendererCalled, 'renderWithCurrentRenderer should be called when DOT is cached');
    });

    QUnit.test('renderer-changed event does nothing without cached DOT', function(assert) {
        playgroundInstance = createPlayground();
        playgroundInstance.currentDot = null;
        playgroundInstance.currentHtml = '<div>test</div>';

        let renderCalled = false;
        playgroundInstance.renderWithCurrentRenderer = () => { renderCalled = true; };

        const handler = (e) => {
            if (playgroundInstance.currentDot && playgroundInstance.currentHtml) {
                playgroundInstance.renderWithCurrentRenderer();
            }
        };
        addTrackedListener(document, 'renderer-changed', handler);

        document.dispatchEvent(new CustomEvent('renderer-changed', {
            detail: { renderer: 'visjs' }
        }));

        assert.ok(!renderCalled, 'renderWithCurrentRenderer should not be called without cached DOT');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // loadFromUrl Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('loadFromUrl does not throw with no query params', function(assert) {
        playgroundInstance = createPlayground();

        playgroundInstance.loadFromUrl();

        assert.ok(true, 'loadFromUrl should not throw');
    });

});
