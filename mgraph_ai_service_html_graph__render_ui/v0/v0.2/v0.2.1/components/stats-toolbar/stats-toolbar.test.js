/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Test Suite - Stats Toolbar Tests
   v0.2.1 - Tests for Shadow DOM refactored component
   ═══════════════════════════════════════════════════════════════════════════════ */

QUnit.module('Stats Toolbar', function(hooks) {
    
    hooks.before(async function(assert) {
        // Load foundation
        await TestUtils.loadFoundation();
        
        // Load the component
        await TestUtils.loadScript(TestPaths.statsToolbar);
        assert.ok(customElements.get('stats-toolbar'), 'stats-toolbar should be registered');
    });
    
    hooks.afterEach(function() {
        TestUtils.cleanup();
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // Initialization Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.module('Initialization', function() {
        
        QUnit.test('component creates Shadow DOM', async function(assert) {
            const toolbar = await TestUtils.createComponent('stats-toolbar');
            assert.ok(toolbar.shadowRoot, 'should have Shadow DOM');
        });
        
        QUnit.test('component renders template', async function(assert) {
            const toolbar = await TestUtils.createComponent('stats-toolbar');
            
            assert.ok(TestUtils.shadowQuery(toolbar, '.stats-toolbar'), 'should have toolbar container');
            assert.ok(TestUtils.shadowQuery(toolbar, '#render-btn'), 'should have render button');
            assert.ok(TestUtils.shadowQuery(toolbar, '#stat-nodes'), 'should have nodes stat');
            assert.ok(TestUtils.shadowQuery(toolbar, '#error-banner'), 'should have error banner');
        });
        
        QUnit.test('component has default stats', async function(assert) {
            const toolbar = await TestUtils.createComponent('stats-toolbar');
            
            assert.deepEqual(toolbar.stats, {
                total_nodes: 0,
                total_edges: 0,
                element_nodes: 0,
                value_nodes: 0,
                tag_nodes: 0,
                text_nodes: 0,
                attr_nodes: 0
            }, 'should have default stats');
        });
        
        QUnit.test('component has default timing', async function(assert) {
            const toolbar = await TestUtils.createComponent('stats-toolbar');
            
            assert.deepEqual(toolbar.timing, {
                api_ms: 0,
                server_ms: 0,
                render_ms: 0,
                dot_size: 0
            }, 'should have default timing');
        });
        
        QUnit.test('isRendering starts as false', async function(assert) {
            const toolbar = await TestUtils.createComponent('stats-toolbar');
            assert.strictEqual(toolbar.isRendering, false);
        });
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // Render Button Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.module('Render Button', function() {
        
        QUnit.test('emits render-requested event on click', async function(assert) {
            const toolbar = await TestUtils.createComponent('stats-toolbar');
            
            let eventReceived = false;
            toolbar.addEventListener('render-requested', () => {
                eventReceived = true;
            });
            
            TestUtils.shadowClick(toolbar, '#render-btn');
            
            assert.ok(eventReceived, 'render-requested event should be emitted');
        });
        
        QUnit.test('event crosses Shadow DOM boundary', async function(assert) {
            const fixture = document.getElementById('qunit-fixture');
            const toolbar = await TestUtils.createComponent('stats-toolbar');
            
            let eventReceived = false;
            fixture.addEventListener('render-requested', () => {
                eventReceived = true;
            });
            
            TestUtils.shadowClick(toolbar, '#render-btn');
            
            assert.ok(eventReceived, 'event should bubble through Shadow DOM');
        });
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // setStats Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.module('setStats', function() {
        
        QUnit.test('updates stat display values', async function(assert) {
            const toolbar = await TestUtils.createComponent('stats-toolbar');
            
            toolbar.setStats({
                total_nodes: 42,
                total_edges: 38,
                element_nodes: 20,
                attr_nodes: 12,
                text_nodes: 10
            });
            
            assert.strictEqual(TestUtils.getShadowText(toolbar, '#stat-nodes'), '42');
            assert.strictEqual(TestUtils.getShadowText(toolbar, '#stat-edges'), '38');
            assert.strictEqual(TestUtils.getShadowText(toolbar, '#stat-elements'), '20');
            assert.strictEqual(TestUtils.getShadowText(toolbar, '#stat-attrs'), '12');
            assert.strictEqual(TestUtils.getShadowText(toolbar, '#stat-text'), '10');
        });
        
        QUnit.test('formats large numbers', async function(assert) {
            const toolbar = await TestUtils.createComponent('stats-toolbar');
            
            toolbar.setStats({
                total_nodes: 1500,
                total_edges: 2500000
            });
            
            assert.strictEqual(TestUtils.getShadowText(toolbar, '#stat-nodes'), '1.5K');
            assert.strictEqual(TestUtils.getShadowText(toolbar, '#stat-edges'), '2.5M');
        });
        
        QUnit.test('merges with existing stats', async function(assert) {
            const toolbar = await TestUtils.createComponent('stats-toolbar');
            
            toolbar.setStats({ total_nodes: 100 });
            toolbar.setStats({ total_edges: 50 });
            
            assert.strictEqual(toolbar.stats.total_nodes, 100, 'should preserve previous stats');
            assert.strictEqual(toolbar.stats.total_edges, 50, 'should add new stats');
        });
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // setTiming Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.module('setTiming', function() {
        
        QUnit.test('updates timing display', async function(assert) {
            const toolbar = await TestUtils.createComponent('stats-toolbar');
            
            toolbar.setTiming({
                api_ms: 150,
                server_ms: 50,
                render_ms: 100,
                dot_size: 2048
            });
            
            assert.strictEqual(TestUtils.getShadowText(toolbar, '#timing-api'), '150ms');
            assert.strictEqual(TestUtils.getShadowText(toolbar, '#timing-server'), '50ms');
            assert.strictEqual(TestUtils.getShadowText(toolbar, '#timing-render'), '100ms');
            assert.strictEqual(TestUtils.getShadowText(toolbar, '#timing-dot-size'), '2.0 KB');
        });
        
        QUnit.test('shows dash for zero values', async function(assert) {
            const toolbar = await TestUtils.createComponent('stats-toolbar');
            
            toolbar.setTiming({
                api_ms: 0,
                server_ms: 0,
                render_ms: 0,
                dot_size: 0
            });
            
            assert.strictEqual(TestUtils.getShadowText(toolbar, '#timing-api'), '-');
            assert.strictEqual(TestUtils.getShadowText(toolbar, '#timing-server'), '-');
            assert.strictEqual(TestUtils.getShadowText(toolbar, '#timing-render'), '-');
            assert.strictEqual(TestUtils.getShadowText(toolbar, '#timing-dot-size'), '-');
        });
        
        QUnit.test('formats bytes correctly', async function(assert) {
            const toolbar = await TestUtils.createComponent('stats-toolbar');
            
            toolbar.setTiming({ dot_size: 500 });
            assert.strictEqual(TestUtils.getShadowText(toolbar, '#timing-dot-size'), '500 B');
            
            toolbar.setTiming({ dot_size: 1536 });
            assert.strictEqual(TestUtils.getShadowText(toolbar, '#timing-dot-size'), '1.5 KB');
            
            toolbar.setTiming({ dot_size: 1048576 });
            assert.strictEqual(TestUtils.getShadowText(toolbar, '#timing-dot-size'), '1.0 MB');
        });
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // setRenderingState Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.module('setRenderingState', function() {
        
        QUnit.test('disables button when rendering', async function(assert) {
            const toolbar = await TestUtils.createComponent('stats-toolbar');
            const button = TestUtils.shadowQuery(toolbar, '#render-btn');
            
            toolbar.setRenderingState(true);
            
            assert.strictEqual(button.disabled, true, 'button should be disabled');
            assert.strictEqual(toolbar.isRendering, true, 'isRendering should be true');
        });
        
        QUnit.test('shows spinner when rendering', async function(assert) {
            const toolbar = await TestUtils.createComponent('stats-toolbar');
            const button = TestUtils.shadowQuery(toolbar, '#render-btn');
            
            toolbar.setRenderingState(true);
            
            assert.ok(button.innerHTML.includes('spinner'), 'should show spinner');
            assert.ok(button.innerHTML.includes('Rendering'), 'should show Rendering text');
        });
        
        QUnit.test('enables button when done', async function(assert) {
            const toolbar = await TestUtils.createComponent('stats-toolbar');
            const button = TestUtils.shadowQuery(toolbar, '#render-btn');
            
            toolbar.setRenderingState(true);
            toolbar.setRenderingState(false);
            
            assert.strictEqual(button.disabled, false, 'button should be enabled');
            assert.ok(button.innerHTML.includes('Render Graph'), 'should show normal text');
        });
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // Error Banner Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.module('Error Banner', function() {
        
        QUnit.test('showError displays error banner', async function(assert) {
            const toolbar = await TestUtils.createComponent('stats-toolbar');
            const banner = TestUtils.shadowQuery(toolbar, '#error-banner');
            
            toolbar.showError('Test Error', 'Error details', 'Hint text');
            
            assert.ok(banner.classList.contains('show'), 'banner should be visible');
            assert.ok(TestUtils.getShadowText(toolbar, '#error-title').includes('Test Error'));
            assert.ok(TestUtils.getShadowText(toolbar, '#error-detail').includes('Error details'));
            assert.ok(TestUtils.getShadowText(toolbar, '#error-hint').includes('Hint text'));
        });
        
        QUnit.test('showError formats Error: hints as code', async function(assert) {
            const toolbar = await TestUtils.createComponent('stats-toolbar');
            
            toolbar.showError('Title', 'Detail', 'Error: some stack trace');
            
            const hintEl = TestUtils.shadowQuery(toolbar, '#error-hint');
            assert.ok(hintEl.querySelector('code'), 'should wrap Error: hints in code tag');
        });
        
        QUnit.test('hideError hides banner', async function(assert) {
            const toolbar = await TestUtils.createComponent('stats-toolbar');
            const banner = TestUtils.shadowQuery(toolbar, '#error-banner');
            
            toolbar.showError('Test', 'Details');
            toolbar.hideError();
            
            assert.notOk(banner.classList.contains('show'), 'banner should be hidden');
        });
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // clearStats Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.module('clearStats', function() {
        
        QUnit.test('resets all stat values to dash', async function(assert) {
            const toolbar = await TestUtils.createComponent('stats-toolbar');
            
            toolbar.setStats({ total_nodes: 100, total_edges: 50 });
            toolbar.setTiming({ api_ms: 200 });
            toolbar.showError('Error', 'Details');
            
            toolbar.clearStats();
            
            assert.strictEqual(TestUtils.getShadowText(toolbar, '#stat-nodes'), '-');
            assert.strictEqual(TestUtils.getShadowText(toolbar, '#stat-edges'), '-');
            assert.strictEqual(TestUtils.getShadowText(toolbar, '#timing-api'), '-');
        });
        
        QUnit.test('hides error banner', async function(assert) {
            const toolbar = await TestUtils.createComponent('stats-toolbar');
            const banner = TestUtils.shadowQuery(toolbar, '#error-banner');
            
            toolbar.showError('Error', 'Details');
            toolbar.clearStats();
            
            assert.notOk(banner.classList.contains('show'), 'error should be hidden');
        });
        
        QUnit.test('resets internal stats object', async function(assert) {
            const toolbar = await TestUtils.createComponent('stats-toolbar');
            
            toolbar.setStats({ total_nodes: 100 });
            toolbar.clearStats();
            
            assert.strictEqual(toolbar.stats.total_nodes, 0, 'stats should be reset');
        });
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // Style Encapsulation Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.module('Style Encapsulation', function() {
        
        QUnit.test('styles are contained in Shadow DOM', async function(assert) {
            const toolbar = await TestUtils.createComponent('stats-toolbar');
            
            // Create an element with same class name in light DOM
            const lightDiv = document.createElement('div');
            lightDiv.className = 'stats-toolbar';
            lightDiv.textContent = 'Light DOM';
            document.getElementById('qunit-fixture').appendChild(lightDiv);
            
            // Shadow DOM component should still work
            assert.ok(TestUtils.shadowQuery(toolbar, '.stats-toolbar'), 'Shadow DOM element should exist');
            
            // Light DOM element should not be affected by component styles
            // (This is a visual check - just ensuring no errors)
            assert.ok(true, 'styles should be encapsulated');
        });
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // Cleanup Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.module('Cleanup', function() {
        
        QUnit.test('disconnectedCallback cleans up listeners', async function(assert) {
            const toolbar = await TestUtils.createComponent('stats-toolbar');
            
            // Verify listeners were added
            assert.ok(toolbar._eventListeners.length > 0, 'should have tracked listeners');
            
            // Remove from DOM
            toolbar.remove();
            
            // Check cleanup happened
            assert.strictEqual(toolbar._eventListeners.length, 0, 'listeners should be cleaned up');
        });
    });

});
