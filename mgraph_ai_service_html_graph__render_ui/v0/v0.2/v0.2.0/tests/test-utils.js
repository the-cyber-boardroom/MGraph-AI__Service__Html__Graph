/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - Test Utilities
   v0.2.0 - Consolidated from v0.1.x
   ═══════════════════════════════════════════════════════════════════════════════ */

/**
 * Test utility functions for component testing
 */
const TestUtils = {
    /**
     * Create and append a custom element to the DOM
     * @param {string} tagName - Custom element tag name
     * @param {object} attributes - Optional attributes to set
     * @returns {HTMLElement} The created element
     */
    createElement(tagName, attributes = {}) {
        const element = document.createElement(tagName);
        
        for (const [key, value] of Object.entries(attributes)) {
            element.setAttribute(key, value);
        }
        
        document.body.appendChild(element);
        return element;
    },

    /**
     * Remove an element from the DOM
     * @param {HTMLElement} element - Element to remove
     */
    removeElement(element) {
        if (element && element.parentNode) {
            element.parentNode.removeChild(element);
        }
    },

    /**
     * Wait for a custom element to be defined
     * @param {string} tagName - Custom element tag name
     * @returns {Promise<void>}
     */
    async waitForElement(tagName) {
        await customElements.whenDefined(tagName);
    },

    /**
     * Wait for next animation frame
     * @returns {Promise<void>}
     */
    nextFrame() {
        return new Promise(resolve => requestAnimationFrame(resolve));
    },

    /**
     * Wait for a specified duration
     * @param {number} ms - Milliseconds to wait
     * @returns {Promise<void>}
     */
    wait(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    },

    /**
     * Trigger a custom event on an element
     * @param {HTMLElement} element - Target element
     * @param {string} eventName - Event name
     * @param {object} detail - Event detail data
     */
    triggerEvent(element, eventName, detail = {}) {
        const event = new CustomEvent(eventName, {
            detail,
            bubbles: true,
            cancelable: true
        });
        element.dispatchEvent(event);
    },

    /**
     * Mock the apiClient for testing
     * @param {object} responses - Map of endpoint to response
     * @returns {object} Mock apiClient
     */
    mockApiClient(responses = {}) {
        return {
            post: async (endpoint, data) => {
                if (responses[endpoint]) {
                    return typeof responses[endpoint] === 'function'
                        ? responses[endpoint](data)
                        : responses[endpoint];
                }
                throw new Error(`No mock response for ${endpoint}`);
            },
            get: async (endpoint) => {
                if (responses[endpoint]) {
                    return responses[endpoint];
                }
                throw new Error(`No mock response for ${endpoint}`);
            },
            checkHealth: async () => responses.health !== false
        };
    },

    /**
     * Create a test fixture container
     * @returns {HTMLElement} Fixture container
     */
    createFixture() {
        const fixture = document.createElement('div');
        fixture.id = 'qunit-fixture';
        document.body.appendChild(fixture);
        return fixture;
    },

    /**
     * Clear the test fixture
     */
    clearFixture() {
        const fixture = document.getElementById('qunit-fixture');
        if (fixture) {
            fixture.innerHTML = '';
        }
    }
};

// Export for both browser and Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TestUtils;
}
if (typeof window !== 'undefined') {
    window.TestUtils = TestUtils;
}
