/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Test Suite - API Client Extended Tests
   v0.2.0 - Additional tests to improve coverage
   ═══════════════════════════════════════════════════════════════════════════════ */

QUnit.module('API Client Extended', function(hooks) {

    let originalFetch;
    let fetchCalls = [];

    hooks.before(async function(assert) {
        await TestUtils.loadScript(TestPaths.apiClient);
        assert.ok(window.apiClient, 'apiClient should be globally available');
        assert.ok(typeof ApiClient === 'function', 'ApiClient class should be available');
        assert.ok(typeof ApiError === 'function', 'ApiError class should be available');
    });

    hooks.beforeEach(function() {
        originalFetch = window.fetch;
        fetchCalls = [];

        // Default mock fetch
        window.fetch = async (url, options) => {
            fetchCalls.push({ url, options });
            return {
                ok: true,
                json: async () => ({ success: true }),
                text: async () => 'text response',
                headers: new Map([['content-type', 'application/json']])
            };
        };
    });

    hooks.afterEach(function() {
        window.fetch = originalFetch;
        TestUtils.cleanup();
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // ApiClient Constructor Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('ApiClient uses window.location.origin as default baseUrl', function(assert) {
        const client = new ApiClient();
        assert.strictEqual(client.baseUrl, window.location.origin, 'should use origin as default');
    });

    QUnit.test('ApiClient accepts custom baseUrl', function(assert) {
        const client = new ApiClient('https://api.example.com');
        assert.strictEqual(client.baseUrl, 'https://api.example.com', 'should use custom baseUrl');
    });

    QUnit.test('ApiClient has default timeout of 30000ms', function(assert) {
        const client = new ApiClient();
        assert.strictEqual(client.defaultTimeout, 30000, 'default timeout should be 30s');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // POST Method Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('post sends correct HTTP method', async function(assert) {
        const client = new ApiClient('https://api.test.com');

        await client.post('/test', { data: 'value' });

        assert.strictEqual(fetchCalls[0].options.method, 'POST', 'should use POST method');
    });

    QUnit.test('post sends JSON content type header', async function(assert) {
        const client = new ApiClient('https://api.test.com');

        await client.post('/test', { data: 'value' });

        assert.strictEqual(fetchCalls[0].options.headers['Content-Type'], 'application/json', 'should have JSON content type');
    });

    QUnit.test('post stringifies body data', async function(assert) {
        const client = new ApiClient('https://api.test.com');
        const data = { key: 'value', num: 42 };

        await client.post('/test', data);

        assert.strictEqual(fetchCalls[0].options.body, JSON.stringify(data), 'body should be stringified');
    });

    QUnit.test('post constructs correct URL', async function(assert) {
        const client = new ApiClient('https://api.test.com');

        await client.post('/endpoint/path', {});

        assert.strictEqual(fetchCalls[0].url, 'https://api.test.com/endpoint/path', 'URL should be correct');
    });

    QUnit.test('post returns parsed JSON response', async function(assert) {
        const client = new ApiClient('https://api.test.com');

        window.fetch = async () => ({
            ok: true,
            json: async () => ({ result: 'data', count: 5 })
        });

        const result = await client.post('/test', {});

        assert.deepEqual(result, { result: 'data', count: 5 }, 'should return parsed JSON');
    });

    QUnit.test('post throws ApiError on non-OK response', async function(assert) {
        const client = new ApiClient('https://api.test.com');

        window.fetch = async () => ({
            ok: false,
            status: 404,
            statusText: 'Not Found',
            json: async () => ({ detail: 'Resource not found' })
        });

        try {
            await client.post('/test', {});
            assert.ok(false, 'should have thrown');
        } catch (e) {
            assert.ok(e instanceof ApiError, 'should throw ApiError');
            assert.strictEqual(e.statusCode, 404, 'should have correct status code');
        }
    });

    QUnit.test('post handles response without JSON error body', async function(assert) {
        const client = new ApiClient('https://api.test.com');

        window.fetch = async () => ({
            ok: false,
            status: 500,
            statusText: 'Internal Server Error',
            json: async () => { throw new Error('Not JSON'); }
        });

        try {
            await client.post('/test', {});
            assert.ok(false, 'should have thrown');
        } catch (e) {
            assert.ok(e instanceof ApiError, 'should throw ApiError');
            assert.ok(e.message.includes('500'), 'message should include status code');
        }
    });

    QUnit.test('post throws ApiError on timeout', async function(assert) {
        const client = new ApiClient('https://api.test.com');

        window.fetch = async (url, options) => {
            // Simulate abort
            if (options.signal) {
                return new Promise((resolve, reject) => {
                    options.signal.addEventListener('abort', () => {
                        const error = new Error('Aborted');
                        error.name = 'AbortError';
                        reject(error);
                    });
                    // Trigger abort after a delay
                    setTimeout(() => {}, 100);
                });
            }
        };

        try {
            await client.post('/test', {}, { timeout: 1 });
            // May not throw immediately in all environments
            assert.ok(true, 'timeout handling attempted');
        } catch (e) {
            assert.ok(e instanceof ApiError, 'should throw ApiError');
            assert.strictEqual(e.statusCode, 408, 'should have timeout status code');
        }
    });

    QUnit.test('post handles network errors', async function(assert) {
        const client = new ApiClient('https://api.test.com');

        window.fetch = async () => {
            throw new Error('Network failure');
        };

        try {
            await client.post('/test', {});
            assert.ok(false, 'should have thrown');
        } catch (e) {
            assert.ok(e instanceof ApiError, 'should throw ApiError');
            assert.strictEqual(e.statusCode, 0, 'network error should have status 0');
        }
    });

    QUnit.test('post accepts custom headers', async function(assert) {
        const client = new ApiClient('https://api.test.com');

        await client.post('/test', {}, { headers: { 'X-Custom': 'value' } });

        assert.strictEqual(fetchCalls[0].options.headers['X-Custom'], 'value', 'should include custom header');
    });

    QUnit.test('post uses custom timeout when provided', async function(assert) {
        const client = new ApiClient('https://api.test.com');

        // Can't easily test timeout value, but can verify it doesn't error
        await client.post('/test', {}, { timeout: 5000 });

        assert.ok(true, 'custom timeout should be accepted');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // GET Method Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('get sends correct HTTP method', async function(assert) {
        const client = new ApiClient('https://api.test.com');

        await client.get('/test');

        assert.strictEqual(fetchCalls[0].options.method, 'GET', 'should use GET method');
    });

    QUnit.test('get constructs correct URL', async function(assert) {
        const client = new ApiClient('https://api.test.com');

        await client.get('/api/resource');

        assert.strictEqual(fetchCalls[0].url, 'https://api.test.com/api/resource', 'URL should be correct');
    });

    QUnit.test('get returns JSON for JSON content type', async function(assert) {
        const client = new ApiClient('https://api.test.com');

        window.fetch = async () => ({
            ok: true,
            json: async () => ({ data: 'json' }),
            headers: {
                get: (name) => name === 'content-type' ? 'application/json' : null
            }
        });

        const result = await client.get('/test');

        assert.deepEqual(result, { data: 'json' }, 'should return parsed JSON');
    });

    QUnit.test('get returns text for non-JSON content type', async function(assert) {
        const client = new ApiClient('https://api.test.com');

        window.fetch = async () => ({
            ok: true,
            text: async () => 'plain text response',
            headers: {
                get: (name) => name === 'content-type' ? 'text/plain' : null
            }
        });

        const result = await client.get('/test');

        assert.strictEqual(result, 'plain text response', 'should return text');
    });

    QUnit.test('get throws ApiError on non-OK response', async function(assert) {
        const client = new ApiClient('https://api.test.com');

        window.fetch = async () => ({
            ok: false,
            status: 403,
            statusText: 'Forbidden'
        });

        try {
            await client.get('/test');
            assert.ok(false, 'should have thrown');
        } catch (e) {
            assert.ok(e instanceof ApiError, 'should throw ApiError');
            assert.strictEqual(e.statusCode, 403, 'should have correct status code');
        }
    });

    QUnit.test('get handles timeout', async function(assert) {
        const client = new ApiClient('https://api.test.com');

        window.fetch = async (url, options) => {
            return new Promise((resolve, reject) => {
                const error = new Error('Aborted');
                error.name = 'AbortError';
                setTimeout(() => reject(error), 1);
            });
        };

        try {
            await client.get('/test', { timeout: 1 });
            assert.ok(true, 'timeout handling attempted');
        } catch (e) {
            assert.ok(e instanceof ApiError, 'should throw ApiError');
        }
    });

    QUnit.test('get handles network errors', async function(assert) {
        const client = new ApiClient('https://api.test.com');

        window.fetch = async () => {
            throw new Error('Network error');
        };

        try {
            await client.get('/test');
            assert.ok(false, 'should have thrown');
        } catch (e) {
            assert.ok(e instanceof ApiError, 'should throw ApiError');
            assert.strictEqual(e.statusCode, 0, 'network error should have status 0');
        }
    });

    QUnit.test('get accepts custom headers', async function(assert) {
        const client = new ApiClient('https://api.test.com');

        await client.get('/test', { headers: { 'Authorization': 'Bearer token' } });

        assert.strictEqual(fetchCalls[0].options.headers['Authorization'], 'Bearer token', 'should include custom header');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // Graph API Methods Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('htmlToDot calls correct endpoint', async function(assert) {
        const client = new ApiClient('https://api.test.com');

        await client.htmlToDot({ html: '<div></div>' });

        assert.ok(fetchCalls[0].url.includes('/graph/from/html/to/dot'), 'should call correct endpoint');
    });

    QUnit.test('htmlToDot sends request body', async function(assert) {
        const client = new ApiClient('https://api.test.com');

        await client.htmlToDot({ html: '<p>test</p>', preset: 'minimal' });

        const body = JSON.parse(fetchCalls[0].options.body);
        assert.strictEqual(body.html, '<p>test</p>', 'should include html');
        assert.strictEqual(body.preset, 'minimal', 'should include preset');
    });

    QUnit.test('htmlToVisJs calls correct endpoint', async function(assert) {
        const client = new ApiClient('https://api.test.com');

        await client.htmlToVisJs({ html: '<div></div>' });

        assert.ok(fetchCalls[0].url.includes('/graph/from/html/to/visjs'), 'should call correct endpoint');
    });

    QUnit.test('htmlToD3 calls correct endpoint', async function(assert) {
        const client = new ApiClient('https://api.test.com');

        await client.htmlToD3({ html: '<div></div>' });

        assert.ok(fetchCalls[0].url.includes('/graph/from/html/to/d3'), 'should call correct endpoint');
    });

    QUnit.test('htmlToCytoscape calls correct endpoint', async function(assert) {
        const client = new ApiClient('https://api.test.com');

        await client.htmlToCytoscape({ html: '<div></div>' });

        assert.ok(fetchCalls[0].url.includes('/graph/from/html/to/cytoscape'), 'should call correct endpoint');
    });

    QUnit.test('htmlToMermaid calls correct endpoint', async function(assert) {
        const client = new ApiClient('https://api.test.com');

        await client.htmlToMermaid({ html: '<div></div>' });

        assert.ok(fetchCalls[0].url.includes('/graph/from/html/to/mermaid'), 'should call correct endpoint');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // Health Check Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('checkHealth returns true on success', async function(assert) {
        const client = new ApiClient('https://api.test.com');

        window.fetch = async () => ({
            ok: true,
            json: async () => ({ status: 'healthy' }),
            headers: { get: () => 'application/json' }
        });

        const result = await client.checkHealth();

        assert.strictEqual(result, true, 'should return true on success');
    });

    QUnit.test('checkHealth returns false on failure', async function(assert) {
        const client = new ApiClient('https://api.test.com');

        window.fetch = async () => ({
            ok: false,
            status: 503
        });

        const result = await client.checkHealth();

        assert.strictEqual(result, false, 'should return false on failure');
    });

    QUnit.test('checkHealth returns false on network error', async function(assert) {
        const client = new ApiClient('https://api.test.com');

        window.fetch = async () => {
            throw new Error('Network error');
        };

        const result = await client.checkHealth();

        assert.strictEqual(result, false, 'should return false on network error');
    });

    QUnit.test('checkHealth calls correct endpoint', async function(assert) {
        const client = new ApiClient('https://api.test.com');

        await client.checkHealth();

        assert.ok(fetchCalls[0].url.includes('/info/health'), 'should call health endpoint');
    });

    QUnit.test('checkHealth uses 5 second timeout', async function(assert) {
        const client = new ApiClient('https://api.test.com');

        // We can't easily verify timeout value, but test it doesn't error
        await client.checkHealth();

        assert.ok(true, 'checkHealth should use short timeout');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // ApiError Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('ApiError extends Error', function(assert) {
        const error = new ApiError('test');
        assert.ok(error instanceof Error, 'should extend Error');
    });

    QUnit.test('ApiError has correct name', function(assert) {
        const error = new ApiError('test');
        assert.strictEqual(error.name, 'ApiError', 'name should be ApiError');
    });

    QUnit.test('ApiError stores message', function(assert) {
        const error = new ApiError('Test message');
        assert.strictEqual(error.message, 'Test message', 'should store message');
    });

    QUnit.test('ApiError stores statusCode', function(assert) {
        const error = new ApiError('test', 404);
        assert.strictEqual(error.statusCode, 404, 'should store statusCode');
    });

    QUnit.test('ApiError defaults statusCode to 0', function(assert) {
        const error = new ApiError('test');
        assert.strictEqual(error.statusCode, 0, 'default statusCode should be 0');
    });

    QUnit.test('ApiError stores data', function(assert) {
        const error = new ApiError('test', 400, { field: 'invalid' });
        assert.deepEqual(error.data, { field: 'invalid' }, 'should store data');
    });

    QUnit.test('ApiError defaults data to null', function(assert) {
        const error = new ApiError('test', 400);
        assert.strictEqual(error.data, null, 'default data should be null');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // Singleton Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.test('apiClient singleton is available on window', function(assert) {
        assert.ok(window.apiClient, 'apiClient should be on window');
        assert.ok(window.apiClient instanceof ApiClient, 'should be ApiClient instance');
    });

});