/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Test Suite - Dashboard Tests
   v0.2.0 - New tests to improve coverage
   ═══════════════════════════════════════════════════════════════════════════════ */

QUnit.module('Dashboard', function(hooks) {

    let originalApiClient;
    let originalSetInterval;
    let originalClearInterval;
    let intervalCallbacks = [];
    let clearedIntervals = [];

    hooks.before(async function(assert) {
        // Load API client first
        await TestUtils.loadScript(TestPaths.apiClient);

        // Load dashboard
        await TestUtils.loadScript(TestPaths.getComponentPath(TestPaths.VERSIONS.V0_2_0, 'js/dashboard.js'));

        assert.ok(typeof Dashboard === 'function', 'Dashboard class should be available');
    });

    hooks.beforeEach(function() {
        originalApiClient     = window.apiClient;
        originalSetInterval   = window.setInterval;
        originalClearInterval = window.clearInterval;
        intervalCallbacks     = [];
        clearedIntervals      = [];

        // Mock setInterval to track callbacks
        window.setInterval = function(callback, delay) {
            const id = intervalCallbacks.length + 1;
            intervalCallbacks.push({ id, callback, delay });
            return id;
        };

        // Mock clearInterval to track cleared intervals
        window.clearInterval = function(id) {
            clearedIntervals.push(id);
        };
    });

    hooks.afterEach(function() {
        window.apiClient     = originalApiClient;
        window.setInterval   = originalSetInterval;
        window.clearInterval = originalClearInterval;
        TestUtils.cleanup();
    });

    QUnit.test('Dashboard class exists', function(assert) {
        assert.ok(typeof Dashboard === 'function', 'Dashboard should be a function/class');
    });

    QUnit.test('constructor initializes properties to null', function(assert) {
        const dashboard = new Dashboard();

        assert.strictEqual(dashboard.statusDot, null, 'statusDot should be null');
        assert.strictEqual(dashboard.statusText, null, 'statusText should be null');
        assert.strictEqual(dashboard.checkInterval, null, 'checkInterval should be null');
    });

    QUnit.test('init sets up DOM element references', function(assert) {
        const fixture = document.getElementById('qunit-fixture');
        fixture.innerHTML = `
            <div id="api-status-dot"></div>
            <div id="api-status-text"></div>
        `;

        const dashboard = new Dashboard();
        dashboard.checkApiStatus = () => {}; // Mock to prevent actual API call
        dashboard.init();

        assert.ok(dashboard.statusDot, 'statusDot should be set');
        assert.ok(dashboard.statusText, 'statusText should be set');
    });

    QUnit.test('init calls checkApiStatus immediately', function(assert) {
        const fixture = document.getElementById('qunit-fixture');
        fixture.innerHTML = `
            <div id="api-status-dot"></div>
            <div id="api-status-text"></div>
        `;

        let checkApiStatusCalled = false;
        const dashboard = new Dashboard();
        dashboard.checkApiStatus = () => { checkApiStatusCalled = true; };
        dashboard.init();

        assert.ok(checkApiStatusCalled, 'checkApiStatus should be called on init');
    });

    QUnit.test('init sets up interval for periodic health checks', function(assert) {
        const fixture = document.getElementById('qunit-fixture');
        fixture.innerHTML = `
            <div id="api-status-dot"></div>
            <div id="api-status-text"></div>
        `;

        const dashboard = new Dashboard();
        dashboard.checkApiStatus = () => {};
        dashboard.init();

        assert.ok(intervalCallbacks.length > 0, 'setInterval should be called');
        assert.strictEqual(intervalCallbacks[0].delay, 30000, 'interval should be 30 seconds');
    });

    QUnit.test('checkApiStatus sets loading state', async function(assert) {
        const fixture = document.getElementById('qunit-fixture');
        fixture.innerHTML = `
            <div id="api-status-dot"></div>
            <div id="api-status-text"></div>
        `;

        window.apiClient = {
            checkHealth: async () => {
                return new Promise(resolve => setTimeout(() => resolve(true), 100));
            }
        };

        const dashboard = new Dashboard();
        dashboard.statusDot = fixture.querySelector('#api-status-dot');
        dashboard.statusText = fixture.querySelector('#api-status-text');

        const checkPromise = dashboard.checkApiStatus();

        // Check loading state was set
        assert.ok(dashboard.statusDot.className.includes('loading'), 'should set loading class');
        assert.strictEqual(dashboard.statusText.textContent, 'Checking...', 'should show Checking... text');

        await checkPromise;
    });

    QUnit.test('checkApiStatus shows Connected on success', async function(assert) {
        const fixture = document.getElementById('qunit-fixture');
        fixture.innerHTML = `
            <div id="api-status-dot"></div>
            <div id="api-status-text"></div>
        `;

        window.apiClient = {
            checkHealth: async () => true
        };
        assert.ok(await window.apiClient.checkHealth())

        const dashboard = new Dashboard();
        dashboard.statusDot = fixture.querySelector('#api-status-dot');
        dashboard.statusText = fixture.querySelector('#api-status-text');

        await dashboard.checkApiStatus();


        assert.strictEqual(dashboard.statusDot.className   , 'api-status-dot', 'should have default class (no error)');
        assert.strictEqual(dashboard.statusText.textContent, 'Connected', 'should show Connected text');
    });

    QUnit.test('checkApiStatus shows Disconnected on health check failure', async function(assert) {
        const fixture = document.getElementById('qunit-fixture');
        fixture.innerHTML = `
            <div id="api-status-dot"></div>
            <div id="api-status-text"></div>
        `;

        window.apiClient = {
            checkHealth: async () => false
        };

        const dashboard = new Dashboard();
        dashboard.statusDot = fixture.querySelector('#api-status-dot');
        dashboard.statusText = fixture.querySelector('#api-status-text');

        await dashboard.checkApiStatus();

        assert.ok(dashboard.statusDot.className.includes('error'), 'should have error class');
        assert.strictEqual(dashboard.statusText.textContent, 'Disconnected', 'should show Disconnected text');
    });

    QUnit.test('checkApiStatus shows Error on exception', async function(assert) {
        const fixture = document.getElementById('qunit-fixture');
        fixture.innerHTML = `
            <div id="api-status-dot"></div>
            <div id="api-status-text"></div>
        `;

        window.apiClient = {
            checkHealth: async () => { throw new Error('Network error'); }
        };

        const dashboard = new Dashboard();
        dashboard.statusDot = fixture.querySelector('#api-status-dot');
        dashboard.statusText = fixture.querySelector('#api-status-text');

        // Suppress console.error for this test
        const originalConsoleError = console.error;
        console.error = () => {};

        await dashboard.checkApiStatus();

        console.error = originalConsoleError;

        assert.ok(dashboard.statusDot.className.includes('error'), 'should have error class');
        assert.strictEqual(dashboard.statusText.textContent, 'Error', 'should show Error text');
    });

    QUnit.test('checkApiStatus does nothing if statusDot is null', async function(assert) {
        const dashboard = new Dashboard();
        dashboard.statusDot = null;
        dashboard.statusText = null;

        // Should not throw
        await dashboard.checkApiStatus();

        assert.ok(true, 'should not throw when elements are null');
    });

    QUnit.test('checkApiStatus does nothing if statusText is null', async function(assert) {
        const fixture = document.getElementById('qunit-fixture');
        fixture.innerHTML = `<div id="api-status-dot"></div>`;

        const dashboard = new Dashboard();
        dashboard.statusDot = fixture.querySelector('#api-status-dot');
        dashboard.statusText = null;

        // Should not throw
        await dashboard.checkApiStatus();

        assert.ok(true, 'should not throw when statusText is null');
    });

    QUnit.test('destroy clears the interval', function(assert) {
        const dashboard = new Dashboard();
        dashboard.checkInterval = 123;

        dashboard.destroy();

        assert.ok(clearedIntervals.includes(123), 'should clear the interval');
    });

    QUnit.test('destroy handles null interval', function(assert) {
        const dashboard = new Dashboard();
        dashboard.checkInterval = null;

        // Should not throw
        dashboard.destroy();

        assert.strictEqual(clearedIntervals.length, 0, 'should not try to clear null interval');
    });

    QUnit.test('init stores interval ID in checkInterval', function(assert) {
        const fixture = document.getElementById('qunit-fixture');
        fixture.innerHTML = `
            <div id="api-status-dot"></div>
            <div id="api-status-text"></div>
        `;

        const dashboard = new Dashboard();
        dashboard.checkApiStatus = () => {};
        dashboard.init();

        assert.ok(dashboard.checkInterval !== null, 'checkInterval should be set');
        assert.strictEqual(dashboard.checkInterval, 1, 'checkInterval should be the interval ID');
    });

    QUnit.test('interval callback calls checkApiStatus', function(assert) {
        const fixture = document.getElementById('qunit-fixture');
        fixture.innerHTML = `
            <div id="api-status-dot"></div>
            <div id="api-status-text"></div>
        `;

        let checkCount = 0;
        const dashboard = new Dashboard();
        dashboard.checkApiStatus = () => { checkCount++; };
        dashboard.init();

        // Reset count after init's immediate call
        checkCount = 0;

        // Simulate interval callback
        if (intervalCallbacks.length > 0) {
            intervalCallbacks[0].callback();
        }

        assert.strictEqual(checkCount, 1, 'interval callback should call checkApiStatus');
    });

});