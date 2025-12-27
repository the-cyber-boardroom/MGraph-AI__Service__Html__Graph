# MGraph-AI__Service__Html__Graph - Render UI Implementation Brief

## 📋 Document Overview

**Purpose**: Complete technical brief for implementing an interactive graph visualization UI for the MGraph Html Graph service  
**Methodology**: Iterative Flow Development (IFD)  
**Target Audience**: LLM assistant with access to MGraph-AI__Service__Html__Graph codebase  
**Implementation Approach**: Backend routes first, then progressive UI enhancement through incremental versions  
**Version**: v0.7.4  
**Date**: December 2025

---

## 🎯 Project Objectives

### Primary Goal

Create an interactive web-based visualization UI that renders HTML-derived MGraphs using JavaScript graph libraries, replacing static PNG output with dynamic, explorable visualizations. Users should be able to input HTML, see the resulting graph structure, and interact with nodes/edges in real-time.

### Key Requirements

✅ **Interactive Visualization** - Zoom, pan, click nodes, explore structure  
✅ **Multiple Renderers** - Support DOT (viz-js), vis.js, D3, Cytoscape, Mermaid  
✅ **DOT as Default** - Visual parity with existing PNG output  
✅ **Zero External UI Dependencies** - Pure native web platform (HTML/CSS/ES6+ JS)  
✅ **CDN-Loaded Visualization Libraries** - External libs loaded via CDN  
✅ **IFD Compliant** - Version independence at major version level, incremental minor versions  
✅ **Real API Integration** - Calls actual service endpoints (no CORS, same server)  
✅ **Leverage Existing Code** - Reuse MGraph-DB and Html-Service patterns  

### What This Project Is NOT

❌ **Not a replacement for PNG export** - PNG remains for static/download use cases  
❌ **Not a full graph editor** - Read-only visualization, not graph modification  
❌ **Not a standalone application** - Served by the same FastAPI service  

---

## 🗃️ Service Context

### MGraph-AI__Service__Html__Graph Overview

The service provides HTML-to-graph transformation capabilities. It parses HTML into an MGraph structure where:

- **Element nodes** represent HTML tags (div, p, span, etc.)
- **Value nodes** store tag names, attributes, and text content
- **Edges** connect elements with predicates (`child`, `tag`, `attr`, `text`)

#### Current Capabilities

| Class | Purpose |
|-------|---------|
| `Html_Dict__To__Html_MGraph` | Converts HTML dict to MGraph |
| `Html_MGraph` | Main interface for HTML graph operations |
| `Html_MGraph__Screenshot` | Renders graph to PNG via Graphviz |
| `Html_MGraph__Render__Config` | Configuration for visualization |
| `Html_MGraph__Render__Colors` | Color schemes by tag category |
| `MGraph__Export__Dot` | Exports MGraph to DOT format |

#### Current PNG Flow

```
HTML → Html_Dict → Html_MGraph → Html_MGraph__Screenshot → MGraph__Export__Dot → Graphviz → PNG
```

#### New Browser Flow

```
HTML → Html_Dict → Html_MGraph → Routes__Graph → DOT/VisJs/D3 JSON → Browser → viz-js/vis.js/D3 → SVG
```

### Existing Route Structure

```
/info/health              # Health check
/info/status              # Service status
/info/versions            # Version info
```

### New Routes to Add

```
/graph/from/html/to/dot        # HTML → DOT string
/graph/from/html/to/visjs      # HTML → vis.js format
/graph/from/html/to/d3         # HTML → D3 format
/graph/from/html/to/cytoscape  # HTML → Cytoscape format
/graph/from/html/to/mermaid    # HTML → Mermaid syntax
```

---

## 🏗️ Architecture Decisions

### Decision 1: Route Design Pattern

**Decision**: Separate routes per output format using path segments  
**Pattern**: `/graph/from/html/to/{format}`

**Rationale**:
- Clear, self-documenting API structure
- Each format may have unique response schemas
- Easier to add new formats without modifying existing routes
- Follows REST resource-oriented design
- Matches existing service naming conventions

**Rejected Alternative**: Single parametrized route (`/graph/from/html?format=dot`)
- Less discoverable
- Harder to document
- Mixed response types complicate OpenAPI schema

### Decision 2: Default Renderer

**Decision**: DOT format via viz-js as the default/primary renderer

**Rationale**:
- **Visual Parity**: Same output as existing PNG, users get consistent results
- **Code Reuse**: Leverages existing `MGraph__Export__Dot` and `Html_MGraph__Render__Config`
- **Proven Styling**: Color schemes, node shapes, edge styles already defined
- **Minimal New Code**: DOT string generation already works
- **viz-js Maturity**: Graphviz compiled to WebAssembly, reliable rendering

**Why viz-js over other Graphviz WASM options**:
- Active maintenance (mdaines/viz-js)
- Clean API: `Viz.instance().then(viz => viz.renderSVGElement(dot))`
- Available on jsDelivr CDN
- Small bundle size (~2.5MB WASM)

### Decision 3: UI Package Location

**Decision**: New package `mgraph_ai_service_html_graph__render_ui` in same repository

