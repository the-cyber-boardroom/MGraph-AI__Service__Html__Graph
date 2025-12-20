# MGraph HTML Graph - Native Export Implementation

## Overview

This implementation adds **native format export** from the backend `Html_MGraph` model directly to each visualization library's format (vis.js, D3.js, Cytoscape.js, Mermaid), eliminating the need for client-side DOT parsing.

## Problem Solved

**Before:** All renderers received DOT format and had to parse it client-side:
```
HTML → Html_MGraph (rich model) → DOT string → [network] → Client parses DOT → Renderer format
```

**After:** Each renderer receives its native format directly:
```
HTML → Html_MGraph (rich model) → Native format per renderer → [network] → Direct render
```

## Benefits

1. **No duplicate parsing** - Removed 4 client-side DOT parsers
2. **Preserved semantics** - Node types, predicates, DOM paths, categories all available
3. **Better performance** - Less client-side processing
4. **Cleaner code** - Each renderer just receives what it needs
5. **Type safety** - Using MGraph-DB Type_Safe patterns throughout

## Architecture

### Backend Components

```
service/
├── Html_Graph__Export__Service.py      # Unified service for all formats
└── html_graph__export/
    ├── __init__.py
    ├── Html_MGraph__Data__Extractor.py  # Core: extracts semantic data from MGraph
    ├── Html_MGraph__To__VisJs.py        # vis.js native format
    ├── Html_MGraph__To__D3.py           # D3.js native format
    ├── Html_MGraph__To__Cytoscape.py    # Cytoscape.js native format
    └── Html_MGraph__To__Mermaid.py      # Mermaid flowchart syntax
```

### Data Flow

```python
# 1. Extract semantic data from MGraph
extractor = Html_MGraph__Data__Extractor(mgraph=html_mgraph.mgraph, config=config)
extractor.extract()

# 2. Convert to target format
exporter = Html_MGraph__To__VisJs(mgraph=html_mgraph.mgraph, config=config)
data = exporter.export()

# 3. Return native format
# {nodes: [...], edges: [...], rootId: '...'}
```

### MGraph-DB Integration

Uses MGraph-DB v1.4.7 features:

- **`node_path`** - DOM path identification (e.g., `"html.body.div[0]"`)
- **`edge_label.predicate`** - Semantic relationships (`child`, `tag`, `attr`, `text`)
- **`edge_path`** - Child position among siblings
- **`mgraph.data()`** - Efficient node/edge access
- **`mgraph.index()`** - O(1) lookups

## API Endpoints

### New Native Endpoints

```
POST /graph/from/html/to/visjs     → {nodes: [...], edges: [...], stats: {...}}
POST /graph/from/html/to/d3        → {nodes: [...], links: [...], stats: {...}}
POST /graph/from/html/to/cytoscape → {elements: {nodes: [...], edges: [...]}, stats: {...}}
POST /graph/from/html/to/mermaid   → {mermaid: "flowchart TB...", stats: {...}}

POST /graph/from/url/to/visjs
POST /graph/from/url/to/d3
POST /graph/from/url/to/cytoscape
POST /graph/from/url/to/mermaid
```

### Existing DOT Endpoint (unchanged)

```
POST /graph/from/html/to/dot       → {dot: "digraph...", stats: {...}}
POST /graph/from/url/to/dot
```

## Response Formats

### vis.js Format
```json
{
  "nodes": [
    {
      "id": "abc123",
      "label": "<div>",
      "title": "<div>",
      "shape": "box",
      "color": {"background": "#E8E8E8", "border": "#CCCCCC"},
      "font": {"color": "#333333", "size": 11},
      "nodeType": "element",
      "domPath": "html.body.div",
      "category": "structural",
      "depth": 3
    }
  ],
  "edges": [
    {
      "id": "edge1",
      "from": "abc123",
      "to": "def456",
      "dashes": false,
      "color": {"color": "#888888"},
      "predicate": "child",
      "position": 0
    }
  ],
  "rootId": "root123",
  "stats": {...},
  "duration": 0.042,
  "format": "visjs"
}
```

### D3.js Format
```json
{
  "nodes": [
    {
      "id": "abc123",
      "label": "<div>",
      "color": "#E8E8E8",
      "fontColor": "#333333",
      "radius": 25,
      "nodeType": "element",
      "domPath": "html.body.div",
      "category": "structural",
      "depth": 3
    }
  ],
  "links": [
    {
      "source": "abc123",
      "target": "def456",
      "color": "#888888",
      "dashed": false,
      "width": 2,
      "predicate": "child"
    }
  ],
  "stats": {...},
  "format": "d3"
}
```

