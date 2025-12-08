/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Test Suite - URL Input Extended Tests
   v0.2.0 - Additional tests to improve coverage
   ═══════════════════════════════════════════════════════════════════════════════ */

QUnit.module('URL Input Extended', function(hooks) {

    let originalApiClient;

    hooks.before(async function(assert) {
        await TestUtils.loadCss(TestPaths.commonCss);
        await TestUtils.loadScript(TestPaths.apiClient);
        await TestUtils.loadScript(TestPaths.urlInput);
        assert.ok(customElements.get('url-input'), 'url-input should be registered');
    });

    hooks.beforeEach(function() {
        originalApiClient = window.apiClient;
    });

    hooks.afterEach(function() {
        window.apiClient = originalApiClient;
        TestUtils.cleanup();
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // Constructor and Initialization Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('constructor initializes properties', function(assert) {
        const input = document.createElement('url-input');

        assert.strictEqual(input.urlInput, null, 'urlInput should be null');
        assert.strictEqual(input.fetchButton, null, 'fetchButton should be null');
        assert.strictEqual(input.statusText, null, 'statusText should be null');
        assert.strictEqual(input.isFetching, false, 'isFetching should be false');
    });

    QUnit.test('connectedCallback sets up DOM references', async function(assert) {
        const input = await TestUtils.createComponent('url-input');

        assert.ok(input.urlInput, 'urlInput should be set');
        assert.ok(input.fetchButton, 'fetchButton should be set');
        assert.ok(input.statusText, 'statusText should be set');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // isValidUrl Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('isValidUrl returns true for https URL', async function(assert) {
        const input = await TestUtils.createComponent('url-input');

        assert.strictEqual(input.isValidUrl('https://example.com'), true, 'https URL should be valid');
    });

    QUnit.test('isValidUrl returns true for http URL', async function(assert) {
        const input = await TestUtils.createComponent('url-input');

        assert.strictEqual(input.isValidUrl('http://example.com'), true, 'http URL should be valid');
    });

    QUnit.test('isValidUrl returns false for ftp URL', async function(assert) {
        const input = await TestUtils.createComponent('url-input');

        assert.strictEqual(input.isValidUrl('ftp://example.com'), false, 'ftp URL should be invalid');
    });

    QUnit.test('isValidUrl returns false for invalid URL', async function(assert) {
        const input = await TestUtils.createComponent('url-input');

        assert.strictEqual(input.isValidUrl('not-a-url'), false, 'invalid URL should return false');
    });

    QUnit.test('isValidUrl returns false for empty string', async function(assert) {
        const input = await TestUtils.createComponent('url-input');

        assert.strictEqual(input.isValidUrl(''), false, 'empty string should return false');
    });

    QUnit.test('isValidUrl returns false for URL without protocol', async function(assert) {
        const input = await TestUtils.createComponent('url-input');

        assert.strictEqual(input.isValidUrl('example.com'), false, 'URL without protocol should return false');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // formatBytes Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('formatBytes formats bytes correctly', async function(assert) {
        const input = await TestUtils.createComponent('url-input');

        assert.strictEqual(input.formatBytes(500), '500 B', 'should format bytes');
    });

    QUnit.test('formatBytes formats KB correctly', async function(assert) {
        const input = await TestUtils.createComponent('url-input');

        assert.strictEqual(input.formatBytes(1536), '1.5 KB', 'should format KB');
    });

    QUnit.test('formatBytes formats MB correctly', async function(assert) {
        const input = await TestUtils.createComponent('url-input');

        assert.strictEqual(input.formatBytes(1048576), '1.0 MB', 'should format MB');
    });

    QUnit.test('formatBytes handles zero', async function(assert) {
        const input = await TestUtils.createComponent('url-input');

        assert.strictEqual(input.formatBytes(0), '0 B', 'should handle zero');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // setStatus Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('setStatus updates text content', async function(assert) {
        const input = await TestUtils.createComponent('url-input');

        input.setStatus('Test status');

        assert.strictEqual(input.statusText.textContent, 'Test status', 'should update text');
    });

    QUnit.test('setStatus applies success class', async function(assert) {
        const input = await TestUtils.createComponent('url-input');

        input.setStatus('Success', 'success');

        assert.ok(input.statusText.classList.contains('success'), 'should have success class');
    });

    QUnit.test('setStatus applies error class', async function(assert) {
        const input = await TestUtils.createComponent('url-input');

        input.setStatus('Error', 'error');

        assert.ok(input.statusText.classList.contains('error'), 'should have error class');
    });

    QUnit.test('setStatus clears previous classes', async function(assert) {
        const input = await TestUtils.createComponent('url-input');

        input.setStatus('Error', 'error');
        input.setStatus('Success', 'success');

        assert.ok(!input.statusText.classList.contains('error'), 'should remove error class');
        assert.ok(input.statusText.classList.contains('success'), 'should have success class');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // setFetchingState Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('setFetchingState disables button when true', async function(assert) {
        const input = await TestUtils.createComponent('url-input');

        input.setFetchingState(true);

        assert.strictEqual(input.fetchButton.disabled, true, 'button should be disabled');
    });

    QUnit.test('setFetchingState shows loading text when true', async function(assert) {
        const input = await TestUtils.createComponent('url-input');

        input.setFetchingState(true);

        assert.ok(input.fetchButton.innerHTML.includes('Fetching'), 'should show Fetching text');
    });

    QUnit.test('setFetchingState enables button when false', async function(assert) {
        const input = await TestUtils.createComponent('url-input');

        input.setFetchingState(true);
        input.setFetchingState(false);

        assert.strictEqual(input.fetchButton.disabled, false, 'button should be enabled');
    });

    QUnit.test('setFetchingState restores normal text when false', async function(assert) {
        const input = await TestUtils.createComponent('url-input');

        input.setFetchingState(true);
        input.setFetchingState(false);

        assert.ok(input.fetchButton.innerHTML.includes('Fetch'), 'should show Fetch text');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // fetchUrl Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('fetchUrl shows error for empty URL', async function(assert) {
        const input = await TestUtils.createComponent('url-input');
        input.setUrl('');

        await input.fetchUrl();

        assert.ok(input.statusText.classList.contains('error'), 'should show error');
        assert.ok(input.statusText.textContent.includes('enter a URL'), 'should mention entering URL');
    });

    QUnit.test('fetchUrl shows error for invalid URL', async function(assert) {
        const input = await TestUtils.createComponent('url-input');
        input.setUrl('not-a-valid-url');

        await input.fetchUrl();

        assert.ok(input.statusText.classList.contains('error'), 'should show error');
        assert.ok(input.statusText.textContent.includes('valid URL'), 'should mention valid URL');
    });

    QUnit.test('fetchUrl prevents double fetch when already fetching', async function(assert) {
        const input = await TestUtils.createComponent('url-input');
        input.setUrl('https://example.com');
        input.isFetching = true;

        let apiCalled = false;
        window.apiClient = {
            post: async () => { apiCalled = true; return { html: '', url: '' }; }
        };

        await input.fetchUrl();

        assert.ok(!apiCalled, 'API should not be called when already fetching');
    });

    QUnit.test('fetchUrl calls API with correct parameters', async function(assert) {
        const input = await TestUtils.createComponent('url-input');
        input.setUrl('https://example.com/page');

        let calledEndpoint = null;
        let calledData = null;

        window.apiClient = {
            post: async (endpoint, data) => {
                calledEndpoint = endpoint;
                calledData = data;
                return { html: '<div></div>', url: 'https://example.com/page', content_type: 'text/html' };
            }
        };

        await input.fetchUrl();

        assert.strictEqual(calledEndpoint, '/html/from/url', 'should call correct endpoint');
        assert.strictEqual(calledData.url, 'https://example.com/page', 'should pass URL');
        assert.strictEqual(calledData.timeout, 30, 'should pass timeout');
    });

    QUnit.test('fetchUrl emits url-html-fetched event on success', async function(assert) {
        const input = await TestUtils.createComponent('url-input');
        input.setUrl('https://example.com');

        window.apiClient = {
            post: async () => ({
                html: '<div>content</div>',
                url: 'https://example.com',
                content_type: 'text/html'
            })
        };

        let eventReceived = null;
        input.addEventListener('url-html-fetched', (e) => {
            eventReceived = e.detail;
        });

        await input.fetchUrl();

        assert.ok(eventReceived, 'event should be dispatched');
        assert.strictEqual(eventReceived.html, '<div>content</div>', 'should include html');
        assert.strictEqual(eventReceived.url, 'https://example.com', 'should include url');
    });

    QUnit.test('fetchUrl shows success status on success', async function(assert) {
        const input = await TestUtils.createComponent('url-input');
        input.setUrl('https://example.com');

        window.apiClient = {
            post: async () => ({
                html: '<div>content</div>',
                url: 'https://example.com',
                content_type: 'text/html'
            })
        };

        await input.fetchUrl();

        assert.ok(input.statusText.classList.contains('success'), 'should show success');
        assert.ok(input.statusText.textContent.includes('Fetched'), 'should show Fetched text');
    });

    QUnit.test('fetchUrl shows error on API failure', async function(assert) {
        const input = await TestUtils.createComponent('url-input');
        input.setUrl('https://example.com');

        window.apiClient = {
            post: async () => { throw new Error('Network error'); }
        };

        // Suppress console.error
        const originalError = console.error;
        console.error = () => {};

        await input.fetchUrl();

        console.error = originalError;

        assert.ok(input.statusText.classList.contains('error'), 'should show error');
    });

    QUnit.test('fetchUrl resets isFetching after completion', async function(assert) {
        const input = await TestUtils.createComponent('url-input');
        input.setUrl('https://example.com');

        window.apiClient = {
            post: async () => ({ html: '', url: '', content_type: '' })
        };

        await input.fetchUrl();

        assert.strictEqual(input.isFetching, false, 'isFetching should be false after completion');
    });

    QUnit.test('fetchUrl resets isFetching after error', async function(assert) {
        const input = await TestUtils.createComponent('url-input');
        input.setUrl('https://example.com');

        window.apiClient = {
            post: async () => { throw new Error('Error'); }
        };

        console.error = () => {};
        await input.fetchUrl();

        assert.strictEqual(input.isFetching, false, 'isFetching should be false after error');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // Event Listener Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('Enter key triggers fetch', async function(assert) {
        const input = await TestUtils.createComponent('url-input');
        input.setUrl('https://example.com');

        let fetchCalled = false;
        input.fetchUrl = async () => { fetchCalled = true; };

        const urlField = input.querySelector('#url-input');
        TestUtils.triggerKeyEvent(urlField, 'keydown', 'Enter');

        await TestUtils.nextFrame();

        assert.ok(fetchCalled, 'Enter should trigger fetch');
    });

    QUnit.test('example button sets URL and fetches', async function(assert) {
        const input = await TestUtils.createComponent('url-input');

        let fetchCalled = false;
        input.fetchUrl = async () => { fetchCalled = true; };

        const exampleBtn = input.querySelector('.url-example-btn');
        const expectedUrl = exampleBtn.dataset.url;

        exampleBtn.click();

        await TestUtils.nextFrame();

        assert.strictEqual(input.getUrl(), expectedUrl, 'URL should be set from example');
        assert.ok(fetchCalled, 'fetch should be triggered');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // UI Element Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('has panel title with icon', async function(assert) {
        const input = await TestUtils.createComponent('url-input');

        const title = input.querySelector('.panel-title');
        assert.ok(title, 'should have panel title');
        assert.ok(title.textContent.includes('Fetch from URL'), 'should have correct title text');
    });

    QUnit.test('has title icon', async function(assert) {
        const input = await TestUtils.createComponent('url-input');

        const icon = input.querySelector('.panel-title-icon');
        assert.ok(icon, 'should have title icon');
        assert.ok(icon.textContent.includes('🌐'), 'should have globe emoji');
    });

    QUnit.test('URL input has autocomplete attribute', async function(assert) {
        const input = await TestUtils.createComponent('url-input');

        const urlField = input.querySelector('#url-input');
        assert.strictEqual(urlField.getAttribute('autocomplete'), 'url', 'should have autocomplete=url');
    });

});