**Rationale**:
- **Separation of Concerns**: UI code separate from service logic
- **IFD Compliance**: UI follows its own versioning (v0.1.0, v0.1.1, etc.)
- **Same Repo Benefits**: Easy cross-referencing, single deployment
- **Naming Convention**: Matches `mgraph_ai_service_html__admin_ui` pattern from Html-Service

**Package Structure**:
```python
# mgraph_ai_service_html_graph__render_ui/__init__.py
package_name = 'mgraph_ai_service_html_graph__render_ui'
path         = __path__[0]
```

### Decision 4: Configuration Approach

**Decision**: Mirror existing `Html_MGraph__Render__Config` in API requests, using existing Enums

**Rationale**:
- **Consistency**: Same config options work for PNG and browser rendering
- **Proven Design**: Presets, visibility toggles, color schemes already tested
- **Code Reuse**: Backend applies same config whether outputting PNG or JSON
- **Type Safety**: Enums provide better validation than Literals
- **Existing Code**: `Enum__Html_Render__Preset` and `Enum__Html_Render__Color_Scheme` already exist

**Existing Enums** (in `Html_MGraph__Render__Config.py` and `Html_MGraph__Render__Colors.py`):
```python
class Enum__Html_Render__Preset(str, Enum):                                   # Rendering presets
    FULL_DETAIL     = 'full_detail'                                           # Show everything
    STRUCTURE_ONLY  = 'structure_only'                                        # Only elements and child edges
    MINIMAL         = 'minimal'                                               # Just element nodes with tags inline

class Enum__Html_Render__Color_Scheme(str, Enum):                             # Color schemes
    DEFAULT       = 'default'
    MONOCHROME    = 'monochrome'
    HIGH_CONTRAST = 'high_contrast'
```

**Config Options**:
```python
preset          : Enum__Html_Render__Preset      = Enum__Html_Render__Preset.FULL_DETAIL
show_tag_nodes  : bool                           = True
show_attr_nodes : bool                           = True  
show_text_nodes : bool                           = True
color_scheme    : Enum__Html_Render__Color_Scheme = Enum__Html_Render__Color_Scheme.DEFAULT
```

### Decision 5: IFD Version Strategy

**Decision**: Incremental minor versions with maximum code sharing

**Rationale**:
- v0.1.0 establishes foundation (dashboard, API client, CSS)
- v0.1.1 adds UI framework (nav, input, config panels)
- v0.1.2+ adds renderers one at a time
- Each version contains ONLY new/changed files
- Later versions reference earlier files via relative paths

**Why Not Copy Full Files**:
- Reduces duplication
- Bug fixes in v0.1.0 automatically apply to v0.1.2
- Smaller version directories
- Clear visibility of what changed per version

### Decision 6: CDN for Visualization Libraries

**Decision**: Load visualization libraries from CDN, not bundled

**Rationale**:
- **IFD Spirit**: "Zero external dependencies" applies to UI framework, not specialized libs
- **Pragmatism**: Writing a graph layout engine is not trivial
- **Caching**: CDN assets cached by browser across sessions
- **Versioning**: Pin specific versions for reproducibility
- **Size**: Don't bloat repository with large JS libraries

**Approved CDN Sources**:
```html
<!-- viz-js (DOT → SVG) -->
<script src="https://cdn.jsdelivr.net/npm/@viz-js/viz@3.2.4/lib/viz-standalone.js"></script>

<!-- vis.js Network -->
<script src="https://cdn.jsdelivr.net/npm/vis-network@9.1.9/dist/vis-network.min.js"></script>

<!-- D3.js -->
<script src="https://cdn.jsdelivr.net/npm/d3@7.8.5/dist/d3.min.js"></script>

<!-- Cytoscape.js -->
<script src="https://cdn.jsdelivr.net/npm/cytoscape@3.28.1/dist/cytoscape.min.js"></script>
```

### Decision 7: Graph Statistics Display

**Decision**: Show graph statistics alongside visualization

**Rationale**:
- Users understand graph complexity at a glance
- Helps debug HTML parsing issues
- Matches `Html_MGraph.stats()` output
- Educational for understanding graph structure

**Statistics to Display**:
- Total nodes / Total edges
- Element nodes / Value nodes
- Tag nodes / Attr nodes / Text nodes
- Graph depth

---

## 📁 Complete Folder Structure

### Backend Additions

```
mgraph_ai_service_html_graph/
├── fast_api/
│   ├── Html_Graph__Service__Fast_API.py    # ADD: Routes__Graph
│   └── routes/
│       └── Routes__Graph.py                 # NEW: Graph export routes
│
├── schemas/
│   └── graph/                               # NEW: Directory
│       ├── __init__.py
│       ├── Schema__Graph__From_Html__Request.py
│       ├── Schema__Graph__VisJs__Response.py
│       ├── Schema__Graph__D3__Response.py
│       └── Schema__Graph__Cytoscape__Response.py
│
└── service/
    └── html_graph/
        └── exporters/                       # NEW: Directory
            ├── __init__.py
            ├── Html_MGraph__To__Dot.py      # Wraps MGraph__Export__Dot with config
            ├── Html_MGraph__To__VisJs.py    # MGraph → {nodes:[], edges:[]}
            ├── Html_MGraph__To__D3.py       # MGraph → {nodes:[], links:[]}
            ├── Html_MGraph__To__Cytoscape.py # MGraph → {elements:{...}}
            └── Html_MGraph__To__Mermaid.py  # MGraph → Mermaid flowchart text
```

