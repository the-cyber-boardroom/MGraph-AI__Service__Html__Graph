/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - QA UI Engine
   v0.2.0 - Automated QA Testing Framework
   
   Supports three execution modes:
   1. Automated Fast Mode - Rapid batch execution for CI/CD
   2. Interactive Slow-Motion Mode - Step-by-step with controls
   3. State Teleportation Mode - Jump to specific application states
   
   Based on IFD QA UI methodology
   ═══════════════════════════════════════════════════════════════════════════════ */

class QAEngine {
    constructor() {
        this.scenarios = new Map();
        this.currentScenario = null;
        this.currentStepIndex = 0;
        this.mode = 'automated'; // 'automated' | 'interactive' | 'teleport'
        this.isPaused = false;
        this.isRunning = false;
        this.stepDelay = 0; // ms between steps in automated mode
        this.interactiveDelay = 1000; // ms between steps in slow-motion
        this.results = [];
        this.onStepComplete = null;
        this.onScenarioComplete = null;
        this.onError = null;
        this.onStateChange = null;
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Scenario Registration
    // ═══════════════════════════════════════════════════════════════════════════

    /**
     * Register a scenario with the engine
     * @param {QAScenario} scenario - Scenario instance
     */
    registerScenario(scenario) {
        if (!scenario.id || !scenario.name) {
            throw new Error('Scenario must have id and name');
        }
        this.scenarios.set(scenario.id, scenario);
        console.log(`[QA Engine] Registered scenario: ${scenario.id} - ${scenario.name}`);
    }

    /**
     * Get all registered scenarios
     * @returns {Array} Array of scenario metadata
     */
    getScenarios() {
        return Array.from(this.scenarios.values()).map(s => ({
            id: s.id,
            name: s.name,
            description: s.description,
            stepCount: s.steps.length,
            tags: s.tags || []
        }));
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Mode Configuration
    // ═══════════════════════════════════════════════════════════════════════════

    /**
     * Set execution mode
     * @param {'automated'|'interactive'|'teleport'} mode
     */
    setMode(mode) {
        if (!['automated', 'interactive', 'teleport'].includes(mode)) {
            throw new Error(`Invalid mode: ${mode}`);
        }
        this.mode = mode;
        this._emitStateChange();
    }

    /**
     * Set delay between steps (for automated mode)
     * @param {number} ms - Milliseconds
     */
    setStepDelay(ms) {
        this.stepDelay = ms;
    }

    /**
     * Set delay for interactive mode
     * @param {number} ms - Milliseconds
     */
    setInteractiveDelay(ms) {
        this.interactiveDelay = ms;
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Execution Control
    // ═══════════════════════════════════════════════════════════════════════════

    /**
     * Run a scenario by ID
     * @param {string} scenarioId 
     * @param {object} options - { startStep, endStep, mode }
     * @returns {Promise<object>} Results
     */
    async runScenario(scenarioId, options = {}) {
        const scenario = this.scenarios.get(scenarioId);
        if (!scenario) {
            throw new Error(`Scenario not found: ${scenarioId}`);
        }

        this.currentScenario = scenario;
        this.currentStepIndex = options.startStep || 0;
        this.isRunning = true;
        this.isPaused = false;
        this.results = [];

        const mode = options.mode || this.mode;
        const endStep = options.endStep ?? scenario.steps.length;

        console.log(`[QA Engine] Running scenario: ${scenario.name} (mode: ${mode})`);
        this._emitStateChange();

        try {
            // Run setup if exists
            if (scenario.setup) {
                await scenario.setup();
            }

            // Execute steps based on mode
            while (this.currentStepIndex < endStep && this.isRunning) {
                if (this.isPaused) {
                    await this._waitForResume();
                }

                const step = scenario.steps[this.currentStepIndex];
                const result = await this._executeStep(step, this.currentStepIndex);
                this.results.push(result);

                if (this.onStepComplete) {
                    this.onStepComplete(result, this.currentStepIndex, scenario.steps.length);
                }

                this.currentStepIndex++;
                this._emitStateChange();

                // Apply delay based on mode
                if (mode === 'automated' && this.stepDelay > 0) {
                    await this._wait(this.stepDelay);
                } else if (mode === 'interactive') {
                    await this._wait(this.interactiveDelay);
                }
            }

            // Run teardown if exists
            if (scenario.teardown) {
                await scenario.teardown();
            }

            const summary = this._summarizeResults();
            
            if (this.onScenarioComplete) {
                this.onScenarioComplete(summary);
            }

            console.log(`[QA Engine] Scenario complete: ${summary.passed}/${summary.total} passed`);
            return summary;

        } catch (error) {
            console.error('[QA Engine] Scenario failed:', error);
            if (this.onError) {
                this.onError(error, this.currentStepIndex);
            }
            throw error;
        } finally {
            this.isRunning = false;
            this._emitStateChange();
        }
    }

    /**
     * Run all registered scenarios
     * @param {object} options
     * @returns {Promise<object>} Combined results
     */
    async runAllScenarios(options = {}) {
        const allResults = [];
        const scenarioIds = Array.from(this.scenarios.keys());

        for (const id of scenarioIds) {
            try {
                const result = await this.runScenario(id, options);
                allResults.push({ id, ...result });
            } catch (error) {
                allResults.push({ id, error: error.message, passed: 0, failed: 1, total: 1 });
            }
        }

        return {
            scenarios: allResults,
            totalPassed: allResults.reduce((sum, r) => sum + (r.passed || 0), 0),
            totalFailed: allResults.reduce((sum, r) => sum + (r.failed || 0), 0),
            totalScenarios: allResults.length
        };
    }

    /**
     * Teleport to a specific step in a scenario
     * Executes all prior steps rapidly, then pauses
     * @param {string} scenarioId 
     * @param {number} targetStep - Step index to teleport to
     */
    async teleportToStep(scenarioId, targetStep) {
        console.log(`[QA Engine] Teleporting to step ${targetStep} in ${scenarioId}`);
        
        // Run all steps up to target in fast mode (no delays)
        const originalDelay = this.stepDelay;
        this.stepDelay = 0;

        await this.runScenario(scenarioId, {
            mode: 'teleport',
            startStep: 0,
            endStep: targetStep
        });

        this.stepDelay = originalDelay;
        this.isPaused = true;
        this._emitStateChange();

        console.log(`[QA Engine] Teleported. Application is now at step ${targetStep}. Paused for interaction.`);
    }

    /**
     * Pause execution (for interactive mode)
     */
    pause() {
        if (this.isRunning) {
            this.isPaused = true;
            console.log('[QA Engine] Paused');
            this._emitStateChange();
        }
    }

    /**
     * Resume execution
     */
    resume() {
        if (this.isPaused) {
            this.isPaused = false;
            console.log('[QA Engine] Resumed');
            this._emitStateChange();
            if (this._resumeResolver) {
                this._resumeResolver();
            }
        }
    }

    /**
     * Execute single next step (for interactive mode)
     */
    async nextStep() {
        if (!this.isRunning || !this.currentScenario) {
            console.warn('[QA Engine] No scenario running');
            return null;
        }

        if (this.currentStepIndex >= this.currentScenario.steps.length) {
            console.log('[QA Engine] No more steps');
            return null;
        }

        const step = this.currentScenario.steps[this.currentStepIndex];
        const result = await this._executeStep(step, this.currentStepIndex);
        this.results.push(result);
        
        if (this.onStepComplete) {
            this.onStepComplete(result, this.currentStepIndex, this.currentScenario.steps.length);
        }

        this.currentStepIndex++;
        this._emitStateChange();
        
        return result;
    }

    /**
     * Stop execution completely
     */
    stop() {
        this.isRunning = false;
        this.isPaused = false;
        console.log('[QA Engine] Stopped');
        this._emitStateChange();
    }

    /**
     * Reset to beginning of current scenario
     */
    reset() {
        this.currentStepIndex = 0;
        this.results = [];
        this.isPaused = false;
        console.log('[QA Engine] Reset');
        this._emitStateChange();
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Internal Methods
    // ═══════════════════════════════════════════════════════════════════════════

    async _executeStep(step, index) {
        const startTime = performance.now();
        const result = {
            index,
            name: step.name,
            description: step.description,
            passed: false,
            error: null,
            duration: 0
        };

        try {
            console.log(`[QA Engine] Step ${index + 1}: ${step.name}`);
            
            // Execute the step action
            await step.action();

            // Run assertions if provided
            if (step.assertions) {
                for (const assertion of step.assertions) {
                    const assertionResult = await assertion();
                    if (!assertionResult.passed) {
                        throw new Error(assertionResult.message || 'Assertion failed');
                    }
                }
            }

            result.passed = true;
            console.log(`[QA Engine] ✓ Step ${index + 1} passed`);

        } catch (error) {
            result.passed = false;
            result.error = error.message;
            console.error(`[QA Engine] ✗ Step ${index + 1} failed:`, error.message);
        }

        result.duration = performance.now() - startTime;
        return result;
    }

    _summarizeResults() {
        const passed = this.results.filter(r => r.passed).length;
        const failed = this.results.filter(r => !r.passed).length;
        
        return {
            scenarioId: this.currentScenario?.id,
            scenarioName: this.currentScenario?.name,
            passed,
            failed,
            total: this.results.length,
            results: [...this.results],
            allPassed: failed === 0
        };
    }

    _wait(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    _waitForResume() {
        return new Promise(resolve => {
            this._resumeResolver = resolve;
        });
    }

    _emitStateChange() {
        if (this.onStateChange) {
            this.onStateChange({
                isRunning: this.isRunning,
                isPaused: this.isPaused,
                mode: this.mode,
                currentScenario: this.currentScenario?.id,
                currentStep: this.currentStepIndex,
                totalSteps: this.currentScenario?.steps.length || 0
            });
        }
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // State Query
    // ═══════════════════════════════════════════════════════════════════════════

    getState() {
        return {
            isRunning: this.isRunning,
            isPaused: this.isPaused,
            mode: this.mode,
            currentScenario: this.currentScenario ? {
                id: this.currentScenario.id,
                name: this.currentScenario.name,
                totalSteps: this.currentScenario.steps.length
            } : null,
            currentStep: this.currentStepIndex,
            results: [...this.results]
        };
    }

    getCurrentStep() {
        if (!this.currentScenario) return null;
        return this.currentScenario.steps[this.currentStepIndex] || null;
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// QA Scenario Base Class
// ═══════════════════════════════════════════════════════════════════════════════

class QAScenario {
    constructor(config) {
        this.id = config.id;
        this.name = config.name;
        this.description = config.description || '';
        this.tags = config.tags || [];
        this.steps = [];
        this.setup = config.setup || null;
        this.teardown = config.teardown || null;
    }

    /**
     * Add a step to the scenario
     * @param {object} step - { name, description, action, assertions }
     */
    addStep(step) {
        if (!step.name || !step.action) {
            throw new Error('Step must have name and action');
        }
        this.steps.push({
            name: step.name,
            description: step.description || '',
            action: step.action,
            assertions: step.assertions || []
        });
        return this; // Allow chaining
    }

    /**
     * Convenience method to add multiple steps
     * @param {Array} steps
     */
    addSteps(steps) {
        steps.forEach(step => this.addStep(step));
        return this;
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// QA Assertion Helpers
// ═══════════════════════════════════════════════════════════════════════════════

const QAAssert = {
    /**
     * Assert element exists
     */
    elementExists(selector, message) {
        return async () => {
            const element = document.querySelector(selector);
            return {
                passed: element !== null,
                message: message || `Element ${selector} should exist`
            };
        };
    },

    /**
     * Assert element contains text
     */
    elementContainsText(selector, text, message) {
        return async () => {
            const element = document.querySelector(selector);
            const contains = element?.textContent?.includes(text);
            return {
                passed: contains,
                message: message || `Element ${selector} should contain "${text}"`
            };
        };
    },

    /**
     * Assert element has value
     */
    elementHasValue(selector, value, message) {
        return async () => {
            const element = document.querySelector(selector);
            return {
                passed: element?.value === value,
                message: message || `Element ${selector} should have value "${value}"`
            };
        };
    },

    /**
     * Assert element is visible
     */
    elementIsVisible(selector, message) {
        return async () => {
            const element = document.querySelector(selector);
            if (!element) return { passed: false, message: `Element ${selector} not found` };
            
            const style = window.getComputedStyle(element);
            const isVisible = style.display !== 'none' && 
                             style.visibility !== 'hidden' && 
                             style.opacity !== '0';
            return {
                passed: isVisible,
                message: message || `Element ${selector} should be visible`
            };
        };
    },

    /**
     * Assert element has class
     */
    elementHasClass(selector, className, message) {
        return async () => {
            const element = document.querySelector(selector);
            return {
                passed: element?.classList.contains(className),
                message: message || `Element ${selector} should have class "${className}"`
            };
        };
    },

    /**
     * Assert custom condition
     */
    custom(fn, message) {
        return async () => {
            const result = await fn();
            return {
                passed: result,
                message: message || 'Custom assertion failed'
            };
        };
    },

    /**
     * Wait for element to appear
     */
    waitForElement(selector, timeout = 5000) {
        return async () => {
            const startTime = Date.now();
            while (Date.now() - startTime < timeout) {
                if (document.querySelector(selector)) {
                    return { passed: true };
                }
                await new Promise(r => setTimeout(r, 100));
            }
            return {
                passed: false,
                message: `Element ${selector} did not appear within ${timeout}ms`
            };
        };
    }
};

// ═══════════════════════════════════════════════════════════════════════════════
// QA Action Helpers
// ═══════════════════════════════════════════════════════════════════════════════

const QAActions = {
    /**
     * Click an element
     */
    click(selector) {
        return async () => {
            const element = document.querySelector(selector);
            if (!element) throw new Error(`Element not found: ${selector}`);
            element.click();
            await this._nextFrame();
        };
    },

    /**
     * Type into an input
     */
    type(selector, text) {
        return async () => {
            const element = document.querySelector(selector);
            if (!element) throw new Error(`Element not found: ${selector}`);
            element.value = text;
            element.dispatchEvent(new Event('input', { bubbles: true }));
            element.dispatchEvent(new Event('change', { bubbles: true }));
            await this._nextFrame();
        };
    },

    /**
     * Select an option
     */
    select(selector, value) {
        return async () => {
            const element = document.querySelector(selector);
            if (!element) throw new Error(`Element not found: ${selector}`);
            element.value = value;
            element.dispatchEvent(new Event('change', { bubbles: true }));
            await this._nextFrame();
        };
    },

    /**
     * Check/uncheck a checkbox
     */
    setCheckbox(selector, checked) {
        return async () => {
            const element = document.querySelector(selector);
            if (!element) throw new Error(`Element not found: ${selector}`);
            element.checked = checked;
            element.dispatchEvent(new Event('change', { bubbles: true }));
            await this._nextFrame();
        };
    },

    /**
     * Wait for a duration
     */
    wait(ms) {
        return async () => {
            await new Promise(resolve => setTimeout(resolve, ms));
        };
    },

    /**
     * Wait for element to appear
     */
    waitForElement(selector, timeout = 5000) {
        return async () => {
            const startTime = Date.now();
            while (Date.now() - startTime < timeout) {
                if (document.querySelector(selector)) return;
                await new Promise(r => setTimeout(r, 100));
            }
            throw new Error(`Element ${selector} did not appear within ${timeout}ms`);
        };
    },

    /**
     * Wait for event
     */
    waitForEvent(element, eventName, timeout = 5000) {
        return async () => {
            const el = typeof element === 'string' ? document.querySelector(element) : element;
            if (!el) throw new Error(`Element not found: ${element}`);
            
            return new Promise((resolve, reject) => {
                const timer = setTimeout(() => {
                    reject(new Error(`Event ${eventName} not received within ${timeout}ms`));
                }, timeout);
                
                el.addEventListener(eventName, () => {
                    clearTimeout(timer);
                    resolve();
                }, { once: true });
            });
        };
    },

    /**
     * Dispatch custom event
     */
    dispatchEvent(selector, eventName, detail = {}) {
        return async () => {
            const element = document.querySelector(selector);
            if (!element) throw new Error(`Element not found: ${selector}`);
            element.dispatchEvent(new CustomEvent(eventName, { detail, bubbles: true }));
            await this._nextFrame();
        };
    },

    /**
     * Navigate to URL (for SPAs)
     */
    navigate(url) {
        return async () => {
            window.location.href = url;
            await new Promise(r => setTimeout(r, 100));
        };
    },

    /**
     * Call a component method directly
     */
    callMethod(selector, methodName, ...args) {
        return async () => {
            const element = document.querySelector(selector);
            if (!element) throw new Error(`Element not found: ${selector}`);
            if (typeof element[methodName] !== 'function') {
                throw new Error(`Method ${methodName} not found on element`);
            }
            await element[methodName](...args);
            await this._nextFrame();
        };
    },

    _nextFrame() {
        return new Promise(resolve => requestAnimationFrame(resolve));
    }
};

// Make available globally
window.QAEngine = QAEngine;
window.QAScenario = QAScenario;
window.QAAssert = QAAssert;
window.QAActions = QAActions;

// Export for Node.js if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { QAEngine, QAScenario, QAAssert, QAActions };
}
