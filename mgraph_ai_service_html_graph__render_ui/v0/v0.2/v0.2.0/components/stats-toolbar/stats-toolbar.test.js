/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Test Suite - Stats Toolbar Tests
   v0.2.0 - Consolidated from v0.1.x
   ═══════════════════════════════════════════════════════════════════════════════ */

QUnit.module('Stats Toolbar', function(hooks) {
    
    hooks.before(async function(assert) {
        await TestUtils.loadCss(TestPaths.commonCss);
        await TestUtils.loadScript(TestPaths.statsToolbar);
        assert.ok(customElements.get('stats-toolbar'), 'stats-toolbar should be registered');
    });
    
    hooks.afterEach(function() {
        TestUtils.cleanup();
    });

    QUnit.test('component renders correctly', async function(assert) {
        const toolbar = await TestUtils.createComponent('stats-toolbar');
        
        assert.ok(toolbar.querySelector('.stats-toolbar'), 'should have toolbar container');
        assert.ok(toolbar.querySelector('#render-btn'), 'should have render button');
        assert.ok(toolbar.querySelector('#stat-nodes'), 'should have nodes stat');
        assert.ok(toolbar.querySelector('#stat-edges'), 'should have edges stat');
        assert.ok(toolbar.querySelector('#error-banner'), 'should have error banner');
    });
    
    QUnit.test('render button exists and is clickable', async function(assert) {
        const toolbar = await TestUtils.createComponent('stats-toolbar');
        const button = toolbar.querySelector('#render-btn');
        
        assert.ok(button, 'render button should exist');
        assert.strictEqual(button.disabled, false, 'button should be enabled by default');
        TestUtils.assertContainsText(assert, button, 'Render', 'button should show Render text');
    });
    
    QUnit.test('emits render-requested event on button click', async function(assert) {
        const toolbar = await TestUtils.createComponent('stats-toolbar');
        const button = toolbar.querySelector('#render-btn');
        
        const eventPromise = TestUtils.waitForEvent(toolbar, 'render-requested');
        
        button.click();
        
        const event = await eventPromise;
        assert.ok(event, 'render-requested event should be dispatched');
    });
    
    QUnit.test('setStats updates display values', async function(assert) {
        const toolbar = await TestUtils.createComponent('stats-toolbar');
        
        toolbar.setStats({
            total_nodes: 42,
            total_edges: 38,
            element_nodes: 20,
            attr_nodes: 12,
            text_nodes: 10
        });
        
        assert.strictEqual(toolbar.querySelector('#stat-nodes').textContent, '42', 'nodes should be updated');
        assert.strictEqual(toolbar.querySelector('#stat-edges').textContent, '38', 'edges should be updated');
        assert.strictEqual(toolbar.querySelector('#stat-elements').textContent, '20', 'elements should be updated');
        assert.strictEqual(toolbar.querySelector('#stat-attrs').textContent, '12', 'attrs should be updated');
        assert.strictEqual(toolbar.querySelector('#stat-text').textContent, '10', 'text should be updated');
    });
    
    QUnit.test('setStats formats large numbers', async function(assert) {
        const toolbar = await TestUtils.createComponent('stats-toolbar');
        
        toolbar.setStats({
            total_nodes: 1500,
            total_edges: 2500000
        });
        
        assert.strictEqual(toolbar.querySelector('#stat-nodes').textContent, '1.5K', 'should format thousands as K');
        assert.strictEqual(toolbar.querySelector('#stat-edges').textContent, '2.5M', 'should format millions as M');
    });
    
    QUnit.test('setTiming updates timing display', async function(assert) {
        const toolbar = await TestUtils.createComponent('stats-toolbar');
        
        toolbar.setTiming({
            api_ms: 150,
            server_ms: 50,
            render_ms: 100,
            dot_size: 2048
        });
        
        assert.strictEqual(toolbar.querySelector('#timing-api').textContent, '150ms', 'API timing should be updated');
        assert.strictEqual(toolbar.querySelector('#timing-server').textContent, '50ms', 'server timing should be updated');
        assert.strictEqual(toolbar.querySelector('#timing-render').textContent, '100ms', 'render timing should be updated');
        assert.strictEqual(toolbar.querySelector('#timing-dot-size').textContent, '2.0 KB', 'dot size should be formatted');
    });
    
    QUnit.test('setTiming formats bytes correctly', async function(assert) {
        const toolbar = await TestUtils.createComponent('stats-toolbar');
        
        toolbar.setTiming({ dot_size: 500 });
        assert.strictEqual(toolbar.querySelector('#timing-dot-size').textContent, '500 B', 'small sizes in bytes');
        
        toolbar.setTiming({ dot_size: 1536 });
        assert.strictEqual(toolbar.querySelector('#timing-dot-size').textContent, '1.5 KB', 'KB with decimal');
        
        toolbar.setTiming({ dot_size: 1048576 });
        assert.strictEqual(toolbar.querySelector('#timing-dot-size').textContent, '1.0 MB', 'MB');
    });
    
    QUnit.test('setRenderingState disables button when rendering', async function(assert) {
        const toolbar = await TestUtils.createComponent('stats-toolbar');
        const button = toolbar.querySelector('#render-btn');
        
        toolbar.setRenderingState(true);
        
        assert.strictEqual(button.disabled, true, 'button should be disabled');
        TestUtils.assertContainsText(assert, button, 'Rendering', 'button should show Rendering text');
    });
    
    QUnit.test('setRenderingState enables button when done', async function(assert) {
        const toolbar = await TestUtils.createComponent('stats-toolbar');
        const button = toolbar.querySelector('#render-btn');
        
        toolbar.setRenderingState(true);
        toolbar.setRenderingState(false);
        
        assert.strictEqual(button.disabled, false, 'button should be enabled');
        TestUtils.assertContainsText(assert, button, 'Render', 'button should show Render text again');
    });
    
    QUnit.test('showError displays error banner', async function(assert) {
        const toolbar = await TestUtils.createComponent('stats-toolbar');
        const banner = toolbar.querySelector('#error-banner');
        
        toolbar.showError('Test Error', 'Error details here', 'Helpful hint');
        
        assert.ok(banner.classList.contains('show'), 'banner should be visible');
        TestUtils.assertContainsText(assert, toolbar.querySelector('#error-title'), 'Test Error', 'should show title');
        TestUtils.assertContainsText(assert, toolbar.querySelector('#error-detail'), 'Error details', 'should show detail');
        TestUtils.assertContainsText(assert, toolbar.querySelector('#error-hint'), 'Helpful hint', 'should show hint');
    });
    
    QUnit.test('hideError hides error banner', async function(assert) {
        const toolbar = await TestUtils.createComponent('stats-toolbar');
        const banner = toolbar.querySelector('#error-banner');
        
        toolbar.showError('Test Error', 'Details');
        toolbar.hideError();
        
        assert.notOk(banner.classList.contains('show'), 'banner should be hidden');
    });
    
    QUnit.test('clearStats resets all values', async function(assert) {
        const toolbar = await TestUtils.createComponent('stats-toolbar');
        
        // First set some values
        toolbar.setStats({ total_nodes: 100, total_edges: 50 });
        toolbar.setTiming({ api_ms: 200 });
        toolbar.showError('Error', 'Details');
        
        // Then clear
        toolbar.clearStats();
        
        assert.strictEqual(toolbar.querySelector('#stat-nodes').textContent, '-', 'nodes should show dash');
        assert.strictEqual(toolbar.querySelector('#stat-edges').textContent, '-', 'edges should show dash');
        assert.strictEqual(toolbar.querySelector('#timing-api').textContent, '-', 'timing should show dash');
        assert.notOk(toolbar.querySelector('#error-banner').classList.contains('show'), 'error should be hidden');
    });

});