### UI Package Structure

```
mgraph_ai_service_html_graph__render_ui/
├── __init__.py
│   # package_name = 'mgraph_ai_service_html_graph__render_ui'
│   # path         = __path__[0]
│
└── v0/
    ├── v0.1.0/                              # FOUNDATION
    │   ├── index.html                        # Dashboard/home page
    │   ├── 404.html                          # Error page
    │   ├── README.md                         # Version documentation
    │   ├── css/
    │   │   ├── common.css                    # Shared styles (gradient, cards, buttons, colors)
    │   │   └── dashboard.css                 # Dashboard-specific styles
    │   ├── js/
    │   │   ├── services/
    │   │   │   └── api-client.js             # API communication service
    │   │   └── dashboard.js                  # Dashboard page logic
    │   └── samples/
    │       ├── simple.html                   # Minimal: <div><p>Hello</p></div>
    │       ├── nested.html                   # Multi-level nesting
    │       ├── attributes.html               # Elements with classes, ids
    │       ├── mixed-content.html            # Text + elements interleaved
    │       └── bootstrap.html                # Real-world complex HTML
    │
    ├── v0.1.1/                              # CORE UI FRAMEWORK (only new files)
    │   ├── playground.html                   # Main playground page
    │   ├── README.md
    │   ├── css/
    │   │   ├── layout.css                    # Grid/flex layouts for playground
    │   │   └── playground.css                # Playground-specific styles
    │   ├── js/
    │   │   └── playground.js                 # Playground orchestrator
    │   └── components/
    │       ├── top-nav/
    │       │   ├── top-nav.js                # Navigation Web Component
    │       │   └── top-nav.css
    │       ├── html-input/
    │       │   ├── html-input.js             # HTML textarea with samples dropdown
    │       │   └── html-input.css
    │       ├── config-panel/
    │       │   ├── config-panel.js           # Preset, visibility, color scheme
    │       │   └── config-panel.css
    │       ├── stats-panel/
    │       │   ├── stats-panel.js            # Graph statistics display
    │       │   └── stats-panel.css
    │       └── graph-canvas/
    │           ├── graph-canvas.js           # Container for renderers
    │           └── graph-canvas.css
    │   # References via relative paths:
    │   # - ../v0.1.0/css/common.css
    │   # - ../v0.1.0/js/services/api-client.js
    │   # - ../v0.1.0/samples/*.html
    │
    ├── v0.1.2/                              # DOT RENDERER (only new files)
    │   ├── README.md
    │   └── components/
    │       └── renderers/
    │           └── dot-renderer/
    │               ├── dot-renderer.js       # viz-js integration
    │               └── dot-renderer.css
    │   # References: v0.1.0/*, v0.1.1/*
    │
    ├── v0.1.3/                              # VIS.JS RENDERER (only new files)
    │   ├── README.md
    │   └── components/
    │       └── renderers/
    │           └── visjs-renderer/
    │               ├── visjs-renderer.js     # vis-network integration
    │               └── visjs-renderer.css
    │
    ├── v0.1.4/                              # D3 RENDERER (only new files)
    │   ├── README.md
    │   └── components/
    │       └── renderers/
    │           └── d3-renderer/
    │               ├── d3-renderer.js        # D3 force-directed
    │               └── d3-renderer.css
    │
    └── v0.1.5/                              # RENDERER SELECTOR (only new files)
        ├── README.md
        └── components/
            └── renderer-selector/
                ├── renderer-selector.js      # Dropdown to switch renderers
                └── renderer-selector.css
```

---

## 🔌 API Specification

### Route: POST /graph/from/html/to/dot

**Purpose**: Convert HTML to DOT format for Graphviz rendering

**Request**:
```python
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Config import Enum__Html_Render__Preset
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Colors import Enum__Html_Render__Color_Scheme

class Schema__Graph__From_Html__Request(Type_Safe):
    html            : Safe_Str__Html                                                              # Required: HTML content
    preset          : Enum__Html_Render__Preset       = Enum__Html_Render__Preset.FULL_DETAIL     # Render preset
    show_tag_nodes  : bool                            = True                                      # Show tag value nodes
    show_attr_nodes : bool                            = True                                      # Show attribute value nodes
    show_text_nodes : bool                            = True                                      # Show text value nodes
    color_scheme    : Enum__Html_Render__Color_Scheme = Enum__Html_Render__Color_Scheme.DEFAULT   # Color scheme
    max_depth       : int                             = 256                                       # Max traversal depth
```

**Response**:
```python
class Schema__Graph__Dot__Response(Type_Safe):
    dot   : Safe_Str__Text                                                        # DOT language string
    stats : Schema__Graph__Stats                                                  # Graph statistics

class Schema__Graph__Stats(Type_Safe):
    total_nodes   : int
    total_edges   : int
    element_nodes : int
    value_nodes   : int
    tag_nodes     : int
    text_nodes    : int
    attr_nodes    : int
```

