/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Test Suite - Utility Functions
   v0.2.1 - Extended with Shadow DOM testing helpers
   
   Common utilities for testing Web Components with Shadow DOM
   ═══════════════════════════════════════════════════════════════════════════════ */

const TestUtils = {
    
    /**
     * Create a component and wait for it to be ready
     * @param {string} tagName - Custom element tag name
     * @param {object} attributes - Optional attributes to set
     * @returns {Promise<HTMLElement>} The ready component
     */
    async createComponent(tagName, attributes = {}) {
        const fixture = document.getElementById('qunit-fixture');
        const element = document.createElement(tagName);
        
        // Set attributes
        Object.entries(attributes).forEach(([key, value]) => {
            element.setAttribute(key, value);
        });
        
        fixture.appendChild(element);
        
        // Wait for component to be ready (Shadow DOM components emit 'component-ready')
        if (element.whenReady) {
            await element.whenReady(3000);
        } else {
            // Fallback for non-BaseComponent elements
            await this.nextFrame();
        }
        
        return element;
    },
    
    /**
     * Remove all components from fixture
     */
    cleanup() {
        const fixture = document.getElementById('qunit-fixture');
        if (fixture) {
            fixture.innerHTML = '';
        }
    },
    
    /**
     * Wait for next animation frame
     * @returns {Promise<void>}
     */
    nextFrame() {
        return new Promise(resolve => requestAnimationFrame(resolve));
    },
    
    /**
     * Wait for specified milliseconds
     * @param {number} ms - Milliseconds to wait
     * @returns {Promise<void>}
     */
    wait(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    },
    
    /**
     * Wait for a custom event to be dispatched
     * @param {HTMLElement} element - Element to listen on
     * @param {string} eventName - Event name to wait for
     * @param {number} timeout - Timeout in ms (default 5000)
     * @returns {Promise<CustomEvent>} The dispatched event
     */
    waitForEvent(element, eventName, timeout = 5000) {
        return new Promise((resolve, reject) => {
            const timer = setTimeout(() => {
                reject(new Error(`Timeout waiting for event: ${eventName}`));
            }, timeout);
            
            element.addEventListener(eventName, (e) => {
                clearTimeout(timer);
                resolve(e);
            }, { once: true });
        });
    },
    
    /**
     * Trigger a DOM event on an element
     * @param {HTMLElement} element - Target element
     * @param {string} eventType - Event type (click, input, change, etc.)
     * @param {object} options - Event options
     */
    triggerEvent(element, eventType, options = {}) {
        const event = new Event(eventType, { bubbles: true, composed: true, ...options });
        element.dispatchEvent(event);
    },
    
    /**
     * Trigger keyboard event
     * @param {HTMLElement} element - Target element
     * @param {string} eventType - keydown, keyup, keypress
     * @param {string} key - Key value
     * @param {object} modifiers - {ctrlKey, shiftKey, altKey, metaKey}
     */
    triggerKeyEvent(element, eventType, key, modifiers = {}) {
        const event = new KeyboardEvent(eventType, {
            key: key,
            bubbles: true,
            composed: true,
            cancelable: true,
            ...modifiers
        });
        element.dispatchEvent(event);
    },
    
    /**
     * Set input value and trigger input/change events
     * @param {HTMLInputElement|HTMLTextAreaElement} element - Input element
     * @param {string} value - Value to set
     */
    setInputValue(element, value) {
        element.value = value;
        this.triggerEvent(element, 'input');
        this.triggerEvent(element, 'change');
    },
    
    // ═══════════════════════════════════════════════════════════════════════════
    // Shadow DOM Helpers
    // ═══════════════════════════════════════════════════════════════════════════
    
    /**
     * Query element within a component's Shadow DOM
     * @param {HTMLElement} component - The custom element
     * @param {string} selector - CSS selector
     * @returns {Element|null}
     */
    shadowQuery(component, selector) {
        return component.shadowRoot?.querySelector(selector) || null;
    },
    
    /**
     * Query all elements within a component's Shadow DOM
     * @param {HTMLElement} component - The custom element
     * @param {string} selector - CSS selector
     * @returns {NodeList}
     */
    shadowQueryAll(component, selector) {
        return component.shadowRoot?.querySelectorAll(selector) || [];
    },
    
    /**
     * Check if component has Shadow DOM
     * @param {HTMLElement} component
     * @returns {boolean}
     */
    hasShadowRoot(component) {
        return component.shadowRoot !== null;
    },
    
    /**
     * Get text content from Shadow DOM element
     * @param {HTMLElement} component
     * @param {string} selector
     * @returns {string}
     */
    getShadowText(component, selector) {
        const el = this.shadowQuery(component, selector);
        return el ? el.textContent : '';
    },
    
    /**
     * Click element within Shadow DOM
     * @param {HTMLElement} component
     * @param {string} selector
     */
    shadowClick(component, selector) {
        const el = this.shadowQuery(component, selector);
        if (el) el.click();
    },
    
    // ═══════════════════════════════════════════════════════════════════════════
    // Script/CSS Loading
    // ═══════════════════════════════════════════════════════════════════════════
    
    /**
     * Load a script dynamically and wait for it
     * @param {string} src - Script source URL
     * @returns {Promise<void>}
     */
    loadScript(src) {
        return new Promise((resolve, reject) => {
            // Check if already loaded
            if (document.querySelector(`script[src="${src}"]`)) {
                resolve();
                return;
            }
            
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = () => reject(new Error(`Failed to load script: ${src}`));
            document.head.appendChild(script);
        });
    },
    
    /**
     * Load CSS dynamically
     * @param {string} href - CSS source URL
     * @returns {Promise<void>}
     */
    loadCss(href) {
        return new Promise((resolve, reject) => {
            if (document.querySelector(`link[href="${href}"]`)) {
                resolve();
                return;
            }
            
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = href;
            link.onload = resolve;
            link.onerror = () => reject(new Error(`Failed to load CSS: ${href}`));
            document.head.appendChild(link);
        });
    },
    
    /**
     * Load the v0.2.1 foundation scripts in correct order
     * @returns {Promise<void>}
     */
    async loadFoundation() {
        await this.loadScript(TestPaths.helpers);
        await this.loadScript(TestPaths.componentPaths);
        await this.loadScript(TestPaths.baseComponent);
    },
    
    // ═══════════════════════════════════════════════════════════════════════════
    // Mock Helpers
    // ═══════════════════════════════════════════════════════════════════════════
    
    /**
     * Mock the API client for isolated testing
     * @param {object} overrides - Methods to override
     * @returns {object} Mock API client
     */
    createMockApiClient(overrides = {}) {
        return {
            checkHealth: async () => true,
            htmlToDot: async (request) => ({
                dot: 'digraph { a -> b }',
                stats: {
                    total_nodes: 2,
                    total_edges: 1,
                    element_nodes: 2,
                    value_nodes: 0,
                    tag_nodes: 0,
                    text_nodes: 0,
                    attr_nodes: 0
                },
                processing_ms: 10,
                dot_size_bytes: 20
            }),
            post: async (endpoint, data) => ({}),
            get: async (endpoint) => ({}),
            ...overrides
        };
    },
    
    // ═══════════════════════════════════════════════════════════════════════════
    // Sample Data
    // ═══════════════════════════════════════════════════════════════════════════
    
    sampleDot: `digraph G {
        rankdir=TB;
        node [shape=box, style=filled];
        
        "node1" [label="<div>", fillcolor="#E8E8E8", fontcolor="#333333"];
        "node2" [label="<p>", fillcolor="#4A90D9", fontcolor="#FFFFFF"];
        "node3" [label="Hello World", fillcolor="#FFFACD", fontcolor="#333333"];
        
        "node1" -> "node2";
        "node2" -> "node3" [style=dashed];
    }`,
    
    sampleHtml: {
        simple: '<div><p>Hello World</p></div>',
        nested: '<article><header><h1>Title</h1></header><section><p>Content</p></section></article>',
        withAttributes: '<div id="main" class="container"><a href="#" class="link">Click</a></div>',
        empty: ''
    },
    
    // ═══════════════════════════════════════════════════════════════════════════
    // Assertions
    // ═══════════════════════════════════════════════════════════════════════════
    
    /**
     * Assert that an element contains expected text
     * @param {QUnit.Assert} assert - QUnit assert object
     * @param {HTMLElement} element - Element to check
     * @param {string} expectedText - Expected text content
     * @param {string} message - Assertion message
     */
    assertContainsText(assert, element, expectedText, message) {
        const text = element.textContent || element.innerText;
        assert.ok(text.includes(expectedText), message || `Element should contain: ${expectedText}`);
    },
    
    /**
     * Assert Shadow DOM contains text
     * @param {QUnit.Assert} assert
     * @param {HTMLElement} component
     * @param {string} selector
     * @param {string} expectedText
     * @param {string} message
     */
    assertShadowContainsText(assert, component, selector, expectedText, message) {
        const text = this.getShadowText(component, selector);
        assert.ok(text.includes(expectedText), message || `${selector} should contain: ${expectedText}`);
    },
    
    /**
     * Assert that an element has a specific attribute value
     * @param {QUnit.Assert} assert - QUnit assert object
     * @param {HTMLElement} element - Element to check
     * @param {string} attrName - Attribute name
     * @param {string} expectedValue - Expected value
     * @param {string} message - Assertion message
     */
    assertAttribute(assert, element, attrName, expectedValue, message) {
        const actualValue = element.getAttribute(attrName);
        assert.strictEqual(actualValue, expectedValue, message || `Attribute ${attrName} should be ${expectedValue}`);
    }
};

// Make available globally for tests
window.TestUtils = TestUtils;

// Export for Node.js if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TestUtils;
}
