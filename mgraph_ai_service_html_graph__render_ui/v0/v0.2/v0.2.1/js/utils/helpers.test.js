/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Test Suite - Helpers Tests
   v0.2.1 - Tests for shared utility functions
   ═══════════════════════════════════════════════════════════════════════════════ */

QUnit.module('Helpers', function(hooks) {
    
    hooks.before(async function(assert) {
        await TestUtils.loadScript(TestPaths.helpers);
        assert.ok(window.Helpers, 'Helpers should be globally available');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // escapeHtml Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.module('escapeHtml', function() {
        
        QUnit.test('escapes angle brackets', function(assert) {
            const result = Helpers.escapeHtml('<div>test</div>');
            assert.ok(result.includes('&lt;'), 'should escape <');
            assert.ok(result.includes('&gt;'), 'should escape >');
        });
        
        QUnit.test('escapes ampersand', function(assert) {
            const result = Helpers.escapeHtml('a & b');
            assert.ok(result.includes('&amp;'), 'should escape &');
        });
        
        QUnit.test('escapes quotes', function(assert) {
            const result = Helpers.escapeHtml('"quoted"');
            assert.ok(result.includes('&quot;'), 'should escape "');
        });
        
        QUnit.test('handles empty string', function(assert) {
            assert.strictEqual(Helpers.escapeHtml(''), '', 'should return empty string');
        });
        
        QUnit.test('handles null', function(assert) {
            assert.strictEqual(Helpers.escapeHtml(null), '', 'should return empty string for null');
        });
        
        QUnit.test('handles undefined', function(assert) {
            assert.strictEqual(Helpers.escapeHtml(undefined), '', 'should return empty string for undefined');
        });
        
        QUnit.test('preserves plain text', function(assert) {
            assert.strictEqual(Helpers.escapeHtml('Hello World'), 'Hello World', 'should preserve plain text');
        });
        
        QUnit.test('handles numbers', function(assert) {
            assert.strictEqual(Helpers.escapeHtml(42), '42', 'should convert number to string');
        });
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // formatNumber Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.module('formatNumber', function() {
        
        QUnit.test('formats small numbers unchanged', function(assert) {
            assert.strictEqual(Helpers.formatNumber(0), '0');
            assert.strictEqual(Helpers.formatNumber(42), '42');
            assert.strictEqual(Helpers.formatNumber(999), '999');
        });
        
        QUnit.test('formats thousands as K', function(assert) {
            assert.strictEqual(Helpers.formatNumber(1000), '1.0K');
            assert.strictEqual(Helpers.formatNumber(1500), '1.5K');
            assert.strictEqual(Helpers.formatNumber(999999), '1000.0K');
        });
        
        QUnit.test('formats millions as M', function(assert) {
            assert.strictEqual(Helpers.formatNumber(1000000), '1.0M');
            assert.strictEqual(Helpers.formatNumber(2500000), '2.5M');
        });
        
        QUnit.test('handles null', function(assert) {
            assert.strictEqual(Helpers.formatNumber(null), '0');
        });
        
        QUnit.test('handles undefined', function(assert) {
            assert.strictEqual(Helpers.formatNumber(undefined), '0');
        });
        
        QUnit.test('handles NaN', function(assert) {
            assert.strictEqual(Helpers.formatNumber(NaN), '0');
        });
        
        QUnit.test('handles string numbers', function(assert) {
            assert.strictEqual(Helpers.formatNumber('1500'), '1.5K');
        });
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // formatBytes Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.module('formatBytes', function() {
        
        QUnit.test('formats bytes', function(assert) {
            assert.strictEqual(Helpers.formatBytes(0), '0 B');
            assert.strictEqual(Helpers.formatBytes(500), '500 B');
            assert.strictEqual(Helpers.formatBytes(1023), '1023 B');
        });
        
        QUnit.test('formats kilobytes', function(assert) {
            assert.strictEqual(Helpers.formatBytes(1024), '1.0 KB');
            assert.strictEqual(Helpers.formatBytes(1536), '1.5 KB');
            assert.strictEqual(Helpers.formatBytes(1048575), '1024.0 KB');
        });
        
        QUnit.test('formats megabytes', function(assert) {
            assert.strictEqual(Helpers.formatBytes(1048576), '1.0 MB');
            assert.strictEqual(Helpers.formatBytes(2621440), '2.5 MB');
        });
        
        QUnit.test('handles null', function(assert) {
            assert.strictEqual(Helpers.formatBytes(null), '0 B');
        });
        
        QUnit.test('handles undefined', function(assert) {
            assert.strictEqual(Helpers.formatBytes(undefined), '0 B');
        });
        
        QUnit.test('handles NaN', function(assert) {
            assert.strictEqual(Helpers.formatBytes(NaN), '0 B');
        });
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // isValidUrl Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.module('isValidUrl', function() {
        
        QUnit.test('accepts https URLs', function(assert) {
            assert.strictEqual(Helpers.isValidUrl('https://example.com'), true);
            assert.strictEqual(Helpers.isValidUrl('https://sub.example.com/path'), true);
        });
        
        QUnit.test('accepts http URLs', function(assert) {
            assert.strictEqual(Helpers.isValidUrl('http://example.com'), true);
        });
        
        QUnit.test('rejects ftp URLs', function(assert) {
            assert.strictEqual(Helpers.isValidUrl('ftp://example.com'), false);
        });
        
        QUnit.test('rejects invalid URLs', function(assert) {
            assert.strictEqual(Helpers.isValidUrl('not-a-url'), false);
            assert.strictEqual(Helpers.isValidUrl('example.com'), false);
        });
        
        QUnit.test('rejects empty string', function(assert) {
            assert.strictEqual(Helpers.isValidUrl(''), false);
        });
        
        QUnit.test('rejects null', function(assert) {
            assert.strictEqual(Helpers.isValidUrl(null), false);
        });
        
        QUnit.test('rejects undefined', function(assert) {
            assert.strictEqual(Helpers.isValidUrl(undefined), false);
        });
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // debounce Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.module('debounce', function() {
        
        QUnit.test('delays function execution', async function(assert) {
            let callCount = 0;
            const debouncedFn = Helpers.debounce(() => callCount++, 50);
            
            debouncedFn();
            debouncedFn();
            debouncedFn();
            
            assert.strictEqual(callCount, 0, 'should not call immediately');
            
            await TestUtils.wait(100);
            
            assert.strictEqual(callCount, 1, 'should call once after delay');
        });
        
        QUnit.test('resets delay on each call', async function(assert) {
            let callCount = 0;
            const debouncedFn = Helpers.debounce(() => callCount++, 50);
            
            debouncedFn();
            await TestUtils.wait(30);
            debouncedFn();
            await TestUtils.wait(30);
            debouncedFn();
            
            assert.strictEqual(callCount, 0, 'should not call while being reset');
            
            await TestUtils.wait(100);
            
            assert.strictEqual(callCount, 1, 'should call once after final delay');
        });
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // nextFrame Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.module('nextFrame', function() {
        
        QUnit.test('returns a promise', function(assert) {
            const result = Helpers.nextFrame();
            assert.ok(result instanceof Promise, 'should return a Promise');
        });
        
        QUnit.test('resolves on next frame', async function(assert) {
            const start = performance.now();
            await Helpers.nextFrame();
            const end = performance.now();
            
            assert.ok(end > start, 'should resolve after some time');
        });
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // wait Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.module('wait', function() {
        
        QUnit.test('waits for specified time', async function(assert) {
            const start = performance.now();
            await Helpers.wait(50);
            const end = performance.now();
            
            assert.ok(end - start >= 45, 'should wait at least ~50ms');
        });
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // Frozen Object Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.module('Object Immutability', function() {
        
        QUnit.test('Helpers object is frozen', function(assert) {
            assert.ok(Object.isFrozen(Helpers), 'Helpers should be frozen');
        });
        
        QUnit.test('cannot add new properties', function(assert) {
            try {
                Helpers.newMethod = () => {};
            } catch (e) {
                // Expected in strict mode
            }
            assert.notOk(Helpers.newMethod, 'should not be able to add properties');
        });
    });

});