**Example Request**:
```json
{
  "html": "<div class=\"main\"><p>Hello</p></div>",
  "preset": "full_detail",
  "show_tag_nodes": true,
  "show_attr_nodes": true,
  "show_text_nodes": true,
  "color_scheme": "default"
}
```

Note: FastAPI automatically converts the enum string values (`"full_detail"`, `"default"`) to their corresponding Enum types.

**Example Response**:
```json
{
  "dot": "digraph G {\n  rankdir=TB;\n  node [shape=box];\n  n1 [label=\"<div>\" fillcolor=\"#FFFFFF\"];\n  ...\n}",
  "stats": {
    "total_nodes": 5,
    "total_edges": 4,
    "element_nodes": 2,
    "value_nodes": 3,
    "tag_nodes": 2,
    "text_nodes": 1,
    "attr_nodes": 1
  }
}
```

### Route: POST /graph/from/html/to/visjs

**Purpose**: Convert HTML to vis.js Network format

**Response**:
```python
class Schema__Graph__VisJs__Response(Type_Safe):
    nodes : List[Schema__VisJs__Node]
    edges : List[Schema__VisJs__Edge]
    stats : Schema__Graph__Stats

class Schema__VisJs__Node(Type_Safe):
    id    : Safe_Id
    label : Safe_Str__Text
    color : Safe_Str__Text                                                        # Hex color
    shape : Literal["box", "ellipse", "circle", "diamond", "dot", "star", "text"]
    title : Safe_Str__Text                                                        # Tooltip (optional)
    group : Safe_Str__Key                                                         # Node category

class Schema__VisJs__Edge(Type_Safe):
    id     : Safe_Id
    from_  : Safe_Id                                                              # Note: 'from' is Python keyword
    to     : Safe_Id
    label  : Safe_Str__Text                                                       # Edge predicate
    color  : Safe_Str__Text
    dashes : bool = False                                                         # Dashed line style
```

**Example Response**:
```json
{
  "nodes": [
    {"id": "n1", "label": "<div>", "color": "#FFFFFF", "shape": "box", "group": "element"},
    {"id": "n2", "label": "<p>", "color": "#F5F5F5", "shape": "box", "group": "element"},
    {"id": "n3", "label": "div", "color": "#4A90D9", "shape": "ellipse", "group": "tag"},
    {"id": "n4", "label": "Hello", "color": "#FFF9C4", "shape": "note", "group": "text"}
  ],
  "edges": [
    {"id": "e1", "from": "n1", "to": "n2", "label": "child", "color": "#333333"},
    {"id": "e2", "from": "n1", "to": "n3", "label": "tag", "color": "#888888", "dashes": true},
    {"id": "e3", "from": "n2", "to": "n4", "label": "text", "color": "#FFC107"}
  ],
  "stats": {...}
}
```

### Route: POST /graph/from/html/to/d3

**Purpose**: Convert HTML to D3 force-directed format

**Response**:
```python
class Schema__Graph__D3__Response(Type_Safe):
    nodes : List[Schema__D3__Node]
    links : List[Schema__D3__Link]                                                # D3 uses "links" not "edges"
    stats : Schema__Graph__Stats

class Schema__D3__Node(Type_Safe):
    id    : Safe_Id
    label : Safe_Str__Text
    color : Safe_Str__Text
    group : int                                                                   # Numeric group for D3 color scale
    size  : int = 10                                                              # Node radius

class Schema__D3__Link(Type_Safe):
    source : Safe_Id
    target : Safe_Id
    label  : Safe_Str__Text
    color  : Safe_Str__Text
    value  : int = 1                                                              # Link strength
```

### Route: POST /graph/from/html/to/cytoscape

**Purpose**: Convert HTML to Cytoscape.js format

**Response**:
```python
class Schema__Graph__Cytoscape__Response(Type_Safe):
    elements : Schema__Cytoscape__Elements
    stats    : Schema__Graph__Stats

class Schema__Cytoscape__Elements(Type_Safe):
    nodes : List[Schema__Cytoscape__Node]
    edges : List[Schema__Cytoscape__Edge]

class Schema__Cytoscape__Node(Type_Safe):
    data : Dict[str, Any]                                                         # {id, label, color, ...}

class Schema__Cytoscape__Edge(Type_Safe):
    data : Dict[str, Any]                                                         # {id, source, target, label, ...}
```

### Route: POST /graph/from/html/to/mermaid

**Purpose**: Convert HTML to Mermaid flowchart syntax

**Response**:
```python
class Schema__Graph__Mermaid__Response(Type_Safe):
    mermaid : Safe_Str__Text                                                      # Mermaid flowchart definition
    stats   : Schema__Graph__Stats
```

**Example Response**:
```json
{
  "mermaid": "flowchart TB\n  n1[\"<div>\"]\n  n2[\"<p>\"]\n  n1 -->|child| n2\n",
  "stats": {...}
}
```

---

## 🔧 Backend Implementation Details

### Routes__Graph Class

