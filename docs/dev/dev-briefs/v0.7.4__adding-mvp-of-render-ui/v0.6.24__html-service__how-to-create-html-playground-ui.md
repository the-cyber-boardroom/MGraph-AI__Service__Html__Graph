# MGraph-AI__Service__Html - Admin UI Implementation Brief

## 📋 Document Overview

**Purpose**: Complete technical brief for implementing an admin UI for the MGraph-AI__Service__Html service  
**Methodology**: Iterative Flow Development (IFD)  
**Target Audience**: LLM assistant with access to MGraph-AI__Service__Html codebase  
**Implementation Approach**: Progressive enhancement through incremental versions  

---

## 🎯 Project Objectives

### Primary Goal
Create an interactive web-based admin UI that serves as both a **testing playground** and **documentation tool** for the HTML transformation service. Users should be able to understand and test all service capabilities without reading documentation or setting up files.

### Key Requirements
✅ **Zero Setup Required** - Pre-loaded samples, no file upload needed to start  
✅ **Self-Documenting** - Examples demonstrate capabilities  
✅ **Zero External Dependencies** - Pure native web platform (HTML/CSS/ES6+ JS)  
✅ **IFD Compliant** - Version independence at major version level, incremental minor versions  
✅ **Real API Integration** - Calls actual service endpoints (no CORS, same server)  
✅ **Responsive Design** - Works on desktop, tablet, mobile  

---

## 🗃️ Service Context

### MGraph-AI__Service__Html Overview

The service provides HTML transformation capabilities through a FastAPI backend with the following routes:

#### **HTML Routes** (`/html/*`)
- `POST /html/to__dict` - Parse HTML to dictionary structure
- `POST /html/to__html` - Round-trip validation (HTML → Dict → HTML)
- `POST /html/to__text__nodes` - Extract text nodes with hash identifiers
- `POST /html/to__lines` - Format HTML as readable lines
- `POST /html/to__html__hashes` - Replace text with hashes (debugging)
- `POST /html/to__html__xxx` - Replace text with x's (privacy masking)

#### **Dict Routes** (`/dict/*`)
- `POST /dict/to__html` - Reconstruct HTML from dictionary
- `POST /dict/to__text__nodes` - Extract text nodes from dictionary
- `POST /dict/to__lines` - Format dictionary as lines

#### **Hashes Routes** (`/hashes/*`)
- `POST /hashes/to__html` - Apply hash mapping to reconstruct modified HTML

### Key Service Concepts

**HTML → Dict**: Parses HTML into a nested dictionary structure representing the DOM tree

**Text Nodes Extraction**: Identifies all text content in HTML and assigns unique 10-character hash identifiers

**Hash Mapping**: Enables semantic text modification by mapping hashes to replacement text, then reconstructing HTML with modifications

**Max Depth Parameter**: Controls traversal depth in tree operations (default: 256)

---

## 📚 IFD Methodology - Core Principles

### Version Independence Model

**CRITICAL UNDERSTANDING:**

**Major Versions are Independent:**
- v0.1.0 is completely independent from v0.2.0
- v0.2.0 is completely independent from v1.0.0
- Each major version is a fresh start with NO dependencies on previous major versions

**Minor Versions are Incremental:**
- v0.1.1 builds on and references files from v0.1.0
- v0.1.2 builds on v0.1.1 and can reference any v0.1.x files
- v0.1.5 may still use files created in v0.1.0, v0.1.2, or v0.1.3
- Minor versions contain ONLY the changed/new files for that specific increment

**Example Structure:**
```
v0.1.0/  (Complete standalone implementation)
├── index.html
├── css/common.css
├── css/dashboard.css
└── js/api-client.js

v0.1.1/  (ONLY new/changed files)
├── playground.html              # NEW file
├── css/playground.css           # NEW file
├── js/playground.js             # NEW file
└── components/                  # NEW directory
    └── html-input/
        ├── html-input.html
        ├── html-input.css
        └── html-input.js

# v0.1.1 references:
# - ../v0.1.0/css/common.css
# - ../v0.1.0/js/api-client.js
# - etc.

v0.1.2/  (ONLY new/changed files)
├── components/
    └── advanced-filter/         # NEW component
        └── ...

# v0.1.2 references:
# - ../v0.1.0/css/common.css
# - ../v0.1.1/components/html-input/
# - etc.

v0.2.0/  (NEW major version - completely independent)
├── index.html                   # Fresh implementation
├── styles/                      # Different structure
└── ...                          # NO references to v0.1.x
```

### Progressive Enhancement
```
v0.1.0 → Core foundation (Dashboard)
v0.1.1 → Add Playground (references v0.1.0 files)
v0.1.2 → Add Text Explorer (references v0.1.0 and v0.1.1 files)
v0.1.3 → Add Hash Mapper (references previous v0.1.x files)
...
v0.2.0 → New major version (fresh start, no v0.1.x dependencies)
```

### Zero External Dependencies
- NO React, Vue, Angular, jQuery, etc.
- Use native Web Components (Custom Elements)
- ES6+ JavaScript only
- Browser APIs: Fetch, DOM manipulation
- Self-contained CSS

### Component Architecture Patterns

**Simple Components** (< 200 lines): Use **flat structure**
```
components/my-component/
├── my-component.html
├── my-component.css
└── my-component.js
```

**Complex Components** (> 200 lines): Use **modular structure**
```
components/complex/
├── complex.js              # Main orchestrator
├── html/
│   └── complex.html
├── css/
│   └── complex.css
└── js/
    ├── data.js
    ├── ui.js
    └── events.js
```

### Event-Driven Communication
Components communicate via CustomEvents, NOT direct method calls:

```javascript
// Component emits
this.dispatchEvent(new CustomEvent('data-changed', {
  detail: { value: newData },
  bubbles: true
}));

// Another component listens
document.addEventListener('data-changed', (e) => {
  console.log('Received:', e.detail.value);
});
```

### Real Data From Day One
NO mocked data or stubbed services. Call actual API endpoints immediately. Test with real responses.

---

## 📁 Complete Folder Structure

### Admin UI Package Structure

```
mgraph_ai_service_html__admin_ui/
├── __init__.py                           # Package definition
│   # Content:
│   # package_name = 'mgraph_ai_service_html__admin_ui'
│   # path         = __path__[0]
│
└── v0/
    ├── v0.1.0/                          # Major Version: Complete Foundation
    │   ├── index.html                    # Dashboard page
    │   ├── 404.html                      # Error page
    │   ├── README.md                     # Version documentation
    │   ├── css/
    │   │   ├── common.css               # Shared styles (gradient, cards, buttons)
    │   │   └── dashboard.css            # Dashboard-specific styles
    │   ├── js/
    │   │   ├── services/
    │   │   │   └── api-client.js        # API communication service
    │   │   └── dashboard.js             # Dashboard page logic
    │   └── samples/                      # Sample HTML files
    │       ├── simple.html              # Minimal example
    │       ├── complex.html             # Nested structure
    │       └── dashboard.html           # Self-referential (this page!)
    │
    └── v0.1.1/                          # Minor Version: ONLY new/changed files
        ├── playground.html               # NEW: Playground page
        ├── README.md                     # NEW: Updated documentation
        ├── css/
        │   └── playground.css           # NEW: Playground-specific styles
        ├── components/                   # NEW: Web Components directory
        │   ├── top-nav/                 # NEW: Navigation component
        │   │   ├── top-nav.html
        │   │   ├── top-nav.css
        │   │   └── top-nav.js
        │   ├── html-input/              # NEW: HTML input panel
        │   │   ├── html-input.html
        │   │   ├── html-input.css
        │   │   └── html-input.js
        │   ├── transformation-selector/ # NEW: Endpoint selector
        │   │   ├── transformation-selector.html
        │   │   ├── transformation-selector.css
        │   │   └── transformation-selector.js
        │   └── output-viewer/           # NEW: Output display
        │       ├── output-viewer.html
        │       ├── output-viewer.css
        │       └── output-viewer.js
        ├── js/
        │   └── playground.js            # NEW: Playground orchestrator
        └── samples/
            └── playground.html          # NEW: Self-referential playground

        # v0.1.1 REFERENCES (via relative paths):
        # - ../v0.1.0/css/common.css
        # - ../v0.1.0/js/services/api-client.js
        # - ../v0.1.0/samples/simple.html
        # - ../v0.1.0/samples/complex.html
        # - ../v0.1.0/404.html
```

