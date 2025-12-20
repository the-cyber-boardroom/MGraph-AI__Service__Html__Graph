/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Test Suite - URL Input Tests
   v0.2.1 - Tests for Shadow DOM refactored component
   ═══════════════════════════════════════════════════════════════════════════════ */

QUnit.module('URL Input', function(hooks) {
    
    let originalApiClient;
    
    hooks.before(async function(assert) {
        // Load foundation
        await TestUtils.loadFoundation();
        
        // Load the component
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
    // Initialization Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.module('Initialization', function() {
        
        QUnit.test('component creates Shadow DOM', async function(assert) {
            const input = await TestUtils.createComponent('url-input');
            assert.ok(input.shadowRoot, 'should have Shadow DOM');
        });
        
        QUnit.test('component renders template', async function(assert) {
            const input = await TestUtils.createComponent('url-input');
            
            assert.ok(TestUtils.shadowQuery(input, '.card'), 'should have card container');
            assert.ok(TestUtils.shadowQuery(input, '#url-input'), 'should have url input');
            assert.ok(TestUtils.shadowQuery(input, '#url-fetch-btn'), 'should have fetch button');
            assert.ok(TestUtils.shadowQuery(input, '#url-status'), 'should have status element');
        });
        
        QUnit.test('has panel header with icon', async function(assert) {
            const input = await TestUtils.createComponent('url-input');
            
            const title = TestUtils.shadowQuery(input, '.panel-title');
            assert.ok(title, 'should have panel title');
            assert.ok(title.textContent.includes('Fetch from URL'), 'should have correct title');
            assert.ok(title.textContent.includes('🌐'), 'should have globe icon');
        });
        
        QUnit.test('isFetching starts as false', async function(assert) {
            const input = await TestUtils.createComponent('url-input');
            assert.strictEqual(input.isFetching, false);
        });
        
        QUnit.test('has example buttons', async function(assert) {
            const input = await TestUtils.createComponent('url-input');
            const examples = TestUtils.shadowQueryAll(input, '.url-example-btn');
            assert.ok(examples.length >= 3, 'should have at least 3 example buttons');
        });
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // getUrl / setUrl Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.module('getUrl / setUrl', function() {
        
        QUnit.test('getUrl returns input value', async function(assert) {
            const input = await TestUtils.createComponent('url-input');
            const urlField = TestUtils.shadowQuery(input, '#url-input');
            
            urlField.value = 'https://test.com';
            
            assert.strictEqual(input.getUrl(), 'https://test.com');
        });
        
        QUnit.test('getUrl trims whitespace', async function(assert) {
            const input = await TestUtils.createComponent('url-input');
            const urlField = TestUtils.shadowQuery(input, '#url-input');
            
            urlField.value = '  https://test.com  ';
            
            assert.strictEqual(input.getUrl(), 'https://test.com');
        });
        
        QUnit.test('setUrl updates input value', async function(assert) {
            const input = await TestUtils.createComponent('url-input');
            
            input.setUrl('https://new-url.com');
            
            const urlField = TestUtils.shadowQuery(input, '#url-input');
            assert.strictEqual(urlField.value, 'https://new-url.com');
        });
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // setStatus Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.module('setStatus', function() {
        
        QUnit.test('updates status text', async function(assert) {
            const input = await TestUtils.createComponent('url-input');
            
            input.setStatus('Test status');
            
            assert.strictEqual(TestUtils.getShadowText(input, '#url-status'), 'Test status');
        });
        
        QUnit.test('applies success class', async function(assert) {
            const input = await TestUtils.createComponent('url-input');
            const status = TestUtils.shadowQuery(input, '#url-status');
            
            input.setStatus('Success', 'success');
            
            assert.ok(status.classList.contains('success'));
        });
        
        QUnit.test('applies error class', async function(assert) {
            const input = await TestUtils.createComponent('url-input');
            const status = TestUtils.shadowQuery(input, '#url-status');
            
            input.setStatus('Error', 'error');
            
            assert.ok(status.classList.contains('error'));
        });
        
        QUnit.test('clears previous classes', async function(assert) {
            const input = await TestUtils.createComponent('url-input');
            const status = TestUtils.shadowQuery(input, '#url-status');
            
            input.setStatus('Error', 'error');
            input.setStatus('Success', 'success');
            
            assert.notOk(status.classList.contains('error'));
            assert.ok(status.classList.contains('success'));
        });
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // setFetchingState Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.module('setFetchingState', function() {
        
        QUnit.test('disables button when fetching', async function(assert) {
            const input = await TestUtils.createComponent('url-input');
            const button = TestUtils.shadowQuery(input, '#url-fetch-btn');
            
            input.setFetchingState(true);
            
            assert.strictEqual(button.disabled, true);
        });
        
        QUnit.test('shows spinner when fetching', async function(assert) {
            const input = await TestUtils.createComponent('url-input');
            const button = TestUtils.shadowQuery(input, '#url-fetch-btn');
            
            input.setFetchingState(true);
            
            assert.ok(button.innerHTML.includes('spinner'));
            assert.ok(button.innerHTML.includes('Fetching'));
        });
        
        QUnit.test('enables button when done', async function(assert) {
            const input = await TestUtils.createComponent('url-input');
            const button = TestUtils.shadowQuery(input, '#url-fetch-btn');
            
            input.setFetchingState(true);
            input.setFetchingState(false);
            
            assert.strictEqual(button.disabled, false);
            assert.ok(button.innerHTML.includes('Fetch'));
        });
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // fetchUrl Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.module('fetchUrl', function() {
        
        QUnit.test('shows error for empty URL', async function(assert) {
            const input = await TestUtils.createComponent('url-input');
            input.setUrl('');
            
            await input.fetchUrl();
            
            const status = TestUtils.shadowQuery(input, '#url-status');
            assert.ok(status.classList.contains('error'));
            assert.ok(status.textContent.includes('enter a URL'));
        });
        
        QUnit.test('shows error for invalid URL', async function(assert) {
            const input = await TestUtils.createComponent('url-input');
            input.setUrl('not-a-url');
            
            await input.fetchUrl();
            
            const status = TestUtils.shadowQuery(input, '#url-status');
            assert.ok(status.classList.contains('error'));
            assert.ok(status.textContent.includes('valid URL'));
        });
        
        QUnit.test('prevents double fetch', async function(assert) {
            const input = await TestUtils.createComponent('url-input');
            input.setUrl('https://example.com');
            input.isFetching = true;
            
            let apiCalled = false;
            window.apiClient = {
                post: async () => { apiCalled = true; return { html: '', url: '' }; }
            };
            
            await input.fetchUrl();
            
            assert.notOk(apiCalled, 'API should not be called when already fetching');
        });
        
        QUnit.test('calls API with correct parameters', async function(assert) {
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
            
            assert.strictEqual(calledEndpoint, '/html/from/url');
            assert.strictEqual(calledData.url, 'https://example.com/page');
            assert.strictEqual(calledData.timeout, 30);
        });
        
        QUnit.test('emits url-html-fetched on success', async function(assert) {
            const input = await TestUtils.createComponent('url-input');
            input.setUrl('https://example.com');
            
            window.apiClient = {
                post: async () => ({
                    html: '<div>content</div>',
                    url: 'https://example.com',
                    content_type: 'text/html'
                })
            };
            
            let eventDetail = null;
            input.addEventListener('url-html-fetched', (e) => {
                eventDetail = e.detail;
            });
            
            await input.fetchUrl();
            
            assert.ok(eventDetail, 'event should be dispatched');
            assert.strictEqual(eventDetail.html, '<div>content</div>');
            assert.strictEqual(eventDetail.url, 'https://example.com');
            assert.strictEqual(eventDetail.contentType, 'text/html');
        });
        
        QUnit.test('shows success status on success', async function(assert) {
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
            
            const status = TestUtils.shadowQuery(input, '#url-status');
            assert.ok(status.classList.contains('success'));
            assert.ok(status.textContent.includes('Fetched'));
        });
        
        QUnit.test('shows error on API failure', async function(assert) {
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
            
            const status = TestUtils.shadowQuery(input, '#url-status');
            assert.ok(status.classList.contains('error'));
        });
        
        QUnit.test('resets isFetching after completion', async function(assert) {
            const input = await TestUtils.createComponent('url-input');
            input.setUrl('https://example.com');
            
            window.apiClient = {
                post: async () => ({ html: '', url: '', content_type: '' })
            };
            
            await input.fetchUrl();
            
            assert.strictEqual(input.isFetching, false);
        });
        
        QUnit.test('resets isFetching after error', async function(assert) {
            const input = await TestUtils.createComponent('url-input');
            input.setUrl('https://example.com');
            
            window.apiClient = {
                post: async () => { throw new Error('Error'); }
            };
            
            console.error = () => {};
            await input.fetchUrl();
            
            assert.strictEqual(input.isFetching, false);
        });
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // Keyboard Event Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.module('Keyboard Events', function() {
        
        QUnit.test('Enter key triggers fetch', async function(assert) {
            const input = await TestUtils.createComponent('url-input');
            input.setUrl('https://example.com');
            
            let fetchCalled = false;
            input.fetchUrl = async () => { fetchCalled = true; };
            
            const urlField = TestUtils.shadowQuery(input, '#url-input');
            TestUtils.triggerKeyEvent(urlField, 'keydown', 'Enter');
            
            await TestUtils.nextFrame();
            
            assert.ok(fetchCalled, 'Enter should trigger fetch');
        });
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // Example Button Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.module('Example Buttons', function() {
        
        QUnit.test('clicking example sets URL and fetches', async function(assert) {
            const input = await TestUtils.createComponent('url-input');
            
            let fetchCalled = false;
            input.fetchUrl = async () => { fetchCalled = true; };
            
            const exampleBtn = TestUtils.shadowQuery(input, '.url-example-btn');
            const expectedUrl = exampleBtn.dataset.url;
            
            exampleBtn.click();
            
            await TestUtils.nextFrame();
            
            assert.strictEqual(input.getUrl(), expectedUrl, 'URL should be set from example');
            assert.ok(fetchCalled, 'fetch should be triggered');
        });
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // Style Encapsulation Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.module('Style Encapsulation', function() {
        
        QUnit.test('uses form-control class from shared CSS', async function(assert) {
            const input = await TestUtils.createComponent('url-input');
            const urlField = TestUtils.shadowQuery(input, '#url-input');
            
            assert.ok(urlField.classList.contains('form-control'), 'should use shared form-control class');
        });
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // Event Crossing Shadow DOM Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.module('Event Crossing Shadow DOM', function() {
        
        QUnit.test('url-html-fetched event bubbles through Shadow DOM', async function(assert) {
            const fixture = document.getElementById('qunit-fixture');
            const input = await TestUtils.createComponent('url-input');
            
            window.apiClient = {
                post: async () => ({ html: 'test', url: 'test', content_type: 'text/html' })
            };
            
            let eventReceived = false;
            fixture.addEventListener('url-html-fetched', () => {
                eventReceived = true;
            });
            
            input.setUrl('https://example.com');
            await input.fetchUrl();
            
            assert.ok(eventReceived, 'event should bubble through Shadow DOM');
        });
    });

});
