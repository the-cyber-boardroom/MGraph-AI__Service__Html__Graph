# Phase D: MGraph Body Transformers

**Status**: 📋 Planning  
**Depends On**: Phase A ✅, Phase B ✅, Phase C ✅

---

## Objective

> Create a foundation of granular, composable MGraph transformers that operate directly on the body graph, enabling clean HTML transformations via the full roundtrip pipeline.

---

## The Problem

`Html_Use_Case__3` contains useful transformation logic but is tightly coupled to:
- DOT visualization output
- Specific 4-step workflow
- Mixed concerns (transform + render)

We need **clean, single-responsibility transformers** that:
- Operate directly on MGraph (not Html_Dict)
- Can be composed/chained
- Support the full roundtrip: HTML → MGraph → Transform → HTML

---

## Architecture

### The Full Roundtrip Pipeline

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
    ├──► head_graph (usually unchanged)
    │
    └──► body_graph.mgraph ◄── TRANSFORM HERE (Phase D)
              │
              ▼
    MGraph_Transformer__Body__Unwrap_Inline
              │
              ▼
    MGraph_Transformer__Body__Merge_Text
              │
              ▼
    ... (chain as needed)
              │
              ▼
    Modified body_graph (same object, modified in-place)
              │
              ▼
Html_MGraph__Document (with modified body)
    │
    ▼ (Already exists)
Html_MGraph__Document__To__Html
    │
    ▼
Clean HTML String
```

### Key Insight: In-Place Modification

The `body_graph` retrieved from `Html_MGraph__Document` is the **same object reference** used by `Html_MGraph__Document__To__Html`. This means:

```python
# Get body graph (same object!)
body_graph = doc.body_graph.mgraph

# Transform in-place
transformer.transform(body_graph)

# Convert to HTML (uses the already-modified graph)
html = Html_MGraph__Document__To__Html().convert(doc)
```

No need to "put the graph back" - modifications propagate automatically.

---

## MGraph Body Structure

### Node Types

**Element Nodes:**
```python
{
    'node_id': 'c0000023',
    'node_path': 'body.div',       # Tag path
    'node_data': {}                # Empty for elements
}
```

**Text Nodes:**
```python
{
    'node_id': 'c0000027',
    'node_path': 'text',
    'node_data': {
        'value': 'Hello World',
        'key': 'c0000025:0',
        'value_type': 'builtins.str'
    }
}
```

### Edge Predicates

| Predicate | Meaning |
|-----------|---------|
| `child` | Parent element → Child element |
| `text` | Element → Text content |

### Identifying Element Types

Extract tag from `node_path`:
```python
'body.div'        → 'div'
'body.div.p'      → 'p'
'body.div[0].a'   → 'a'
'body.div.b'      → 'b'
```

---

## Transformer Design

### Base Class

```python
class MGraph_Transformer__Body__Base(Type_Safe):
    """Base class for body graph transformations.
    
    Transformers operate in-place on the MGraph and return
    the same graph reference for chaining.
    """
    
    def transform(self, body_graph: MGraph) -> MGraph:
        """Apply transformation in-place, return same graph for chaining."""
        raise NotImplementedError
    
    # ═══════════════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════════════
    
    def get_node_tag(self, node_path: str) -> str:
        """Extract tag from node_path: 'body.div.a' → 'a'"""
        if not node_path:
            return ''
        last_part = node_path.split('.')[-1]
        return last_part.split('[')[0]  # Handle 'div[0]' → 'div'
    
    def is_text_node(self, domain_node) -> bool:
        """Check if node is a text node."""
        return str(domain_node.node.data.node_path) == 'text'
    
    def get_text_value(self, domain_node) -> str:
        """Get text value from text node."""
        node_data = domain_node.node.data.node_data
        if node_data and hasattr(node_data, 'value'):
            return str(node_data.value) if node_data.value else ''
        return ''
    
    def get_parent_node(self, mgraph: MGraph, node_id: str):
        """Find parent node via incoming 'child' edge."""
        # Implementation using mgraph.index() or edge traversal
        ...
    
    def get_child_edges(self, mgraph: MGraph, node_id: str) -> list:
        """Get all outgoing edges (child or text) from a node."""
        ...