### Path References in v0.1.1

When v0.1.1 needs files from v0.1.0, it uses relative paths:

**Example: v0.1.1/playground.html**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Transformation Playground - HTML Service</title>
    
    <!-- Reference v0.1.0 common styles -->
    <link rel="stylesheet" href="../v0.1.0/css/common.css">
    
    <!-- v0.1.1 specific styles -->
    <link rel="stylesheet" href="./css/playground.css">
</head>
<body>
    <div class="container">
        <!-- Component markup -->
    </div>

    <!-- Reference v0.1.0 API client -->
    <script src="../v0.1.0/js/services/api-client.js"></script>

    <!-- v0.1.1 components -->
    <script src="./components/top-nav/top-nav.js"></script>
    <script src="./components/html-input/html-input.js"></script>
    
    <!-- v0.1.1 orchestrator -->
    <script src="./js/playground.js"></script>
</body>
</html>
```

**Example: v0.1.1/components/html-input/html-input.js**
```javascript
/**
 * HTML Input Component
 * Loads samples from v0.1.0 using relative paths
 */
class HtmlInput extends HTMLElement {
    // ...
    
    async loadSample(sampleName) {
        try {
            // Reference v0.1.0 samples
            const response = await fetch(`../../v0.1.0/samples/${sampleName}.html`);
            const html = await response.text();
            // ... rest of implementation
        } catch (error) {
            console.error('Failed to load sample:', error);
        }
    }
}
```

---

## 📌 Backend Integration

### Python Service Class

Create a new file in the main service:

**Location**: `mgraph_ai_service_html/html__fast_api/Html__Admin__Service.py`

**Purpose**: Serves static admin UI files and handles routing, following the exact pattern from `Proxy__Admin__Service.py` in the mitmproxy codebase.

**Key Implementation Details**:

```python
import mgraph_ai_service_html__admin_ui
from pathlib import Path
from osbot_utils.type_safe.Type_Safe import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Version import Safe_Str__Version
# ... other imports

class Html__Admin__Service(Type_Safe):
    current_version: Safe_Str__Version = Safe_Str__Version("v0.1.1")
    admin_ui_root: Path

    def setup(self):
        self.admin_ui_root = Path(mgraph_ai_service_html__admin_ui.path)
        return self

    def is_admin_path(self, path) -> bool:
        return str(path).startswith('/html-service')

    def handle_admin_request(self, path) -> Optional[Dict]:
        # Route admin requests:
        # - /html-service/ → redirect to latest version
        # - /html-service/v0/{version}/* → serve static files
        # Files are resolved across version boundaries
        # e.g., v0.1.1/playground.html can reference ../v0.1.0/css/common.css
        pass

    def redirect_to_latest(self) -> Dict:
        redirect_url = f"/html-service/v0/{self.current_version}/index.html"
        return {
            "status_code": 302,
            "body": f'<html><head><meta http-equiv="refresh" content="0; url={redirect_url}"></head></html>',
            "headers": {
                "Location": str(redirect_url),
                "content-type": "text/html; charset=utf-8"
            }
        }

    def serve_static_file(self, path) -> Optional[Dict]:
        # Serve files from admin_ui_root/v0/{version}/
        # Resolve relative paths (../) to support cross-version references
        # Security: ensure resolved path doesn't escape admin_ui_root
        # Return 404 if file not found
        pass

    def serve_404(self, path) -> Dict:
        # Look for 404.html in current version first
        # If not found, look in parent major version (v0.1.0)
        # Fallback to generic 404
        pass

    def get_content_type(self, suffix) -> str:
        # Map file extensions: .html, .css, .js, .json
        pass
```

### URL Structure

```
# Admin UI URLs (served by Html__Admin__Service)
http://localhost:8000/html-service/                           → 302 redirect to latest
http://localhost:8000/html-service/v0/v0.1.0/index.html      → Dashboard v0.1.0
http://localhost:8000/html-service/v0/v0.1.1/playground.html → Playground v0.1.1

# Cross-version references (handled by serve_static_file)
http://localhost:8000/html-service/v0/v0.1.0/css/common.css  → Served from v0.1.0
http://localhost:8000/html-service/v0/v0.1.1/css/playground.css → Served from v0.1.1

# Service API URLs (existing FastAPI routes)
http://localhost:8000/html/to__dict                          → POST endpoint
http://localhost:8000/html/to__text__nodes                   → POST endpoint
http://localhost:8000/dict/to__html                          → POST endpoint
http://localhost:8000/hashes/to__html                        → POST endpoint
# ... all other routes
```

**Critical**: Admin UI and API share the same origin → **NO CORS issues!**

---

## 🎨 Design System

### Color Palette

```css
/* Primary Colors */
--color-primary: #667eea;        /* Purple-blue */
--color-secondary: #764ba2;      /* Purple */
--gradient-bg: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Status Colors */
--color-success: #10b981;        /* Green */
--color-error: #ef4444;          /* Red */
--color-warning: #f59e0b;        /* Orange */
--color-info: #3b82f6;           /* Blue */

/* Neutral Colors */
--color-text-primary: #333;
--color-text-secondary: #666;
--color-text-muted: #999;
--color-bg-card: #ffffff;
--color-bg-muted: #f7f7f7;
--color-border: #ddd;
```

### Typography

```css
/* Font Families */
--font-primary: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
--font-code: 'Courier New', monospace;

/* Font Sizes */
--font-size-base: 1em;           /* 16px */
--font-size-small: 0.9em;        /* 14.4px */
--font-size-large: 1.1em;        /* 17.6px */
--font-size-h1: 2em;             /* 32px */
--font-size-h2: 1.5em;           /* 24px */
--font-size-h3: 1.3em;           /* 20.8px */
```

### Layout Constants

```css
/* Spacing */
--spacing-xs: 5px;
--spacing-sm: 10px;
--spacing-md: 20px;
--spacing-lg: 30px;
--spacing-xl: 40px;

/* Border Radius */
--radius-sm: 5px;
--radius-md: 10px;
--radius-lg: 15px;

/* Shadows */
--shadow-sm: 0 2px 4px rgba(0,0,0,0.1);
--shadow-md: 0 4px 6px rgba(0,0,0,0.1);
--shadow-lg: 0 6px 12px rgba(0,0,0,0.15);

/* Container */
--container-max-width: 1200px;
--card-padding: 30px;
```

### Common CSS Patterns

**Base Styles** (`v0.1.0/css/common.css` - created in v0.1.0, referenced by all v0.1.x versions):
```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: var(--font-primary);
    background: var(--gradient-bg);
    min-height: 100vh;
    padding: 20px;
}

.container {
    max-width: var(--container-max-width);
    margin: 0 auto;
}

.card {
    background: var(--color-bg-card);
    border-radius: var(--radius-md);
    padding: var(--card-padding);
    margin-bottom: var(--spacing-md);
    box-shadow: var(--shadow-md);
}

.card-title {
    font-size: var(--font-size-h2);
    color: var(--color-text-primary);
    margin-bottom: var(--spacing-md);
    border-bottom: 2px solid var(--color-primary);
    padding-bottom: var(--spacing-sm);
}

/* Buttons */
.btn {
    padding: 12px 30px;
    border: none;
    border-radius: var(--radius-sm);
    font-size: var(--font-size-base);
    font-weight: 600;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
}

.btn:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

.btn-primary {
    background: var(--color-primary);
    color: white;
}

.btn-secondary {
    background: #6c757d;
    color: white;
}

/* Loading States */
.loading {
    opacity: 0.5;
    pointer-events: none;
}

