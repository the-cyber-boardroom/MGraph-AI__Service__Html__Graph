# Phase C: Source Node Tracking in Transformations

**Status**: ✅ Complete  
**Depends On**: Phase A ✅, Phase B ✅

---

## Objective

> Add source tracking to the flatten transformation so we can trace merged nodes back to original source node_ids, enabling reverse operations (delete, highlight, unwrap) on the original HTML.

---

## The Problem

When we flatten HTML like this:
```html
<div>This is a <a href="">link</a> with some <b>bold</b> in the mix</div>
```

The transformation merges text nodes:
```
Before: div → [TEXT, a→TEXT, TEXT, b→TEXT, TEXT]  (5 text nodes)
After:  div → [TEXT "This is a link with some bold in the mix"]  (1 merged node)
```

**Question**: How do we get back to the original structure to produce clean HTML?

**Answer**: Track which original node_ids were merged, then use that mapping to modify the original `Html_Dict`.

---

## Implementation: Subclass Pattern (Minimal Overrides)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    INHERITANCE HIERARCHY                                 │
└─────────────────────────────────────────────────────────────────────────┘

Html_Use_Case__3                                   (Base - 4-step transform)
    │
    └──► Html_Use_Case__3__Source_Tracking              (Subclass - adds tracking)
              │
              ├── Adds: source_mapping, wrapper_mapping attributes
              ├── Overrides: transform_mgraph()         → Reset mappings + super()
              ├── Overrides: step_1___add_shortcut_edges() → Track wrapper info
              ├── Overrides: step_3___merge_text_nodes()   → Track source node_ids
              └── Adds: Query methods (get_source_node_ids, etc.)
              
              Inherits (unchanged):
              ├── step_2___remove_wrapper_nodes()
              ├── step_4___collapse_single_parents()
              ├── update_node_labels()
              ├── create_dot_code()
              └── All utility methods
```

---

## Tracking Data Structures

### `wrapper_mapping`: Inline Element Tracking
```python
wrapper_mapping = {
    'a_node_id_001': {
        'parent_id': 'div_node_id',
        'child_id' : 'text_node_id_inside_a'
    },
    'b_node_id_002': {
        'parent_id': 'div_node_id', 
        'child_id' : 'text_node_id_inside_b'
    }
}
```

**Use Case**: Find and unwrap inline elements (`<a>`, `<b>`, `<i>`, etc.) in original Html_Dict.

### `source_mapping`: Merged Text Node Tracking
```python
source_mapping = {
    'merged_text_001': [
        'text_001',  # "This is a "
        'text_002',  # "link"
        'text_003',  # " with some "
        'text_004',  # "bold"
        'text_005'   # " in the mix"
    ]
}
```

**Use Case**: Know which original text nodes contributed to a merged node.

---

## Full Pipeline Workflow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    COMPLETE WORKFLOW                                     │
└─────────────────────────────────────────────────────────────────────────┘

INPUT HTML
    │
    ▼
┌─────────────────────────────────────┐
│ Phase A: Html__To__Html_Dict__With__Node_Ids │
│ - Parse HTML                         │
│ - Assign unique node_id to every node │
└─────────────────────────────────────┘
    │
    ▼
Html_Dict (with node_ids)
    │
    ▼
┌─────────────────────────────────────┐
│ Phase B: Html__To__Html_MGraph__Document__Node_Id_Reuse │
│ - Convert to MGraph                  │
│ - Preserve node_ids from dict        │
└─────────────────────────────────────┘
    │
    ▼
MGraph Document (same node_ids)
    │
    ├──────────────────────────────────┐
    │                                  │
    ▼                                  ▼
┌─────────────────────────────────────┐  ┌────────────────────────────┐
│ Phase C: Html_Use_Case__3__Source_Tracking │  │ Keep Original Html_Dict  │
│ - Transform copy of body_graph       │  │ (unchanged, with node_ids) │
│ - Track wrapper_mapping              │  │                            │
│ - Track source_mapping               │  │                            │
└─────────────────────────────────────┘  └────────────────────────────┘
    │                                           │
    ▼                                           │
Flattened Graph + Tracking Data                 │
    │                                           │
    ▼                                           │
┌─────────────────────────────────────┐         │
│ Use wrapper_mapping to find          │         │
│ inline elements (a, b, i, etc.)      │─────────┤
└─────────────────────────────────────┘         │
    │                                           │
    ▼                                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Phase E (Preview): Unwrap elements in original Html_Dict                │
│ - For each wrapper_id in wrapper_mapping                                │
│ - Find wrapper in Html_Dict by node_id                                  │
│ - Replace wrapper with its children (unwrap)                            │
│ - Merge adjacent text nodes                                             │
└─────────────────────────────────────────────────────────────────────────┘
    │
    ▼
Modified Html_Dict (inline tags removed)
    │
    ▼
┌─────────────────────────────────────┐
│ Html_Dict__To__Html                  │
│ - Convert back to HTML string        │
└─────────────────────────────────────┘
    │
    ▼
CLEAN OUTPUT HTML
```

