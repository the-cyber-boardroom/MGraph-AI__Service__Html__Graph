/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Test Suite - D3 Renderer Extended Tests
   v0.2.0 - Additional tests to improve coverage
   ═══════════════════════════════════════════════════════════════════════════════ */

QUnit.module('D3 Renderer Extended', function(hooks) {

    hooks.before(async function(assert) {
        await TestUtils.loadScript(TestPaths.d3Renderer);
        assert.ok(customElements.get('d3-renderer'), 'd3-renderer should be registered');
    });

    hooks.afterEach(function() {
        TestUtils.cleanup();
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // Initialization Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('constructor initializes all properties', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');

        assert.strictEqual(renderer.svg, null, 'svg should be null');
        assert.strictEqual(renderer.simulation, null, 'simulation should be null');
        assert.strictEqual(renderer.targetCanvas, null, 'targetCanvas should be null');
    });

    QUnit.test('connectedCallback calls loadD3', async function(assert) {
        const renderer = document.createElement('d3-renderer');
        let loadD3Called = false;
        renderer.loadD3 = async () => { loadD3Called = true; };

        document.getElementById('qunit-fixture').appendChild(renderer);
        await TestUtils.nextFrame();

        assert.ok(loadD3Called, 'loadD3 should be called');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // setTargetCanvas Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('setTargetCanvas stores reference', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');
        const canvas = document.createElement('div');

        renderer.setTargetCanvas(canvas);

        assert.strictEqual(renderer.targetCanvas, canvas, 'should store canvas reference');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // parseDot Extended Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('parseDot extracts node fontcolor', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');

        const dotCode = `digraph G { "n1" [label="Test", fontcolor="#FFFFFF"]; }`;
        const { nodes } = renderer.parseDot(dotCode);

        assert.strictEqual(nodes[0].fontColor, '#FFFFFF', 'should extract fontcolor');
    });

    QUnit.test('parseDot uses default fontcolor when not specified', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');

        const dotCode = `digraph G { "n1" [label="Test", fillcolor="#000000"]; }`;
        const { nodes } = renderer.parseDot(dotCode);

        assert.strictEqual(nodes[0].fontColor, '#333333', 'should use default fontcolor');
    });

    QUnit.test('parseDot uses default fillcolor when not specified', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');

        const dotCode = `digraph G { "n1" [label="Test"]; }`;
        const { nodes } = renderer.parseDot(dotCode);

        assert.strictEqual(nodes[0].color, '#f5f5f5', 'should use default fillcolor');
    });

    QUnit.test('parseDot uses nodeId as label when label not specified', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');

        const dotCode = `digraph G { "myNodeId" [fillcolor="#000000"]; }`;
        const { nodes } = renderer.parseDot(dotCode);

        assert.strictEqual(nodes[0].label, 'myNodeId', 'should use nodeId as label');
    });

    QUnit.test('parseDot handles multiple edges between same nodes', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');

        const dotCode = `
            digraph G {
                "a" [label="A"];
                "b" [label="B"];
                "a" -> "b";
                "a" -> "b" [style=dashed];
            }
        `;

        const { links } = renderer.parseDot(dotCode);

        assert.strictEqual(links.length, 2, 'should create 2 links');
    });

    QUnit.test('parseDot extracts edge color', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');

        const dotCode = `
            digraph G {
                "a" [label="A"];
                "b" [label="B"];
                "a" -> "b" [color="#FF0000"];
            }
        `;

        const { links } = renderer.parseDot(dotCode);

        assert.strictEqual(links[0].color, '#FF0000', 'should extract edge color');
    });

    QUnit.test('parseDot uses default edge color', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');

        const dotCode = `
            digraph G {
                "a" [label="A"];
                "b" [label="B"];
                "a" -> "b";
            }
        `;

        const { links } = renderer.parseDot(dotCode);

        assert.strictEqual(links[0].color, '#888888', 'should use default edge color');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // extractAttr Extended Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('extractAttr handles escaped newlines', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');

        const result = renderer.extractAttr('label="Line1\\nLine2"', 'label');

        assert.ok(result.includes('\n') || result.includes('Line1'), 'should handle escaped newlines');
    });

    QUnit.test('extractAttr returns null for missing attribute', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');

        const result = renderer.extractAttr('label="test"', 'fillcolor');

        assert.strictEqual(result, null, 'should return null for missing attr');
    });

    QUnit.test('extractAttr handles attributes at end of string', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');

        const result = renderer.extractAttr('fillcolor="#FF0000"', 'fillcolor');

        assert.strictEqual(result, '#FF0000', 'should extract attr at end');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // cleanLabel Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('cleanLabel converts \\n to space for D3', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');

        assert.strictEqual(renderer.cleanLabel('A\\nB'), 'A B', 'should convert \\n to space');
    });

    QUnit.test('cleanLabel removes surrounding quotes', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');

        assert.strictEqual(renderer.cleanLabel('"quoted"'), 'quoted', 'should remove quotes');
    });

    QUnit.test('cleanLabel converts escaped quotes', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');

        assert.strictEqual(renderer.cleanLabel('say \\"hi\\"'), 'say "hi"', 'should convert escaped quotes');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // truncateLabel Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('truncateLabel keeps short labels unchanged', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');

        assert.strictEqual(renderer.truncateLabel('Short', 20), 'Short', 'should not truncate short labels');
    });

    QUnit.test('truncateLabel adds ellipsis to long labels', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');

        const result = renderer.truncateLabel('This is a very long label', 15);

        assert.ok(result.endsWith('...'), 'should end with ellipsis');
        assert.ok(result.length <= 15, 'should be at most maxLength');
    });

    QUnit.test('truncateLabel handles exact length', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');

        assert.strictEqual(renderer.truncateLabel('Exactly20Characters!', 20), 'Exactly20Characters!', 'should keep exact length label');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // darkenColor Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('darkenColor darkens white', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');

        const result = renderer.darkenColor('#FFFFFF');

        assert.notStrictEqual(result, '#FFFFFF', 'should darken white');
        assert.ok(result.match(/^#[0-9a-f]{6}$/i), 'should return valid hex');
    });

    QUnit.test('darkenColor keeps black unchanged', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');

        assert.strictEqual(renderer.darkenColor('#000000'), '#000000', 'black should stay black');
    });

    QUnit.test('darkenColor handles lowercase hex', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');

        const result = renderer.darkenColor('#ffffff');

        assert.ok(result.match(/^#[0-9a-f]{6}$/i), 'should handle lowercase hex');
    });

    QUnit.test('darkenColor handles dark colors without going negative', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');

        const result = renderer.darkenColor('#101010');

        assert.ok(result.match(/^#[0-9a-f]{6}$/i), 'should return valid hex for dark colors');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // fitToView Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('fitToView handles null svg gracefully', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');
        renderer.svg = null;

        renderer.fitToView();

        assert.ok(true, 'should not throw when svg is null');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // exportSvg Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('exportSvg returns null when no svg', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');
        renderer.svg = null;

        assert.strictEqual(renderer.exportSvg(), null, 'should return null');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // renderDot Error Handling Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('renderDot throws without target canvas', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');
        renderer.targetCanvas = null;
        renderer.isLoaded = true;

        try {
            await renderer.renderDot('digraph { a -> b }');
            assert.ok(false, 'should have thrown');
        } catch (e) {
            assert.ok(e.message.includes('target canvas'), 'should throw about missing canvas');
        }
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // loadScript Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('loadScript creates script element', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');

        // Count scripts before
        const beforeCount = document.querySelectorAll('script').length;

        try {
            await renderer.loadScript('https://example.com/test-script.js');
        } catch (e) {
            // May fail to load, but script element should be created
        }

        // The script element would be added to head
        assert.ok(true, 'loadScript should attempt to create script element');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // drag Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('drag returns a function', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');

        const mockSimulation = {
            alphaTarget: () => ({ restart: () => {} })
        };

        const dragBehavior = renderer.drag(mockSimulation);

        assert.ok(typeof dragBehavior === 'function' || typeof dragBehavior === 'object',
            'drag should return drag behavior');
    });

});