.spinner {
    border: 4px solid #f3f3f3;
    border-top: 4px solid var(--color-primary);
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
    margin: 20px auto;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
```

---

## 📦 v0.1.0 - Dashboard Implementation

### Purpose
Create service overview page with navigation to future features. Establish design patterns and project structure.

### Files to Create (Complete Foundation)

This is a **major version** - contains ALL files needed for this version to function independently.

#### File List:
- `index.html` - Dashboard page
- `404.html` - Error page  
- `README.md` - Version documentation
- `css/common.css` - Shared design system
- `css/dashboard.css` - Dashboard-specific styles
- `js/services/api-client.js` - API communication
- `js/dashboard.js` - Dashboard logic
- `samples/simple.html` - Basic sample
- `samples/complex.html` - Complex sample
- `samples/dashboard.html` - Self-referential sample

### Pages

#### `index.html` - Dashboard

**Structure**:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HTML Service Admin - Dashboard</title>
    <link rel="stylesheet" href="./css/common.css">
    <link rel="stylesheet" href="./css/dashboard.css">
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header class="page-header">
            <h1>🔧 HTML Transformation Service</h1>
            <p class="subtitle">Interactive API testing and documentation</p>
        </header>

        <!-- Service Info Card -->
        <section class="card" id="service-info">
            <!-- Will be populated by dashboard.js -->
        </section>

        <!-- API Endpoints Overview -->
        <section class="card" id="endpoints-overview">
            <!-- Will be populated by dashboard.js -->
        </section>

        <!-- Quick Actions -->
        <section class="card" id="quick-actions">
            <!-- Will be populated by dashboard.js -->
        </section>

        <!-- Footer -->
        <footer class="footer">
            <p>HTML Service Admin UI v0.1.0</p>
        </footer>
    </div>

    <!-- Services -->
    <script src="./js/services/api-client.js"></script>
    
    <!-- Main App -->
    <script src="./js/dashboard.js"></script>
</body>
</html>
```

**Content Requirements**:

1. **Service Info Card**:
   - Service name: "MGraph-AI HTML Service"
   - Version: (from service)
   - Description: Brief explanation of capabilities
   - Status indicator (e.g., "Running")

2. **API Endpoints Overview**:
   Display all routes grouped by category with descriptions:
   
   ```
   HTML Transformations:
   - POST /html/to__dict - Parse HTML to dictionary structure
   - POST /html/to__text__nodes - Extract text nodes with hashes
   - POST /html/to__lines - Format HTML as readable lines
   - POST /html/to__html__hashes - Replace text with hashes
   - POST /html/to__html__xxx - Replace text with x's (privacy)
   
   Dictionary Operations:
   - POST /dict/to__html - Reconstruct HTML from dictionary
   - POST /dict/to__text__nodes - Extract text from dictionary
   - POST /dict/to__lines - Format dictionary as lines
   
   Hash Operations:
   - POST /hashes/to__html - Apply hash mappings to HTML
   ```

3. **Quick Actions**:
   Cards linking to future pages:
   - "🎮 Try Playground" → `/html-service/v0/v0.1.1/playground.html` (coming soon badge)
   - "📊 Explore Text Nodes" → (coming soon)
   - "🔐 Hash Mapper" → (coming soon)

#### `404.html` - Error Page

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Not Found - HTML Service</title>
    <link rel="stylesheet" href="./css/common.css">
    <style>
        .error-container {
            background: white;
            border-radius: 10px;
            padding: 60px 50px;
            text-align: center;
            max-width: 600px;
            margin: 100px auto;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .error-code {
            font-size: 6em;
            color: #667eea;
            font-weight: bold;
            margin: 0;
        }
    </style>
</head>
<body>
    <div class="error-container">
        <div class="error-code">404</div>
        <h1>Page Not Found</h1>
        <p>The requested page does not exist.</p>
        <a href="/html-service/" class="btn btn-primary">← Back to Dashboard</a>
    </div>
</body>
</html>
```

### JavaScript Services

#### `js/services/api-client.js`

**Purpose**: Handle all API communication with the HTML service

**Implementation**:
```javascript
/**
 * API Client Service for HTML Transformation Service
 * Handles all communication with service endpoints
 */
class APIClient {
    constructor() {
        this.baseURL = window.location.origin; // Same server, no CORS!
    }

    /**
     * Generic endpoint caller
     * @param {string} endpoint - API route (e.g., '/html/to__dict')
     * @param {object} payload - Request body
     * @returns {Promise<object>} - Response data
     */
    async callEndpoint(endpoint, payload) {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json' 
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`API Error ${response.status}: ${errorText}`);
        }

        return await response.json();
    }

    /**
     * Convenience methods for specific endpoints
     */
    
    // HTML transformations
    async htmlToDict(html) {
        return this.callEndpoint('/html/to__dict', { html });
    }

    async htmlToTextNodes(html, maxDepth = 256) {
        return this.callEndpoint('/html/to__text__nodes', { 
            html, 
            max_depth: maxDepth 
        });
    }

    async htmlToLines(html) {
        return this.callEndpoint('/html/to__lines', { html });
    }

    async htmlToHtmlHashes(html, maxDepth = 256) {
        return this.callEndpoint('/html/to__html__hashes', { 
            html, 
            max_depth: maxDepth 
        });
    }

    async htmlToHtmlXxx(html, maxDepth = 256) {
        return this.callEndpoint('/html/to__html__xxx', { 
            html, 
            max_depth: maxDepth 
        });
    }

    // Dict operations
    async dictToHtml(htmlDict) {
        return this.callEndpoint('/dict/to__html', { html_dict: htmlDict });
    }

    async dictToTextNodes(htmlDict, maxDepth = 256) {
        return this.callEndpoint('/dict/to__text__nodes', { 
            html_dict: htmlDict, 
            max_depth: maxDepth 
        });
    }

    async dictToLines(htmlDict) {
        return this.callEndpoint('/dict/to__lines', { html_dict: htmlDict });
    }

    // Hash operations
    async hashesToHtml(htmlDict, hashMapping) {
        return this.callEndpoint('/hashes/to__html', { 
            html_dict: htmlDict, 
            hash_mapping: hashMapping 
        });
    }

    /**
     * Event emitter for cross-component communication
     */
    emit(eventName, detail) {
        window.dispatchEvent(new CustomEvent(eventName, { detail }));
    }

    on(eventName, handler) {
        window.addEventListener(eventName, handler);
    }

    off(eventName, handler) {
        window.removeEventListener(eventName, handler);
    }
}

// Create global instance
window.apiClient = new APIClient();
```

#### `js/dashboard.js`

**Purpose**: Populate dashboard page with service information

**Implementation**:
```javascript
/**
 * Dashboard Page Logic
 * Populates service info, endpoints, and quick actions
 */
