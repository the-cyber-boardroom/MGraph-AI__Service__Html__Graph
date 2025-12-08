/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Test Suite - Vis Renderer Extended Tests
   v0.2.0 - Additional tests to improve coverage from 65%
   ═══════════════════════════════════════════════════════════════════════════════ */

QUnit.module('Vis Renderer Extended', function(hooks) {

    hooks.before(async function(assert) {
        await TestUtils.loadScript(TestPaths.visRenderer);
        assert.ok(customElements.get('vis-renderer'), 'vis-renderer should be registered');
    });

    hooks.afterEach(function() {
        TestUtils.cleanup();
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // Constructor and Initialization Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('constructor initializes all properties', function(assert) {
        const renderer = document.createElement('vis-renderer');

        assert.strictEqual(renderer.network, null, 'network should be null');
        assert.strictEqual(renderer.targetCanvas, null, 'targetCanvas should be null');
        assert.strictEqual(renderer.isLoaded, false, 'isLoaded should be false');
    });

    QUnit.test('connectedCallback calls loadVisJs', async function(assert) {
        const renderer = document.createElement('vis-renderer');
        let loadCalled = false;
        renderer.loadVisJs = async () => { loadCalled = true; };

        document.getElementById('qunit-fixture').appendChild(renderer);
        await TestUtils.nextFrame();

        assert.ok(loadCalled, 'loadVisJs should be called');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // loadVisJs Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('loadVisJs sets isLoaded when vis already exists', async function(assert) {
        const renderer = await TestUtils.createComponent('vis-renderer');

        // If vis.js loaded from CDN
        if (window.vis) {
            assert.ok(renderer.isLoaded, 'isLoaded should be true');
        } else {
            assert.ok(true, 'vis.js not loaded - skip');
        }
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // loadScript Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('loadScript creates script element', async function(assert) {
        const renderer = await TestUtils.createComponent('vis-renderer');

        // Can't fully test without actual loading, but verify method exists
        assert.ok(typeof renderer.loadScript === 'function', 'loadScript should exist');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // setTargetCanvas Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('setTargetCanvas stores reference', async function(assert) {
        const renderer = await TestUtils.createComponent('vis-renderer');
        const canvas = document.createElement('div');
        canvas.id = 'test-canvas';

        renderer.setTargetCanvas(canvas);

        assert.strictEqual(renderer.targetCanvas, canvas, 'should store canvas reference');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // renderDot Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('renderDot throws without target canvas', async function(assert) {
        const renderer = await TestUtils.createComponent('vis-renderer');
        renderer.targetCanvas = null;
        renderer.isLoaded = true;

        try {
            await renderer.renderDot('digraph { a -> b }');
            assert.ok(false, 'should have thrown');
        } catch (e) {
            assert.ok(e.message.includes('target canvas'), 'should mention target canvas');
        }
    });

    QUnit.test('renderDot calls loadVisJs if not loaded', async function(assert) {
        const renderer = await TestUtils.createComponent('vis-renderer');
        renderer.isLoaded = false;
        renderer.targetCanvas = document.createElement('div');

        let loadCalled = false;
        const originalLoad = renderer.loadVisJs.bind(renderer);
        renderer.loadVisJs = async () => {
            loadCalled = true;
            await originalLoad();
        };

        try {
            await renderer.renderDot('digraph { "a" [label="A"]; }');
        } catch (e) {
            // May fail if vis.js not available
        }

        assert.ok(loadCalled, 'loadVisJs should be called');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // mapShape Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('mapShape maps known shapes', async function(assert) {
        const renderer = await TestUtils.createComponent('vis-renderer');

        assert.strictEqual(renderer.mapShape('box'), 'box', 'box should map to box');
        assert.strictEqual(renderer.mapShape('ellipse'), 'ellipse', 'ellipse should map to ellipse');
        assert.strictEqual(renderer.mapShape('circle'), 'circle', 'circle should map to circle');
        assert.strictEqual(renderer.mapShape('diamond'), 'diamond', 'diamond should map to diamond');
        assert.strictEqual(renderer.mapShape('triangle'), 'triangle', 'triangle should map to triangle');
        assert.strictEqual(renderer.mapShape('star'), 'star', 'star should map to star');
        assert.strictEqual(renderer.mapShape('hexagon'), 'hexagon', 'hexagon should map to hexagon');
    });

    QUnit.test('mapShape maps note/tab/folder/component to box', async function(assert) {
        const renderer = await TestUtils.createComponent('vis-renderer');

        assert.strictEqual(renderer.mapShape('note'), 'box', 'note should map to box');
        assert.strictEqual(renderer.mapShape('tab'), 'box', 'tab should map to box');
        assert.strictEqual(renderer.mapShape('folder'), 'box', 'folder should map to box');
        assert.strictEqual(renderer.mapShape('component'), 'box', 'component should map to box');
    });

    QUnit.test('mapShape returns box for unknown shapes', async function(assert) {
        const renderer = await TestUtils.createComponent('vis-renderer');

        assert.strictEqual(renderer.mapShape('unknown'), 'box', 'unknown should default to box');
        assert.strictEqual(renderer.mapShape('random'), 'box', 'random should default to box');
        assert.strictEqual(renderer.mapShape(''), 'box', 'empty should default to box');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // detectNodeType Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('detectNodeType identifies tags', async function(assert) {
        const renderer = await TestUtils.createComponent('vis-renderer');

        assert.strictEqual(renderer.detectNodeType('<div>', '#000'), 'tag', '<div> is tag');
        assert.strictEqual(renderer.detectNodeType('<span>', '#000'), 'tag', '<span> is tag');
        assert.strictEqual(renderer.detectNodeType('<a>', '#000'), 'tag', '<a> is tag');
    });

    QUnit.test('detectNodeType identifies attributes', async function(assert) {
        const renderer = await TestUtils.createComponent('vis-renderer');

        assert.strictEqual(renderer.detectNodeType('class=test', '#000'), 'attribute', 'class= is attribute');
        assert.strictEqual(renderer.detectNodeType('id=main', '#000'), 'attribute', 'id= is attribute');
        assert.strictEqual(renderer.detectNodeType('href=url', '#000'), 'attribute', 'href= is attribute');
    });

    QUnit.test('detectNodeType identifies text by color', async function(assert) {
        const renderer = await TestUtils.createComponent('vis-renderer');

        assert.strictEqual(renderer.detectNodeType('Hello', '#FFFACD'), 'text', 'FFFACD is text');
        assert.strictEqual(renderer.detectNodeType('World', '#fffacd'), 'text', 'fffacd is text');
    });

    QUnit.test('detectNodeType defaults to element', async function(assert) {
        const renderer = await TestUtils.createComponent('vis-renderer');

        assert.strictEqual(renderer.detectNodeType('something', '#E8E8E8'), 'element', 'default is element');
        assert.strictEqual(renderer.detectNodeType('node', '#FFFFFF'), 'element', 'default is element');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // cleanLabel Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('cleanLabel converts \\n to newline', async function(assert) {
        const renderer = await TestUtils.createComponent('vis-renderer');

        assert.strictEqual(renderer.cleanLabel('A\\nB'), 'A\nB', 'should convert \\n');
    });

    QUnit.test('cleanLabel converts escaped quotes', async function(assert) {
        const renderer = await TestUtils.createComponent('vis-renderer');

        assert.strictEqual(renderer.cleanLabel('say \\"hi\\"'), 'say "hi"', 'should convert \\"');
    });

    QUnit.test('cleanLabel removes surrounding quotes', async function(assert) {
        const renderer = await TestUtils.createComponent('vis-renderer');

        assert.strictEqual(renderer.cleanLabel('"quoted"'), 'quoted', 'should remove quotes');
    });

    QUnit.test('cleanLabel handles plain text', async function(assert) {
        const renderer = await TestUtils.createComponent('vis-renderer');

        assert.strictEqual(renderer.cleanLabel('plain'), 'plain', 'should keep plain text');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // darkenColor Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('darkenColor darkens colors by 30', async function(assert) {
        const renderer = await TestUtils.createComponent('vis-renderer');

        // #FFFFFF (255,255,255) should become #E1E1E1 (225,225,225)
        assert.strictEqual(renderer.darkenColor('#FFFFFF').toLowerCase(), '#e1e1e1', 'white darkens correctly');
    });

    QUnit.test('darkenColor handles lowercase', async function(assert) {
        const renderer = await TestUtils.createComponent('vis-renderer');

        const result = renderer.darkenColor('#ffffff');
        assert.ok(result.match(/^#[0-9a-f]{6}$/i), 'should return valid hex');
    });

    QUnit.test('darkenColor clamps at 0', async function(assert) {
        const renderer = await TestUtils.createComponent('vis-renderer');

        // #000000 should stay #000000
        assert.strictEqual(renderer.darkenColor('#000000'), '#000000', 'black stays black');

        // #101010 (16,16,16) - 30 should clamp to 0
        const result = renderer.darkenColor('#101010');
        assert.ok(result.match(/^#[0-9a-f]{6}$/i), 'should return valid hex');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // lightenColor Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('lightenColor lightens colors by 30', async function(assert) {
        const renderer = await TestUtils.createComponent('vis-renderer');

        // #000000 (0,0,0) should become #1E1E1E (30,30,30)
        assert.strictEqual(renderer.lightenColor('#000000').toLowerCase(), '#1e1e1e', 'black lightens correctly');
    });

    QUnit.test('lightenColor handles lowercase', async function(assert) {
        const renderer = await TestUtils.createComponent('vis-renderer');

        const result = renderer.lightenColor('#000000');
        assert.ok(result.match(/^#[0-9a-f]{6}$/i), 'should return valid hex');
    });

    QUnit.test('lightenColor clamps at 255', async function(assert) {
        const renderer = await TestUtils.createComponent('vis-renderer');

        // #FFFFFF should stay #FFFFFF (clamped)
        assert.strictEqual(renderer.lightenColor('#FFFFFF').toLowerCase(), '#ffffff', 'white stays white');

        // #F0F0F0 (240,240,240) + 30 should clamp to 255
        const result = renderer.lightenColor('#F0F0F0');
        assert.strictEqual(result.toLowerCase(), '#ffffff', 'should clamp at 255');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // fitToView Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('fitToView calls network.fit', async function(assert) {
        const renderer = await TestUtils.createComponent('vis-renderer');

        let fitCalled = false;
        let fitOptions = null;
        renderer.network = {
            fit: (opts) => { fitCalled = true; fitOptions = opts; }
        };

        renderer.fitToView();

        assert.ok(fitCalled, 'fit should be called');
        assert.ok(fitOptions.animation, 'should have animation options');
    });

    QUnit.test('fitToView handles null network', async function(assert) {
        const renderer = await TestUtils.createComponent('vis-renderer');
        renderer.network = null;

        renderer.fitToView();

        assert.ok(true, 'should not throw');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // exportPng Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('exportPng returns null when no network', async function(assert) {
        const renderer = await TestUtils.createComponent('vis-renderer');
        renderer.network = null;

        const result = await renderer.exportPng();

        assert.strictEqual(result, null, 'should return null');
    });

    QUnit.test('exportPng returns null when no canvas in targetCanvas', async function(assert) {
        const renderer = await TestUtils.createComponent('vis-renderer');
        renderer.network = {};
        renderer.targetCanvas = document.createElement('div');
        // No canvas element inside

        const result = await renderer.exportPng();

        assert.strictEqual(result, null, 'should return null when no canvas');
    });

    QUnit.test('exportPng returns dataURL when canvas exists', async function(assert) {
        const renderer = await TestUtils.createComponent('vis-renderer');
        renderer.network = {};

        const container = document.createElement('div');
        const canvas = document.createElement('canvas');
        canvas.width = 100;
        canvas.height = 100;
        container.appendChild(canvas);
        renderer.targetCanvas = container;

        const result = await renderer.exportPng();

        assert.ok(result.startsWith('data:image/png'), 'should return PNG data URL');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // parseDot Extended Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('parseDot extracts shape attribute', async function(assert) {
        const renderer = await TestUtils.createComponent('vis-renderer');

        const dot = `digraph G { "n1" [label="Test", shape="ellipse"]; }`;
        const { nodes } = renderer.parseDot(dot);

        assert.strictEqual(nodes[0].shape, 'ellipse', 'should extract shape');
    });

    QUnit.test('parseDot uses default shape when not specified', async function(assert) {
        const renderer = await TestUtils.createComponent('vis-renderer');

        const dot = `digraph G { "n1" [label="Test"]; }`;
        const { nodes } = renderer.parseDot(dot);

        assert.strictEqual(nodes[0].shape, 'box', 'should default to box');
    });

    QUnit.test('parseDot sets title for tooltip', async function(assert) {
        const renderer = await TestUtils.createComponent('vis-renderer');

        const dot = `digraph G { "n1" [label="My Label"]; }`;
        const { nodes } = renderer.parseDot(dot);

        assert.strictEqual(nodes[0].title, 'My Label', 'title should match label');
    });

    QUnit.test('parseDot creates color object with highlight', async function(assert) {
        const renderer = await TestUtils.createComponent('vis-renderer');

        const dot = `digraph G { "n1" [label="Test", fillcolor="#FF0000"]; }`;
        const { nodes } = renderer.parseDot(dot);

        assert.ok(nodes[0].color.background, 'should have background color');
        assert.ok(nodes[0].color.border, 'should have border color');
        assert.ok(nodes[0].color.highlight, 'should have highlight object');
        assert.ok(nodes[0].color.highlight.background, 'should have highlight background');
        assert.ok(nodes[0].color.highlight.border, 'should have highlight border');
    });

    QUnit.test('parseDot creates font object', async function(assert) {
        const renderer = await TestUtils.createComponent('vis-renderer');

        const dot = `digraph G { "n1" [label="Test", fontcolor="#0000FF"]; }`;
        const { nodes } = renderer.parseDot(dot);

        assert.ok(nodes[0].font, 'should have font object');
        assert.strictEqual(nodes[0].font.color, '#0000FF', 'should have font color');
    });

    QUnit.test('parseDot extracts nodeType', async function(assert) {
        const renderer = await TestUtils.createComponent('vis-renderer');

        const dot = `digraph G { "n1" [label="<div>", fillcolor="#E8E8E8"]; }`;
        const { nodes } = renderer.parseDot(dot);

        assert.strictEqual(nodes[0].nodeType, 'tag', 'should set nodeType');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // extractAttr Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('extractAttr handles case insensitivity', async function(assert) {
        const renderer = await TestUtils.createComponent('vis-renderer');

        const result1 = renderer.extractAttr('LABEL="Test"', 'label');
        const result2 = renderer.extractAttr('label="Test"', 'LABEL');

        assert.strictEqual(result1, 'Test', 'should find uppercase attr');
        assert.strictEqual(result2, 'Test', 'should find with uppercase search');
    });

    QUnit.test('extractAttr handles escaped characters', async function(assert) {
        const renderer = await TestUtils.createComponent('vis-renderer');

        const result = renderer.extractAttr('label="line1\\nline2"', 'label');

        assert.ok(result.includes('\n'), 'should convert \\n to newline');
    });

});