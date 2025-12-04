# MGraph HTML Graph - Test Suite

**Version**: v0.1.4  
**Framework**: QUnit 2.20 (CDN)

## Overview

Browser-based unit and integration tests for the MGraph HTML Graph Render UI.

## Running Tests

### All Tests (Consolidated)
Open `index.html` in a browser - runs all unit and integration tests together.

### Individual Component Tests
Each component has its own test file that can be run independently:

- `unit/api-client.test.html` - API Client tests
- `unit/config-panel.test.html` - Config Panel tests
- `unit/html-input.test.html` - HTML Input tests
- `unit/stats-toolbar.test.html` - Stats Toolbar tests
- `unit/graph-canvas.test.html` - Graph Canvas tests
- `unit/dot-renderer.test.html` - DOT Renderer tests
- `unit/dot-parser.test.html` - DOT Parser logic tests
- `unit/url-input.test.html` - URL Input tests
- `integration/playground.test.html` - Playground integration tests

## Directory Structure

```
tests/
├── index.html                    # Consolidated test runner
├── test-paths.js                 # Component path configuration
├── test-paths.v0.2.0.template.js # Template for v0.2.0 consolidation
├── test-utils.js                 # Test utilities and helpers
├── README.md                     # This file
├── unit/                         # Unit tests (one per component)
│   ├── api-client.test.html
│   ├── api-client.test.js
│   ├── config-panel.test.html
│   ├── config-panel.test.js
│   └── ...
└── integration/                  # Integration tests
    ├── playground.test.html
    └── playground.test.js
```

## Design Principles

### 1. No npm/node_modules Required Locally
- QUnit loaded from CDN
- No build step needed
- Tests run directly in browser

### 2. Path Configuration via `test-paths.js`
All component paths are centralized in `test-paths.js`. This is the **only file that changes** when consolidating versions.

### 3. Version-Agnostic Tests
Tests are written against component behavior, not implementation details. The same tests work for v0.1.x and v0.2.0.

## Consolidating to v0.2.0

When creating v0.2.0 from v0.1.4:

1. Copy entire `tests/` folder to `v0.2.0/tests/`
2. Copy `test-paths.v0.2.0.template.js` to `test-paths.js`
3. Run tests - **all should pass without modifications**

The template file updates paths from cross-version references (e.g., `../v0.1.1/components/...`) to local paths (e.g., `../components/...`).

## Test Categories

### Unit Tests
Test individual components in isolation:
- Component rendering
- Public methods (getters/setters)
- Event emission
- State management

### Integration Tests
Test component interactions:
- Event flow between components
- Mock API responses
- Error handling flows
- State preservation during interactions

## Writing New Tests

Use the `TestUtils` helper:

```javascript
QUnit.module('My Component', function(hooks) {
    hooks.before(async function(assert) {
        await TestUtils.loadScript(TestPaths.myComponent);
        assert.ok(customElements.get('my-component'), 'should be registered');
    });
    
    hooks.afterEach(function() {
        TestUtils.cleanup();
    });

    QUnit.test('basic render', async function(assert) {
        const component = await TestUtils.createComponent('my-component');
        assert.ok(component.querySelector('.expected-class'), 'should render');
    });
});
```

## CI Pipeline Integration

For CI, use a headless browser runner:

```bash
# Example with puppeteer-qunit
npx puppeteer-qunit tests/index.html

# Or with playwright
npx playwright test --config=playwright.config.js
```

The tests use QUnit's standard TAP output which integrates with most CI systems.

## Troubleshooting

### Tests fail to load components
- Check `test-paths.js` paths are correct
- Ensure components exist at specified locations
- Check browser console for 404 errors

### Async tests timeout
- Increase timeout in `TestUtils.waitForEvent()`
- Check for missing event emissions in component code

### Tests pass individually but fail consolidated
- Check for global state pollution between tests
- Ensure `TestUtils.cleanup()` is called in `afterEach`