document.addEventListener('DOMContentLoaded', () => {
    // Service info
    const serviceInfo = document.getElementById('service-info');
    serviceInfo.innerHTML = `
        <div class="card-title">📋 Service Information</div>
        <div class="info-grid">
            <div class="info-item">
                <span class="info-label">Service Name:</span>
                <span class="info-value">MGraph-AI HTML Service</span>
            </div>
            <div class="info-item">
                <span class="info-label">Version:</span>
                <span class="info-value">v0.6.1</span>
            </div>
            <div class="info-item">
                <span class="info-label">Status:</span>
                <span class="info-value status-active">● Running</span>
            </div>
            <div class="info-item">
                <span class="info-label">Description:</span>
                <span class="info-value">Transform HTML documents using various operations including parsing, text extraction, and hash-based modifications</span>
            </div>
        </div>
    `;

    // Endpoints overview
    const endpointsOverview = document.getElementById('endpoints-overview');
    const endpoints = [
        {
            category: 'HTML Transformations',
            routes: [
                { route: 'POST /html/to__dict', desc: 'Parse HTML to dictionary structure' },
                { route: 'POST /html/to__text__nodes', desc: 'Extract text nodes with hash identifiers' },
                { route: 'POST /html/to__lines', desc: 'Format HTML as readable lines' },
                { route: 'POST /html/to__html__hashes', desc: 'Replace text with hashes (debugging)' },
                { route: 'POST /html/to__html__xxx', desc: 'Replace text with x\'s (privacy masking)' }
            ]
        },
        {
            category: 'Dictionary Operations',
            routes: [
                { route: 'POST /dict/to__html', desc: 'Reconstruct HTML from dictionary' },
                { route: 'POST /dict/to__text__nodes', desc: 'Extract text nodes from dictionary' },
                { route: 'POST /dict/to__lines', desc: 'Format dictionary as lines' }
            ]
        },
        {
            category: 'Hash Operations',
            routes: [
                { route: 'POST /hashes/to__html', desc: 'Apply hash mappings to reconstruct HTML' }
            ]
        }
    ];

    let endpointsHTML = '<div class="card-title">📌 API Endpoints</div>';
    endpoints.forEach(group => {
        endpointsHTML += `<div class="endpoint-group">
            <h3>${group.category}</h3>
            <ul class="endpoint-list">`;
        group.routes.forEach(route => {
            endpointsHTML += `<li>
                <code class="route-name">${route.route}</code>
                <span class="route-desc">${route.desc}</span>
            </li>`;
        });
        endpointsHTML += '</ul></div>';
    });
    endpointsOverview.innerHTML = endpointsHTML;

    // Quick actions
    const quickActions = document.getElementById('quick-actions');
    quickActions.innerHTML = `
        <div class="card-title">⚡ Quick Actions</div>
        <div class="actions-grid">
            <div class="action-card coming-soon">
                <div class="action-icon">🎮</div>
                <h3>Transformation Playground</h3>
                <p>Interactive testing of all endpoints</p>
                <span class="badge">Coming in v0.1.1</span>
            </div>
            <div class="action-card coming-soon">
                <div class="action-icon">📊</div>
                <h3>Text Nodes Explorer</h3>
                <p>Deep dive into text extraction</p>
                <span class="badge">Coming Soon</span>
            </div>
            <div class="action-card coming-soon">
                <div class="action-icon">🔐</div>
                <h3>Hash Mapper</h3>
                <p>Semantic text modification workflow</p>
                <span class="badge">Coming Soon</span>
            </div>
        </div>
    `;
});
```

### CSS Styles

#### `css/common.css`

See "Design System" section above for complete common styles.

#### `css/dashboard.css`

```css
/* Dashboard-specific styles */

.page-header {
    background: white;
    border-radius: 10px;
    padding: 30px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    text-align: center;
}

.page-header h1 {
    color: #667eea;
    font-size: 2.5em;
    margin-bottom: 10px;
}

.page-header .subtitle {
    color: #666;
    font-size: 1.2em;
}

/* Service Info */
.info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
}

.info-item {
    display: flex;
    flex-direction: column;
    gap: 5px;
}

.info-label {
    color: #666;
    font-weight: 600;
    font-size: 0.9em;
}

.info-value {
    color: #333;
    font-size: 1.1em;
}

.status-active {
    color: #10b981;
    font-weight: 600;
}

/* Endpoints */
.endpoint-group {
    margin-bottom: 30px;
}

.endpoint-group h3 {
    color: #667eea;
    margin-bottom: 15px;
    font-size: 1.2em;
}

.endpoint-list {
    list-style: none;
}

.endpoint-list li {
    padding: 10px;
    margin: 5px 0;
    background: #f7f7f7;
    border-radius: 5px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
}

.route-name {
    background: #667eea;
    color: white;
    padding: 4px 12px;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
    font-size: 0.9em;
    font-weight: 600;
}

.route-desc {
    color: #666;
    flex: 1;
    min-width: 200px;
}

/* Quick Actions */
.actions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
}

.action-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 30px;
    border-radius: 10px;
    text-align: center;
    transition: transform 0.2s;
    cursor: pointer;
    position: relative;
}

.action-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 16px rgba(0,0,0,0.2);
}

.action-card.coming-soon {
    opacity: 0.7;
    cursor: not-allowed;
}

.action-icon {
    font-size: 3em;
    margin-bottom: 15px;
}

.action-card h3 {
    margin-bottom: 10px;
    font-size: 1.3em;
}

.action-card p {
    opacity: 0.9;
    font-size: 0.95em;
}

.badge {
    display: inline-block;
    background: rgba(255,255,255,0.2);
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 0.8em;
    margin-top: 15px;
}

/* Footer */
.footer {
    text-align: center;
    color: white;
    margin-top: 40px;
    font-size: 0.9em;
}
```

### Sample Files

#### `samples/simple.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Simple HTML Example</title>
</head>
<body>
    <h1>Welcome to HTML Service</h1>
    <p>This is a simple HTML document with basic elements.</p>
    
    <h2>Features</h2>
    <ul>
        <li>Parse HTML to dictionary</li>
        <li>Extract text nodes</li>
        <li>Transform and reconstruct</li>
    </ul>
    
    <div class="content">
        <p>You can test various transformations with this sample.</p>
        <p>Try converting it to different formats!</p>
    </div>
</body>
</html>
```

#### `samples/complex.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Complex HTML Example</title>
    <style>
        .nested { padding: 10px; }
        .deeper { margin-left: 20px; }
    </style>
</head>
<body>
    <header>
        <nav>
            <ul>
                <li><a href="#section1">Section 1</a></li>
                <li><a href="#section2">Section 2</a></li>
                <li><a href="#section3">Section 3</a></li>
            </ul>
        </nav>
    </header>
    
    <main>
        <article id="section1">
            <h1>Deep Nesting Example</h1>
            <section>
                <h2>Level 1</h2>
                <p>This document demonstrates <strong>deep nesting</strong> of HTML elements.</p>
                <div class="nested">
                    <h3>Level 2</h3>
                    <p>Text at the second level of nesting.</p>
                    <div class="deeper">
                        <h4>Level 3</h4>
                        <p>Text at the <em>third level</em> of nesting.</p>
                        <div class="nested">
                            <h5>Level 4</h5>
                            <span>Even deeper nesting here!</span>
                            <div class="deeper">
                                <h6>Level 5</h6>
                                <p>This tests the max_depth parameter effectively.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </article>
        
        <article id="section2">
            <h2>Mixed Content</h2>
            <p>This section has <a href="#">links</a>, <code>code snippets</code>, and <mark>highlighted text</mark>.</p>
            <table>
                <thead>
                    <tr>
                        <th>Column 1</th>
                        <th>Column 2</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Data 1</td>
                        <td>Data 2</td>
                    </tr>
                </tbody>
            </table>
        </article>
    </main>
    
    <footer>
        <p>Footer content with nested <span>elements <strong>inside</strong></span>.</p>
    </footer>
</body>
</html>
```

#### `samples/dashboard.html`

This should be a **copy of the actual rendered `index.html`** (without scripts). Users can transform the dashboard itself!

### README.md

```markdown
# HTML Service Admin UI - v0.1.0

## Overview

First version of the HTML Service admin interface. Provides service overview and API documentation.

## Features

✅ Service information display
✅ Complete API endpoint listing
✅ Quick action cards (future features)
✅ Sample HTML files for testing
✅ Responsive design
✅ Zero external dependencies

## Structure

- `index.html` - Dashboard page
- `404.html` - Error page
- `css/` - Stylesheets
- `js/` - JavaScript logic
- `samples/` - Sample HTML files

## Next Version

v0.1.1 will add the Transformation Playground for interactive API testing.

---