---

## Code Example: Full Workflow

```python
# ═══════════════════════════════════════════════════════════════════════════
# Input
# ═══════════════════════════════════════════════════════════════════════════

html = "<div>This is a <a href=''>link</a> with some <b>bold</b> in the mix</div>"

# ═══════════════════════════════════════════════════════════════════════════
# Phase A: Parse with node_ids
# ═══════════════════════════════════════════════════════════════════════════

html_dict = Html__To__Html_Dict__With__Node_Ids(html=html).convert()

# ═══════════════════════════════════════════════════════════════════════════
# Phase B: Convert to MGraph (preserves node_ids)
# ═══════════════════════════════════════════════════════════════════════════

doc = Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(html_dict)

# ═══════════════════════════════════════════════════════════════════════════
# Phase C: Transform with tracking
# ═══════════════════════════════════════════════════════════════════════════

transformer = Html_Use_Case__3__Source_Tracking()
flat_graph = transformer.transform_mgraph(doc.body_graph.graph.copy())

# Get tracking data
wrapper_mapping = transformer.get_all_wrapper_mappings()
source_mapping  = transformer.get_all_source_mappings()

print(f"Wrappers found: {len(wrapper_mapping)}")    # 2 (a, b)
print(f"Merged nodes: {len(source_mapping)}")       # 1

# ═══════════════════════════════════════════════════════════════════════════
# Phase E Preview: Unwrap elements in original Html_Dict
# ═══════════════════════════════════════════════════════════════════════════

for wrapper_id in wrapper_mapping.keys():
    unwrap_element_in_dict(html_dict, wrapper_id)

merge_adjacent_text_nodes(html_dict)

# ═══════════════════════════════════════════════════════════════════════════
# Output
# ═══════════════════════════════════════════════════════════════════════════

clean_html = html_dict_to_html(html_dict)
# Result: "<div>This is a link with some bold in the mix</div>"
```

---

## Test Coverage

### Test 1: Node_Id Flow (Phase A → B → C)
- Verify node_ids from Html_Dict appear in MGraph
- Verify node_ids in tracking data match original dict

### Test 2: Wrapper Mapping
- `wrapper_mapping` captures inline elements (`<a>`, `<b>`, `<i>`)
- Each entry has `parent_id` and `child_id`
- wrapper_ids are findable in original Html_Dict

### Test 3: Source Mapping
- `source_mapping` captures merged text node origins
- Each merged node has 2+ source node_ids
- source_ids are findable in original Html_Dict

### Test 4: Traceability
- Can locate wrapper elements in Html_Dict by node_id
- Can locate source text nodes in Html_Dict by node_id

### Test 5: Unwrap Workflow (Phase E Preview)
- Unwrapping single element preserves children
- Unwrapping multiple elements produces clean HTML
- Full workflow with nested structure works end-to-end

---

## Files

| File | Description |
|------|-------------|
| `Html_Use_Case__3__Source_Tracking.py` | Subclass with tracking |
| `test_Html_Use_Case__3__Source_Tracking.py` | Unit tests |
| `test_Html_Use_Case__3__Flatten__Source_Tracking__Integration.py` | MGraph integration tests |
| `test_Phase_C__Full_Pipeline_Integration.py` | Full pipeline tests (A→B→C→E) |

---

## Key Design Decisions

### 1. Subclass, Don't Modify
- Base `Html_Use_Case__3` unchanged
- Tracking added via subclass with minimal overrides
- Can use base class when tracking not needed

### 2. Track at the Right Moment
- `wrapper_mapping`: Populated in step_1 before wrappers removed
- `source_mapping`: Populated in step_3 before text nodes deleted

### 3. Use node_ids as Keys
- All tracking uses string node_ids
- Enables lookup in any structure (dict, MGraph, etc.)

### 4. Keep Original Html_Dict
- Transform operates on MGraph copy
- Original Html_Dict preserved for modifications
- Tracking bridges the two

---

## Next Steps

1. ✅ Phase A: Html_Dict Node_Id Assignment
2. ✅ Phase B: MGraph Integration  
3. ✅ Phase C: Source Tracking (this phase)
4. ✅ Phase D: Web Fetching
5. ⏳ Phase E: Reverse Mapping Operations (formalize unwrap helpers)
6. ⏳ Phase F: Text Classification Pipeline