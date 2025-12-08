# QA UI Testing Framework for IFD v0.2.0

## Overview

This QA UI framework implements the automated testing strategy described in the "Integrating Automated QA Testing into the IFD Pipeline" brief. It provides:

1. **Automated Fast Mode** - Run all tests rapidly for CI/CD
2. **Interactive Slow-Motion Mode** - Step through tests with visual feedback
3. **State Teleportation Mode** - Jump to specific application states for debugging

## File Structure

```
qa-ui/
├── qa-runner.html              # Main QA test runner page
├── qa-tests.html               # QUnit tests for the QA framework itself
├── qa/
│   ├── qa-engine.js            # Core QA execution engine
│   ├── qa-engine.test.js       # Tests for the QA engine
│   ├── components/
│   │   └── qa-control-panel.js # Visual control panel component
│   └── scenarios/
│       └── playground-scenarios.js  # UAT scenarios for playground
```

## Integration Instructions

### Step 1: Copy to v0.2.0

Copy the `qa` folder and HTML files to your v0.2.0 project:

```
v0.2.0/
├── qa/                         # ← Copy here
│   ├── qa-engine.js
│   ├── qa-engine.test.js
│   ├── components/
│   │   └── qa-control-panel.js
│   └── scenarios/
│       └── playground-scenarios.js
├── qa-runner.html              # ← Copy here
├── qa-tests.html               # ← Copy here
├── components/
├── css/
├── js/
├── tests/
└── playground.html
```

### Step 2: Update qa-runner.html Paths

The `qa-runner.html` file assumes this folder structure. Update the paths if needed:

```html
<!-- Application CSS -->
<link rel="stylesheet" href="css/common.css">
<link rel="stylesheet" href="css/playground.css">

<!-- Iframe source -->
<iframe id="app-frame" src="playground.html"></iframe>

<!-- QA Framework Scripts -->
<script src="qa/qa-engine.js"></script>
<script src="qa/components/qa-control-panel.js"></script>
<script src="qa/scenarios/playground-scenarios.js"></script>
```

### Step 3: Add to Test Suite

Add QA engine tests to your existing test runner (`tests/index.html`):

```html
<!-- Add after other test scripts -->
<script src="../qa/qa-engine.js"></script>
<script src="../qa/qa-engine.test.js"></script>
```

## Usage

### Running the QA UI

1. Start your development server
2. Navigate to `qa-runner.html`
3. Select a scenario from the dropdown
4. Choose a mode:
   - **Fast** - Runs all steps immediately
   - **Slow-Mo** - Runs with pauses between steps
   - **Teleport** - Jump to a specific step number
5. Click **Run** or use keyboard shortcut `Ctrl+R`

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+R` | Run scenario |
| `Ctrl+N` | Next step |
| `Ctrl+P` | Pause/Resume |
| `Ctrl+S` | Stop |

### Creating New Scenarios

Create a new file in `qa/scenarios/`:

```javascript
const myScenario = new QAScenario({
    id: 'my-scenario',
    name: 'My User Journey',
    description: 'Tests a specific user workflow',
    tags: ['feature', 'regression']
});

myScenario.addSteps([
    {
        name: 'Step 1: Navigate to page',
        description: 'User opens the application',
        action: async () => {
            // Your action code here
            await new Promise(r => setTimeout(r, 100));
        },
        assertions: [
            QAAssert.elementExists('#main-element'),
            QAAssert.elementContainsText('.header', 'Welcome')
        ]
    },
    {
        name: 'Step 2: Perform action',
        description: 'User clicks a button',
        action: async () => {
            document.querySelector('#my-button').click();
            await new Promise(r => setTimeout(r, 500));
        },
        assertions: [
            QAAssert.custom(async () => {
                // Custom assertion logic
                return someCondition;
            }, 'Custom condition should be true')
        ]
    }
]);

// Register in registerAllScenarios() function
```

### Available Assertions

| Assertion | Usage |
|-----------|-------|
| `elementExists(selector)` | Check element exists in DOM |
| `elementContainsText(selector, text)` | Check element contains text |
| `elementHasValue(selector, value)` | Check input value |
| `elementIsVisible(selector)` | Check element is visible |
| `elementHasClass(selector, className)` | Check element has CSS class |
| `waitForElement(selector, timeout)` | Wait for element to appear |
| `custom(fn, message)` | Custom assertion function |

### Available Actions (QAActions helper)

| Action | Usage |
|--------|-------|
| `click(selector)` | Click an element |
| `type(selector, text)` | Type into an input |
| `select(selector, value)` | Select dropdown option |
| `setCheckbox(selector, checked)` | Check/uncheck checkbox |
| `wait(ms)` | Wait for duration |
| `waitForElement(selector, timeout)` | Wait for element |
| `waitForEvent(element, eventName, timeout)` | Wait for event |
| `dispatchEvent(selector, eventName, detail)` | Dispatch custom event |
| `callMethod(selector, methodName, ...args)` | Call component method |

## Included Scenarios

The framework includes 6 pre-built scenarios for the playground:

1. **s01-basic-render** - Basic graph rendering workflow
2. **s02-config-changes** - Configuration panel interactions
3. **s03-renderer-switching** - Switching between renderers
4. **s04-sample-loading** - Loading sample HTML files
5. **s05-stats-display** - Statistics and timing display
6. **s06-error-handling** - Error handling and recovery

## CI/CD Integration

Run all scenarios in headless mode:

```javascript
// In a Node.js test runner with Puppeteer
const browser = await puppeteer.launch({ headless: true });
const page = await browser.newPage();
await page.goto('http://localhost:8000/qa-runner.html');

// Wait for QA engine to be ready
await page.waitForFunction(() => window.qaEngine);

// Run all scenarios
const results = await page.evaluate(async () => {
    return await window.qaEngine.runAllScenarios();
});

console.log(`Results: ${results.totalPassed} passed, ${results.totalFailed} failed`);
process.exit(results.totalFailed > 0 ? 1 : 0);
```

## Best Practices

1. **Test user journeys, not implementation** - Focus on what users do, not how code works
2. **Keep steps atomic** - Each step should do one thing
3. **Use meaningful assertions** - Assert on visible outcomes
4. **Avoid flaky waits** - Use `waitForElement` instead of fixed delays
5. **Update tests with features** - When changing UI, update scenarios too
6. **Run locally first** - Use Fast mode before committing

## Aligns with IFD Principles

- ✅ **Pure HTML/JS** - No external test frameworks beyond QUnit
- ✅ **Co-located with code** - Scenarios live in the project
- ✅ **Real data testing** - Tests run against the actual application
- ✅ **Version-specific** - Test suites evolve with the application
- ✅ **Developer-maintained** - Tests are part of "definition of done"
