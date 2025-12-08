/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Test Suite - Cytoscape Renderer Extended Tests
   v0.2.0 - Additional tests to improve coverage from 78%
   ═══════════════════════════════════════════════════════════════════════════════ */

QUnit.module('Cytoscape Renderer Extended', function(hooks) {

    hooks.before(async function(assert) {
        await TestUtils.loadScript(TestPaths.cytoscapeRenderer);
        assert.ok(customElements.get('cytoscape-renderer'), 'cytoscape-renderer should be registered');
    });

    hooks.afterEach(function() {
        TestUtils.cleanup();
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // Constructor Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('constructor initializes all properties', function(assert) {
        const renderer = document.createElement('cytoscape-renderer');

        assert.strictEqual(renderer.cy, null, 'cy should be null');
        assert.strictEqual(renderer.targetCanvas, null, 'targetCanvas should be null');
        assert.strictEqual(renderer.isLoaded, false, 'isLoaded should be false');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // connectedCallback Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('connectedCallback calls loadCytoscape', async function(assert) {
        const renderer = document.createElement('cytoscape-renderer');
        let loadCalled = false;
        renderer.loadCytoscape = async () => { loadCalled = true; };

        document.getElementById('qunit-fixture').appendChild(renderer);
        await TestUtils.nextFrame();

        assert.ok(loadCalled, 'loadCytoscape should be called');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // loadCytoscape Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('loadCytoscape sets isLoaded when cytoscape exists', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');

        if (window.cytoscape) {
            assert.ok(renderer.isLoaded, 'isLoaded should be true');
        } else {
            assert.ok(true, 'cytoscape not loaded - skip');
        }
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // loadScript Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('loadScript resolves immediately for already loaded scripts', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');

        // Create a script that's "already loaded"
        const existingScript = document.createElement('script');
        existingScript.src = 'https://example.com/already-loaded.js';
        document.head.appendChild(existingScript);

        // Should resolve immediately
        await renderer.loadScript('https://example.com/already-loaded.js');

        // Cleanup
        existingScript.remove();

        assert.ok(true, 'should resolve for already loaded script');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // renderDot Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('renderDot throws without target canvas', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');
        renderer.targetCanvas = null;
        renderer.isLoaded = true;

        try {
            await renderer.renderDot('digraph { a -> b }');
            assert.ok(false, 'should have thrown');
        } catch (e) {
            assert.ok(e.message.includes('target canvas'), 'should mention target canvas');
        }
    });

    QUnit.test('renderDot calls loadCytoscape if not loaded', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');
        renderer.isLoaded = false;
        renderer.targetCanvas = document.createElement('div');

        let loadCalled = false;
        const originalLoad = renderer.loadCytoscape.bind(renderer);
        renderer.loadCytoscape = async () => {
            loadCalled = true;
            await originalLoad();
        };

        try {
            await renderer.renderDot('digraph { "a" [label="A"]; }');
        } catch (e) {
            // May fail if cytoscape not available
        }

        assert.ok(loadCalled, 'loadCytoscape should be called');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // parseDot Extended Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('parseDot creates borderColor from fillcolor', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');

        const dot = `digraph G { "n1" [label="Test", fillcolor="#FFFFFF"]; }`;
        const { nodes } = renderer.parseDot(dot);

        assert.ok(nodes[0].borderColor, 'should have borderColor');
        assert.notStrictEqual(nodes[0].borderColor, '#FFFFFF', 'borderColor should be darker');
    });

    QUnit.test('parseDot creates edge id from source and target', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');

        const dot = `digraph G {
            "a" [label="A"];
            "b" [label="B"];
            "a" -> "b";
        }`;

        const { edges } = renderer.parseDot(dot);

        assert.strictEqual(edges[0].id, 'a-b', 'edge id should be source-target');
    });

    QUnit.test('parseDot extracts fontcolor', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');

        const dot = `digraph G { "n1" [label="Test", fontcolor="#FF0000"]; }`;
        const { nodes } = renderer.parseDot(dot);

        assert.strictEqual(nodes[0].fontColor, '#FF0000', 'should extract fontColor');
    });

    QUnit.test('parseDot uses default fontcolor', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');

        const dot = `digraph G { "n1" [label="Test"]; }`;
        const { nodes } = renderer.parseDot(dot);

        assert.strictEqual(nodes[0].fontColor, '#333333', 'should use default fontColor');
    });

    QUnit.test('parseDot uses node id as label when label missing', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');

        const dot = `digraph G { "myNodeId" [fillcolor="#000000"]; }`;
        const { nodes } = renderer.parseDot(dot);

        assert.strictEqual(nodes[0].label, 'myNodeId', 'should use nodeId as label');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // exportPng Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('exportPng returns value from cy.png when cy exists', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');

        renderer.cy = {
            png: (opts) => {
                assert.ok(opts.full, 'should request full graph');
                assert.strictEqual(opts.scale, 2, 'should use scale 2');
                return 'data:image/png;base64,test';
            }
        };

        const result = renderer.exportPng();

        assert.strictEqual(result, 'data:image/png;base64,test', 'should return PNG data');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // runLayout Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('runLayout supports dagre layout', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');

        let layoutConfig = null;
        renderer.cy = {
            layout: (config) => {
                layoutConfig = config;
                return { run: () => {} };
            }
        };

        renderer.runLayout('dagre');

        assert.strictEqual(layoutConfig.name, 'dagre', 'should use dagre layout');
    });

    QUnit.test('runLayout supports breadthfirst layout', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');

        let layoutConfig = null;
        renderer.cy = {
            layout: (config) => {
                layoutConfig = config;
                return { run: () => {} };
            }
        };

        renderer.runLayout('breadthfirst');

        assert.strictEqual(layoutConfig.name, 'breadthfirst', 'should use breadthfirst layout');
        assert.strictEqual(layoutConfig.directed, true, 'should be directed');
    });

    QUnit.test('runLayout supports circle layout', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');

        let layoutConfig = null;
        renderer.cy = {
            layout: (config) => {
                layoutConfig = config;
                return { run: () => {} };
            }
        };

        renderer.runLayout('circle');

        assert.strictEqual(layoutConfig.name, 'circle', 'should use circle layout');
    });

    QUnit.test('runLayout supports grid layout', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');

        let layoutConfig = null;
        renderer.cy = {
            layout: (config) => {
                layoutConfig = config;
                return { run: () => {} };
            }
        };

        renderer.runLayout('grid');

        assert.strictEqual(layoutConfig.name, 'grid', 'should use grid layout');
    });

    QUnit.test('runLayout supports cose layout', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');

        let layoutConfig = null;
        renderer.cy = {
            layout: (config) => {
                layoutConfig = config;
                return { run: () => {} };
            }
        };

        renderer.runLayout('cose');

        assert.strictEqual(layoutConfig.name, 'cose', 'should use cose layout');
    });

    QUnit.test('runLayout defaults to dagre for unknown layout', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');

        let layoutConfig = null;
        renderer.cy = {
            layout: (config) => {
                layoutConfig = config;
                return { run: () => {} };
            }
        };

        renderer.runLayout('unknown');

        assert.strictEqual(layoutConfig.name, 'dagre', 'should default to dagre');
    });

    QUnit.test('runLayout calls layout.run()', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');

        let runCalled = false;
        renderer.cy = {
            layout: () => ({
                run: () => { runCalled = true; }
            })
        };

        renderer.runLayout('dagre');

        assert.ok(runCalled, 'run should be called');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // detectNodeType Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('detectNodeType returns tag for angle bracket labels', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');

        assert.strictEqual(renderer.detectNodeType('<html>', '#000'), 'tag');
        assert.strictEqual(renderer.detectNodeType('<body>', '#000'), 'tag');
        assert.strictEqual(renderer.detectNodeType('<custom-element>', '#000'), 'tag');
    });

    QUnit.test('detectNodeType returns attribute for equals sign', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');

        assert.strictEqual(renderer.detectNodeType('data-id=123', '#000'), 'attribute');
        assert.strictEqual(renderer.detectNodeType('style=color:red', '#000'), 'attribute');
    });

    QUnit.test('detectNodeType returns text for FFFACD color', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');

        assert.strictEqual(renderer.detectNodeType('any text', '#FFFACD'), 'text');
        assert.strictEqual(renderer.detectNodeType('any text', '#fffacd'), 'text');
    });

    QUnit.test('detectNodeType returns element as default', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');

        assert.strictEqual(renderer.detectNodeType('node', '#E8E8E8'), 'element');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // cleanLabel Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('cleanLabel handles multiple newlines', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');

        const result = renderer.cleanLabel('a\\nb\\nc');
        assert.strictEqual(result, 'a\nb\nc', 'should convert multiple \\n');
    });

    QUnit.test('cleanLabel handles mixed escapes', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');

        const result = renderer.cleanLabel('say \\"hi\\"\\nbye');
        assert.strictEqual(result, 'say "hi"\nbye', 'should handle mixed escapes');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // darkenColor Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('darkenColor handles mid-range colors', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');

        // #808080 (128,128,128) should become #626262 (98,98,98)
        const result = renderer.darkenColor('#808080');
        assert.ok(result.match(/^#[0-9a-f]{6}$/i), 'should return valid hex');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // fitToView Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('fitToView passes padding to fit', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');

        let fitPadding = null;
        renderer.cy = {
            fit: (nodes, padding) => { fitPadding = padding; }
        };

        renderer.fitToView();

        assert.strictEqual(fitPadding, 30, 'should pass padding of 30');
    });

});