```python
# mgraph_ai_service_html_graph/fast_api/routes/Routes__Graph.py

from osbot_fast_api.api.routes.Fast_API__Routes                              import Fast_API__Routes
from typing                                                                  import Literal

TAG__ROUTES_GRAPH = 'graph'
ROUTES_PATHS__GRAPH = [
    f'/{TAG__ROUTES_GRAPH}/from/html/to/dot'      ,
    f'/{TAG__ROUTES_GRAPH}/from/html/to/visjs'    ,
    f'/{TAG__ROUTES_GRAPH}/from/html/to/d3'       ,
    f'/{TAG__ROUTES_GRAPH}/from/html/to/cytoscape',
    f'/{TAG__ROUTES_GRAPH}/from/html/to/mermaid'  ,
]

class Routes__Graph(Fast_API__Routes):
    tag : str = TAG__ROUTES_GRAPH
    
    graph_service : Html_Graph__Export__Service                               # Auto-initialized by Type_Safe
    
    def from__html__to__dot(self, request: Schema__Graph__From_Html__Request  # POST /graph/from/html/to/dot
                            ) -> Schema__Graph__Dot__Response:
        return self.graph_service.to_dot(request)
    
    def from__html__to__visjs(self, request: Schema__Graph__From_Html__Request
                              ) -> Schema__Graph__VisJs__Response:
        return self.graph_service.to_visjs(request)
    
    def from__html__to__d3(self, request: Schema__Graph__From_Html__Request
                           ) -> Schema__Graph__D3__Response:
        return self.graph_service.to_d3(request)
    
    def from__html__to__cytoscape(self, request: Schema__Graph__From_Html__Request
                                  ) -> Schema__Graph__Cytoscape__Response:
        return self.graph_service.to_cytoscape(request)
    
    def from__html__to__mermaid(self, request: Schema__Graph__From_Html__Request
                                ) -> Schema__Graph__Mermaid__Response:
        return self.graph_service.to_mermaid(request)
    
    def setup_routes(self):
        self.add_route_post(self.from__html__to__dot      )
        self.add_route_post(self.from__html__to__visjs    )
        self.add_route_post(self.from__html__to__d3       )
        self.add_route_post(self.from__html__to__cytoscape)
        self.add_route_post(self.from__html__to__mermaid  )
        return self
```

### Html_Graph__Export__Service Class

```python
# mgraph_ai_service_html_graph/service/html_graph/Html_Graph__Export__Service.py

from osbot_utils.type_safe.Type_Safe                                         import Type_Safe
from osbot_utils.helpers.html.transformers.Html__To__Html_Dict               import Html__To__Html_Dict
from mgraph_ai_service_html_graph.service.html_graph.Html_Dict__OSBot__To__Html_Dict import Html_Dict__OSBot__To__Html_Dict
from mgraph_ai_service_html_graph.service.html_graph.Html_MGraph             import Html_MGraph
from mgraph_ai_service_html_graph.service.html_graph.exporters.Html_MGraph__To__Dot import Html_MGraph__To__Dot

class Html_Graph__Export__Service(Type_Safe):
    
    def html_to_mgraph(self, html: str) -> Html_MGraph:                       # Shared conversion logic
        html_dict__osbot = Html__To__Html_Dict(html=html).convert()
        html_dict        = Html_Dict__OSBot__To__Html_Dict().convert(html_dict__osbot)
        return Html_MGraph.from_html_dict(html_dict)
    
    def apply_config(self, html_mgraph: Html_MGraph, 
                           request    : Schema__Graph__From_Html__Request
                     ) -> Html_MGraph__Render__Config:
        config = Html_MGraph__Render__Config()
        config.apply_preset(request.preset)
        config.show_tag_nodes  = request.show_tag_nodes
        config.show_attr_nodes = request.show_attr_nodes
        config.show_text_nodes = request.show_text_nodes
        config.set_color_scheme(request.color_scheme)
        return config
    
    def to_dot(self, request: Schema__Graph__From_Html__Request
               ) -> Schema__Graph__Dot__Response:
        html_mgraph = self.html_to_mgraph(request.html)
        config      = self.apply_config(html_mgraph, request)
        exporter    = Html_MGraph__To__Dot(mgraph=html_mgraph.mgraph, config=config)
        
        return Schema__Graph__Dot__Response(dot   = exporter.to_string(),
                                            stats = self.get_stats(html_mgraph))
    
    def get_stats(self, html_mgraph: Html_MGraph) -> Schema__Graph__Stats:
        raw_stats = html_mgraph.stats()
        return Schema__Graph__Stats(**raw_stats)
```

### Exporter Base Pattern

```python
# mgraph_ai_service_html_graph/service/html_graph/exporters/Html_MGraph__To__Dot.py

from osbot_utils.type_safe.Type_Safe                                         import Type_Safe
from mgraph_db.mgraph.MGraph                                                 import MGraph
from mgraph_db.mgraph.actions.exporters.dot.MGraph__Export__Dot              import MGraph__Export__Dot
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Config import Html_MGraph__Render__Config

class Html_MGraph__To__Dot(Type_Safe):
    mgraph : MGraph
    config : Html_MGraph__Render__Config
    
    def to_string(self) -> str:                                               # Returns DOT language string
        with MGraph__Export__Dot(graph=self.mgraph.graph) as dot:
            self.config.configure_dot_export(dot)
            return dot.to_string()
```

