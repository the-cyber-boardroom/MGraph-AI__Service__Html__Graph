/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Test Suite - Base Component Tests
   v0.2.1 - Tests for Shadow DOM base component class
   ═══════════════════════════════════════════════════════════════════════════════ */

QUnit.module('BaseComponent', function(hooks) {
    
    // Track registered elements to avoid re-registration errors
    let testComponentCounter = 0;
    
    hooks.before(async function(assert) {
        await TestUtils.loadFoundation();
        assert.ok(window.BaseComponent, 'BaseComponent should be globally available');
        assert.ok(window.Helpers, 'Helpers should be loaded');
        assert.ok(window.ComponentPaths, 'ComponentPaths should be loaded');
    });
    
    hooks.afterEach(function() {
        TestUtils.cleanup();
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // Constructor Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.module('Constructor', function() {
        
        QUnit.test('creates Shadow DOM', function(assert) {
            class TestComp extends BaseComponent {}
            const tagName = `test-shadow-${++testComponentCounter}`;
            customElements.define(tagName, TestComp);
            
            const el = document.createElement(tagName);
            assert.ok(el.shadowRoot, 'should have shadowRoot');
            assert.strictEqual(el.shadowRoot.mode, 'open', 'shadowRoot should be open');
        });
        
        QUnit.test('initializes event listeners array', function(assert) {
            class TestComp extends BaseComponent {}
            const tagName = `test-listeners-${++testComponentCounter}`;
            customElements.define(tagName, TestComp);
            
            const el = document.createElement(tagName);
            assert.ok(Array.isArray(el._eventListeners), '_eventListeners should be array');
            assert.strictEqual(el._eventListeners.length, 0, 'should start empty');
        });
        
        QUnit.test('initializes ready state to false', function(assert) {
            class TestComp extends BaseComponent {}
            const tagName = `test-ready-${++testComponentCounter}`;
            customElements.define(tagName, TestComp);
            
            const el = document.createElement(tagName);
            assert.strictEqual(el._isReady, false, '_isReady should be false');
            assert.strictEqual(el.isReady, false, 'isReady getter should return false');
        });
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // Query Helper Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.module('Query Helpers', function() {
        
        QUnit.test('$ queries Shadow DOM', function(assert) {
            class TestComp extends BaseComponent {}
            const tagName = `test-query-${++testComponentCounter}`;
            customElements.define(tagName, TestComp);
            
            const el = document.createElement(tagName);
            el.shadowRoot.innerHTML = '<div id="test-div">Hello</div>';
            
            const result = el.$('#test-div');
            assert.ok(result, 'should find element');
            assert.strictEqual(result.textContent, 'Hello');
        });
        
        QUnit.test('$$ queries all in Shadow DOM', function(assert) {
            class TestComp extends BaseComponent {}
            const tagName = `test-query-all-${++testComponentCounter}`;
            customElements.define(tagName, TestComp);
            
            const el = document.createElement(tagName);
            el.shadowRoot.innerHTML = '<span class="item">1</span><span class="item">2</span>';
            
            const results = el.$$('.item');
            assert.strictEqual(results.length, 2, 'should find all elements');
        });
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // Event Helper Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.module('Event Helpers', function() {
        
        QUnit.test('emit dispatches CustomEvent', function(assert) {
            class TestComp extends BaseComponent {}
            const tagName = `test-emit-${++testComponentCounter}`;
            customElements.define(tagName, TestComp);
            
            const el = document.createElement(tagName);
            
            let receivedEvent = null;
            el.addEventListener('test-event', (e) => {
                receivedEvent = e;
            });
            
            el.emit('test-event', { value: 42 });
            
            assert.ok(receivedEvent, 'event should be dispatched');
            assert.strictEqual(receivedEvent.detail.value, 42, 'should have detail');
        });
        
        QUnit.test('emit creates composed event', function(assert) {
            class TestComp extends BaseComponent {}
            const tagName = `test-emit-composed-${++testComponentCounter}`;
            customElements.define(tagName, TestComp);
            
            const el = document.createElement(tagName);
            
            let eventComposed = false;
            el.addEventListener('test-event', (e) => {
                eventComposed = e.composed;
            });
            
            el.emit('test-event');
            
            assert.ok(eventComposed, 'event should be composed');
        });
        
        QUnit.test('addTrackedListener tracks listener', function(assert) {
            class TestComp extends BaseComponent {}
            const tagName = `test-tracked-${++testComponentCounter}`;
            customElements.define(tagName, TestComp);
            
            const el = document.createElement(tagName);
            const btn = document.createElement('button');
            
            el.addTrackedListener(btn, 'click', () => {});
            
            assert.strictEqual(el._eventListeners.length, 1, 'should track listener');
        });
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // Utility Accessor Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.module('Utility Accessors', function() {
        
        QUnit.test('escapeHtml delegates to Helpers', function(assert) {
            class TestComp extends BaseComponent {}
            const tagName = `test-escape-${++testComponentCounter}`;
            customElements.define(tagName, TestComp);
            
            const el = document.createElement(tagName);
            const result = el.escapeHtml('<script>');
            
            assert.ok(result.includes('&lt;'), 'should escape HTML');
        });
        
        QUnit.test('formatNumber delegates to Helpers', function(assert) {
            class TestComp extends BaseComponent {}
            const tagName = `test-format-num-${++testComponentCounter}`;
            customElements.define(tagName, TestComp);
            
            const el = document.createElement(tagName);
            assert.strictEqual(el.formatNumber(1500), '1.5K');
        });
        
        QUnit.test('formatBytes delegates to Helpers', function(assert) {
            class TestComp extends BaseComponent {}
            const tagName = `test-format-bytes-${++testComponentCounter}`;
            customElements.define(tagName, TestComp);
            
            const el = document.createElement(tagName);
            assert.strictEqual(el.formatBytes(1024), '1.0 KB');
        });
        
        QUnit.test('isValidUrl delegates to Helpers', function(assert) {
            class TestComp extends BaseComponent {}
            const tagName = `test-valid-url-${++testComponentCounter}`;
            customElements.define(tagName, TestComp);
            
            const el = document.createElement(tagName);
            assert.strictEqual(el.isValidUrl('https://example.com'), true);
            assert.strictEqual(el.isValidUrl('invalid'), false);
        });
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // Cleanup Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.module('Cleanup', function() {
        
        QUnit.test('cleanup removes tracked listeners', function(assert) {
            class TestComp extends BaseComponent {}
            const tagName = `test-cleanup-${++testComponentCounter}`;
            customElements.define(tagName, TestComp);
            
            const el = document.createElement(tagName);
            const btn = document.createElement('button');
            
            let clickCount = 0;
            el.addTrackedListener(btn, 'click', () => clickCount++);
            
            btn.click();
            assert.strictEqual(clickCount, 1, 'listener should work before cleanup');
            
            el.cleanup();
            btn.click();
            assert.strictEqual(clickCount, 1, 'listener should be removed after cleanup');
        });
        
        QUnit.test('cleanup resets ready state', function(assert) {
            class TestComp extends BaseComponent {}
            const tagName = `test-cleanup-ready-${++testComponentCounter}`;
            customElements.define(tagName, TestComp);
            
            const el = document.createElement(tagName);
            el._isReady = true;
            
            el.cleanup();
            
            assert.strictEqual(el._isReady, false, 'isReady should be false after cleanup');
        });
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // whenReady Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.module('whenReady', function() {
        
        QUnit.test('resolves immediately if already ready', async function(assert) {
            class TestComp extends BaseComponent {}
            const tagName = `test-when-ready-${++testComponentCounter}`;
            customElements.define(tagName, TestComp);
            
            const el = document.createElement(tagName);
            el._isReady = true;
            
            await el.whenReady();
            assert.ok(true, 'should resolve immediately');
        });
        
        QUnit.test('rejects on timeout', async function(assert) {
            class TestComp extends BaseComponent {}
            const tagName = `test-when-ready-timeout-${++testComponentCounter}`;
            customElements.define(tagName, TestComp);
            
            const el = document.createElement(tagName);
            
            try {
                await el.whenReady(50);
                assert.ok(false, 'should have rejected');
            } catch (e) {
                assert.ok(e.message.includes('timeout'), 'should timeout');
            }
        });
        
        QUnit.test('resolves when component-ready fires', async function(assert) {
            class TestComp extends BaseComponent {}
            const tagName = `test-when-ready-event-${++testComponentCounter}`;
            customElements.define(tagName, TestComp);
            
            const el = document.createElement(tagName);
            
            // Simulate delayed ready
            setTimeout(() => {
                el._isReady = true;
                el.dispatchEvent(new CustomEvent('component-ready'));
            }, 20);
            
            await el.whenReady(100);
            assert.ok(true, 'should resolve on event');
        });
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // showError Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.module('showError', function() {
        
        QUnit.test('displays error in shadowRoot', function(assert) {
            class TestComp extends BaseComponent {}
            const tagName = `test-show-error-${++testComponentCounter}`;
            customElements.define(tagName, TestComp);
            
            const el = document.createElement(tagName);
            el.showError('Test error message');
            
            const errorDiv = el.shadowRoot.querySelector('.component-error');
            assert.ok(errorDiv, 'should show error container');
            assert.ok(el.shadowRoot.textContent.includes('Test error message'), 'should show message');
        });
        
        QUnit.test('escapes HTML in error message', function(assert) {
            class TestComp extends BaseComponent {}
            const tagName = `test-show-error-escape-${++testComponentCounter}`;
            customElements.define(tagName, TestComp);
            
            const el = document.createElement(tagName);
            el.showError('<script>alert("xss")</script>');
            
            assert.ok(!el.shadowRoot.innerHTML.includes('<script>'), 'should escape script tags');
        });
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // Lifecycle Hook Tests
    // ═══════════════════════════════════════════════════════════════════════════

    QUnit.module('Lifecycle Hooks', function() {
        
        QUnit.test('bindElements is called', function(assert) {
            let bindCalled = false;
            
            class TestComp extends BaseComponent {
                async loadResources() {
                    this.shadowRoot.innerHTML = '<div id="test"></div>';
                }
                bindElements() {
                    bindCalled = true;
                }
            }
            const tagName = `test-bind-${++testComponentCounter}`;
            customElements.define(tagName, TestComp);
            
            const el = document.createElement(tagName);
            document.getElementById('qunit-fixture').appendChild(el);
            
            return el.whenReady().then(() => {
                assert.ok(bindCalled, 'bindElements should be called');
            });
        });
        
        QUnit.test('setupEventListeners is called', function(assert) {
            let setupCalled = false;
            
            class TestComp extends BaseComponent {
                async loadResources() {
                    this.shadowRoot.innerHTML = '<div></div>';
                }
                setupEventListeners() {
                    setupCalled = true;
                }
            }
            const tagName = `test-setup-${++testComponentCounter}`;
            customElements.define(tagName, TestComp);
            
            const el = document.createElement(tagName);
            document.getElementById('qunit-fixture').appendChild(el);
            
            return el.whenReady().then(() => {
                assert.ok(setupCalled, 'setupEventListeners should be called');
            });
        });
        
        QUnit.test('onReady is called', function(assert) {
            let onReadyCalled = false;
            
            class TestComp extends BaseComponent {
                async loadResources() {
                    this.shadowRoot.innerHTML = '<div></div>';
                }
                onReady() {
                    onReadyCalled = true;
                }
            }
            const tagName = `test-on-ready-${++testComponentCounter}`;
            customElements.define(tagName, TestComp);
            
            const el = document.createElement(tagName);
            document.getElementById('qunit-fixture').appendChild(el);
            
            return el.whenReady().then(() => {
                assert.ok(onReadyCalled, 'onReady should be called');
            });
        });
        
        QUnit.test('emits component-ready event', function(assert) {
            class TestComp extends BaseComponent {
                async loadResources() {
                    this.shadowRoot.innerHTML = '<div></div>';
                }
            }
            const tagName = `test-ready-event-${++testComponentCounter}`;
            customElements.define(tagName, TestComp);
            
            const el = document.createElement(tagName);
            
            let eventReceived = null;
            el.addEventListener('component-ready', (e) => {
                eventReceived = e.detail;
            });
            
            document.getElementById('qunit-fixture').appendChild(el);
            
            return el.whenReady().then(() => {
                assert.ok(eventReceived, 'component-ready event should be emitted');
                assert.strictEqual(eventReceived.component, tagName, 'should include component name');
            });
        });
    });

});
