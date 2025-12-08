/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Test Suite - API Client Tests
   v0.2.0 - Consolidated from v0.1.x
   ═══════════════════════════════════════════════════════════════════════════════ */

QUnit.module('API Client', function(hooks) {
    
    hooks.before(async function(assert) {
        // Load the API client
        await TestUtils.loadScript(TestPaths.apiClient);
        assert.ok(window.apiClient, 'apiClient should be globally available');
    });
    
    hooks.afterEach(function() {
        TestUtils.cleanup();
    });

    QUnit.test('apiClient exists and has required methods', function(assert) {
        assert.ok(apiClient, 'apiClient should exist');
        assert.ok(typeof apiClient.post === 'function', 'should have post method');
        assert.ok(typeof apiClient.get === 'function', 'should have get method');
        assert.ok(typeof apiClient.checkHealth === 'function', 'should have checkHealth method');
        assert.ok(typeof apiClient.htmlToDot === 'function', 'should have htmlToDot method');
    });
    
    QUnit.test('apiClient has all graph conversion methods', function(assert) {
        assert.ok(typeof apiClient.htmlToVisJs === 'function', 'should have htmlToVisJs method');
        assert.ok(typeof apiClient.htmlToD3 === 'function', 'should have htmlToD3 method');
        assert.ok(typeof apiClient.htmlToCytoscape === 'function', 'should have htmlToCytoscape method');
        assert.ok(typeof apiClient.htmlToMermaid === 'function', 'should have htmlToMermaid method');
    });
    
    QUnit.test('apiClient has correct default configuration', function(assert) {
        assert.ok(apiClient.baseUrl !== undefined, 'should have baseUrl');
        assert.ok(apiClient.defaultTimeout > 0, 'should have positive timeout');
        assert.strictEqual(apiClient.defaultTimeout, 30000, 'default timeout should be 30 seconds');
    });
    
    QUnit.test('ApiError class exists and works correctly', function(assert) {
        assert.ok(typeof ApiError === 'function', 'ApiError should exist');
        
        const error = new ApiError('Test error', 404, { detail: 'Not found' });
        assert.strictEqual(error.message, 'Test error', 'should have correct message');
        assert.strictEqual(error.statusCode, 404, 'should have correct status code');
        assert.deepEqual(error.data, { detail: 'Not found' }, 'should have correct data');
        assert.strictEqual(error.name, 'ApiError', 'should have correct name');
    });
    
    QUnit.test('ApiClient can be instantiated with custom baseUrl', function(assert) {
        const customClient = new ApiClient('https://custom.example.com');
        assert.strictEqual(customClient.baseUrl, 'https://custom.example.com', 'should use custom baseUrl');
    });

});
