/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Test Suite - Cytoscape Renderer Tests
   v0.2.0 - Consolidated from v0.1.x
   ═══════════════════════════════════════════════════════════════════════════════ */

QUnit.module('Cytoscape Renderer', function(hooks) {
    
    hooks.before(async function(assert) {
        await TestUtils.loadScript(TestPaths.cytoscapeRenderer);
        assert.ok(customElements.get('cytoscape-renderer'), 'cytoscape-renderer should be registered');
    });
    
    hooks.afterEach(function() {
        TestUtils.cleanup();
    });

    QUnit.test('component initializes correctly', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');
        
        assert.ok(renderer, 'renderer should exist');
        assert.strictEqual(renderer.cy, null, 'cy should initially be null');
        assert.strictEqual(renderer.targetCanvas, null, 'targetCanvas should initially be null');
    });

    QUnit.test('setTargetCanvas sets the target', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');
        const canvas = document.createElement('div');
        canvas.id = 'test-canvas';
        
        renderer.setTargetCanvas(canvas);
        
        assert.strictEqual(renderer.targetCanvas, canvas, 'targetCanvas should be set');
    });

    QUnit.test('parseDot extracts nodes correctly', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');
        
        const dotCode = `
            digraph G {
                "node1" [label="<div>", fillcolor="#E8E8E8", fontcolor="#333333"];
                "node2" [label="<p>", fillcolor="#4A90D9", fontcolor="#FFFFFF"];
                "node3" [label="Hello", fillcolor="#FFFACD", fontcolor="#333333"];
            }
        `;
        
        const { nodes, edges } = renderer.parseDot(dotCode);
        
        assert.strictEqual(nodes.length, 3, 'should extract 3 nodes');
        assert.strictEqual(nodes[0].id, 'node1', 'first node should have correct id');
        assert.strictEqual(nodes[0].label, '<div>', 'first node should have correct label');
        assert.strictEqual(nodes[0].color, '#E8E8E8', 'first node should have correct color');
    });

    QUnit.test('parseDot extracts edges correctly', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');
        
        const dotCode = `
            digraph G {
                "node1" [label="A"];
                "node2" [label="B"];
                "node3" [label="C"];
                "node1" -> "node2";
                "node2" -> "node3" [style=dashed];
            }
        `;
        
        const { nodes, edges } = renderer.parseDot(dotCode);
        
        assert.strictEqual(edges.length, 2, 'should extract 2 edges');
        assert.strictEqual(edges[0].source, 'node1', 'first edge should have correct source');
        assert.strictEqual(edges[0].target, 'node2', 'first edge should have correct target');
        assert.strictEqual(edges[1].dashed, true, 'second edge should be dashed');
    });

    QUnit.test('extractAttr extracts quoted values', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');
        
        const attrString = 'label="Hello World", fillcolor="#FF0000"';
        
        assert.strictEqual(renderer.extractAttr(attrString, 'label'), 'Hello World', 'should extract label');
        assert.strictEqual(renderer.extractAttr(attrString, 'fillcolor'), '#FF0000', 'should extract fillcolor');
        assert.strictEqual(renderer.extractAttr(attrString, 'nonexistent'), null, 'should return null for missing attr');
    });

    QUnit.test('extractAttr extracts unquoted values', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');
        
        const attrString = 'style=dashed, width=2';
        
        assert.strictEqual(renderer.extractAttr(attrString, 'style'), 'dashed', 'should extract unquoted style');
    });

    QUnit.test('detectNodeType identifies tag nodes', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');
        
        assert.strictEqual(renderer.detectNodeType('<div>', '#E8E8E8'), 'tag', '<div> should be tag');
        assert.strictEqual(renderer.detectNodeType('<p>', '#4A90D9'), 'tag', '<p> should be tag');
    });

    QUnit.test('detectNodeType identifies attribute nodes', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');
        
        assert.strictEqual(renderer.detectNodeType('class=container', '#B39DDB'), 'attribute', 'class= should be attribute');
        assert.strictEqual(renderer.detectNodeType('id=main', '#B39DDB'), 'attribute', 'id= should be attribute');
    });

    QUnit.test('detectNodeType identifies text nodes', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');
        
        assert.strictEqual(renderer.detectNodeType('Hello', '#FFFACD'), 'text', 'text with FFFACD should be text node');
        assert.strictEqual(renderer.detectNodeType('World', '#fffacd'), 'text', 'text with lowercase fffacd should be text node');
    });

    QUnit.test('detectNodeType identifies element nodes', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');
        
        assert.strictEqual(renderer.detectNodeType('something', '#E8E8E8'), 'element', 'default should be element');
    });

    QUnit.test('cleanLabel removes escape sequences', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');
        
        assert.strictEqual(renderer.cleanLabel('Hello\\nWorld'), 'Hello\nWorld', 'should convert \\n to newline');
        assert.strictEqual(renderer.cleanLabel('Say \\"Hi\\"'), 'Say "Hi"', 'should convert \\" to quote');
        assert.strictEqual(renderer.cleanLabel('"quoted"'), 'quoted', 'should remove surrounding quotes');
    });

    QUnit.test('darkenColor darkens hex colors', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');
        
        const darkened = renderer.darkenColor('#FFFFFF');
        assert.ok(darkened.startsWith('#'), 'should return hex color');
        assert.notStrictEqual(darkened, '#FFFFFF', 'should be different from input');
        assert.strictEqual(darkened.toLowerCase(), '#e1e1e1', 'white should darken to #e1e1e1');
    });

    QUnit.test('darkenColor handles edge cases', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');
        
        const result = renderer.darkenColor('#000000');
        assert.strictEqual(result, '#000000', 'black should stay black');
        
        const result2 = renderer.darkenColor('#101010');
        assert.ok(result2.match(/^#[0-9a-f]{6}$/i), 'should return valid hex');
    });

    QUnit.test('fitToView calls fit on cy instance', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');
        
        let fitCalled = false;
        renderer.cy = {
            fit: () => { fitCalled = true; }
        };
        
        renderer.fitToView();
        
        assert.ok(fitCalled, 'fit should be called');
    });

    QUnit.test('fitToView handles null cy', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');
        renderer.cy = null;
        
        renderer.fitToView();
        assert.ok(true, 'should not throw when cy is null');
    });

    QUnit.test('exportSvg returns null (not supported)', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');
        
        const result = renderer.exportSvg();
        
        assert.strictEqual(result, null, 'exportSvg should return null');
    });

    QUnit.test('exportPng returns null when no cy instance', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');
        renderer.cy = null;
        
        const result = renderer.exportPng();
        
        assert.strictEqual(result, null, 'exportPng should return null when no cy');
    });

    QUnit.test('runLayout handles null cy', async function(assert) {
        const renderer = await TestUtils.createComponent('cytoscape-renderer');
        renderer.cy = null;
        
        renderer.runLayout('dagre');
        assert.ok(true, 'should not throw when cy is null');
    });

});