### Cytoscape.js Format
```json
{
  "elements": {
    "nodes": [
      {
        "data": {
          "id": "abc123",
          "label": "<div>",
          "color": "#E8E8E8",
          "nodeType": "element",
          "domPath": "html.body.div"
        },
        "group": "nodes"
      }
    ],
    "edges": [
      {
        "data": {
          "id": "edge1",
          "source": "abc123",
          "target": "def456",
          "predicate": "child"
        },
        "group": "edges"
      }
    ]
  },
  "stats": {...},
  "format": "cytoscape"
}
```

### Mermaid Format
```json
{
  "mermaid": "flowchart TB\n    n0[\"html\"]\n    n1[\"body\"]\n    ...",
  "mermaid_size": 1234,
  "stats": {...},
  "format": "mermaid"
}
```

## Frontend Updates

### Updated Renderers

Each renderer now has a simplified `render(graphData)` method that receives native format:

```javascript
// vis-renderer.js
async render(graphData) {
    const { nodes, edges } = graphData;
    const nodesDataset = new vis.DataSet(nodes);
    const edgesDataset = new vis.DataSet(edges);
    // ... direct render
}

// Legacy method kept for backwards compatibility
async renderDot(dotCode) {
    console.warn('Deprecated. Use render(graphData)');
    // Falls back to DOT parsing
}
```

### Updated Playground

The playground calls the appropriate API for each renderer:

```javascript
switch (renderer) {
    case 'dot':
        response = await apiClient.htmlToDot(request);
        break;
    case 'visjs':
        response = await apiClient.htmlToVisJs(request);
        break;
    case 'd3':
        response = await apiClient.htmlToD3(request);
        break;
    case 'cytoscape':
        response = await apiClient.htmlToCytoscape(request);
        break;
    case 'mermaid':
        response = await apiClient.htmlToMermaid(request);
        break;
}
```

## Semantic Metadata

All formats include semantic metadata from the Html_MGraph:

| Field | Description | Example |
|-------|-------------|---------|
| `nodeType` | Node classification | `element`, `tag`, `attr`, `text` |
| `domPath` | DOM path identifier | `html.body.div[0].p` |
| `category` | Tag category | `structural`, `text`, `form`, `media` |
| `depth` | DOM depth level | `3` |
| `predicate` | Edge relationship type | `child`, `tag`, `attr`, `text` |
| `position` | Child position among siblings | `0`, `1`, `2` |

## Usage Example

```python
from mgraph_ai_service_html_graph.service.Html_Graph__Export__Service import Html_Graph__Export__Service
from mgraph_ai_service_html_graph.schemas.routes.Schema__Graph__From_Html__Request import Schema__Graph__From_Html__Request

service = Html_Graph__Export__Service()

request = Schema__Graph__From_Html__Request(
    html='<div><p>Hello</p></div>',
    preset='FULL_DETAIL',
    show_tag_nodes=True,
    show_attr_nodes=True,
    show_text_nodes=True,
    color_scheme='DEFAULT'
)

# Get vis.js format
visjs_data = service.to_visjs(request)

# Get D3 format
d3_data = service.to_d3(request)

# Get Cytoscape format
cy_data = service.to_cytoscape(request)

# Get Mermaid format
mermaid_data = service.to_mermaid(request)
```

## File Locations

### Backend (Python)
- `/mgraph_ai_service_html_graph/service/html_graph__export/` - New exporters
- `/mgraph_ai_service_html_graph/service/Html_Graph__Export__Service.py` - Updated service
- `/mgraph_ai_service_html_graph/routes/Routes__Graph.py` - New endpoints

### Frontend (JavaScript)
- `/components/vis-renderer/vis-renderer.js` - Updated vis.js renderer
- `/components/d3-renderer/d3-renderer.js` - Updated D3 renderer
- `/components/cytoscape-renderer/cytoscape-renderer.js` - Updated Cytoscape renderer
- `/components/mermaid-renderer/mermaid-renderer.js` - Updated Mermaid renderer
- `/js/services/api-client.js` - New API methods
- `/js/playground.js` - Updated orchestrator
