# v0.2.1 - Component Architecture Refactoring (Phase 1)

## Overview

Phase 1 implements the foundation for Shadow DOM components and refactors two pilot components (`stats-toolbar` and `url-input`) to validate the architecture.

## What's New

### Foundation Files

| File | Purpose |
|------|---------|
| `config/component-paths.js` | Centralized path configuration for resources |
| `components/_base/base-component.js` | Base class for Shadow DOM components |
| `js/utils/helpers.js` | Shared utilities (`escapeHtml`, `formatBytes`, etc.) |
| `css/components-shared.css` | Shared component CSS patterns |

### Refactored Components

| Component | JS Lines | Reduction | Notes |
|-----------|----------|-----------|-------|
| `stats-toolbar` | 121 | ~40% | Now uses Shadow DOM, external template |
| `url-input` | 123 | ~38% | Now uses Shadow DOM, external template |

Each component now has three files:
- `component.js` - Slim logic extending BaseComponent
- `component.html` - External template loaded via fetch
- `component.css` - Component-specific styles

## File Structure

```
v0.2.1/
├── config/
│   └── component-paths.js       # Resource path configuration
├── css/
│   └── components-shared.css    # Shared component patterns
├── components/
│   ├── _base/
│   │   ├── base-component.js    # Base class for all components
│   │   └── base-component.test.js
│   ├── stats-toolbar/
│   │   ├── stats-toolbar.js     # Slim component logic
│   │   ├── stats-toolbar.html   # External template
│   │   ├── stats-toolbar.css    # Component-specific styles
│   │   └── stats-toolbar.test.js
│   └── url-input/
│       ├── url-input.js
│       ├── url-input.html
│       ├── url-input.css
│       └── url-input.test.js
├── js/
│   └── utils/
│       ├── helpers.js           # Shared utility functions
│       └── helpers.test.js
├── tests/
│   ├── index.html               # Test runner
│   ├── test-paths.js            # Test path configuration
│   └── test-utils.js            # Test utilities with Shadow DOM helpers
└── playground.html              # Demo page
```

## Key Architecture Decisions

### 1. Shadow DOM for Style Isolation
Each component uses Shadow DOM (`attachShadow({ mode: 'open' })`), providing:
- Encapsulated styles (no CSS leakage)
- Clean template injection
- Independent component styling

### 2. BaseComponent Class
All refactored components extend `BaseComponent`, which provides:
- Automatic resource loading (CSS + HTML templates)
- Shadow DOM setup
- Event listener tracking and cleanup
- Common utility methods (`$()`, `$$()`, `emit()`)
- Standardized lifecycle hooks

### 3. Composed Events
Events use `composed: true` to cross Shadow DOM boundaries:
```javascript
this.dispatchEvent(new CustomEvent('event-name', {
    detail: { ... },
    bubbles: true,
    composed: true  // Crosses Shadow DOM
}));
```

### 4. CSS Variables Inheritance
CSS variables from `common.css` are inherited through `:host` with fallbacks:
```css
:host {
    --spacing-md: 20px;  /* Fallback if not defined */
}
```

## How to Test

### Browser Tests
Open `tests/index.html` in a browser to run QUnit tests.

### Demo Page
Open `playground.html` to see the refactored components in action alongside v0.2.0 components.

## Linking Back to v0.2.0

The `playground.html` demonstrates how v0.2.1 links back to v0.2.0 for unchanged components:

```html
<!-- v0.2.1 Foundation -->
<script src="./js/utils/helpers.js"></script>
<script src="./config/component-paths.js"></script>
<script src="./components/_base/base-component.js"></script>

<!-- v0.2.0 unchanged components -->
<script src="../v0.2.0/components/config-panel/config-panel.js"></script>

<!-- v0.2.1 refactored components -->
<script src="./components/stats-toolbar/stats-toolbar.js"></script>
```

## Next Steps (Phase 2)

Refactor remaining UI components:
- `config-panel`
- `html-input`
- `graph-canvas`
- `top-nav`

## Success Criteria Met

✅ Components use Shadow DOM for style isolation  
✅ CSS extracted to external files  
✅ HTML templates extracted to external files  
✅ BaseComponent provides shared infrastructure  
✅ Helpers extracted and shared  
✅ JS files ~40% smaller  
✅ Comprehensive test coverage  