**Created**: [Date]
**Methodology**: Iterative Flow Development (IFD)
**Dependencies**: None (100% native web)
```

---

## 📦 v0.1.1 - Transformation Playground

### Purpose
Add interactive playground page where users can test all service endpoints with pre-loaded samples.

### Implementation Strategy

**CRITICAL**: This is a **minor version** - create ONLY new/changed files. Reference v0.1.0 files using relative paths (../).

### Files to Create (ONLY New/Changed)

#### New Files:
- `playground.html` - NEW playground page
- `README.md` - UPDATED version documentation
- `css/playground.css` - NEW playground-specific styles
- `js/playground.js` - NEW playground orchestrator
- `components/` - NEW entire components directory
  - `top-nav/` (3 files)
  - `html-input/` (3 files)
  - `transformation-selector/` (3 files)
  - `output-viewer/` (3 files)
- `samples/playground.html` - NEW self-referential sample

#### Referenced from v0.1.0 (NO copies):
- `../v0.1.0/css/common.css`
- `../v0.1.0/js/services/api-client.js`
- `../v0.1.0/samples/simple.html`
- `../v0.1.0/samples/complex.html`
- `../v0.1.0/404.html`

### New Pages

#### `playground.html` - Transformation Playground

**Structure**:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Transformation Playground - HTML Service</title>
    
    <!-- Reference v0.1.0 common styles -->
    <link rel="stylesheet" href="../v0.1.0/css/common.css">
    
    <!-- v0.1.1 specific styles -->
    <link rel="stylesheet" href="./css/playground.css">
</head>
<body>
    <div class="container">
        <!-- Top Navigation -->
        <top-nav current-page="playground"></top-nav>

        <!-- Header -->
        <header class="page-header">
            <h1>🎮 Transformation Playground</h1>
            <p class="subtitle">Interactive testing of HTML transformation endpoints</p>
        </header>

        <!-- Main Playground Area -->
        <div class="playground-layout">
            <!-- Input Panel -->
            <section class="panel input-panel">
                <html-input id="html-input"></html-input>
            </section>

            <!-- Controls Panel -->
            <section class="panel controls-panel">
                <transformation-selector id="transformation-selector"></transformation-selector>
            </section>

            <!-- Output Panel -->
            <section class="panel output-panel">
                <output-viewer id="output-viewer"></output-viewer>
            </section>
        </div>

        <!-- Footer -->
        <footer class="footer">
            <p>HTML Service Admin UI v0.1.1</p>
        </footer>
    </div>

    <!-- Reference v0.1.0 API client -->
    <script src="../v0.1.0/js/services/api-client.js"></script>

    <!-- v0.1.1 Components -->
    <script src="./components/top-nav/top-nav.js"></script>
    <script src="./components/html-input/html-input.js"></script>
    <script src="./components/transformation-selector/transformation-selector.js"></script>
    <script src="./components/output-viewer/output-viewer.js"></script>

    <!-- v0.1.1 Main App -->
    <script src="./js/playground.js"></script>
</body>
</html>
```

### Web Components

#### Component 1: `top-nav` (Flat Structure)

**Purpose**: Navigation banner across all pages

**Files**: `components/top-nav/top-nav.html`, `top-nav.css`, `top-nav.js`

**`top-nav.html`**:
```html
<nav class="top-nav">
    <div class="nav-container">
        <div class="nav-brand">
            <span class="nav-icon">🔧</span>
            <span class="nav-title">HTML Service</span>
        </div>
        <ul class="nav-links">
            <li><a href="../v0.1.0/index.html" data-page="index">Dashboard</a></li>
            <li><a href="playground.html" data-page="playground">Playground</a></li>
        </ul>
    </div>
</nav>
```

**`top-nav.css`**:
```css
.top-nav {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    margin: -20px -20px 20px -20px;
    padding: 0 20px;
}

.nav-container {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 0;
}

.nav-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    color: white;
    font-weight: 600;
    font-size: 1.2em;
}

.nav-links {
    display: flex;
    list-style: none;
    gap: 5px;
    margin: 0;
    padding: 0;
}

.nav-links a {
    color: white;
    text-decoration: none;
    padding: 10px 20px;
    border-radius: 5px;
    transition: background 0.2s;
    font-weight: 500;
}

.nav-links a:hover {
    background: rgba(255,255,255,0.2);
}

.nav-links a.active {
    background: rgba(255,255,255,0.3);
    font-weight: 600;
}
```

**`top-nav.js`**:
```javascript
/**
 * Top Navigation Component
 * Displays navigation bar with active page highlighting
 */
class TopNav extends HTMLElement {
    constructor() {
        super();
        this.templateURL = './components/top-nav/top-nav.html';
        this.styleURL = './components/top-nav/top-nav.css';
    }

    async connectedCallback() {
        await this.loadStyles();
        await this.loadTemplate();
        this.setActivePage();
    }

    async loadStyles() {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = this.styleURL;
        document.head.appendChild(link);
    }

    async loadTemplate() {
        const response = await fetch(this.templateURL);
        const html = await response.text();
        this.innerHTML = html;
    }

    setActivePage() {
        const currentPage = this.getAttribute('current-page');
        const links = this.querySelectorAll('.nav-links a');
        links.forEach(link => {
            if (link.getAttribute('data-page') === currentPage) {
                link.classList.add('active');
            }
        });
    }
}

customElements.define('top-nav', TopNav);
```

#### Component 2: `html-input` (Flat Structure)

**Purpose**: HTML input area with sample selector

**`html-input.html`**:
```html
<div class="html-input-container">
    <div class="input-header">
        <h3>📝 HTML Input</h3>
        <div class="input-controls">
            <select id="sample-selector" class="sample-selector">
                <option value="">-- Select a Sample --</option>
                <option value="simple">Simple HTML</option>
                <option value="complex">Complex HTML (Deep Nesting)</option>
                <option value="dashboard">Dashboard HTML (This Page!)</option>
                <option value="custom">Custom (Paste Your Own)</option>
            </select>
            <button id="clear-btn" class="btn-small" title="Clear input">🗑️ Clear</button>
        </div>
    </div>
    
    <textarea id="html-textarea" 
              class="html-textarea" 
              placeholder="Select a sample or paste your HTML here..."></textarea>
    
    <div class="input-footer">
        <span id="char-count" class="char-count">0 characters</span>
        <span id="size-warning" class="size-warning" style="display: none;">⚠️ Approaching 1MB limit</span>
    </div>
</div>
```

**`html-input.css`**:
```css
.html-input-container {
    background: white;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.input-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    flex-wrap: wrap;
    gap: 10px;
}

.input-header h3 {
    margin: 0;
    color: #333;
}

.input-controls {
    display: flex;
    gap: 10px;
    align-items: center;
}

.sample-selector {
    padding: 8px 12px;
    border: 2px solid #ddd;
    border-radius: 5px;
    font-size: 0.95em;
    cursor: pointer;
}

.btn-small {
    padding: 8px 12px;
    background: #ef4444;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 0.9em;
}

.btn-small:hover {
    background: #dc2626;
}

.html-textarea {
    width: 100%;
    min-height: 300px;
    padding: 15px;
    border: 2px solid #ddd;
    border-radius: 5px;
    font-family: 'Courier New', monospace;
    font-size: 0.9em;
    resize: vertical;
    line-height: 1.5;
}

.html-textarea:focus {
    outline: none;
    border-color: #667eea;
}

.input-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 10px;
    font-size: 0.9em;
}

.char-count {
    color: #666;
}

.size-warning {
    color: #f59e0b;
    font-weight: 600;
}
```

**`html-input.js`**:
```javascript
/**
 * HTML Input Component
 * Provides textarea with sample selector and character counting
 */
class HtmlInput extends HTMLElement {
    constructor() {
        super();
        this.templateURL = './components/html-input/html-input.html';
        this.styleURL = './components/html-input/html-input.css';
        this.state = {
            html: '',
            currentSample: ''
        };
    }

    async connectedCallback() {
        await this.loadStyles();
        await this.loadTemplate();
        this.attachEventListeners();
        this.loadDefaultSample();
    }

    async loadStyles() {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = this.styleURL;
        document.head.appendChild(link);
    }

    async loadTemplate() {
        const response = await fetch(this.templateURL);
        const html = await response.text();
        this.innerHTML = html;
    }

    attachEventListeners() {
        const textarea = this.querySelector('#html-textarea');
        const sampleSelector = this.querySelector('#sample-selector');
        const clearBtn = this.querySelector('#clear-btn');

        // Textarea changes
        textarea.addEventListener('input', () => {
            this.updateCharCount();
            this.state.html = textarea.value;
            this.emit('html-changed', { html: this.state.html });
        });

        // Sample selection
        sampleSelector.addEventListener('change', async (e) => {
            const sample = e.target.value;
            if (sample && sample !== 'custom') {
                await this.loadSample(sample);
            } else if (sample === 'custom') {
                textarea.value = '';
                this.updateCharCount();
            }
        });

        // Clear button
        clearBtn.addEventListener('click', () => {
            textarea.value = '';
            sampleSelector.value = 'custom';
            this.updateCharCount();
            this.emit('html-changed', { html: '' });
        });
    }

    async loadDefaultSample() {
        // Load 'simple' sample by default
        await this.loadSample('simple');
        const selector = this.querySelector('#sample-selector');
        selector.value = 'simple';
    }

    async loadSample(sampleName) {
        try {
            // Reference v0.1.0 samples for simple/complex
            // Reference v0.1.1 samples for playground
            let samplePath;
            if (sampleName === 'playground') {
                samplePath = `./samples/${sampleName}.html`;
            } else {
                samplePath = `../v0.1.0/samples/${sampleName}.html`;
            }
            
            const response = await fetch(samplePath);
            const html = await response.text();
            const textarea = this.querySelector('#html-textarea');
            textarea.value = html;
            this.state.html = html;
            this.state.currentSample = sampleName;
            this.updateCharCount();
            this.emit('html-changed', { html });
        } catch (error) {
            console.error('Failed to load sample:', error);
            alert('Failed to load sample file');
        }
    }

    updateCharCount() {
        const textarea = this.querySelector('#html-textarea');
        const charCount = this.querySelector('#char-count');
        const sizeWarning = this.querySelector('#size-warning');
        const length = textarea.value.length;
        
        charCount.textContent = `${length.toLocaleString()} characters`;
        
        // Show warning at 900KB (90% of 1MB limit)
        const MB_LIMIT = 1024 * 1024;
        if (length > MB_LIMIT * 0.9) {
            sizeWarning.style.display = 'inline';
        } else {
            sizeWarning.style.display = 'none';
        }
    }

    getValue() {
        return this.state.html;
    }

    emit(eventName, detail) {
        this.dispatchEvent(new CustomEvent(eventName, { 
            detail, 
            bubbles: true 
        }));
    }
}

customElements.define('html-input', HtmlInput);
```

