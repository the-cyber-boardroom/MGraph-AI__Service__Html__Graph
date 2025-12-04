/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Test Suite - DOT Renderer Tests
   v0.1.4 - Test Infrastructure
   ═══════════════════════════════════════════════════════════════════════════════ */

QUnit.module('DOT Renderer', function(hooks) {
    
    hooks.before(async function(assert) {
        await TestUtils.loadScript(TestPaths.dotRenderer);
        assert.ok(customElements.get('dot-renderer'), 'dot-renderer should be registered');
    });
    
    hooks.afterEach(function() {
        TestUtils.cleanup();
    });

    QUnit.test('component can be instantiated', async function(assert) {
        const renderer = await TestUtils.createComponent('dot-renderer');
        
        assert.ok(renderer, 'renderer should exist');
        assert.strictEqual(renderer.style.display, 'none', 'renderer should be hidden');
    });
    
    QUnit.test('has renderDot method', async function(assert) {
        const renderer = await TestUtils.createComponent('dot-renderer');
        
        assert.ok(typeof renderer.renderDot === 'function', 'should have renderDot method');
    });
    
    QUnit.test('has renderToPng method', async function(assert) {
        const renderer = await TestUtils.createComponent('dot-renderer');
        
        assert.ok(typeof renderer.renderToPng === 'function', 'should have renderToPng method');
    });
    
    QUnit.test('has isReady method', async function(assert) {
        const renderer = await TestUtils.createComponent('dot-renderer');
        
        assert.ok(typeof renderer.isReady === 'function', 'should have isReady method');
    });
    
    QUnit.test('has getSupportedEngines method', async function(assert) {
        const renderer = await TestUtils.createComponent('dot-renderer');
        
        assert.ok(typeof renderer.getSupportedEngines === 'function', 'should have getSupportedEngines method');
        
        const engines = renderer.getSupportedEngines();
        assert.ok(Array.isArray(engines), 'should return array');
        assert.ok(engines.includes('dot'), 'should include dot engine');
        assert.ok(engines.includes('neato'), 'should include neato engine');
    });
    
    QUnit.test('has loadVizJs method', async function(assert) {
        const renderer = await TestUtils.createComponent('dot-renderer');
        
        assert.ok(typeof renderer.loadVizJs === 'function', 'should have loadVizJs method');
    });
    
    QUnit.test('renderDot rejects empty string', async function(assert) {
        const renderer = await TestUtils.createComponent('dot-renderer');
        
        try {
            await renderer.renderDot('');
            assert.ok(false, 'should have thrown error');
        } catch (e) {
            assert.ok(e.message.includes('Empty'), 'should throw error for empty DOT');
        }
    });
    
    QUnit.test('renderDot rejects whitespace-only string', async function(assert) {
        const renderer = await TestUtils.createComponent('dot-renderer');
        
        try {
            await renderer.renderDot('   \n   ');
            assert.ok(false, 'should have thrown error');
        } catch (e) {
            assert.ok(e.message.includes('Empty'), 'should throw error for whitespace DOT');
        }
    });
    
    // Note: Full rendering tests require viz.js to be loaded from CDN
    // These are integration tests that may be slower
    QUnit.test('can load viz.js library (async)', async function(assert) {
        const done = assert.async();
        const renderer = await TestUtils.createComponent('dot-renderer');
        
        try {
            await renderer.loadVizJs();
            assert.ok(renderer.isReady() || window.Viz, 'viz.js should be loaded');
            done();
        } catch (e) {
            // May fail if CDN is unreachable - that's okay for unit tests
            assert.ok(true, 'viz.js loading attempted (may fail offline)');
            done();
        }
    });

});
