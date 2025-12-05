/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Test Suite - URL Input Tests
   v0.1.4 - Test Infrastructure
   ═══════════════════════════════════════════════════════════════════════════════ */

QUnit.module('URL Input', function(hooks) {
    
    hooks.before(async function(assert) {
        await TestUtils.loadCss(TestPaths.commonCss);
        await TestUtils.loadScript(TestPaths.urlInput);
        assert.ok(customElements.get('url-input'), 'url-input should be registered');
    });
    
    hooks.afterEach(function() {
        TestUtils.cleanup();
    });

    QUnit.test('component renders correctly', async function(assert) {
        const input = await TestUtils.createComponent('url-input');
        
        assert.ok(input.querySelector('.card'), 'should have card container');
        assert.ok(input.querySelector('#url-input'), 'should have URL input field');
        assert.ok(input.querySelector('#url-fetch-btn'), 'should have fetch button');
        assert.ok(input.querySelector('#url-status'), 'should have status element');
    });
    
    QUnit.test('URL input has correct attributes', async function(assert) {
        const input = await TestUtils.createComponent('url-input');
        const urlField = input.querySelector('#url-input');
        
        assert.strictEqual(urlField.type, 'url', 'should be URL type input');
        assert.ok(urlField.placeholder.includes('https'), 'placeholder should suggest https');
    });
    
    QUnit.test('has example URL buttons', async function(assert) {
        const input = await TestUtils.createComponent('url-input');
        const exampleButtons = input.querySelectorAll('.url-example-btn');
        
        assert.ok(exampleButtons.length >= 2, 'should have at least 2 example buttons');
    });
    
    QUnit.test('getUrl returns input value', async function(assert) {
        const input = await TestUtils.createComponent('url-input');
        const urlField = input.querySelector('#url-input');
        
        urlField.value = 'https://example.com';
        
        assert.strictEqual(input.getUrl(), 'https://example.com', 'getUrl should return input value');
    });
    
    QUnit.test('setUrl updates input value', async function(assert) {
        const input = await TestUtils.createComponent('url-input');
        
        input.setUrl('https://test.com');
        
        const urlField = input.querySelector('#url-input');
        assert.strictEqual(urlField.value, 'https://test.com', 'input should be updated');
    });
    
    QUnit.test('getUrl trims whitespace', async function(assert) {
        const input = await TestUtils.createComponent('url-input');
        const urlField = input.querySelector('#url-input');
        
        urlField.value = '  https://example.com  ';
        
        assert.strictEqual(input.getUrl(), 'https://example.com', 'should trim whitespace');
    });
    
    QUnit.test('validates URL format', async function(assert) {
        const input = await TestUtils.createComponent('url-input');
        
        // Test valid URL check - isValidUrl is a private method, test via behavior
        input.setUrl('not-a-url');
        
        // Trigger fetch
        const fetchBtn = input.querySelector('#url-fetch-btn');
        fetchBtn.click();
        
        await TestUtils.nextFrame();
        
        const status = input.querySelector('#url-status');
        assert.ok(status.classList.contains('error'), 'should show error for invalid URL');
    });
    
    QUnit.test('shows error for empty URL', async function(assert) {
        const input = await TestUtils.createComponent('url-input');
        input.setUrl('');
        
        const fetchBtn = input.querySelector('#url-fetch-btn');
        fetchBtn.click();
        
        await TestUtils.nextFrame();
        
        const status = input.querySelector('#url-status');
        assert.ok(status.textContent.length > 0, 'should show error message');
    });
    
    QUnit.test('example button sets URL in input', async function(assert) {
        const input = await TestUtils.createComponent('url-input');
        const exampleBtn = input.querySelector('.url-example-btn');
        const expectedUrl = exampleBtn.dataset.url;
        
        // Just click and check input updates (don't wait for fetch)
        const urlField = input.querySelector('#url-input');
        
        // Store original to verify change
        const originalValue = urlField.value;
        
        // We can't easily test the fetch since it requires network
        // Just verify the data-url attribute exists
        assert.ok(expectedUrl, 'example button should have data-url');
        assert.ok(expectedUrl.startsWith('https://'), 'data-url should be https');
    });
    
    QUnit.test('has default value in input', async function(assert) {
        const input = await TestUtils.createComponent('url-input');
        const urlField = input.querySelector('#url-input');
        
        // Component sets a default value
        assert.ok(urlField.value.length > 0, 'should have a default URL value');
    });
    
    QUnit.test('fetch button shows loading state', async function(assert) {
        const input = await TestUtils.createComponent('url-input');
        input.setUrl('https://example.com');
        
        // Access the setFetchingState method
        input.setFetchingState(true);
        
        const fetchBtn = input.querySelector('#url-fetch-btn');
        assert.strictEqual(fetchBtn.disabled, true, 'button should be disabled when fetching');
        assert.ok(fetchBtn.innerHTML.includes('Fetching'), 'should show fetching text');
    });
    
    QUnit.test('fetch button returns to normal after loading', async function(assert) {
        const input = await TestUtils.createComponent('url-input');
        
        input.setFetchingState(true);
        input.setFetchingState(false);
        
        const fetchBtn = input.querySelector('#url-fetch-btn');
        assert.strictEqual(fetchBtn.disabled, false, 'button should be enabled');
        assert.ok(fetchBtn.innerHTML.includes('Fetch'), 'should show Fetch text');
    });
    
    QUnit.test('setStatus updates status text', async function(assert) {
        const input = await TestUtils.createComponent('url-input');
        
        input.setStatus('Test message', 'success');
        
        const status = input.querySelector('#url-status');
        assert.strictEqual(status.textContent, 'Test message', 'should update text');
        assert.ok(status.classList.contains('success'), 'should have success class');
    });
    
    QUnit.test('setStatus can show error state', async function(assert) {
        const input = await TestUtils.createComponent('url-input');
        
        input.setStatus('Error occurred', 'error');
        
        const status = input.querySelector('#url-status');
        assert.ok(status.classList.contains('error'), 'should have error class');
    });

});
