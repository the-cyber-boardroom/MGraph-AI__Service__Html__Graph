# Phase B: MGraph Integration - Reuse Node_Ids from Html_Dict

**Status**: ✅ Complete  
**Depends On**: Phase A (Html_Dict Node_Id Assignment) ✅

---

## Objective

> Create a subclass of `Html__To__Html_MGraph__Document` that reuses `node_id` values from the Html_Dict when present, ensuring the same Node_Ids flow through the entire pipeline.

---

## Implementation Approach: Subclassing (No Core Modification)

**Key Decision**: Rather than modifying `Html__To__Html_MGraph__Document` directly, we created a subclass `Html__To__Html_MGraph__Document__Node_Id_Reuse`. This allows:

- ✅ No changes to production code during experimentation
- ✅ Clean separation of concerns
- ✅ Easy rollback if needed
- ✅ Can promote to base class later if proven

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    INHERITANCE HIERARCHY                                 │
└─────────────────────────────────────────────────────────────────────────┘

Html__To__Html_MGraph__Document                    (Base - UNCHANGED)
    │
    └──► Html__To__Html_MGraph__Document__Node_Id_Reuse   (New Subclass)
              │
              ├── Overrides: _generate_node_id()
              ├── Overrides: convert()               → Uses Node_Id-aware parser
              ├── Overrides: _process_head()         → Passes dict to _generate_node_id
              ├── Overrides: _process_head_children()
              ├── Overrides: _process_body()
              ├── Overrides: _process_body__text_node()
              └── Overrides: _process_body__element()
              
              Inherits (unchanged):
              ├── _process_body_children()           → Calls overridden methods
              ├── _process_body__create_in_graph()
              ├── _process_body__register_attrs()
              └── _process_body__handle_script()
```

---

## Core Changes

### 1. `_generate_node_id()` - The Key Override

```python
def _generate_node_id(self, node_dict: Dict[str, Any] = None) -> Node_Id:
    if node_dict and STRING__NODE_ID in node_dict:
        return Node_Id(node_dict[STRING__NODE_ID])      # Reuse from dict
    return super()._generate_node_id()                  # Fallback to base behavior
```

### 2. `convert()` - Uses Node_Id-Aware Parser

```python
def convert(self, html: str) -> Html_MGraph__Document:
    html_dict = Html__To__Html_Dict__With__Node_Ids(html=html).convert()  # Node_Id parser
    return self.convert_from_dict(html_dict)
```

### 3. Processing Methods - Pass Dict to `_generate_node_id()`

```python
def _process_head(self, document, head_dict):
    head_node_id = self._generate_node_id(head_dict)    # Pass dict
    # ... rest uses head_node_id

def _process_body__text_node(self, document, parent_id, node, position):
    text = node.get('data', '')
    if text.strip():
        node_id = self._generate_node_id(node)          # Pass dict
        document.body_graph.create_text(text=text, parent_id=parent_id,
                                        position=position, node_id=node_id)
```

---

## Dependency: `create_text()` Bug Fix

The graph's `create_text()` method needed to accept an optional `node_id` parameter.

**Before** (always generated):
```python
def create_text(self, text: str, parent_id: Node_Id, position: int) -> Node_Id:
    node_id = Node_Id(Obj_Id())  # Always generates
```

**After** (optional override):
```python
@type_safe
def create_text(self, text      : str            ,
                      parent_id : Node_Id        ,
                      position  : int     = 0    ,
                      node_id   : Node_Id = None ) -> Node_Id:
    if node_id is None:
        node_id = Node_Id(Obj_Id())               # Generate if not provided
```

This was the **only change to core code** - a backward-compatible enhancement.

---

## Files Created/Modified

| File | Type | Description |
|------|------|-------------|
| `Html__To__Html_MGraph__Document__Node_Id_Reuse.py` | **New** | Subclass with node_id reuse |
| `test_Html__To__Html_MGraph__Document__Node_Id_Reuse.py` | **New** | Comprehensive tests |
| `Html_MGraph__Body.create_text()` | **Bug Fix** | Added optional `node_id` param |

---

## Test Coverage

### Unit Tests
- `test__generate_node_id__reuses_from_dict` - Reuses when present
- `test__generate_node_id__generates_when_missing` - Generates when absent
- `test__generate_node_id__generates_when_none` - Handles None
- `test__generate_node_id__generates_when_empty_dict` - Handles {}

### Integration Tests
- `test_convert_from_dict__reuses_head_node_id`
- `test_convert_from_dict__reuses_body_node_id`
- `test_convert_from_dict__reuses_element_node_id`
- `test_convert_from_dict__reuses_text_node_id`

### Backward Compatibility
- `test_convert_from_dict__backward_compatible_no_node_ids`
- `test_convert__backward_compatible`

### Mixed Scenarios
- `test_convert_from_dict__mixed_node_ids` - Some present, some missing

### End-to-End
- `test_full_pipeline__html_to_dict_with_node_ids_to_mgraph`
- `test_full_pipeline__node_ids_shared_across_graphs`
- `test_convert_from_dict__deep_nesting_preserves_node_ids`

---

## Usage

```python
# Option 1: Full pipeline (HTML string)
doc = Html__To__Html_MGraph__Document__Node_Id_Reuse().convert(html)

# Option 2: From pre-parsed dict with node_ids
html_dict = Html__To__Html_Dict__With__Node_Ids(html).convert()
doc = Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(html_dict)

# Node_ids are now preserved throughout!
```

---

## Key Insight: Polymorphism at Work

The base class's `_process_body_children()` iterates through nodes and calls:
- `_process_body__text_node()` for text nodes
- `_process_body__element()` for element nodes

Since we override these methods in our subclass, Python's method resolution ensures our versions are called, even when invoked from the inherited `_process_body_children()`.

```
Base._process_body_children()
    │
    ├──► calls self._process_body__text_node()
    │         └──► Subclass._process_body__text_node() ← Our override!
    │
    └──► calls self._process_body__element()
              └──► Subclass._process_body__element() ← Our override!
```

---

## Next Steps

1. ✅ Phase A: Html_Dict Node_Id Assignment
2. ✅ Phase B: MGraph Integration (this phase)
3. ✅ Phase C: Source Tracking in Transformations
4. ✅ Phase D: Web Page Fetching
5. ⏳ Phase E: Reverse Mapping Operations