#### Component 3: `transformation-selector` (Flat Structure)

**Purpose**: Select transformation endpoint and configure parameters

**`transformation-selector.html`**:
```html
<div class="transformation-container">
    <h3>⚙️ Select Transformation</h3>
    
    <div class="selector-group">
        <label for="endpoint-selector">Endpoint:</label>
        <select id="endpoint-selector" class="endpoint-selector">
            <option value="">-- Select Transformation --</option>
            <optgroup label="HTML Transformations">
                <option value="html-to-dict">HTML → Dict</option>
                <option value="html-to-text-nodes">HTML → Text Nodes</option>
                <option value="html-to-lines">HTML → Lines</option>
                <option value="html-to-html-hashes">HTML → HTML (Hashes)</option>
                <option value="html-to-html-xxx">HTML → HTML (XXX)</option>
            </optgroup>
            <optgroup label="Dict Operations">
                <option value="dict-to-html">Dict → HTML</option>
                <option value="dict-to-text-nodes">Dict → Text Nodes</option>
                <option value="dict-to-lines">Dict → Lines</option>
            </optgroup>
            <optgroup label="Hash Operations">
                <option value="hashes-to-html">Hashes → HTML</option>
            </optgroup>
        </select>
    </div>
    
    <div id="endpoint-info" class="endpoint-info" style="display: none;">
        <div class="info-box">
            <strong>Description:</strong> <span id="endpoint-description"></span>
        </div>
    </div>
    
    <div id="config-panel" class="config-panel" style="display: none;">
        <!-- Max depth slider (for applicable endpoints) -->
        <div class="config-item">
            <label for="max-depth-slider">Max Depth:</label>
            <div class="slider-container">
                <input type="range" id="max-depth-slider" min="1" max="512" value="256" step="1">
                <span id="max-depth-value" class="slider-value">256</span>
            </div>
        </div>
    </div>
    
    <button id="transform-btn" class="btn btn-primary transform-btn" disabled>
        ▶️ Transform
    </button>
</div>
```

**`transformation-selector.css`**:
```css
.transformation-container {
    background: white;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.transformation-container h3 {
    margin: 0 0 20px 0;
    color: #333;
}

.selector-group {
    margin-bottom: 20px;
}

.selector-group label {
    display: block;
    margin-bottom: 8px;
    color: #333;
    font-weight: 600;
}

.endpoint-selector {
    width: 100%;
    padding: 12px;
    border: 2px solid #ddd;
    border-radius: 5px;
    font-size: 1em;
    cursor: pointer;
}

.endpoint-selector:focus {
    outline: none;
    border-color: #667eea;
}

.endpoint-info {
    margin: 15px 0;
}

.info-box {
    background: #e7f3ff;
    border-left: 4px solid #3b82f6;
    padding: 12px;
    border-radius: 4px;
    font-size: 0.95em;
}

.config-panel {
    margin: 20px 0;
    padding: 15px;
    background: #f7f7f7;
    border-radius: 5px;
}

.config-item {
    margin-bottom: 15px;
}

.config-item label {
    display: block;
    margin-bottom: 8px;
    font-weight: 600;
    color: #333;
}

.slider-container {
    display: flex;
    align-items: center;
    gap: 15px;
}

.slider-container input[type="range"] {
    flex: 1;
}

.slider-value {
    min-width: 40px;
    text-align: center;
    font-weight: 600;
    color: #667eea;
}

.transform-btn {
    width: 100%;
    padding: 15px;
    font-size: 1.1em;
    margin-top: 20px;
}

.transform-btn:disabled {
    background: #ccc;
    cursor: not-allowed;
}
```

**`transformation-selector.js`**:
```javascript
/**
 * Transformation Selector Component
 * Allows user to select endpoint and configure parameters
 */
class TransformationSelector extends HTMLElement {
    constructor() {
        super();
        this.templateURL = './components/transformation-selector/transformation-selector.html';
        this.styleURL = './components/transformation-selector/transformation-selector.css';
        
        // Endpoint definitions
        this.endpoints = {
            'html-to-dict': {
                route: '/html/to__dict',
                description: 'Parse HTML into a nested dictionary structure representing the DOM tree',
                method: 'POST',
                requiresMaxDepth: false,
                inputType: 'html'
            },
            'html-to-text-nodes': {
                route: '/html/to__text__nodes',
                description: 'Extract all text nodes with unique hash identifiers for semantic modification',
                method: 'POST',
                requiresMaxDepth: true,
                inputType: 'html'
            },
            'html-to-lines': {
                route: '/html/to__lines',
                description: 'Format HTML as readable indented lines showing structure',
                method: 'POST',
                requiresMaxDepth: false,
                inputType: 'html'
            },
            'html-to-html-hashes': {
                route: '/html/to__html__hashes',
                description: 'Replace all text content with hash identifiers (debugging visualization)',
                method: 'POST',
                requiresMaxDepth: true,
                inputType: 'html'
            },
            'html-to-html-xxx': {
                route: '/html/to__html__xxx',
                description: 'Replace all text content with x\'s (privacy masking visualization)',
                method: 'POST',
                requiresMaxDepth: true,
                inputType: 'html'
            },
            'dict-to-html': {
                route: '/dict/to__html',
                description: 'Reconstruct HTML from dictionary structure',
                method: 'POST',
                requiresMaxDepth: false,
                inputType: 'dict'
            },
            'dict-to-text-nodes': {
                route: '/dict/to__text__nodes',
                description: 'Extract text nodes from dictionary structure',
                method: 'POST',
                requiresMaxDepth: true,
                inputType: 'dict'
            },
            'dict-to-lines': {
                route: '/dict/to__lines',
                description: 'Format dictionary as readable lines',
                method: 'POST',
                requiresMaxDepth: false,
                inputType: 'dict'
            },
            'hashes-to-html': {
                route: '/hashes/to__html',
                description: 'Apply hash mappings to reconstruct HTML with modified text',
                method: 'POST',
                requiresMaxDepth: false,
                inputType: 'hashes'
            }
        };
    }

    async connectedCallback() {
        await this.loadStyles();
        await this.loadTemplate();
        this.attachEventListeners();
    }

    async loadStyles() {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = this.styleURL;
        document.head.appendChild(link);
    }

    async loadTemplate() {
        const response = await fetch(this.templateURL);
        const html = await response.text();
        this.innerHTML = html;
    }

    attachEventListeners() {
        const selector = this.querySelector('#endpoint-selector');
        const transformBtn = this.querySelector('#transform-btn');
        const maxDepthSlider = this.querySelector('#max-depth-slider');
        const maxDepthValue = this.querySelector('#max-depth-value');

        // Endpoint selection
        selector.addEventListener('change', (e) => {
            const endpointId = e.target.value;
            if (endpointId) {
                this.showEndpointInfo(endpointId);
                transformBtn.disabled = false;
            } else {
                this.hideEndpointInfo();
                transformBtn.disabled = true;
            }
        });

        // Max depth slider
        maxDepthSlider.addEventListener('input', (e) => {
            maxDepthValue.textContent = e.target.value;
        });

        // Transform button
        transformBtn.addEventListener('click', () => {
            this.handleTransform();
        });
    }

    showEndpointInfo(endpointId) {
        const endpoint = this.endpoints[endpointId];
        const infoDiv = this.querySelector('#endpoint-info');
        const descSpan = this.querySelector('#endpoint-description');
        const configPanel = this.querySelector('#config-panel');

        descSpan.textContent = endpoint.description;
        infoDiv.style.display = 'block';

        // Show config panel if max_depth is needed
        if (endpoint.requiresMaxDepth) {
            configPanel.style.display = 'block';
        } else {
            configPanel.style.display = 'none';
        }
    }

    hideEndpointInfo() {
        const infoDiv = this.querySelector('#endpoint-info');
        const configPanel = this.querySelector('#config-panel');
        infoDiv.style.display = 'none';
        configPanel.style.display = 'none';
    }

    handleTransform() {
        const selector = this.querySelector('#endpoint-selector');
        const endpointId = selector.value;
        const endpoint = this.endpoints[endpointId];
        
        const config = {
            endpointId,
            route: endpoint.route,
            inputType: endpoint.inputType
        };

        // Add max_depth if required
        if (endpoint.requiresMaxDepth) {
            const maxDepthSlider = this.querySelector('#max-depth-slider');
            config.maxDepth = parseInt(maxDepthSlider.value);
        }

        this.emit('transformation-requested', config);
    }

    emit(eventName, detail) {
        this.dispatchEvent(new CustomEvent(eventName, { 
            detail, 
            bubbles: true 
        }));
    }
}

customElements.define('transformation-selector', TransformationSelector);
```

