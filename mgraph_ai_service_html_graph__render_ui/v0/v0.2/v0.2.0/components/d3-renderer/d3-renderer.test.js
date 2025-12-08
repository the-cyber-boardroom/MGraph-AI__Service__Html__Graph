/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Test Suite - D3 Renderer Tests
   v0.2.0 - Consolidated from v0.1.x
   ═══════════════════════════════════════════════════════════════════════════════ */

QUnit.module('D3 Renderer', function(hooks) {
    
    hooks.before(async function(assert) {
        await TestUtils.loadScript(TestPaths.d3Renderer);
        assert.ok(customElements.get('d3-renderer'), 'd3-renderer should be registered');
    });
    
    hooks.afterEach(function() {
        TestUtils.cleanup();
    });

    QUnit.test('component initializes correctly', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');
        
        assert.ok(renderer, 'renderer should exist');
        assert.strictEqual(renderer.svg, null, 'svg should initially be null');
        assert.strictEqual(renderer.simulation, null, 'simulation should initially be null');
        assert.strictEqual(renderer.targetCanvas, null, 'targetCanvas should initially be null');
    });

    QUnit.test('setTargetCanvas sets the target', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');
        const canvas = document.createElement('div');
        canvas.id = 'test-canvas';
        
        renderer.setTargetCanvas(canvas);
        
        assert.strictEqual(renderer.targetCanvas, canvas, 'targetCanvas should be set');
    });

    QUnit.test('parseDot extracts nodes correctly', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');
        
        const dotCode = `
            digraph G {
                "node1" [label="<div>", fillcolor="#E8E8E8", fontcolor="#333333"];
                "node2" [label="<p>", fillcolor="#4A90D9", fontcolor="#FFFFFF"];
                "node3" [label="Hello", fillcolor="#FFFACD", fontcolor="#333333"];
            }
        `;
        
        const { nodes, links } = renderer.parseDot(dotCode);
        
        assert.strictEqual(nodes.length, 3, 'should extract 3 nodes');
        assert.strictEqual(nodes[0].id, 'node1', 'first node should have correct id');
        assert.strictEqual(nodes[0].label, '<div>', 'first node should have correct label');
        assert.strictEqual(nodes[0].color, '#E8E8E8', 'first node should have correct color');
    });

    QUnit.test('parseDot extracts links correctly', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');
        
        const dotCode = `
            digraph G {
                "node1" [label="A"];
                "node2" [label="B"];
                "node3" [label="C"];
                "node1" -> "node2";
                "node2" -> "node3" [style=dashed, color="#FF0000"];
            }
        `;
        
        const { nodes, links } = renderer.parseDot(dotCode);
        
        assert.strictEqual(links.length, 2, 'should extract 2 links');
        assert.strictEqual(links[0].source, 'node1', 'first link should have correct source');
        assert.strictEqual(links[0].target, 'node2', 'first link should have correct target');
        assert.strictEqual(links[1].dashed, true, 'second link should be dashed');
        assert.strictEqual(links[1].color, '#FF0000', 'second link should have color');
    });

    QUnit.test('extractAttr extracts quoted values', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');
        
        const attrString = 'label="Hello World", fillcolor="#FF0000"';
        
        assert.strictEqual(renderer.extractAttr(attrString, 'label'), 'Hello World', 'should extract label');
        assert.strictEqual(renderer.extractAttr(attrString, 'fillcolor'), '#FF0000', 'should extract fillcolor');
        assert.strictEqual(renderer.extractAttr(attrString, 'nonexistent'), null, 'should return null for missing attr');
    });

    QUnit.test('extractAttr extracts unquoted values', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');
        
        const attrString = 'style=dashed, width=2';
        
        assert.strictEqual(renderer.extractAttr(attrString, 'style'), 'dashed', 'should extract unquoted style');
    });

    QUnit.test('cleanLabel removes escape sequences', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');
        
        // D3 converts \n to space for single-line display
        assert.strictEqual(renderer.cleanLabel('Hello\\nWorld'), 'Hello World', 'should convert \\n to space');
        assert.strictEqual(renderer.cleanLabel('Say \\"Hi\\"'), 'Say "Hi"', 'should convert \\" to quote');
        assert.strictEqual(renderer.cleanLabel('"quoted"'), 'quoted', 'should remove surrounding quotes');
    });

    QUnit.test('truncateLabel truncates long labels', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');
        
        const shortLabel = 'Short';
        const longLabel = 'This is a very long label that should be truncated';
        
        assert.strictEqual(renderer.truncateLabel(shortLabel, 20), 'Short', 'short labels should not be truncated');
        assert.ok(renderer.truncateLabel(longLabel, 20).endsWith('...'), 'long labels should end with ...');
        assert.ok(renderer.truncateLabel(longLabel, 20).length <= 20, 'truncated label should be <= maxLength');
    });

    QUnit.test('darkenColor darkens hex colors', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');
        
        const darkened = renderer.darkenColor('#FFFFFF');
        assert.ok(darkened.startsWith('#'), 'should return hex color');
        assert.notStrictEqual(darkened, '#FFFFFF', 'should be different from input');
        assert.strictEqual(darkened.toLowerCase(), '#e1e1e1', 'white should darken to #e1e1e1');
    });

    QUnit.test('darkenColor handles edge cases', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');
        
        const result = renderer.darkenColor('#000000');
        assert.strictEqual(result, '#000000', 'black should stay black');
    });

    QUnit.test('fitToView handles null svg', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');
        renderer.svg = null;
        
        renderer.fitToView();
        assert.ok(true, 'should not throw when svg is null');
    });

    QUnit.test('exportSvg returns null when no svg', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');
        renderer.svg = null;
        
        const result = renderer.exportSvg();
        
        assert.strictEqual(result, null, 'exportSvg should return null when no svg');
    });

    QUnit.test('parseDot handles empty input', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');
        
        const { nodes, links } = renderer.parseDot('digraph G {}');
        
        assert.strictEqual(nodes.length, 0, 'should have no nodes');
        assert.strictEqual(links.length, 0, 'should have no links');
    });

    QUnit.test('parseDot ignores edges with missing nodes', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');
        
        const dotCode = `
            digraph G {
                "node1" [label="A"];
                "node1" -> "node2";
            }
        `;
        
        const { nodes, links } = renderer.parseDot(dotCode);
        
        assert.strictEqual(nodes.length, 1, 'should have 1 node');
        assert.strictEqual(links.length, 0, 'should have no links (node2 not defined)');
    });

    QUnit.test('drag creates d3 drag behavior', async function(assert) {
        const renderer = await TestUtils.createComponent('d3-renderer');
        
        const mockSimulation = {
            alphaTarget: () => ({ restart: () => {} })
        };
        
        const dragBehavior = renderer.drag(mockSimulation);
        
        assert.ok(dragBehavior, 'should return drag behavior');
        assert.ok(typeof dragBehavior.on === 'function', 'should have on method');
    });

});