```

### Pipeline Class

```python
class MGraph_Transformer__Body__Pipeline(Type_Safe):
    """Chain multiple body transformers."""
    
    transformers: List[MGraph_Transformer__Body__Base] = []
    
    def transform(self, body_graph: MGraph) -> MGraph:
        """Apply all transformers in sequence."""
        for transformer in self.transformers:
            transformer.transform(body_graph)
        return body_graph
    
    def add(self, transformer: MGraph_Transformer__Body__Base) -> 'MGraph_Transformer__Body__Pipeline':
        """Add transformer to pipeline, return self for chaining."""
        self.transformers.append(transformer)
        return self
```

---

## Transformers to Implement

### 1. MGraph_Transformer__Body__Unwrap_Inline

**Purpose**: Remove inline wrapper elements (`<a>`, `<b>`, `<i>`, `<span>`, etc.) while keeping their children.

**Configuration**:
```python
class MGraph_Transformer__Body__Unwrap_Inline(MGraph_Transformer__Body__Base):
    
    inline_tags: List[str] = ['a', 'b', 'i', 'span', 'strong', 'em', 'u', 's', 'mark', 'small', 'sub', 'sup']
```

**Operation**:
```
BEFORE:                              AFTER:
parent ──child──► <a> ──text──► "link"    parent ──text──► "link"
```

**MGraph Steps**:
1. Find nodes where `get_node_tag(node_path)` is in `inline_tags`
2. For each inline node:
   - Get parent via incoming `child` edge
   - Get children via outgoing edges (`child` or `text`)
   - Delete edge: parent → inline
   - Delete edges: inline → children
   - Create new edges: parent → children (preserve predicate)
   - Delete the inline node

### 2. MGraph_Transformer__Body__Merge_Text

**Purpose**: Combine adjacent text nodes under the same parent into a single text node.

**Operation**:
```
BEFORE:                              AFTER:
parent ──text──► "Hello "            parent ──text──► "Hello World!"
       ──text──► "World!"
```

**MGraph Steps**:
1. For each element node with multiple `text` edges:
   - Collect all text children (preserving order via edge_path)
   - Concatenate values
   - Keep first text node, update its value
   - Delete other text nodes and their edges

### 3. MGraph_Transformer__Body__Remove_Empty_Text

**Purpose**: Delete text nodes that contain only whitespace.

**Configuration**:
```python
class MGraph_Transformer__Body__Remove_Empty_Text(MGraph_Transformer__Body__Base):
    
    preserve_single_space: bool = False  # If True, keep nodes with exactly one space
```

### 4. MGraph_Transformer__Body__Collapse_Single_Child

**Purpose**: Remove wrapper elements that have only one child element (no text).

**Operation**:
```
BEFORE:                              AFTER:
grandparent ──child──► wrapper ──child──► child    grandparent ──child──► child
```

### 5. MGraph_Transformer__Body__Remove_By_Tag

**Purpose**: Remove all elements with specific tags (e.g., `<script>`, `<style>`, `<nav>`).

**Configuration**:
```python
class MGraph_Transformer__Body__Remove_By_Tag(MGraph_Transformer__Body__Base):
    
    tags_to_remove: List[str] = []
    remove_children: bool = True  # If False, children move to parent
```

---

## Usage Examples

### Basic Transformation

```python
from Html__To__Html_Dict__With__Node_Ids            import Html__To__Html_Dict__With__Node_Ids
from Html__To__Html_MGraph__Document__Node_Id_Reuse import Html__To__Html_MGraph__Document__Node_Id_Reuse
from Html_MGraph__Document__To__Html                import Html_MGraph__Document__To__Html

# Input
html = "<div>Hello <b>World</b>!</div>"

# Phase A + B: HTML → MGraph
html_dict = Html__To__Html_Dict__With__Node_Ids(html).convert()
doc = Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(html_dict)

# Phase D: Transform body graph
body = doc.body_graph.mgraph
MGraph_Transformer__Body__Unwrap_Inline().transform(body)
MGraph_Transformer__Body__Merge_Text().transform(body)

# Convert back to HTML
clean_html = Html_MGraph__Document__To__Html().convert(doc)
# Result: "<div>Hello World!</div>"
```

### Using Pipeline

```python
pipeline = MGraph_Transformer__Body__Pipeline(
    transformers = [ MGraph_Transformer__Body__Remove_By_Tag(tags_to_remove=['script', 'style']),
                     MGraph_Transformer__Body__Unwrap_Inline()                                   ,
                     MGraph_Transformer__Body__Merge_Text()                                      ,
                     MGraph_Transformer__Body__Remove_Empty_Text()                               ]
)

