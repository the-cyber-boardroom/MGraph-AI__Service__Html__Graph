# Documentation

This folder contains development documentation, LLM briefs, and guides for the MGraph AI Service Html Graph project.

## Folder Structure

```
docs/
├── dev/
│   ├── dev-briefs/          # Feature development documentation by version
│   └── llm-briefs/          # LLM-optimized documentation for AI assistants
└── README.md                # This file
```

---

## Dev Briefs

Development briefs document the implementation journey for specific features and versions. Each folder contains artifacts, diagrams, and notes from the development process.

| Version | Brief | Description |
|---------|-------|-------------|
| v0.7.2 | `first-html-mgraph-visualisations` | Initial HTML to MGraph visualization implementation |
| v0.7.4 | `adding-graph-render-routes` | FastAPI routes for graph rendering endpoints |
| v0.7.4 | `adding-mvp-of-render-ui` | Minimum viable product for the visualization UI |
| v1.0.8 | `ifd-refactoring-to-v1.2.0` | Refactoring using Iterative Flow Development methodology |
| v1.1.9 | `add-to-ui__tree-and-tree-text-engines` | Tree and Tree-Text rendering engine integration |
| v1.1.10 | `add-live-reload-of-graph-from-code-changes` | Hot reload functionality for development |
| v1.1.10 | `html-graph-transformations` | Transformation system (Default, Attributes, Full Doc, etc.) |
| v1.2.0 | `html-mgraph_multi_graph-architecture` | 5-subgraph architecture (Body, Head, Attrs, Scripts, Styles) |
| v1.3.2 | `export-service-refactoring` | 5-phase pipeline refactor with transformation hooks |

---

## LLM Briefs

LLM briefs are documentation specifically designed to help AI assistants (like Claude) understand the codebase, architecture, and conventions. These documents provide context that enables more effective AI-assisted development.

### Core Project Briefs

| File | Description |
|------|-------------|
| `v1.4.0__html-graph-service__llm-brief.md` | **Main project brief** - Html_MGraph architecture, 5-phase pipeline, transformations, engines |
| `v1.1.9__html-graph__frontend-llm_brief_to_backend-llm.md` | Frontend-to-backend integration guide |
| `v1_4_7__mGraph-db__llm-brief.md` | MGraph database layer - nodes, edges, graph operations |

### IFD (Iterative Flow Development) Guides

The IFD methodology is our development approach for building features iteratively with continuous testing and versioning.

| File | Description |
|------|-------------|
| `v1.2.1__ifd__intro-and-how-to-use.md` | Introduction to IFD methodology |
| `v1.1.0__idf__iterative_flow_development.md` | Core IFD concepts and workflow |
| `v1.2.0__ifd_testing_guide.md` | Testing practices within IFD |
| `v1.2.0__ifd_versioning_guide.md` | Version numbering and release practices |

### OSBot Utils Guides

OSBot Utils is our foundational utility library providing Type_Safe classes and testing patterns.

| File | Description |
|------|-------------|
| `v3.1.1__osbot-utils_type-safe__and__python-formatting__guidance.md` | Type_Safe patterns and Python formatting conventions |
| `v3.1.1__osbot-utils_type-safe__testing-guidance.md` | Testing patterns for Type_Safe classes |
| `v3.28.0__osbot-utils-safe-primitives__reference-guide.md` | Safe primitives reference (Node_Id, Obj_Id, etc.) |

---

## How to Use These Documents

### For Developers

1. **Starting a new feature?** Check dev-briefs for similar past implementations
2. **Understanding architecture?** Read `v1.4.0__html-graph-service__llm-brief.md`
3. **Learning the methodology?** Start with the IFD guides

### For AI Assistants

When working with an LLM on this codebase, provide relevant briefs as context:

```
# Example: Working on transformations
"Please read docs/dev/llm-briefs/v1.4.0__html-graph-service__llm-brief.md 
for context on the transformation system"

# Example: Working on Type_Safe classes
"Please review docs/dev/llm-briefs/v3.1.1__osbot-utils_type-safe__and__python-formatting__guidance.md"
```

---

## Key Concepts Quick Reference

### Html_MGraph Architecture

```
Html_MGraph Document
├── body_graph      # DOM structure for <body>
├── head_graph      # DOM structure for <head>
├── attrs_graph     # Tags and attributes (3-node model)
├── scripts_graph   # <script> elements
└── styles_graph    # <style> elements
```

### 5-Phase Pipeline

```
Phase 1: html__to__html_mgraph()      # Parse HTML
Phase 2: html_mgraph__to__mgraph()    # Select graph
Phase 3: transform_mgraph()           # Modify graph
Phase 4: configure_*()                # Configure engine
Phase 5: transform_export()           # Post-process output
```

### Rendering Engines

- **DOT** - Graphviz static diagrams
- **D3** - Interactive D3.js visualizations
- **Cytoscape** - Network analysis
- **VisJs** - Physics-based layouts
- **Mermaid** - Markdown-embeddable
- **Tree** - Hierarchical JSON

### Transformations

- **default** - Body DOM structure
- **attributes-view** - Tags and attributes
- **full-document** - All subgraphs clustered
- **head-view** - Head section
- **scripts-view** - Script elements
- **styles-view** - Style elements

---

## Version Naming Convention

Documents follow the pattern: `v{version}__{feature-name}.md`

- **Version** matches the release where the feature was introduced
- **Feature name** describes the content in kebab-case

Example: `v1.2.0__html-mgraph_multi_graph-architecture` documents the multi-graph architecture introduced in v1.2.0

---

## Contributing

When adding documentation:

1. **Dev briefs** go in `dev/dev-briefs/v{version}__{feature}/`
2. **LLM briefs** go in `dev/llm-briefs/` with version prefix
3. Use clear, descriptive names
4. Include diagrams where helpful (ASCII art works well for LLM briefs)
5. Keep LLM briefs focused and scannable