---

## 🎨 UI Implementation Details

### IFD Methodology - Critical Reminders

**Major Versions are Independent:**
- v0.1.0 is completely independent from v0.2.0
- Each major version is a fresh start with NO dependencies on previous major versions

**Minor Versions are Incremental:**
- v0.1.1 builds on and references files from v0.1.0
- v0.1.2 can reference any v0.1.x files
- Minor versions contain ONLY the changed/new files

**Cross-Version References:**
```html
<!-- In v0.1.1/playground.html -->
<link rel="stylesheet" href="../v0.1.0/css/common.css">
<script src="../v0.1.0/js/services/api-client.js"></script>
```

### Web Component Pattern

```javascript
// components/html-input/html-input.js

class HtmlInput extends HTMLElement {
    constructor() {
        super();
        this.samples = {};                                                    // Loaded sample files
    }
    
    connectedCallback() {
        this.render();
        this.setupEventListeners();
        this.loadSamples();
    }
    
    disconnectedCallback() {
        this.cleanup();                                                       // Remove event listeners
    }
    
    render() {
        this.innerHTML = `
            <div class="html-input">
                <div class="html-input__header">
                    <h3>HTML Input</h3>
                    <select class="sample-selector">
                        <option value="">Select a sample...</option>
                    </select>
                </div>
                <textarea class="html-input__textarea" 
                          placeholder="Enter HTML here..."></textarea>
                <div class="html-input__footer">
                    <span class="char-count">0 characters</span>
                </div>
            </div>
        `;
    }
    
    setupEventListeners() {
        const textarea = this.querySelector('.html-input__textarea');
        const selector = this.querySelector('.sample-selector');
        
        textarea.addEventListener('input', () => {
            this.updateCharCount();
            this.emitChange();
        });
        
        selector.addEventListener('change', (e) => {
            if (e.target.value) {
                this.loadSample(e.target.value);
            }
        });
    }
    
    emitChange() {
        this.dispatchEvent(new CustomEvent('html-changed', {
            detail: { html: this.getHtml() },
            bubbles: true
        }));
    }
    
    getHtml() {
        return this.querySelector('.html-input__textarea').value;
    }
    
    setHtml(html) {
        this.querySelector('.html-input__textarea').value = html;
        this.updateCharCount();
    }
    
    async loadSamples() {
        const samples = ['simple', 'nested', 'attributes', 'mixed-content', 'bootstrap'];
        const selector = this.querySelector('.sample-selector');
        
        for (const name of samples) {
            const option = document.createElement('option');
            option.value = name;
            option.textContent = name.charAt(0).toUpperCase() + name.slice(1);
            selector.appendChild(option);
        }
    }
    
    async loadSample(name) {
        try {
            const response = await fetch(`../v0.1.0/samples/${name}.html`);
            const html = await response.text();
            this.setHtml(html);
            this.emitChange();
        } catch (error) {
            console.error(`Failed to load sample: ${name}`, error);
        }
    }
    
    updateCharCount() {
        const count = this.getHtml().length;
        this.querySelector('.char-count').textContent = `${count} characters`;
    }
    
    cleanup() {
        // Remove listeners if needed
    }
}

customElements.define('html-input', HtmlInput);
```

### Renderer Component Pattern

```javascript
// components/renderers/dot-renderer/dot-renderer.js

class DotRenderer extends HTMLElement {
    constructor() {
        super();
        this.viz = null;                                                      // viz-js instance
    }
    
    async connectedCallback() {
        this.render();
        await this.initViz();
    }
    
    render() {
        this.innerHTML = `
            <div class="dot-renderer">
                <div class="dot-renderer__canvas"></div>
                <div class="dot-renderer__loading" style="display: none;">
                    Loading Graphviz...
                </div>
                <div class="dot-renderer__error" style="display: none;"></div>
            </div>
        `;
    }
    
    async initViz() {
        this.showLoading(true);
        try {
            // viz-js loaded via CDN in parent HTML
            this.viz = await Viz.instance();
            this.showLoading(false);
        } catch (error) {
            this.showError('Failed to initialize Graphviz: ' + error.message);
        }
    }
    
    async renderDot(dotString) {
        if (!this.viz) {
            this.showError('Graphviz not initialized');
            return;
        }
        
        try {
            const canvas = this.querySelector('.dot-renderer__canvas');
            canvas.innerHTML = '';                                            // Clear previous
            
            const svg = this.viz.renderSVGElement(dotString);
            canvas.appendChild(svg);
            
            this.hideError();
            this.emitRendered();
        } catch (error) {
            this.showError('Render error: ' + error.message);
        }
    }
    
    showLoading(show) {
        this.querySelector('.dot-renderer__loading').style.display = 
            show ? 'flex' : 'none';
    }
    
    showError(message) {
        const errorEl = this.querySelector('.dot-renderer__error');
        errorEl.textContent = message;
        errorEl.style.display = 'block';
    }
    
    hideError() {
        this.querySelector('.dot-renderer__error').style.display = 'none';
    }
    
    emitRendered() {
        this.dispatchEvent(new CustomEvent('graph-rendered', {
            bubbles: true
        }));
    }
}

customElements.define('dot-renderer', DotRenderer);
```

