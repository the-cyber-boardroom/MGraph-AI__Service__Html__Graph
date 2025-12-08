/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Test Suite - Playground Integration Tests
   v0.2.0 - Consolidated from v0.1.x
   
   Integration tests that verify components work together correctly.
   ═══════════════════════════════════════════════════════════════════════════════ */

QUnit.module('Playground Integration', function(hooks) {
    
    let originalApiClient = null;
    
    hooks.before(async function(assert) {
        // Load CSS
        await TestUtils.loadCss(TestPaths.commonCss);
        await TestUtils.loadCss(TestPaths.playgroundCss);
        
        // Load API client first
        await TestUtils.loadScript(TestPaths.apiClient);
        
        // Load all required components
        await TestUtils.loadScript(TestPaths.htmlInput);
        await TestUtils.loadScript(TestPaths.configPanel);
        await TestUtils.loadScript(TestPaths.statsToolbar);
        await TestUtils.loadScript(TestPaths.graphCanvas);
        await TestUtils.loadScript(TestPaths.urlInput);
        await TestUtils.loadScript(TestPaths.dotRenderer);
        
        assert.ok(true, 'All components loaded');
    });
    
    hooks.beforeEach(function() {
        originalApiClient = window.apiClient;
    });
    
    hooks.afterEach(function() {
        window.apiClient = originalApiClient;
        TestUtils.cleanup();
    });

    QUnit.test('all playground components can be instantiated together', async function(assert) {
        const fixture = document.getElementById('qunit-fixture');
        
        fixture.innerHTML = `
            <html-input></html-input>
            <config-panel></config-panel>
            <stats-toolbar></stats-toolbar>
            <graph-canvas></graph-canvas>
            <url-input></url-input>
            <dot-renderer></dot-renderer>
        `;
        
        await TestUtils.nextFrame();
        
        assert.ok(fixture.querySelector('html-input'), 'html-input should render');
        assert.ok(fixture.querySelector('config-panel'), 'config-panel should render');
        assert.ok(fixture.querySelector('stats-toolbar'), 'stats-toolbar should render');
        assert.ok(fixture.querySelector('graph-canvas'), 'graph-canvas should render');
        assert.ok(fixture.querySelector('url-input'), 'url-input should render');
        assert.ok(fixture.querySelector('dot-renderer'), 'dot-renderer should render');
    });
    
    QUnit.skip('[bug] html-input emits event that can be received by other components', async function(assert) {
        // Skipped: needs better wait mechanism for debounced events
        const fixture = document.getElementById('qunit-fixture');
        fixture.innerHTML = `<html-input></html-input>`;
        
        await TestUtils.nextFrame();
        
        const htmlInput = fixture.querySelector('html-input');
        let receivedHtml = null;
        
        document.addEventListener('html-changed', (e) => {
            receivedHtml = e.detail.html;
        }, { once: true });
        
        htmlInput.setHtml('<div>Test</div>');
        const textarea = htmlInput.querySelector('#html-input');
        TestUtils.triggerEvent(textarea, 'input');
        
        await TestUtils.wait(400);
        
        assert.strictEqual(receivedHtml, '<div>Test</div>', 'html-changed event should be received');
    });
    
    QUnit.test('config-panel emits event that bubbles up', async function(assert) {
        const fixture = document.getElementById('qunit-fixture');
        fixture.innerHTML = `<div id="wrapper"><config-panel></config-panel></div>`;
        
        await TestUtils.nextFrame();
        
        const configPanel = fixture.querySelector('config-panel');
        let receivedConfig = null;
        
        fixture.addEventListener('config-changed', (e) => {
            receivedConfig = e.detail.config;
        }, { once: true });
        
        const presetSelect = configPanel.querySelector('#config-preset');
        presetSelect.value = 'minimal';
        TestUtils.triggerEvent(presetSelect, 'change');
        
        await TestUtils.nextFrame();
        
        assert.ok(receivedConfig, 'config-changed event should be received');
        assert.strictEqual(receivedConfig.preset, 'minimal', 'config should have new preset');
    });
    
    QUnit.test('stats-toolbar render button emits render-requested event', async function(assert) {
        const fixture = document.getElementById('qunit-fixture');
        fixture.innerHTML = `<stats-toolbar></stats-toolbar>`;
        
        await TestUtils.nextFrame();
        
        const statsToolbar = fixture.querySelector('stats-toolbar');
        const eventPromise = TestUtils.waitForEvent(fixture, 'render-requested');
        
        const renderBtn = statsToolbar.querySelector('#render-btn');
        renderBtn.click();
        
        const event = await eventPromise;
        assert.ok(event, 'render-requested event should bubble up');
    });
    
    QUnit.test('graph-canvas renderer-changed event includes renderer type', async function(assert) {
        const fixture = document.getElementById('qunit-fixture');
        fixture.innerHTML = `<graph-canvas></graph-canvas>`;
        
        await TestUtils.nextFrame();
        
        const graphCanvas = fixture.querySelector('graph-canvas');
        const eventPromise = TestUtils.waitForEvent(fixture, 'renderer-changed');
        
        const select = graphCanvas.querySelector('#renderer-select');
        select.value = 'cytoscape';
        TestUtils.triggerEvent(select, 'change');
        
        const event = await eventPromise;
        assert.strictEqual(event.detail.renderer, 'cytoscape', 'event should contain renderer name');
    });
    
    QUnit.test('mock API flow: html → config → stats update', async function(assert) {
        const fixture = document.getElementById('qunit-fixture');
        fixture.innerHTML = `
            <html-input></html-input>
            <config-panel></config-panel>
            <stats-toolbar></stats-toolbar>
            <graph-canvas></graph-canvas>
        `;
        
        await TestUtils.nextFrame();
        
        const htmlInput = fixture.querySelector('html-input');
        const configPanel = fixture.querySelector('config-panel');
        const statsToolbar = fixture.querySelector('stats-toolbar');
        
        htmlInput.setHtml('<div><p>Hello</p></div>');
        
        const config = configPanel.getConfig();
        assert.ok(config.preset, 'config should have preset');
        
        statsToolbar.setStats({
            total_nodes: 5,
            total_edges: 4,
            element_nodes: 2,
            text_nodes: 1,
            attr_nodes: 0
        });
        
        assert.strictEqual(
            statsToolbar.querySelector('#stat-nodes').textContent, 
            '5', 
            'stats should be updated'
        );
    });
    
    QUnit.test('component communication works with mock API', async function(assert) {
        window.apiClient = TestUtils.createMockApiClient({
            htmlToDot: async () => ({
                dot: 'digraph { a -> b }',
                stats: { total_nodes: 10, total_edges: 9 },
                processing_ms: 50
            })
        });
        
        const fixture = document.getElementById('qunit-fixture');
        fixture.innerHTML = `
            <stats-toolbar></stats-toolbar>
            <graph-canvas></graph-canvas>
        `;
        
        await TestUtils.nextFrame();
        
        const statsToolbar = fixture.querySelector('stats-toolbar');
        const graphCanvas = fixture.querySelector('graph-canvas');
        
        const response = await window.apiClient.htmlToDot({ html: '<div></div>' });
        
        statsToolbar.setStats(response.stats);
        statsToolbar.setTiming({ 
            api_ms: 100, 
            server_ms: response.processing_ms 
        });
        
        assert.strictEqual(
            statsToolbar.querySelector('#stat-nodes').textContent, 
            '10', 
            'nodes should show API response value'
        );
    });
    
    QUnit.test('error handling flow works correctly', async function(assert) {
        const fixture = document.getElementById('qunit-fixture');
        fixture.innerHTML = `
            <stats-toolbar></stats-toolbar>
            <graph-canvas></graph-canvas>
        `;
        
        await TestUtils.nextFrame();
        
        const statsToolbar = fixture.querySelector('stats-toolbar');
        const graphCanvas = fixture.querySelector('graph-canvas');
        
        statsToolbar.showError('API Error', 'Connection failed', 'Check server');
        graphCanvas.showError('Rendering failed', 'Could not parse response');
        
        const errorBanner = statsToolbar.querySelector('#error-banner');
        const canvasError = graphCanvas.querySelector('.canvas-error');
        
        assert.ok(errorBanner.classList.contains('show'), 'error banner should be visible');
        assert.ok(canvasError, 'canvas should show error');
    });

    //todo: fix this tests which fails in Wallaby (only when running with other tests
    QUnit.skip('renderer switching preserves other component states', async function(assert) {
        const fixture = document.getElementById('qunit-fixture');
        fixture.innerHTML = `
            <html-input></html-input>
            <config-panel></config-panel>
            <graph-canvas></graph-canvas>
        `;
        
        await TestUtils.nextFrame();
        
        const htmlInput = fixture.querySelector('html-input');
        const configPanel = fixture.querySelector('config-panel');
        const graphCanvas = fixture.querySelector('graph-canvas');
        
        htmlInput.setHtml('<div>Test Content</div>');
        configPanel.setConfig({ preset: 'structure_only' });
        
        const select = graphCanvas.querySelector('#renderer-select');
        select.value = 'd3';
        TestUtils.triggerEvent(select, 'change');
        
        await TestUtils.nextFrame();
        
        assert.strictEqual(htmlInput.getHtml(), '<div>Test Content</div>', 'HTML should be preserved');
        assert.strictEqual(configPanel.getConfig().preset, 'structure_only', 'config should be preserved');
        assert.strictEqual(graphCanvas.getCurrentRenderer(), 'd3', 'renderer should be updated');
    });

});