#### Component 4: `output-viewer` (Flat Structure)

**Purpose**: Display transformation results with formatting

**`output-viewer.html`**:
```html
<div class="output-container">
    <div class="output-header">
        <h3>📊 Output</h3>
        <div class="output-controls" style="display: none;">
            <button id="copy-btn" class="btn-small" title="Copy to clipboard">📋 Copy</button>
            <button id="download-btn" class="btn-small" title="Download result">💾 Download</button>
        </div>
    </div>
    
    <div id="output-content" class="output-content">
        <div class="empty-state">
            <p>👆 Select a transformation and click "Transform" to see results</p>
        </div>
    </div>
</div>
```

**`output-viewer.css`**:
```css
.output-container {
    background: white;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.output-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.output-header h3 {
    margin: 0;
    color: #333;
}

.output-controls {
    display: flex;
    gap: 10px;
}

.output-content {
    min-height: 300px;
    max-height: 600px;
    overflow-y: auto;
    border: 2px solid #ddd;
    border-radius: 5px;
    padding: 15px;
    background: #f9f9f9;
}

.empty-state {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 300px;
    color: #999;
    font-size: 1.1em;
    text-align: center;
}

.loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 300px;
}

.error-state {
    color: #ef4444;
    padding: 20px;
    background: #fee2e2;
    border-radius: 5px;
    border-left: 4px solid #ef4444;
}

.error-state h4 {
    margin: 0 0 10px 0;
}

/* JSON formatting */
.json-output {
    font-family: 'Courier New', monospace;
    font-size: 0.9em;
    line-height: 1.6;
    white-space: pre-wrap;
    word-break: break-all;
}

.json-key {
    color: #0066cc;
    font-weight: 600;
}

.json-string {
    color: #008000;
}

.json-number {
    color: #0000ff;
}

.json-boolean {
    color: #cc00cc;
    font-weight: bold;
}

/* HTML formatting */
.html-output {
    font-family: 'Courier New', monospace;
    font-size: 0.9em;
    line-height: 1.6;
    white-space: pre-wrap;
}

/* Text formatting */
.text-output {
    font-family: 'Courier New', monospace;
    font-size: 0.9em;
    line-height: 1.6;
    white-space: pre-wrap;
}
```

**`output-viewer.js`**:
```javascript
/**
 * Output Viewer Component
 * Displays transformation results with appropriate formatting
 */
class OutputViewer extends HTMLElement {
    constructor() {
        super();
        this.templateURL = './components/output-viewer/output-viewer.html';
        this.styleURL = './components/output-viewer/output-viewer.css';
        this.state = {
            data: null,
            type: null
        };
    }

    async connectedCallback() {
        await this.loadStyles();
        await this.loadTemplate();
        this.attachEventListeners();
    }

    async loadStyles() {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = this.styleURL;
        document.head.appendChild(link);
    }

    async loadTemplate() {
        const response = await fetch(this.templateURL);
        const html = await response.text();
        this.innerHTML = html;
    }

    attachEventListeners() {
        const copyBtn = this.querySelector('#copy-btn');
        const downloadBtn = this.querySelector('#download-btn');

        copyBtn.addEventListener('click', () => this.copyToClipboard());
        downloadBtn.addEventListener('click', () => this.downloadResult());
    }

    showLoading() {
        const content = this.querySelector('#output-content');
        content.innerHTML = `
            <div class="loading-state">
                <div class="spinner"></div>
                <p>Transforming...</p>
            </div>
        `;
        this.hideControls();
    }

    showError(error) {
        const content = this.querySelector('#output-content');
        content.innerHTML = `
            <div class="error-state">
                <h4>❌ Transformation Failed</h4>
                <p>${error.message || 'An unknown error occurred'}</p>
            </div>
        `;
        this.hideControls();
    }

    showResult(data, type) {
        this.state.data = data;
        this.state.type = type;

        const content = this.querySelector('#output-content');
        
        if (type === 'json') {
            content.innerHTML = `<pre class="json-output">${this.formatJSON(data)}</pre>`;
        } else if (type === 'html') {
            content.innerHTML = `<pre class="html-output">${this.escapeHtml(data)}</pre>`;
        } else if (type === 'text') {
            content.innerHTML = `<pre class="text-output">${this.escapeHtml(data)}</pre>`;
        }

        this.showControls();
    }

    formatJSON(obj) {
        return JSON.stringify(obj, null, 2)
            .replace(/"([^"]+)":/g, '<span class="json-key">"$1"</span>:')
            .replace(/: "([^"]+)"/g, ': <span class="json-string">"$1"</span>')
            .replace(/: (\d+)/g, ': <span class="json-number">$1</span>')
            .replace(/: (true|false)/g, ': <span class="json-boolean">$1</span>');
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showControls() {
        const controls = this.querySelector('.output-controls');
        controls.style.display = 'flex';
    }

    hideControls() {
        const controls = this.querySelector('.output-controls');
        controls.style.display = 'none';
    }

    async copyToClipboard() {
        const text = this.getRawOutput();
        try {
            await navigator.clipboard.writeText(text);
            alert('Copied to clipboard! ✅');
        } catch (error) {
            console.error('Failed to copy:', error);
            alert('Failed to copy to clipboard');
        }
    }

    downloadResult() {
        const text = this.getRawOutput();
        const type = this.state.type;
        
        let filename, mimeType;
        if (type === 'json') {
            filename = 'result.json';
            mimeType = 'application/json';
        } else if (type === 'html') {
            filename = 'result.html';
            mimeType = 'text/html';
        } else {
            filename = 'result.txt';
            mimeType = 'text/plain';
        }

        const blob = new Blob([text], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    }

    getRawOutput() {
        if (this.state.type === 'json') {
            return JSON.stringify(this.state.data, null, 2);
        } else {
            return this.state.data;
        }
    }
}

customElements.define('output-viewer', OutputViewer);
```

### Playground Orchestrator

#### `js/playground.js`

**Purpose**: Coordinate communication between components

