# Phase D Debrief: MGraph Body Transformers

**Date**: January 2026  
**Status**: ✅ Complete  
**Tests**: All passing

---

## Executive Summary

Phase D created a foundation of **granular, composable MGraph transformers** that operate directly on the body graph, enabling clean HTML transformations via the full roundtrip pipeline:

```
HTML → MGraph → Transform (in-place) → HTML
```

**Key Achievement**: Successfully unwrap inline elements (`<a>`, `<b>`, `<i>`, etc.) and reconstruct valid HTML with text content in correct order.

---

## Architecture

### Full Roundtrip Pipeline

```
HTML String
    │
    ▼ (Phase A)
Html__To__Html_Dict__With__Node_Ids
    │
    ▼
Html_Dict (with node_ids)
    │
    ▼ (Phase B)
Html__To__Html_MGraph__Document__Node_Id_Reuse
    │
    ▼
Html_MGraph__Document
    │
    └──► body_graph.mgraph ◄── TRANSFORM HERE (Phase D)
              │
              ▼
    MGraph_Transformer__Body__Pipeline
        ├── Unwrap_Inline
        ├── Merge_Text
        ├── Remove_Empty_Text
        └── Remove_By_Tag
              │
              ▼
    Modified body_graph (same object)
              │
              ▼
Html_MGraph__Document__To__Html
    │
    ▼
Clean HTML String
```

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **In-place modification** | `body_graph` is the same object reference used by `Html_MGraph__Document__To__Html`, so modifications propagate automatically |
| **Single responsibility** | Each transformer does one thing well, making them composable and testable |
| **Base class with helpers** | 20+ helper methods for common operations (traversal, inspection, modification) |
| **Pipeline pattern** | Chain transformers in sequence with fluent API |

---

## Files Created

| File | Purpose |
|------|---------|
| **Documentation** | |
| `PHASE_D__MGraph_Body_Transformers__Brief.md` | Specification and design |
| `PHASE_D__MGraph_Body_Transformers__Debrief.md` | This document |
| **Implementation** | |
| `MGraph_Transformer__Body__Base.py` | Base class with 20+ helper methods |
| `MGraph_Transformer__Body__Unwrap_Inline.py` | Remove inline wrappers, keep children |
| `MGraph_Transformer__Body__Merge_Text.py` | Combine adjacent text nodes |
| `MGraph_Transformer__Body__Remove_Empty_Text.py` | Delete whitespace-only text |
| `MGraph_Transformer__Body__Remove_By_Tag.py` | Remove elements by tag name |
| `MGraph_Transformer__Body__Pipeline.py` | Chain transformers |
| **Tests** | |
| `test_MGraph_Transformer__Body.py` | Unit tests for each transformer |
| `test_MGraph_Transformer__Roundtrip_Integration.py` | Full HTML → Transform → HTML tests |

### Suggested File Location

```
mgraph_ai_service_html_graph/
└── service/
    └── html_mgraph/
        └── transformers/                          # NEW FOLDER
            ├── __init__.py
            ├── MGraph_Transformer__Body__Base.py
            ├── MGraph_Transformer__Body__Unwrap_Inline.py
            ├── MGraph_Transformer__Body__Merge_Text.py
            ├── MGraph_Transformer__Body__Remove_Empty_Text.py
            ├── MGraph_Transformer__Body__Remove_By_Tag.py
            └── MGraph_Transformer__Body__Pipeline.py
```

---

## Bugs Fixed

### Bug 1: Text Content Lost After Unwrap

**Symptom**:
```
Input:  <div>Hello <b>World</b>!</div>
Output: <div>Hello !</div>          ← "World" missing!
```

**Root Cause**: Created shortcut edges **without predicates**. The `Html_MGraph__Document__To__Html` converter uses edge predicates (`child`, `text`) to understand relationships. Edges without predicates were being ignored.

**Fix**: Capture and preserve the edge predicate when creating shortcut edges:

```python
# Before (broken)
self.create_edge(mgraph, parent_id, child_id)

# After (fixed)
predicate = self.get_edge_predicate(mgraph, child_edge_id)
self.create_edge(mgraph, parent_id, child_id, predicate)
```

Updated `create_edge()` in base class:

