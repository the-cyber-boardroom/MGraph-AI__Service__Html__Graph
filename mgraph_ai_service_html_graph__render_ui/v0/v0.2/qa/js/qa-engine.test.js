/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - QA Engine Tests
   v0.2.0 - Tests for the QA framework itself
   
   These tests verify the QA Engine works correctly before using it to test
   the application. This is essential for maintaining confidence in test results.
   ═══════════════════════════════════════════════════════════════════════════════ */

QUnit.module('QA Engine', function(hooks) {
    
    let engine;
    
    hooks.beforeEach(function() {
        engine = new QAEngine();
    });
    
    hooks.afterEach(function() {
        engine.stop();
        engine = null;
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // Initialization Tests
    // ═══════════════════════════════════════════════════════════════════════════
    
    QUnit.test('QAEngine initializes with correct defaults', function(assert) {
        assert.strictEqual(engine.mode, 'automated', 'default mode should be automated');
        assert.strictEqual(engine.isPaused, false, 'should not be paused initially');
        assert.strictEqual(engine.isRunning, false, 'should not be running initially');
        assert.strictEqual(engine.currentScenario, null, 'no current scenario initially');
        assert.strictEqual(engine.currentStepIndex, 0, 'step index should be 0');
    });
    
    QUnit.test('QAScenario initializes with config', function(assert) {
        const scenario = new QAScenario({
            id: 'test-id',
            name: 'Test Scenario',
            description: 'A test',
            tags: ['unit', 'test']
        });
        
        assert.strictEqual(scenario.id, 'test-id');
        assert.strictEqual(scenario.name, 'Test Scenario');
        assert.strictEqual(scenario.description, 'A test');
        assert.deepEqual(scenario.tags, ['unit', 'test']);
        assert.deepEqual(scenario.steps, []);
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // Scenario Registration Tests
    // ═══════════════════════════════════════════════════════════════════════════
    
    QUnit.test('registerScenario adds scenario to engine', function(assert) {
        const scenario = new QAScenario({
            id: 's01',
            name: 'Scenario 1'
        });
        
        engine.registerScenario(scenario);
        
        const scenarios = engine.getScenarios();
        assert.strictEqual(scenarios.length, 1);
        assert.strictEqual(scenarios[0].id, 's01');
    });
    
    QUnit.test('registerScenario throws without id', function(assert) {
        const scenario = new QAScenario({
            name: 'No ID'
        });
        scenario.id = undefined;
        
        assert.throws(() => {
            engine.registerScenario(scenario);
        }, /id and name/, 'should throw for missing id');
    });
    
    QUnit.test('getScenarios returns metadata', function(assert) {
        const scenario = new QAScenario({
            id: 's01',
            name: 'Test',
            description: 'Desc',
            tags: ['a', 'b']
        });
        scenario.addStep({ name: 'Step 1', action: async () => {} });
        scenario.addStep({ name: 'Step 2', action: async () => {} });
        
        engine.registerScenario(scenario);
        
        const scenarios = engine.getScenarios();
        assert.strictEqual(scenarios[0].stepCount, 2);
        assert.deepEqual(scenarios[0].tags, ['a', 'b']);
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // Mode Configuration Tests
    // ═══════════════════════════════════════════════════════════════════════════
    
    QUnit.test('setMode changes mode', function(assert) {
        engine.setMode('interactive');
        assert.strictEqual(engine.mode, 'interactive');
        
        engine.setMode('teleport');
        assert.strictEqual(engine.mode, 'teleport');
        
        engine.setMode('automated');
        assert.strictEqual(engine.mode, 'automated');
    });
    
    QUnit.test('setMode throws for invalid mode', function(assert) {
        assert.throws(() => {
            engine.setMode('invalid');
        }, /Invalid mode/, 'should throw for invalid mode');
    });
    
    QUnit.test('setStepDelay configures delay', function(assert) {
        engine.setStepDelay(500);
        assert.strictEqual(engine.stepDelay, 500);
    });
    
    QUnit.test('setInteractiveDelay configures delay', function(assert) {
        engine.setInteractiveDelay(2000);
        assert.strictEqual(engine.interactiveDelay, 2000);
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // Step Execution Tests
    // ═══════════════════════════════════════════════════════════════════════════
    
    QUnit.test('addStep adds step to scenario', function(assert) {
        const scenario = new QAScenario({ id: 's', name: 'S' });
        
        scenario.addStep({
            name: 'Step 1',
            description: 'First step',
            action: async () => { /* do something */ }
        });
        
        assert.strictEqual(scenario.steps.length, 1);
        assert.strictEqual(scenario.steps[0].name, 'Step 1');
    });
    
    QUnit.test('addStep allows chaining', function(assert) {
        const scenario = new QAScenario({ id: 's', name: 'S' });
        
        const result = scenario
            .addStep({ name: 'S1', action: async () => {} })
            .addStep({ name: 'S2', action: async () => {} })
            .addStep({ name: 'S3', action: async () => {} });
        
        assert.strictEqual(result, scenario);
        assert.strictEqual(scenario.steps.length, 3);
    });
    
    QUnit.test('addSteps adds multiple steps', function(assert) {
        const scenario = new QAScenario({ id: 's', name: 'S' });
        
        scenario.addSteps([
            { name: 'S1', action: async () => {} },
            { name: 'S2', action: async () => {} }
        ]);
        
        assert.strictEqual(scenario.steps.length, 2);
    });
    
    QUnit.test('addStep throws without name', function(assert) {
        const scenario = new QAScenario({ id: 's', name: 'S' });
        
        assert.throws(() => {
            scenario.addStep({ action: async () => {} });
        }, /name and action/, 'should throw for missing name');
    });
    
    QUnit.test('addStep throws without action', function(assert) {
        const scenario = new QAScenario({ id: 's', name: 'S' });
        
        assert.throws(() => {
            scenario.addStep({ name: 'Step' });
        }, /name and action/, 'should throw for missing action');
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // Scenario Execution Tests
    // ═══════════════════════════════════════════════════════════════════════════
    
    QUnit.test('runScenario executes all steps', async function(assert) {
        const executed = [];
        
        const scenario = new QAScenario({ id: 's01', name: 'Test' });
        scenario.addSteps([
            { name: 'S1', action: async () => { executed.push(1); } },
            { name: 'S2', action: async () => { executed.push(2); } },
            { name: 'S3', action: async () => { executed.push(3); } }
        ]);
        
        engine.registerScenario(scenario);
        
        const result = await engine.runScenario('s01');
        
        assert.deepEqual(executed, [1, 2, 3], 'all steps should execute in order');
        assert.strictEqual(result.passed, 3);
        assert.strictEqual(result.failed, 0);
        assert.strictEqual(result.total, 3);
    });
    
    QUnit.test('runScenario handles step failures', async function(assert) {
        const scenario = new QAScenario({ id: 's01', name: 'Test' });
        scenario.addSteps([
            { name: 'S1', action: async () => {} },
            { 
                name: 'S2', 
                action: async () => {},
                assertions: [
                    async () => ({ passed: false, message: 'Intentional failure' })
                ]
            },
            { name: 'S3', action: async () => {} }
        ]);
        
        engine.registerScenario(scenario);
        
        const result = await engine.runScenario('s01');
        
        assert.strictEqual(result.passed, 2);
        assert.strictEqual(result.failed, 1);
        assert.strictEqual(result.allPassed, false);
    });
    
    QUnit.test('runScenario throws for unknown scenario', async function(assert) {
        try {
            await engine.runScenario('nonexistent');
            assert.ok(false, 'should have thrown');
        } catch (e) {
            assert.ok(e.message.includes('not found'));
        }
    });
    
    QUnit.test('runScenario runs setup and teardown', async function(assert) {
        const sequence = [];
        
        const scenario = new QAScenario({
            id: 's01',
            name: 'Test',
            setup: async () => { sequence.push('setup'); },
            teardown: async () => { sequence.push('teardown'); }
        });
        scenario.addStep({ 
            name: 'Step', 
            action: async () => { sequence.push('step'); } 
        });
        
        engine.registerScenario(scenario);
        
        await engine.runScenario('s01');
        
        assert.deepEqual(sequence, ['setup', 'step', 'teardown']);
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // Pause/Resume Tests
    // ═══════════════════════════════════════════════════════════════════════════
    
    QUnit.test('pause sets isPaused', function(assert) {
        engine.isRunning = true;
        engine.pause();
        assert.ok(engine.isPaused);
    });
    
    QUnit.test('pause does nothing when not running', function(assert) {
        engine.isRunning = false;
        engine.pause();
        assert.notOk(engine.isPaused);
    });
    
    QUnit.test('resume clears isPaused', function(assert) {
        engine.isPaused = true;
        engine.resume();
        assert.notOk(engine.isPaused);
    });
    
    QUnit.test('stop clears running and paused', function(assert) {
        engine.isRunning = true;
        engine.isPaused = true;
        engine.stop();
        assert.notOk(engine.isRunning);
        assert.notOk(engine.isPaused);
    });
    
    QUnit.test('reset clears step index and results', function(assert) {
        engine.currentStepIndex = 5;
        engine.results = [{ passed: true }];
        engine.reset();
        assert.strictEqual(engine.currentStepIndex, 0);
        assert.deepEqual(engine.results, []);
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // State Query Tests
    // ═══════════════════════════════════════════════════════════════════════════
    
    QUnit.test('getState returns current state', function(assert) {
        engine.isRunning = true;
        engine.isPaused = true;
        engine.mode = 'interactive';
        
        const state = engine.getState();
        
        assert.ok(state.isRunning);
        assert.ok(state.isPaused);
        assert.strictEqual(state.mode, 'interactive');
    });
    
    QUnit.test('getCurrentStep returns null when no scenario', function(assert) {
        assert.strictEqual(engine.getCurrentStep(), null);
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // Callback Tests
    // ═══════════════════════════════════════════════════════════════════════════
    
    QUnit.test('onStepComplete callback is called', async function(assert) {
        const stepResults = [];
        engine.onStepComplete = (result, index, total) => {
            stepResults.push({ result, index, total });
        };
        
        const scenario = new QAScenario({ id: 's', name: 'S' });
        scenario.addSteps([
            { name: 'S1', action: async () => {} },
            { name: 'S2', action: async () => {} }
        ]);
        
        engine.registerScenario(scenario);
        await engine.runScenario('s');
        
        assert.strictEqual(stepResults.length, 2);
        assert.strictEqual(stepResults[0].index, 0);
        assert.strictEqual(stepResults[1].index, 1);
    });
    
    QUnit.test('onScenarioComplete callback is called', async function(assert) {
        let completeSummary = null;
        engine.onScenarioComplete = (summary) => {
            completeSummary = summary;
        };
        
        const scenario = new QAScenario({ id: 's', name: 'Test Scenario' });
        scenario.addStep({ name: 'S1', action: async () => {} });
        
        engine.registerScenario(scenario);
        await engine.runScenario('s');
        
        assert.ok(completeSummary);
        assert.strictEqual(completeSummary.scenarioName, 'Test Scenario');
        assert.strictEqual(completeSummary.total, 1);
    });
    
    QUnit.test('onStateChange callback is called', async function(assert) {
        const stateChanges = [];
        engine.onStateChange = (state) => {
            stateChanges.push({ ...state });
        };
        
        const scenario = new QAScenario({ id: 's', name: 'S' });
        scenario.addStep({ name: 'S1', action: async () => {} });
        
        engine.registerScenario(scenario);
        await engine.runScenario('s');
        
        assert.ok(stateChanges.length > 0, 'should have state changes');
    });
});

// ═══════════════════════════════════════════════════════════════════════════════
// QA Assertion Helper Tests
// ═══════════════════════════════════════════════════════════════════════════════

QUnit.module('QA Assertions', function(hooks) {
    
    hooks.beforeEach(function() {
        document.getElementById('qunit-fixture').innerHTML = `
            <div id="test-element" class="test-class">Test Content</div>
            <input id="test-input" value="test-value">
            <div id="hidden-element" style="display: none;">Hidden</div>
        `;
    });
    
    hooks.afterEach(function() {
        document.getElementById('qunit-fixture').innerHTML = '';
    });
    
    QUnit.test('elementExists returns true for existing element', async function(assert) {
        const assertion = QAAssert.elementExists('#test-element');
        const result = await assertion();
        assert.ok(result.passed);
    });
    
    QUnit.test('elementExists returns false for missing element', async function(assert) {
        const assertion = QAAssert.elementExists('#nonexistent');
        const result = await assertion();
        assert.notOk(result.passed);
    });
    
    QUnit.test('elementContainsText checks content', async function(assert) {
        const assertion = QAAssert.elementContainsText('#test-element', 'Test');
        const result = await assertion();
        assert.ok(result.passed);
        
        const assertion2 = QAAssert.elementContainsText('#test-element', 'Missing');
        const result2 = await assertion2();
        assert.notOk(result2.passed);
    });
    
    QUnit.test('elementHasValue checks input value', async function(assert) {
        const assertion = QAAssert.elementHasValue('#test-input', 'test-value');
        const result = await assertion();
        assert.ok(result.passed);
        
        const assertion2 = QAAssert.elementHasValue('#test-input', 'wrong');
        const result2 = await assertion2();
        assert.notOk(result2.passed);
    });
    
    QUnit.test('elementHasClass checks class', async function(assert) {
        const assertion = QAAssert.elementHasClass('#test-element', 'test-class');
        const result = await assertion();
        assert.ok(result.passed);
        
        const assertion2 = QAAssert.elementHasClass('#test-element', 'missing-class');
        const result2 = await assertion2();
        assert.notOk(result2.passed);
    });
    
    QUnit.test('elementIsVisible checks visibility', async function(assert) {
        const visibleAssertion = QAAssert.elementIsVisible('#test-element');
        const visibleResult = await visibleAssertion();
        assert.ok(visibleResult.passed, 'visible element should pass');
        
        const hiddenAssertion = QAAssert.elementIsVisible('#hidden-element');
        const hiddenResult = await hiddenAssertion();
        assert.notOk(hiddenResult.passed, 'hidden element should fail');
    });
    
    QUnit.test('custom assertion works', async function(assert) {
        const assertion = QAAssert.custom(() => 1 + 1 === 2, 'Math works');
        const result = await assertion();
        assert.ok(result.passed);
        
        const assertion2 = QAAssert.custom(() => false, 'This fails');
        const result2 = await assertion2();
        assert.notOk(result2.passed);
    });
});
