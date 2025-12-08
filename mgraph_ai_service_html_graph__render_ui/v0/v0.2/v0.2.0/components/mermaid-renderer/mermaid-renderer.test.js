/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Test Suite - Mermaid Renderer Tests
   v0.2.0 - Consolidated from v0.1.x
   ═══════════════════════════════════════════════════════════════════════════════ */

QUnit.module('Mermaid Renderer', function(hooks) {

    let originalConsoleError;

    hooks.before(async function(assert) {
        originalConsoleError = console.error;

        await TestUtils.loadScript(TestPaths.mermaidRenderer);
        assert.ok(customElements.get('mermaid-renderer'), 'mermaid-renderer should be registered');
    });

    hooks.beforeEach(function() {
        // Suppress mermaid loading errors (expected in test env)
        console.error = (...args) => {
            if (args[0]?.includes?.('Mermaid')) return;
            originalConsoleError.apply(console, args);
        };
    });

    hooks.afterEach(function() {
        console.error = originalConsoleError;
        TestUtils.cleanup();
    });

    QUnit.test('component initializes correctly', async function(assert) {
        const renderer = await TestUtils.createComponent('mermaid-renderer');

        assert.ok(renderer, 'renderer should exist');
    });

    QUnit.test('setTargetCanvas sets the target', async function(assert) {
        const renderer = await TestUtils.createComponent('mermaid-renderer');
        const canvas = document.createElement('div');
        canvas.id = 'test-canvas';

        renderer.setTargetCanvas(canvas);

        assert.strictEqual(renderer.targetCanvas, canvas, 'targetCanvas should be set');
    });

    QUnit.test('dotToMermaid converts simple graph', async function(assert) {
        const renderer = await TestUtils.createComponent('mermaid-renderer');

        const dotCode = `
            digraph G {
                "node1" [label="<div>", fillcolor="#E8E8E8"];
                "node2" [label="Hello", fillcolor="#FFFACD"];
                "node1" -> "node2";
            }
        `;

        const mermaidCode = renderer.dotToMermaid(dotCode);

        assert.ok(mermaidCode.startsWith('flowchart TB'), 'should start with flowchart TB');
        assert.ok(mermaidCode.includes('-->'), 'should contain arrow');
    });

    QUnit.test('dotToMermaid converts dashed edges', async function(assert) {
        const renderer = await TestUtils.createComponent('mermaid-renderer');

        const dotCode = `
            digraph G {
                "node1" [label="A"];
                "node2" [label="B"];
                "node1" -> "node2" [style=dashed];
            }
        `;

        const mermaidCode = renderer.dotToMermaid(dotCode);

        assert.ok(mermaidCode.includes('-.->'), 'should contain dashed arrow');
    });

    QUnit.test('dotToMermaid applies node type styling', async function(assert) {
        const renderer = await TestUtils.createComponent('mermaid-renderer');

        const dotCode = `
            digraph G {
                "node1" [label="<div>", fillcolor="#4A90D9"];
                "node2" [label="Hello", fillcolor="#FFFACD"];
            }
        `;

        const mermaidCode = renderer.dotToMermaid(dotCode);

        assert.ok(mermaidCode.includes('style'), 'should contain style directives');
    });

    QUnit.test('extractAttr extracts quoted values', async function(assert) {
        const renderer = await TestUtils.createComponent('mermaid-renderer');

        const attrString = 'label="Hello World", fillcolor="#FF0000"';

        assert.strictEqual(renderer.extractAttr(attrString, 'label'), 'Hello World', 'should extract label');
        assert.strictEqual(renderer.extractAttr(attrString, 'fillcolor'), '#FF0000', 'should extract fillcolor');
        assert.strictEqual(renderer.extractAttr(attrString, 'nonexistent'), null, 'should return null for missing attr');
    });

    QUnit.test('detectNodeType identifies tag nodes', async function(assert) {
        const renderer = await TestUtils.createComponent('mermaid-renderer');

        assert.strictEqual(renderer.detectNodeType('<div>', '#E8E8E8'), 'tag', '<div> should be tag');
        assert.strictEqual(renderer.detectNodeType('<p>', '#4A90D9'), 'tag', '<p> should be tag');
    });

    QUnit.test('detectNodeType identifies attribute nodes', async function(assert) {
        const renderer = await TestUtils.createComponent('mermaid-renderer');

        assert.strictEqual(renderer.detectNodeType('class=container', '#B39DDB'), 'attribute', 'class= should be attribute');
        assert.strictEqual(renderer.detectNodeType('id=main', '#B39DDB'), 'attribute', 'id= should be attribute');
    });

    QUnit.test('detectNodeType identifies text nodes', async function(assert) {
        const renderer = await TestUtils.createComponent('mermaid-renderer');

        assert.strictEqual(renderer.detectNodeType('Hello', '#FFFACD'), 'text', 'text with FFFACD should be text node');
        assert.strictEqual(renderer.detectNodeType('World', '#fffacd'), 'text', 'text with lowercase fffacd should be text node');
    });

    QUnit.test('detectNodeType identifies element nodes', async function(assert) {
        const renderer = await TestUtils.createComponent('mermaid-renderer');

        assert.strictEqual(renderer.detectNodeType('something', '#E8E8E8'), 'element', 'default should be element');
    });

    QUnit.test('cleanLabel removes special characters', async function(assert) {
        const renderer = await TestUtils.createComponent('mermaid-renderer');

        assert.strictEqual(renderer.cleanLabel('Hello\\nWorld'), 'Hello World', 'should convert \\n to space');
        assert.strictEqual(renderer.cleanLabel('<div>'), 'div', 'should remove angle brackets');
        assert.strictEqual(renderer.cleanLabel('[test]'), 'test', 'should remove square brackets');
        assert.strictEqual(renderer.cleanLabel('{test}'), 'test', 'should remove curly brackets');
    });

    QUnit.test('cleanLabel truncates long labels', async function(assert) {
        const renderer = await TestUtils.createComponent('mermaid-renderer');

        const longLabel = 'This is a very long label that exceeds the maximum length allowed';
        const cleaned = renderer.cleanLabel(longLabel);

        assert.ok(cleaned.length <= 30, 'should be truncated to 30 chars or less');
    });

    QUnit.test('escapeHtml escapes HTML entities', async function(assert) {
        const renderer = await TestUtils.createComponent('mermaid-renderer');

        const result = renderer.escapeHtml('<script>alert("xss")</script>');

        assert.ok(!result.includes('<script>'), 'should not contain script tag');
        assert.ok(result.includes('&lt;'), 'should contain escaped <');
    });

    QUnit.test('fitToView handles null targetCanvas', async function(assert) {
        const renderer = await TestUtils.createComponent('mermaid-renderer');
        renderer.targetCanvas = null;

        renderer.fitToView();
        assert.ok(true, 'should not throw when targetCanvas is null');
    });

    QUnit.test('exportSvg returns null when no targetCanvas', async function(assert) {
        const renderer = await TestUtils.createComponent('mermaid-renderer');
        renderer.targetCanvas = null;

        const result = renderer.exportSvg();

        assert.strictEqual(result, null, 'exportSvg should return null');
    });

    QUnit.test('renderCount increments on each render attempt', async function(assert) {
        const renderer = await TestUtils.createComponent('mermaid-renderer');

        const canvas = document.createElement('div');
        canvas.style.width = '400px';
        canvas.style.height = '300px';
        document.getElementById('qunit-fixture').appendChild(canvas);
        renderer.setTargetCanvas(canvas);

        const initialCount = renderer.renderCount;

        try {
            await renderer.renderDot('digraph { "a" [label="A"]; "b" [label="B"]; "a" -> "b" }');
        } catch (e) {
            // Expected - mermaid may not be loaded
        }

        assert.ok(renderer.renderCount > initialCount, 'renderCount should increment');
    });

    QUnit.test('dotToMermaid handles nodes with different shapes', async function(assert) {
        const renderer = await TestUtils.createComponent('mermaid-renderer');

        const dotCode = `
            digraph G {
                "tag" [label="<div>", fillcolor="#4A90D9"];
                "attr" [label="class=test", fillcolor="#B39DDB"];
                "text" [label="Hello", fillcolor="#FFFACD"];
                "elem" [label="Element", fillcolor="#E8E8E8"];
            }
        `;

        const mermaidCode = renderer.dotToMermaid(dotCode);

        // Tag nodes get (( )) circle shape
        assert.ok(mermaidCode.includes('(('), 'should have circle shape for tags');
        // Attribute nodes get {{ }} hexagon shape
        assert.ok(mermaidCode.includes('{{'), 'should have hexagon shape for attributes');
        // Text nodes get >...] flag shape
        assert.ok(mermaidCode.includes('>"'), 'should have flag shape for text');
        // Element nodes get [...] rectangle shape
        assert.ok(mermaidCode.includes('['), 'should have rectangle shape for elements');
    });

});