```python
def create_edge(self, mgraph, from_node_id, to_node_id, predicate=None, edge_path=None):
    edge_label = None
    if predicate:
        edge_label = Schema__MGraph__Edge__Label(predicate=Safe_Id(predicate))
    
    return mgraph.edit().new_edge(from_node_id=from_node_id,
                                  to_node_id=to_node_id,
                                  edge_label=edge_label,
                                  edge_path=edge_path_obj)
```

---

### Bug 2: Non-Deterministic Text Order

**Symptom**:
```
Input:  <div>Hello <b>World</b>!</div>
Output: <div>WorldHello !</div>     ← Sometimes!
Output: <div>Hello World!</div>     ← Other times!
```

**Root Cause**: Two issues:
1. Iterating over **sets** which don't preserve order
2. Not preserving `edge_path` which tells the HTML converter the order of children

**Fix**: Capture `edge_path` from the **parent→wrapper** edge and preserve it on the new shortcut edge:

```python
for parent_edge_id in incoming_edges:
    parent_id        = index.edges_index.get_edge_from_node(parent_edge_id)
    parent_edge_path = self.get_edge_path(mgraph, parent_edge_id)  # ← Position!
    
    ...
    
    edges_to_add.append({'from_node_id': str(parent_id),
                         'to_node_id'  : str(child_id),
                         'predicate'   : predicate,
                         'edge_path'   : parent_edge_path})  # ← Preserve!
```

**Visualization of the fix**:

```
Before unwrap:
  div → "Hello " (edge_path: 0)
  div → b        (edge_path: 1)  ← wrapper at position 1
  div → "!"      (edge_path: 2)
  b   → "World"  (edge_path: 0)

After unwrap:
  div → "Hello " (edge_path: 0)  ← unchanged
  div → "World"  (edge_path: 1)  ← NEW, inherits position 1 from div→b
  div → "!"      (edge_path: 2)  ← unchanged

Result: "Hello World!" (correct order!)
```

---

## MGraph Edge Structure Reference

Understanding gained during debugging:

```python
class Schema__MGraph__Edge:
    edge_id    : Edge_Id
    edge_data  : Schema__MGraph__Edge__Data   # Empty for HTML graphs
    edge_type  : Type['Schema__MGraph__Edge']
    edge_label : Schema__MGraph__Edge__Label  # Contains predicate!
    edge_path  : Edge_Path                    # Contains position!

class Schema__MGraph__Edge__Label:
    incoming  : Safe_Id  # Not used in HTML graphs
    outgoing  : Safe_Id  # Not used in HTML graphs
    predicate : Safe_Id  # 'child' or 'text' - CRITICAL!
```

**Key insight**: Both `predicate` and `edge_path` must be preserved when creating new edges, or the HTML reconstruction will fail.

---

## Base Class Helper Methods

The `MGraph_Transformer__Body__Base` class provides these helpers:

### Node Inspection
- `get_node_tag(node_path)` - Extract tag: `'body.div.a'` → `'a'`
- `is_text_node(domain_node)` - Check if text node
- `get_text_value(domain_node)` - Get text content
- `set_text_value(domain_node, value)` - Update text content
- `get_node_id(domain_node)` - Get node_id as string
- `get_node_path(domain_node)` - Get node_path as string

### Graph Traversal
- `get_all_nodes(mgraph)` - List all nodes
- `get_node_by_id(mgraph, node_id)` - Find node by ID
- `get_parent_node_ids(mgraph, node_id)` - Get parents
- `get_child_node_ids(mgraph, node_id)` - Get children
- `get_incoming_edges(mgraph, node_id)` - Get incoming edge IDs
- `get_outgoing_edges(mgraph, node_id)` - Get outgoing edge IDs
- `get_edge_predicate(mgraph, edge_id)` - Get edge predicate
- `get_edge_path(mgraph, edge_id)` - Get edge position

### Graph Modification
- `delete_node(mgraph, node_id)` - Remove node and edges
- `create_edge(mgraph, from_id, to_id, predicate, edge_path)` - Create edge with metadata
- `create_text_node(mgraph, text_value)` - Create new text node

### Batch Operations
- `find_nodes_by_tag(mgraph, tags)` - Find nodes with specific tags
- `find_text_nodes(mgraph)` - Find all text nodes
- `find_element_nodes(mgraph)` - Find all element nodes

---

## Usage Example