### Event-Driven Communication Flow

```
┌─────────────┐     html-changed      ┌─────────────────┐
│ html-input  │ ─────────────────────► │                 │
└─────────────┘                        │                 │
                                       │   playground.js │
┌─────────────┐    config-changed     │  (orchestrator) │
│ config-panel│ ─────────────────────► │                 │
└─────────────┘                        │                 │
                                       └────────┬────────┘
                                                │
                                    POST /graph/from/html/to/dot
                                                │
                                                ▼
                                       ┌────────────────┐
                                       │    Backend     │
                                       │ Routes__Graph  │
                                       └────────┬───────┘
                                                │
                                         {dot, stats}
                                                │
                                                ▼
                      ┌─────────────────────────┴─────────────────────────┐
                      │                                                   │
                      ▼                                                   ▼
              ┌──────────────┐                                   ┌─────────────┐
              │ dot-renderer │                                   │ stats-panel │
              │ .renderDot() │                                   │ .setStats() │
              └──────────────┘                                   └─────────────┘
```

---

## 🧪 Testing Strategy

### Backend Route Tests

```python
# tests/unit/fast_api/routes/test_Routes__Graph.py

from unittest                                                import TestCase
from tests.unit.Html_Graph__Service__Fast_API__Test_Objs     import setup__html_graph_service__fast_api_test_objs

class test_Routes__Graph(TestCase):
    
    @classmethod
    def setUpClass(cls):
        with setup__html_graph_service__fast_api_test_objs() as _:
            cls.client = _.fast_api__client
    
    def test__from_html_to_dot__simple(self):
        response = self.client.post('/graph/from/html/to/dot', json={
            'html': '<div><p>Hello</p></div>'
        })
        
        assert response.status_code == 200
        result = response.json()
        
        assert 'dot' in result
        assert 'digraph' in result['dot']
        assert 'stats' in result
        assert result['stats']['element_nodes'] == 2
    
    def test__from_html_to_dot__with_config(self):
        response = self.client.post('/graph/from/html/to/dot', json={
            'html': '<div class="main"><p>Hello</p></div>',
            'preset': 'structure_only',
            'show_attr_nodes': False
        })
        
        assert response.status_code == 200
        # Verify config was applied (attr nodes filtered)
    
    def test__from_html_to_visjs__format(self):
        response = self.client.post('/graph/from/html/to/visjs', json={
            'html': '<div><p>Hello</p></div>'
        })
        
        assert response.status_code == 200
        result = response.json()
        
        assert 'nodes' in result
        assert 'edges' in result
        assert isinstance(result['nodes'], list)
        assert all('id' in n and 'label' in n for n in result['nodes'])
```

### Exporter Unit Tests

```python
# tests/unit/service/html_graph/exporters/test_Html_MGraph__To__VisJs.py

from unittest                                                import TestCase
from mgraph_ai_service_html_graph.service.html_graph.Html_MGraph import Html_MGraph
from mgraph_ai_service_html_graph.service.html_graph.exporters.Html_MGraph__To__VisJs import Html_MGraph__To__VisJs

class test_Html_MGraph__To__VisJs(TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.simple_dict = {
            'tag': 'div',
            'attrs': {'class': 'main'},
            'child_nodes': [],
            'text_nodes': [{'data': 'Hello', 'position': 0}]
        }
        cls.html_mgraph = Html_MGraph.from_html_dict(cls.simple_dict)
    
    def test__to_visjs__returns_nodes_and_edges(self):
        exporter = Html_MGraph__To__VisJs(mgraph=self.html_mgraph.mgraph)
        result   = exporter.convert()
        
        assert 'nodes' in result
        assert 'edges' in result
        assert len(result['nodes']) > 0
        assert len(result['edges']) > 0
    
    def test__to_visjs__node_structure(self):
        exporter = Html_MGraph__To__VisJs(mgraph=self.html_mgraph.mgraph)
        result   = exporter.convert()
        
        node = result['nodes'][0]
        assert 'id'    in node
        assert 'label' in node
        assert 'color' in node
        assert 'shape' in node
    
    def test__to_visjs__edge_structure(self):
        exporter = Html_MGraph__To__VisJs(mgraph=self.html_mgraph.mgraph)
        result   = exporter.convert()
        
        edge = result['edges'][0]
        assert 'id'    in edge
        assert 'from'  in edge
        assert 'to'    in edge
        assert 'label' in edge
```

---

## 🚀 Implementation Phases

### Phase 1: Backend Routes (Do First)

**Deliverables**:
1. `Routes__Graph` class with all 5 routes
2. `Html_Graph__Export__Service` orchestrator
3. `Html_MGraph__To__Dot` exporter (wraps existing code)
4. Request/response schemas
5. Tests for DOT route

**Files to Create**:
```
mgraph_ai_service_html_graph/
├── fast_api/routes/Routes__Graph.py
├── schemas/graph/
│   ├── __init__.py
│   ├── Schema__Graph__From_Html__Request.py
│   └── Schema__Graph__Dot__Response.py
├── service/html_graph/
│   ├── Html_Graph__Export__Service.py
│   └── exporters/
│       ├── __init__.py
│       └── Html_MGraph__To__Dot.py
└── tests/unit/fast_api/routes/test_Routes__Graph.py
```

