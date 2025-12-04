/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Test Suite - HTML Input Tests
   v0.1.4 - Test Infrastructure
   ═══════════════════════════════════════════════════════════════════════════════ */

QUnit.module('HTML Input', function(hooks) {
    
    hooks.before(async function(assert) {
        await TestUtils.loadCss(TestPaths.commonCss);
        await TestUtils.loadScript(TestPaths.htmlInput);
        assert.ok(customElements.get('html-input'), 'html-input should be registered');
    });
    
    hooks.afterEach(function() {
        TestUtils.cleanup();
    });

    QUnit.test('component renders correctly', async function(assert) {
        const input = await TestUtils.createComponent('html-input');
        
        assert.ok(input.querySelector('.card'), 'should have card container');
        assert.ok(input.querySelector('#html-input'), 'should have textarea');
        assert.ok(input.querySelector('#sample-select'), 'should have sample selector');
    });
    
    QUnit.test('textarea has correct attributes', async function(assert) {
        const input = await TestUtils.createComponent('html-input');
        const textarea = input.querySelector('#html-input');
        
        assert.ok(textarea.classList.contains('html-input-area'), 'should have correct class');
        assert.strictEqual(textarea.getAttribute('spellcheck'), 'false', 'should have spellcheck disabled');
        assert.ok(textarea.placeholder.length > 0, 'should have placeholder text');
    });
    
    QUnit.test('sample selector has correct options', async function(assert) {
        const input = await TestUtils.createComponent('html-input');
        const select = input.querySelector('#sample-select');
        const options = select.querySelectorAll('option');
        
        assert.ok(options.length >= 5, 'should have at least 5 sample options');
        
        const optionValues = Array.from(options).map(o => o.value);
        assert.ok(optionValues.includes('simple'), 'should have simple sample');
        assert.ok(optionValues.includes('nested'), 'should have nested sample');
        assert.ok(optionValues.includes('attributes'), 'should have attributes sample');
    });
    
    QUnit.test('getHtml returns textarea value', async function(assert) {
        const input = await TestUtils.createComponent('html-input');
        const textarea = input.querySelector('#html-input');
        
        textarea.value = '<div>Test</div>';
        
        assert.strictEqual(input.getHtml(), '<div>Test</div>', 'getHtml should return textarea value');
    });
    
    QUnit.test('setHtml updates textarea value', async function(assert) {
        const input = await TestUtils.createComponent('html-input');
        
        input.setHtml('<p>New content</p>');
        
        const textarea = input.querySelector('#html-input');
        assert.strictEqual(textarea.value, '<p>New content</p>', 'textarea should be updated');
    });
    
    QUnit.test('setHtml clears sample selection', async function(assert) {
        const input = await TestUtils.createComponent('html-input');
        const select = input.querySelector('#sample-select');
        
        // First set a sample value
        select.value = 'simple';
        
        // Then set custom HTML
        input.setHtml('<div>Custom</div>');
        
        assert.strictEqual(select.value, '', 'sample selection should be cleared');
    });
    
    QUnit.test('emits html-changed event on input', async function(assert) {
        const done = assert.async();
        const input = await TestUtils.createComponent('html-input');
        const textarea = input.querySelector('#html-input');
        
        // Listen for debounced event
        document.addEventListener('html-changed', function handler(e) {
            document.removeEventListener('html-changed', handler);
            assert.strictEqual(e.detail.html, '<span>Hello</span>', 'event should contain new HTML');
            done();
        });
        
        textarea.value = '<span>Hello</span>';
        TestUtils.triggerEvent(textarea, 'input');
        
        // Event is debounced, wait a bit
        await TestUtils.wait(400);
    });
    
    QUnit.test('typing does not clear sample selection', async function(assert) {
        const input = await TestUtils.createComponent('html-input');
        const textarea = input.querySelector('#html-input');
        const select = input.querySelector('#sample-select');
        
        // Set a sample first
        select.value = 'nested';
        
        // Simulate typing
        textarea.value = 'custom content';
        TestUtils.triggerEvent(textarea, 'input');
        
        await TestUtils.nextFrame();
        assert.strictEqual(select.value, 'simple', '[bug] sample selection is not cleared')
    });
    
    QUnit.test('getHtml returns empty string when textarea is empty', async function(assert) {
        const input = await TestUtils.createComponent('html-input');
        const textarea = input.querySelector('#html-input');
        
        textarea.value = '';
        
        assert.strictEqual(input.getHtml(), '', 'should return empty string');
    });

});