```python
from Html__To__Html_Dict__With__Node_Ids            import Html__To__Html_Dict__With__Node_Ids
from Html__To__Html_MGraph__Document__Node_Id_Reuse import Html__To__Html_MGraph__Document__Node_Id_Reuse
from Html_MGraph__Document__To__Html                import Html_MGraph__Document__To__Html

from MGraph_Transformer__Body__Pipeline             import MGraph_Transformer__Body__Pipeline
from MGraph_Transformer__Body__Unwrap_Inline        import MGraph_Transformer__Body__Unwrap_Inline
from MGraph_Transformer__Body__Merge_Text           import MGraph_Transformer__Body__Merge_Text
from MGraph_Transformer__Body__Remove_Empty_Text    import MGraph_Transformer__Body__Remove_Empty_Text
from MGraph_Transformer__Body__Remove_By_Tag        import MGraph_Transformer__Body__Remove_By_Tag

# Input HTML
html = '''<html>
    <body>
        <div>Hello <b>World</b>!</div>
        <script>console.log("test");</script>
    </body>
</html>'''

# Phase A + B: HTML → MGraph
html_dict = Html__To__Html_Dict__With__Node_Ids(html=html).convert()
doc       = Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(html_dict)

# Phase D: Transform body graph
body = doc.body_graph.mgraph

pipeline = (MGraph_Transformer__Body__Pipeline()
    .add(MGraph_Transformer__Body__Remove_By_Tag(tags_to_remove={'script', 'style'}))
    .add(MGraph_Transformer__Body__Unwrap_Inline())
    .add(MGraph_Transformer__Body__Merge_Text())
    .add(MGraph_Transformer__Body__Remove_Empty_Text()))

pipeline.transform(body)

# Convert back to HTML
clean_html = Html_MGraph__Document__To__Html().convert(doc)

# Result:
# <html>
#     <body>
#         <div>Hello World!</div>
#     </body>
# </html>
```

---

## Test Coverage

### Unit Tests (`test_MGraph_Transformer__Body.py`)

| Test Class | Tests |
|------------|-------|
| `test_MGraph_Transformer__Body__Base` | `get_node_tag` variations, `transform` raises NotImplementedError |
| `test_MGraph_Transformer__Body__Unwrap_Inline` | Find wrappers, remove tags, preserve text, custom tags |
| `test_MGraph_Transformer__Body__Merge_Text` | Find parents, merge nodes |
| `test_MGraph_Transformer__Body__Remove_Empty_Text` | Find empty, remove whitespace |
| `test_MGraph_Transformer__Body__Remove_By_Tag` | Find by tag, remove subtrees, preserve others |
| `test_MGraph_Transformer__Body__Pipeline` | Chain, fluent API, list, clear |

### Integration Tests (`test_MGraph_Transformer__Roundtrip_Integration.py`)

| Test | Description |
|------|-------------|
| `test_roundtrip__no_transform` | HTML → MGraph → HTML preserves structure |
| `test_roundtrip__unwrap_inline__removes_b_tag` | Unwrap removes `<b>`, preserves text |
| `test_roundtrip__unwrap_inline__complex_html` | Multiple inline elements |
| `test_roundtrip__pipeline__unwrap_and_merge` | Pipeline chains correctly |
| `test_roundtrip__remove_script` | Remove `<script>` tags |
| `test_inplace_modification` | Verify same object reference |
| `test_full_workflow__clean_html` | Complete cleanup pipeline |

---

## Key Takeaways

1. **Edge metadata is critical** - `predicate` and `edge_path` must both be preserved when creating new edges, or HTML reconstruction fails silently.

2. **Sets are non-deterministic** - When order matters, capture position data (`edge_path`) before iterating.

3. **In-place modification works** - The body_graph reference is shared, so modifications propagate to `Html_MGraph__Document__To__Html` automatically.

4. **Single responsibility pays off** - Each transformer is simple, testable, and composable.

5. **Base class helpers save time** - Centralizing traversal/modification logic in the base class prevented code duplication and bugs.

6. **Integration tests catch real bugs** - The unit tests passed, but integration tests revealed the predicate and ordering bugs.

---

## Next Steps

| Phase | Description | Status |
|-------|-------------|--------|
| Phase E | Reverse Mapping Operations | ⏳ Pending |
| Phase F | Text Classification Pipeline | ⏳ Pending |

### Potential Enhancements

- Add `MGraph_Transformer__Body__Collapse_Single_Child` - Remove wrappers with only one child
- Add `MGraph_Transformer__Body__Unwrap_By_Tag` - Configurable unwrap by specific tags (not just inline)
- Add source tracking to transformers (like Phase C) if needed for reverse operations