**Modify**:
- `Html_Graph__Service__Fast_API.setup_routes()` - add `Routes__Graph`

### Phase 2: UI Foundation (v0.1.0)

**Deliverables**:
1. Package structure with `__init__.py`
2. Dashboard page (index.html)
3. Common CSS (gradient, cards, typography)
4. API client (fetch wrapper)
5. Sample HTML files
6. 404 error page

**Focus**: Establish foundation that all subsequent versions will reference.

### Phase 3: Core UI Framework (v0.1.1)

**Deliverables**:
1. Playground page layout
2. top-nav component
3. html-input component (with samples dropdown)
4. config-panel component
5. stats-panel component
6. graph-canvas component (placeholder)
7. playground.js orchestrator

**Focus**: All UI pieces except the actual rendering.

### Phase 4: DOT Renderer (v0.1.2)

**Deliverables**:
1. dot-renderer component
2. viz-js CDN integration
3. Wire up playground to call `/graph/from/html/to/dot`
4. Display rendered SVG

**Focus**: First working end-to-end visualization.

### Phase 5: Additional Renderers (v0.1.3+)

**v0.1.3**: vis.js renderer (interactive node exploration)
**v0.1.4**: D3 renderer (force-directed layout)
**v0.1.5**: Renderer selector component

---

## ✅ Success Criteria

### Backend Success

- [ ] All 5 routes return correct format
- [ ] Config options properly filter nodes/edges
- [ ] Color schemes applied correctly
- [ ] Stats accurate for all graph types
- [ ] Tests pass for all routes

### UI Success (v0.1.2 milestone)

- [ ] Dashboard loads and shows service info
- [ ] Playground loads with HTML input
- [ ] Sample selector populates and works
- [ ] Config panel changes apply to API calls
- [ ] DOT route called successfully
- [ ] viz-js renders SVG in browser
- [ ] Stats display correctly
- [ ] Zoom/pan work on SVG
- [ ] No console errors
- [ ] Responsive on mobile

### IFD Compliance

- [ ] v0.1.1 references v0.1.0 files (no duplication)
- [ ] v0.1.2 references v0.1.0 and v0.1.1 files
- [ ] Each version folder contains ONLY new/changed files
- [ ] Components use CustomEvents for communication
- [ ] No external UI frameworks (React, Vue, etc.)
- [ ] Visualization libs loaded from CDN

---

## 📝 Critical Reminders

### Backend

- **Always use Type_Safe** for schemas, never Pydantic
- **Follow route naming** - double underscore separates path segments
- **Implement setup_routes()** - don't forget to register routes
- **Reuse existing code** - `Html_MGraph__Render__Config`, `MGraph__Export__Dot`

### UI

- **IFD Version Independence** - Major versions are fresh starts
- **IFD Minor Increments** - Only new/changed files per version
- **Event-Driven** - Components communicate via CustomEvents
- **Real API** - No mock data, call actual endpoints
- **Relative Paths** - `../v0.1.0/css/common.css` for cross-version refs

### Formatting

- **Align parameters** at consistent column positions
- **Align dictionary values** for readability
- **Comments at end of lines**, aligned at column 80+
- **No docstrings** - use inline comments

---

## 🔗 Related Documents

- **IFD Methodology**: `v1_0_0__idf__iterative_flow_development.md`
- **Routes Development**: `v0_24_2__osbot-fast-api__routes_development_guide.md`
- **Type_Safe Guide**: `v3_1_1__osbot-utils__type-safe__and__python-formatting__guidance.md`
- **HTML Service UI**: `v0_6_24__html-service__how-to-create-html-playground-ui.md`

---

## 📊 Quick Reference Tables

### Route Summary

| Route | Method | Input | Output |
|-------|--------|-------|--------|
| `/graph/from/html/to/dot` | POST | HTML + config | DOT string + stats |
| `/graph/from/html/to/visjs` | POST | HTML + config | nodes/edges + stats |
| `/graph/from/html/to/d3` | POST | HTML + config | nodes/links + stats |
| `/graph/from/html/to/cytoscape` | POST | HTML + config | elements + stats |
| `/graph/from/html/to/mermaid` | POST | HTML + config | mermaid text + stats |

### Version Contents

| Version | Contents |
|---------|----------|
| v0.1.0 | Dashboard, common CSS, API client, samples, 404 |
| v0.1.1 | Playground, nav, input, config, stats, canvas (placeholder) |
| v0.1.2 | dot-renderer (viz-js) |
| v0.1.3 | visjs-renderer |
| v0.1.4 | d3-renderer |
| v0.1.5 | renderer-selector |

### CDN Dependencies

| Library | Version | Purpose |
|---------|---------|---------|
| @viz-js/viz | 3.2.4 | DOT → SVG rendering |
| vis-network | 9.1.9 | Interactive graph exploration |
| d3 | 7.8.5 | Force-directed layouts |
| cytoscape | 3.28.1 | Graph algorithms + rendering |