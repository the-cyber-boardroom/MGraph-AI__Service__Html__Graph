# MGraph AI Service Html Graph

[![Current Release](https://img.shields.io/badge/release-v1.4.8-blue)](https://github.com/the-cyber-boardroom/MGraph-AI__Service__Html__Graph/releases)
[![Python](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-009688)](https://fastapi.tiangolo.com/)
[![AWS Lambda](https://img.shields.io/badge/AWS-Lambda-orange)](https://aws.amazon.com/lambda/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](LICENSE)
[![CI Pipeline - DEV](https://github.com/the-cyber-boardroom/MGraph-AI__Service__Html__Graph/actions/workflows/ci-pipeline__dev.yml/badge.svg)](https://github.com/the-cyber-boardroom/MGraph-AI__Service__Html__Graph/actions)

A powerful service that transforms HTML documents into graph representations for visualization, analysis, and manipulation. Built on the MGraph AI framework.

## Overview

```
HTML Document  ──────►  Graph Representation  ──────►  Visual Output

<html>                     ┌─────────────┐              ┌─────────────┐
  <body>           ──►     │   Nodes     │      ──►     │   DOT       │
    <div>                  │   Edges     │              │   D3        │
  </body>                  │   Clusters  │              │   Cytoscape │
</html>                    └─────────────┘              │   VisJs     │
                                                        │   Mermaid   │
                                                        │   Tree      │
                                                        └─────────────┘
```

The Html Graph Service converts any HTML into a multi-graph model where different aspects of the document (DOM structure, attributes, scripts, styles) are represented as interconnected graphs that can be visualized using multiple rendering engines.

## Features

| Feature | Description |
|---------|-------------|
| **Multi-Graph Model** | 5 interconnected graphs: Body, Head, Attributes, Scripts, Styles |
| **6 Rendering Engines** | DOT (Graphviz), D3, Cytoscape, VisJs, Mermaid, Tree |
| **8 Transformations** | Default, Attributes View, Full Document, Head, Scripts, Styles, and more |
| **Round-Trip Fidelity** | HTML → Graph → HTML preserves all structure including boolean attributes |
| **Clustered Views** | Group subgraphs with colored clusters for full document visualization |
| **REST API** | FastAPI-based endpoints for programmatic access |
| **AWS Lambda Ready** | Deployable as serverless function |

## Quick Start

### Installation

```bash
pip install mgraph-ai-service-html-graph
```

### Basic Usage

```python
from mgraph_ai_service_html_graph.service.html_graph.Html_Graph__Export__Service import Html_Graph__Export__Service

service = Html_Graph__Export__Service()

html = """
<html>
    <body>
        <div class="container">
            <p>Hello World</p>
        </div>
    </body>
</html>
"""

# Export to DOT format
result = service.export(
    html           = html,
    engine         = 'dot',
    transformation = 'default'
)

print(result['output'])
```

### Running the Server

```bash
# Development
uvicorn mgraph_ai_service_html_graph.web.Html_Graph__Web:app --reload

# Production
uvicorn mgraph_ai_service_html_graph.web.Html_Graph__Web:app --host 0.0.0.0 --port 8000
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Html_MGraph Document                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────────────────────────┐  │
│   │  HEAD GRAPH │   │  BODY GRAPH │   │       ATTRIBUTES GRAPH          │  │
│   │             │   │             │   │                                 │  │
│   │  <head>     │   │  <body>     │   │  element ──► instance ──► name  │  │
│   │    └─title  │   │    └─div    │   │                    └──► value   │  │
│   └─────────────┘   └─────────────┘   └─────────────────────────────────┘  │
│                                                                             │
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────────────────────────┐  │
│   │SCRIPTS GRAPH│   │STYLES GRAPH │   │       DOCUMENT GRAPH            │  │
│   │             │   │             │   │         (Meta View)             │  │
│   │  <script>   │   │  <style>    │   │  Connects all subgraphs         │  │
│   └─────────────┘   └─────────────┘   └─────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## API Endpoints

### Export HTML to Graph

```http
POST /api/v1/html-graph/export
Content-Type: application/json

{
    "html": "<html><body><div>Hello</div></body></html>",
    "engine": "dot",
    "transformation": "default"
}
```

### List Available Engines

```http
GET /api/v1/html-graph/engines
```

Returns: `["dot", "d3", "cytoscape", "visjs", "mermaid", "tree"]`

### List Available Transformations

```http
GET /api/v1/html-graph/transformations
```

Returns transformation metadata including name, label, and description.

## Rendering Engines

| Engine | Output | Best For |
|--------|--------|----------|
| **DOT** | Graphviz DOT → SVG | Static diagrams, documentation |
| **D3** | JSON for D3.js | Interactive web visualizations |
| **Cytoscape** | JSON for Cytoscape.js | Complex network analysis |
| **VisJs** | JSON for vis.js | Dynamic, physics-based layouts |
| **Mermaid** | Mermaid syntax | Markdown-embeddable diagrams |
| **Tree** | JSON tree structure | Hierarchical views |

## Transformations

| Transformation | Description |
|----------------|-------------|
| `default` | Body DOM structure |
| `attributes-view` | Tags and their attributes |
| `full-document` | All 5 subgraphs with colored clusters |
| `head-view` | Head section structure |
| `scripts-view` | Script elements and content |
| `styles-view` | Style elements and CSS |

## Creating Custom Transformations

```python
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base import Graph_Transformation__Base

class My_Custom_Transformation(Graph_Transformation__Base):

    name        : str = "my-custom"
    label       : str = "My Custom View"
    description : str = "Custom visualization"

    def html_mgraph__to__mgraph(self, html_mgraph):
        # Select which graph to visualize
        return html_mgraph.attrs_graph.mgraph

    def configure_dot(self, config):
        # Customize DOT rendering
        config.rankdir = 'LR'
        return config
```

## The 5-Phase Pipeline

```
Phase 1              Phase 2              Phase 3              Phase 4              Phase 5
────────             ────────             ────────             ────────             ────────
   │                    │                    │                    │                    │
   ▼                    ▼                    ▼                    ▼                    ▼

┌───────┐          ┌───────────┐        ┌─────────┐        ┌──────────┐        ┌────────┐
│ HTML  │────────► │Html_MGraph│───────►│ MGraph  │───────►│  Engine  │───────►│ Output │
└───────┘          └───────────┘        └─────────┘        └──────────┘        └────────┘

html__to__         html_mgraph__        transform_         configure_*         transform_
html_mgraph()      to__mgraph()         mgraph()           callbacks           export()
```

Each phase has a transformation hook allowing complete customization of the visualization pipeline.

## Development

### Setup

```bash
git clone https://github.com/the-cyber-boardroom/MGraph-AI__Service__Html__Graph.git
cd MGraph-AI__Service__Html__Graph
poetry install
```

### Running Tests

```bash
pytest tests/
```

### Project Structure

```
mgraph_ai_service_html_graph/
├── service/
│   ├── html_graph/              # Export service
│   ├── html_mgraph/             # Multi-graph HTML model
│   │   ├── converters/          # HTML ↔ MGraph converters
│   │   └── graphs/              # Subgraph implementations
│   ├── html_graph__transformations/  # View transformations
│   └── mgraph__engines/         # Rendering engines
└── web/                         # FastAPI endpoints
```

## Use Cases

- **Web Scraping Analysis** - Visualize DOM structure of scraped pages
- **HTML Diff Visualization** - Compare documents via graph representations
- **Accessibility Auditing** - Analyze attribute patterns for ARIA compliance
- **DOM Manipulation Planning** - Visualize before/after transformation states
- **Educational Tool** - Teach HTML structure through visual graphs
- **Security Analysis** - Analyze script and style injection points

## Documentation

- [Project Brief](docs/Html_MGraph_Service__Project_Brief.md) - Comprehensive overview
- [Attribute Refactor](docs/IMPLEMENTATION_BRIEF__Attribute_Graph_Storage_Refactor.md) - 3-node attribute model

## License

Apache 2.0 - See [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please read our contributing guidelines and submit pull requests.

## Related Projects

- [MGraph AI](https://github.com/the-cyber-boardroom/MGraph-AI) - Core graph framework
- [The Cyber Boardroom](https://github.com/the-cyber-boardroom) - Parent organization