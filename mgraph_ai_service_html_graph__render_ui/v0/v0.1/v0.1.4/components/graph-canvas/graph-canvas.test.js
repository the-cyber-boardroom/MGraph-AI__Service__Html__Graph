/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Test Suite - Graph Canvas Tests
   v0.1.4 - Test Infrastructure
   ═══════════════════════════════════════════════════════════════════════════════ */

QUnit.module('Graph Canvas', function(hooks) {
    
    hooks.before(async function(assert) {
        await TestUtils.loadCss(TestPaths.commonCss);
        // Load the v0.1.4 version which has all 5 renderers enabled
        await TestUtils.loadScript(TestPaths.graphCanvas);
        assert.ok(customElements.get('graph-canvas'), 'graph-canvas should be registered');
    });
    
    hooks.afterEach(function() {
        TestUtils.cleanup();
    });

    QUnit.test('component renders correctly', async function(assert) {
        const canvas = await TestUtils.createComponent('graph-canvas');
        
        assert.ok(canvas.querySelector('.graph-canvas-container'), 'should have container');
        assert.ok(canvas.querySelector('.canvas-toolbar'), 'should have toolbar');
        assert.ok(canvas.querySelector('#canvas-area'), 'should have canvas area');
        assert.ok(canvas.querySelector('#renderer-select'), 'should have renderer selector');
    });
    
    QUnit.test('has all zoom controls', async function(assert) {
        const canvas = await TestUtils.createComponent('graph-canvas');
        
        assert.ok(canvas.querySelector('#btn-zoom-in'), 'should have zoom in button');
        assert.ok(canvas.querySelector('#btn-zoom-out'), 'should have zoom out button');
        assert.ok(canvas.querySelector('#btn-reset-zoom'), 'should have reset zoom button');
        assert.ok(canvas.querySelector('#btn-download'), 'should have download button');
    });
    
    QUnit.test('renderer selector has 5 renderer options', async function(assert) {
        const canvas = await TestUtils.createComponent('graph-canvas');
        const select = canvas.querySelector('#renderer-select');
        const options = select.querySelectorAll('option');
        
        assert.strictEqual(options.length, 5, 'should have 5 renderers');
        
        const values = Array.from(options).map(o => o.value);
        assert.ok(values.includes('dot'), 'should have DOT renderer');
        assert.ok(values.includes('visjs'), 'should have vis.js renderer');
        assert.ok(values.includes('d3'), 'should have D3 renderer');
        assert.ok(values.includes('cytoscape'), 'should have Cytoscape renderer');
        assert.ok(values.includes('mermaid'), 'should have Mermaid renderer');
    });
    
    QUnit.test('all renderers are enabled (not disabled)', async function(assert) {
        const canvas = await TestUtils.createComponent('graph-canvas');
        const select = canvas.querySelector('#renderer-select');
        const options = select.querySelectorAll('option');
        
        const disabledCount = Array.from(options).filter(o => o.disabled).length;
        assert.strictEqual(disabledCount, 0, 'no renderers should be disabled in v0.1.4');
    });
    
    QUnit.test('default renderer is DOT', async function(assert) {
        const canvas = await TestUtils.createComponent('graph-canvas');
        
        assert.strictEqual(canvas.getCurrentRenderer(), 'dot', 'default renderer should be dot');
    });
    
    QUnit.test('emits renderer-changed event on selection change', async function(assert) {
        const canvas = await TestUtils.createComponent('graph-canvas');
        const select = canvas.querySelector('#renderer-select');
        
        const eventPromise = TestUtils.waitForEvent(canvas, 'renderer-changed');
        
        select.value = 'visjs';
        TestUtils.triggerEvent(select, 'change');
        
        const event = await eventPromise;
        assert.strictEqual(event.detail.renderer, 'visjs', 'event should contain new renderer');
    });
    
    QUnit.test('getCurrentRenderer returns selected value', async function(assert) {
        const canvas = await TestUtils.createComponent('graph-canvas');
        const select = canvas.querySelector('#renderer-select');
        
        select.value = 'd3';
        TestUtils.triggerEvent(select, 'change');
        
        await TestUtils.nextFrame();
        
        assert.strictEqual(canvas.getCurrentRenderer(), 'd3', 'should return current selection');
    });
    
    QUnit.test('showLoading displays loading state', async function(assert) {
        const canvas = await TestUtils.createComponent('graph-canvas');
        
        canvas.showLoading();
        
        const area = canvas.querySelector('#canvas-area');
        assert.ok(area.querySelector('.spinner'), 'should show spinner');
        TestUtils.assertContainsText(assert, area, 'Rendering', 'should show rendering text');
    });
    
    QUnit.test('showError displays error message', async function(assert) {
        const canvas = await TestUtils.createComponent('graph-canvas');
        
        canvas.showError('Something went wrong', 'Detailed error info');
        
        const area = canvas.querySelector('#canvas-area');
        assert.ok(area.querySelector('.canvas-error'), 'should have error class');
        TestUtils.assertContainsText(assert, area, 'Something went wrong', 'should show error message');
        TestUtils.assertContainsText(assert, area, 'Detailed error info', 'should show error details');
    });
    
    QUnit.test('showEmpty resets to initial state', async function(assert) {
        const canvas = await TestUtils.createComponent('graph-canvas');
        
        canvas.showLoading();
        canvas.showEmpty();
        
        const area = canvas.querySelector('#canvas-area');
        assert.ok(area.querySelector('.canvas-empty'), 'should show empty state');
    });
    
    QUnit.test('renderSvg displays SVG content', async function(assert) {
        const canvas = await TestUtils.createComponent('graph-canvas');
        const testSvg = '<svg width="100" height="100"><circle cx="50" cy="50" r="40"/></svg>';
        
        canvas.renderSvg(testSvg);
        
        const area = canvas.querySelector('#canvas-area');
        const svg = area.querySelector('svg');
        assert.ok(svg, 'should have SVG element');
        assert.ok(svg.querySelector('circle'), 'SVG should contain circle');
    });
    
    QUnit.test('zoom modifies SVG scale', async function(assert) {
        const canvas = await TestUtils.createComponent('graph-canvas');
        canvas.renderSvg('<svg width="100" height="100"><rect width="100" height="100"/></svg>');
        
        canvas.zoom(1.5);
        
        const svg = canvas.querySelector('#canvas-area svg');
        assert.ok(svg.style.transform.includes('scale'), 'SVG should have scale transform');
    });
    
    QUnit.test('resetZoom restores original scale', async function(assert) {
        const canvas = await TestUtils.createComponent('graph-canvas');
        canvas.renderSvg('<svg width="100" height="100"><rect width="100" height="100"/></svg>');
        
        canvas.zoom(2);
        canvas.resetZoom();
        
        const svg = canvas.querySelector('#canvas-area svg');
        assert.ok(svg.style.transform.includes('scale(1)'), 'SVG should have scale(1)');
    });
    
    QUnit.test('canvasArea property is accessible', async function(assert) {
        const canvas = await TestUtils.createComponent('graph-canvas');
        
        assert.ok(canvas.canvasArea, 'canvasArea should be accessible');
        assert.strictEqual(canvas.canvasArea.id, 'canvas-area', 'should be the canvas area element');
    });

});