body = doc.body_graph.mgraph
pipeline.transform(body)

clean_html = Html_MGraph__Document__To__Html().convert(doc)
```

### Fluent Pipeline Building

```python
pipeline = (MGraph_Transformer__Body__Pipeline()
    .add(MGraph_Transformer__Body__Remove_By_Tag(tags_to_remove=['nav', 'footer']))
    .add(MGraph_Transformer__Body__Unwrap_Inline())
    .add(MGraph_Transformer__Body__Merge_Text()))

pipeline.transform(doc.body_graph.mgraph)
```

---

## Test Plan

### Unit Tests (per transformer)

| Test | Description |
|------|-------------|
| `test__unwrap_inline__single_element` | Unwrap single `<b>` |
| `test__unwrap_inline__nested_inline` | Unwrap `<a><b>text</b></a>` |
| `test__unwrap_inline__preserves_non_inline` | `<div>` not unwrapped |
| `test__unwrap_inline__multiple_children` | Element with multiple children |
| `test__merge_text__two_adjacent` | Merge two text nodes |
| `test__merge_text__three_adjacent` | Merge three text nodes |
| `test__merge_text__preserves_separate` | Different parents not merged |
| `test__remove_empty__whitespace_only` | Remove whitespace nodes |
| `test__remove_by_tag__removes_with_children` | Remove `<script>` and contents |
| `test__pipeline__chains_correctly` | Multiple transformers in sequence |

### Integration Tests (full roundtrip)

| Test | Description |
|------|-------------|
| `test__roundtrip__simple_html` | HTML → Transform → HTML |
| `test__roundtrip__preserves_structure` | Non-transformed elements intact |
| `test__roundtrip__complex_nested` | Nested structure with multiple transforms |

---

## Files to Create

| File | Description |
|------|-------------|
| `MGraph_Transformer__Body__Base.py` | Base class with helpers |
| `MGraph_Transformer__Body__Unwrap_Inline.py` | Unwrap inline elements |
| `MGraph_Transformer__Body__Merge_Text.py` | Merge adjacent text |
| `MGraph_Transformer__Body__Remove_Empty_Text.py` | Remove whitespace text |
| `MGraph_Transformer__Body__Collapse_Single_Child.py` | Collapse wrappers |
| `MGraph_Transformer__Body__Remove_By_Tag.py` | Remove elements by tag |
| `MGraph_Transformer__Body__Pipeline.py` | Chain transformers |
| `test_MGraph_Transformer__Body__*.py` | Tests for each |
| `Phase_D__Test_Data_Generator.py` | Generate fixtures for Phase E |

### File Location

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
            ├── MGraph_Transformer__Body__Collapse_Single_Child.py
            ├── MGraph_Transformer__Body__Remove_By_Tag.py
            └── MGraph_Transformer__Body__Pipeline.py
```

---

## Dependencies

- `MGraph` from `mgraph_db.mgraph.MGraph`
- `Type_Safe` from `osbot_utils.type_safe.Type_Safe`
- Phase A: `Html__To__Html_Dict__With__Node_Ids`
- Phase B: `Html__To__Html_MGraph__Document__Node_Id_Reuse`
- Existing: `Html_MGraph__Document__To__Html`

---

## Success Criteria

1. ✅ Each transformer is single-responsibility
2. ✅ Transformers work in-place on MGraph
3. ✅ Full roundtrip produces correct HTML
4. ✅ Pipeline chains transformers correctly
5. ✅ Node_ids preserved through transformation
6. ✅ All tests pass

---

## Out of Scope (Future Phases)

- Web fetching (moved to later phase)
- Source tracking/mapping (Phase C already handles if needed)
- Text classification (Phase F)
- LLM integration

---

## Next Steps

1. Implement `MGraph_Transformer__Body__Base` with helper methods
2. Implement `MGraph_Transformer__Body__Unwrap_Inline` (most complex)
3. Write tests, validate roundtrip works
4. Implement remaining transformers
5. Create `Phase_D__Test_Data_Generator` for Phase E
6. Write `PHASE_D__debrief.md`
