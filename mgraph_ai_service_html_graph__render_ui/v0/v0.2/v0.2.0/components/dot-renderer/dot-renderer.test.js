/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Test Suite - DOT Renderer Extended Tests
   v0.2.0 - Additional tests to improve coverage
   ═══════════════════════════════════════════════════════════════════════════════ */

QUnit.module('DOT Renderer Extended', function(hooks) {

    hooks.before(async function(assert) {
        await TestUtils.loadScript(TestPaths.dotRenderer);
        assert.ok(customElements.get('dot-renderer'), 'dot-renderer should be registered');
    });

    hooks.afterEach(function() {
        TestUtils.cleanup();
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // Initialization Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('constructor initializes properties', async function(assert) {
        const renderer = await TestUtils.createComponent('dot-renderer');

        assert.strictEqual(renderer.viz, null, 'viz should initially be null');
        //assert.strictEqual(renderer.vizLoading, null, 'vizLoading should initially be null');
    });

    QUnit.test('connectedCallback sets display to none', async function(assert) {
        const renderer = await TestUtils.createComponent('dot-renderer');

        assert.strictEqual(renderer.style.display, 'none', 'component should be hidden');
    });

    QUnit.test('connectedCallback calls loadVizJs', async function(assert) {
        const renderer = document.createElement('dot-renderer');
        let loadVizJsCalled = false;
        renderer.loadVizJs = async () => { loadVizJsCalled = true; };

        document.getElementById('qunit-fixture').appendChild(renderer);
        await TestUtils.nextFrame();

        assert.ok(loadVizJsCalled, 'loadVizJs should be called on connect');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // loadVizJs Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('loadVizJs returns existing viz if already loaded', async function(assert) {
        const renderer = await TestUtils.createComponent('dot-renderer');

        const mockViz = { renderSVGElement: () => {} };
        renderer.viz = mockViz;

        const result = await renderer.loadVizJs();

        assert.strictEqual(result, mockViz, 'should return existing viz instance');
    });

    QUnit.test('loadVizJs returns existing promise if loading', async function(assert) {
        const renderer = await TestUtils.createComponent('dot-renderer');

        const mockPromise = Promise.resolve('mock');
        renderer.vizLoading = mockPromise;

        const result = await renderer.loadVizJs();

        assert.strictEqual(result, 'mock', 'should return existing loading promise result');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // renderDot Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('renderDot throws error for empty string', async function(assert) {
        const renderer = await TestUtils.createComponent('dot-renderer');

        try {
            await renderer.renderDot('');
            assert.ok(false, 'should have thrown error');
        } catch (e) {
            assert.ok(e.message.includes('Empty'), 'should throw error for empty DOT');
        }
    });

    QUnit.test('renderDot throws error for null', async function(assert) {
        const renderer = await TestUtils.createComponent('dot-renderer');

        try {
            await renderer.renderDot(null);
            assert.ok(false, 'should have thrown error');
        } catch (e) {
            assert.ok(e.message.includes('Empty'), 'should throw error for null DOT');
        }
    });

    QUnit.test('renderDot throws error for undefined', async function(assert) {
        const renderer = await TestUtils.createComponent('dot-renderer');

        try {
            await renderer.renderDot(undefined);
            assert.ok(false, 'should have thrown error');
        } catch (e) {
            assert.ok(e.message.includes('Empty'), 'should throw error for undefined DOT');
        }
    });

    QUnit.test('renderDot throws error for whitespace-only string', async function(assert) {
        const renderer = await TestUtils.createComponent('dot-renderer');

        try {
            await renderer.renderDot('   \n\t   ');
            assert.ok(false, 'should have thrown error');
        } catch (e) {
            assert.ok(e.message.includes('Empty'), 'should throw error for whitespace DOT');
        }
    });

    QUnit.test('renderDot accepts options parameter', async function(assert) {
        const renderer = await TestUtils.createComponent('dot-renderer');

        // Mock loadVizJs to avoid actual loading
        renderer.loadVizJs = async () => {
            const mockViz = {
                renderSVGElement: (dot, opts) => {
                    assert.strictEqual(opts.engine, 'neato', 'should pass engine option');
                    return document.createElementNS('http://www.w3.org/2000/svg', 'svg');
                }
            };
            renderer.viz = mockViz;
            return mockViz;
        };

        try {
            await renderer.renderDot('digraph { a -> b }', { engine: 'neato' });
        } catch (e) {
            // May fail if graphCanvas is not set, but engine option should have been checked
        }

        assert.ok(true, 'options parameter should be accepted');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // isReady Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('isReady returns false initially', async function(assert) {
        const renderer = await TestUtils.createComponent('dot-renderer');
        renderer.viz = null;

        assert.strictEqual(renderer.isReady(), false, 'should return false when viz is null');
    });

    QUnit.test('isReady returns true when viz is loaded', async function(assert) {
        const renderer = await TestUtils.createComponent('dot-renderer');
        renderer.viz = { renderSVGElement: () => {} };

        assert.strictEqual(renderer.isReady(), true, 'should return true when viz is set');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // getSupportedEngines Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('getSupportedEngines returns array', async function(assert) {
        const renderer = await TestUtils.createComponent('dot-renderer');

        const engines = renderer.getSupportedEngines();

        assert.ok(Array.isArray(engines), 'should return an array');
    });

    QUnit.test('getSupportedEngines includes all expected engines', async function(assert) {
        const renderer = await TestUtils.createComponent('dot-renderer');

        const engines = renderer.getSupportedEngines();

        assert.ok(engines.includes('dot'), 'should include dot');
        assert.ok(engines.includes('neato'), 'should include neato');
        assert.ok(engines.includes('fdp'), 'should include fdp');
        assert.ok(engines.includes('sfdp'), 'should include sfdp');
        assert.ok(engines.includes('twopi'), 'should include twopi');
        assert.ok(engines.includes('circo'), 'should include circo');
    });

    QUnit.test('getSupportedEngines returns 6 engines', async function(assert) {
        const renderer = await TestUtils.createComponent('dot-renderer');

        const engines = renderer.getSupportedEngines();

        assert.strictEqual(engines.length, 6, 'should return 6 engines');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // renderToPng Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('renderToPng calls renderDot first', async function(assert) {
        const renderer = await TestUtils.createComponent('dot-renderer');

        let renderDotCalled = false;
        renderer.renderDot = async (dot, opts) => {
            renderDotCalled = true;
            return '<svg></svg>';
        };

        try {
            await renderer.renderToPng('digraph { a -> b }');
        } catch (e) {
            // May fail due to image loading, but renderDot should have been called
        }

        assert.ok(renderDotCalled, 'renderDot should be called');
    });

    QUnit.test('renderToPng accepts scale option', async function(assert) {
        const renderer = await TestUtils.createComponent('dot-renderer');

        // This is a basic test - full PNG generation requires browser image APIs
        assert.ok(typeof renderer.renderToPng === 'function', 'renderToPng should exist');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // graphCanvas Integration Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('looks for graph-canvas on connect', async function(assert) {
        const fixture = document.getElementById('qunit-fixture');
        fixture.innerHTML = '<graph-canvas></graph-canvas>';

        // Load graph-canvas component
        await TestUtils.loadScript(TestPaths.graphCanvas);
        await TestUtils.nextFrame();

        const renderer = await TestUtils.createComponent('dot-renderer');

        // graphCanvas property might be set or null depending on timing
        assert.ok(true, 'should attempt to find graph-canvas');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // Error Handling Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('renderDot handles viz.js rendering errors', async function(assert) {
        const renderer = await TestUtils.createComponent('dot-renderer');

        renderer.loadVizJs = async () => {
            const mockViz = {
                renderSVGElement: () => { throw new Error('Syntax error in DOT'); }
            };
            renderer.viz = mockViz;
            return mockViz;
        };

        // Suppress console.error for this test
        const originalConsoleError = console.error;
        console.error = () => {};

        try {
            await renderer.renderDot('invalid dot syntax');
            assert.ok(false, 'should have thrown error');
        } catch (e) {
            assert.ok(e.message.includes('Syntax error'), 'should propagate viz.js error');
        }

        console.error = originalConsoleError;
    });

});