```javascript
/**
 * Playground Page Orchestrator
 * Coordinates events between html-input, transformation-selector, and output-viewer
 */
document.addEventListener('DOMContentLoaded', () => {
    const htmlInput = document.getElementById('html-input');
    const transformationSelector = document.getElementById('transformation-selector');
    const outputViewer = document.getElementById('output-viewer');

    let currentHtml = '';

    // Listen for HTML changes
    document.addEventListener('html-changed', (e) => {
        currentHtml = e.detail.html;
        console.log('HTML updated:', currentHtml.length, 'characters');
    });

    // Listen for transformation requests
    document.addEventListener('transformation-requested', async (e) => {
        const config = e.detail;
        console.log('Transformation requested:', config);

        if (!currentHtml) {
            alert('Please enter or select HTML first!');
            return;
        }

        // Show loading
        outputViewer.showLoading();

        try {
            let result, outputType;

            // Build payload based on input type
            let payload = {};
            
            if (config.inputType === 'html') {
                payload.html = currentHtml;
            } else if (config.inputType === 'dict') {
                // Parse current HTML as JSON (assumes it's already a dict)
                try {
                    payload.html_dict = JSON.parse(currentHtml);
                } catch (error) {
                    throw new Error('Input must be valid JSON for dict operations');
                }
            } else if (config.inputType === 'hashes') {
                // For hash operations, need both dict and hash_mapping
                alert('Hash operations require a dict and hash mapping. This will be implemented in a future version.');
                return;
            }

            // Add max_depth if provided
            if (config.maxDepth) {
                payload.max_depth = config.maxDepth;
            }

            // Call API (using v0.1.0 api-client.js)
            result = await window.apiClient.callEndpoint(config.route, payload);

            // Determine output type
            if (typeof result === 'object') {
                outputType = 'json';
            } else if (result.startsWith('<')) {
                outputType = 'html';
            } else {
                outputType = 'text';
            }

            // Show result
            outputViewer.showResult(result, outputType);

        } catch (error) {
            console.error('Transformation failed:', error);
            outputViewer.showError(error);
        }
    });
});
```

### New Sample File

#### `samples/playground.html`

This should be a **copy of the rendered `playground.html`** (the page itself), allowing users to transform the playground page!

### CSS for Playground

#### `css/playground.css`

```css
/* Playground-specific layout */

.playground-layout {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: auto auto;
    gap: 20px;
    margin-bottom: 20px;
}

.panel {
    background: white;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.input-panel {
    grid-column: 1 / 2;
    grid-row: 1 / 3;
}

.controls-panel {
    grid-column: 2 / 3;
    grid-row: 1 / 2;
}

.output-panel {
    grid-column: 2 / 3;
    grid-row: 2 / 3;
}

/* Responsive layout */
@media (max-width: 1024px) {
    .playground-layout {
        grid-template-columns: 1fr;
        grid-template-rows: auto auto auto;
    }
    
    .input-panel {
        grid-column: 1 / 2;
        grid-row: 1 / 2;
    }
    
    .controls-panel {
        grid-column: 1 / 2;
        grid-row: 2 / 3;
    }
    
    .output-panel {
        grid-column: 1 / 2;
        grid-row: 3 / 4;
    }
}
```

---

## 🚀 Implementation Steps

### Phase 1: Setup (v0.1.0)

1. **Create Package Structure**
   - Create `mgraph_ai_service_html__admin_ui/__init__.py`
   - Create `v0/v0.1.0/` folder structure

2. **Create ALL v0.1.0 Files**
   - Sample files (simple.html, complex.html, dashboard.html)
   - Dashboard page (index.html)
   - Error page (404.html)
   - CSS (common.css, dashboard.css)
   - JavaScript (api-client.js, dashboard.js)
   - README.md

3. **Create Backend Service**
   - `mgraph_ai_service_html/html__fast_api/Html__Admin__Service.py`
   - Wire up to FastAPI routes
   - Test serving at `/html-service/`

4. **Test v0.1.0**
   - Dashboard loads correctly
   - Endpoints display
   - Samples accessible
   - Navigation works

### Phase 2: Playground (v0.1.1)

1. **Create v0.1.1 Folder**
   - Create `v0/v0.1.1/` directory
   - DO NOT copy v0.1.0 files

2. **Create ONLY New Files**
   - playground.html (with relative paths to v0.1.0)
   - css/playground.css
   - js/playground.js
   - components/ (entire directory with 4 components)
   - samples/playground.html
   - README.md

3. **Update Backend Service**
   - Change `current_version` to "v0.1.1"
   - Ensure serve_static_file resolves relative paths correctly

4. **Test v0.1.1**
   - Playground loads at `/html-service/v0/v0.1.1/playground.html`
   - References to v0.1.0 files work (CSS, JS, samples)
   - All components load
   - Transformations work
   - Output displays correctly
   - Navigation works

---

## ✅ Testing Checklist

### v0.1.0 Testing
- [ ] Dashboard loads at `/html-service/v0/v0.1.0/index.html`
- [ ] Service info displays correctly
- [ ] All endpoints listed
- [ ] Quick action cards visible
- [ ] Sample files accessible at `/html-service/v0/v0.1.0/samples/*.html`
- [ ] 404 page displays for invalid routes
- [ ] Responsive on mobile

### v0.1.1 Testing
- [ ] Playground loads at `/html-service/v0/v0.1.1/playground.html`
- [ ] v0.1.0 common.css loads correctly (cross-version reference)
- [ ] v0.1.0 api-client.js loads correctly (cross-version reference)
- [ ] v0.1.0 samples load in dropdown (simple, complex, dashboard)
- [ ] v0.1.1 playground sample loads
- [ ] Sample selector works (loads all samples)
- [ ] Simple sample loads by default
- [ ] Character counter updates
- [ ] All transformations work (HTML → Dict, Text Nodes, Lines, Hashes, XXX)
- [ ] Max depth slider works (for applicable endpoints)
- [ ] Output displays correctly (JSON/HTML/text)
- [ ] Copy button works
- [ ] Download button works
- [ ] Error handling works (invalid HTML, API errors)
- [ ] Navigation between pages works (Dashboard ↔ Playground)
- [ ] Responsive on mobile
- [ ] No console errors

---

## 🎓 Critical IFD Reminders

### Version Independence at Major Version Level
- v0.1.0, v0.2.0, v1.0.0 are COMPLETELY SEPARATE
- NO imports between major versions

### Minor Version Incremental Build
- v0.1.1 contains ONLY new/changed files
- v0.1.1 references v0.1.0 files via relative paths
- v0.1.2 can reference any v0.1.x files
- Minimize duplication within a major version family

### Component Communication
- Use CustomEvents, NOT direct method calls
- Components emit events upward
- Parent orchestrator listens and coordinates

### Real API Integration
- NO mock data
- Call actual service endpoints from day one
- Test with real responses

### Progressive Enhancement
- v0.1.0 works standalone (complete foundation)
- v0.1.1 adds components (references v0.1.0)
- Each version is potentially shippable

---

## 📝 Final Notes

### File Serving with Cross-Version References
The admin UI is served as static files from the Python backend using `Html__Admin__Service`. The backend must handle relative path resolution (../) to allow minor versions to reference files from their parent major version.

### No CORS Issues
Because the admin UI and service API are on the same origin (served by same FastAPI app), there are no CORS restrictions. JavaScript can directly call service endpoints.

### Sample Files Strategy
The **killer feature** is pre-loaded samples. Users can explore all functionality without uploading any files. They learn by doing immediately!

### Self-Referential Samples
Including `dashboard.html` and `playground.html` as samples creates a meta/cool factor where users can transform the very pages they're using. This is both educational and engaging.

---

## 🎯 Success Criteria

**v0.1.0 is successful when:**
- Users understand what the service does from dashboard alone
- All endpoints clearly documented
- Sample files demonstrate capabilities
- Zero external dependencies
- Complete standalone implementation

**v0.1.1 is successful when:**
- Users can test any endpoint within 30 seconds of landing
- No file upload required to start
- All transformations work correctly
- Results are clearly displayed
- Copy/download functionality works
- Successfully references v0.1.0 files without duplication
- Demonstrates proper IFD incremental versioning