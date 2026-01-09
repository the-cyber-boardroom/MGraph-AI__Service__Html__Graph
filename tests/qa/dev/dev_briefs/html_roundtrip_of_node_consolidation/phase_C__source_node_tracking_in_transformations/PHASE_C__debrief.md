# Phase C Debrief: Source Node Tracking in Transformations

**Date**: January 9, 2026  
**Status**: ✅ Complete  
**Tests**: 15/15 passing

---

## Executive Summary

Phase C adds source tracking to the HTML flatten transformation, enabling reverse operations on the original HTML. The key achievement is a **complete end-to-end pipeline** that:

1. Parses HTML with node_id tracking (Phase A)
2. Converts to MGraph preserving node_ids (Phase B)
3. Transforms with source tracking (Phase C)
4. Applies reverse operations to produce clean HTML

### The Proof

**Input:**
```html
<!DOCTYPE html>
<html>
    <body>
        <div>
            This is a <a href="">link</a> with some <b>bold</b> in the mix
        </div>
        <div>
            this is the <i>2nd div</i> in here
        </div>
    </body>
</html>
```

**Output:**
```html
<html><body><div>
            This is a link with some bold in the mix
        </div><div>
            this is the 2nd div in here
        </div></body></html>
```

---

## Architecture Decisions

### 1. Subclass Pattern (Minimal Core Changes)

Rather than modifying `Html_Use_Case__3`, we created a subclass:

```
Html_Use_Case__3 (Base - unchanged)
    │
    └──► Html_Use_Case__3__Source_Tracking (Subclass)
              ├── Adds: source_mapping, wrapper_mapping
              ├── Overrides: transform_mgraph() → Reset + super()
              ├── Overrides: step_1___add_shortcut_edges() → Track wrappers
              └── Overrides: step_3___merge_text_nodes() → Track sources
```

**Benefits:**
- Zero changes to production code
- Can use base class when tracking not needed
- Easy rollback (delete 2 files)
- Clear separation of concerns

### 2. Phase Independence via JSON Fixtures

Phase C tests run **without importing Phase A or Phase B classes**. Instead:

```
Phase B Environment                     Phase C Environment
┌─────────────────────┐                ┌─────────────────────┐
│ Phase_B__Test_Data_ │                │ Phase_C__Test_      │
│ Generator.py        │ ──generates──► │ Fixtures.py         │
│                     │   JSON files   │ (loads JSON)        │
└─────────────────────┘                └─────────────────────┘
```

This allows:
- Independent testing of each phase
- No circular dependencies
- Clear phase boundaries
- Reproducible test fixtures

### 3. Deterministic IDs for Testing

Using `graph_deterministic_ids()` context manager:

```python
for name, html in HTML_SAMPLES.items():
    with graph_deterministic_ids():
        fixture = generate_test_fixture(html, name)
```

Produces predictable IDs like `f0000001`, `f0000002` instead of random UUIDs - much easier to debug and validate.

---

## Files Created

### Phase B Utilities

| File | Purpose |
|------|---------|
| `Phase_B__Test_Data_Generator.py` | Generates JSON fixtures from HTML samples |
| `test_Phase_B__Test_Data_Generator.py` | Tests for generator (20 tests) |

### Phase C Core

| File | Purpose |
|------|---------|
| `Html_Use_Case__3__Source_Tracking.py` | Subclass with tracking |
| `Html_Dict__Helpers.py` | Utility functions for Html_Dict manipulation |
| `test_Html_Use_Case__3__Source_Tracking.py` | Unit tests |
| `test_Html_Dict__Helpers.py` | Helper function tests |

### Phase C Fixture System

| File | Purpose |
|------|---------|
| `Phase_C__Test_Fixtures.py` | Loads fixture__*.json files |
| `Phase_C__Test_Data_Loader.py` | Reconstructs MGraph from JSON |
| `test_Phase_C__Test_Fixtures.py` | Tests for fixture loading |
| `test_Phase_C__Test_Data_Loader.py` | Tests for MGraph reconstruction |
| `fixture__simple.json` | Test fixture (generated) |
| `fixture__multiple_wrappers.json` | Test fixture (generated) |
| `fixture__nested_structure.json` | Test fixture (generated) |

### Integration Tests

| File | Purpose |
|------|---------|
| `test_Phase_C__Full_Pipeline_Integration.py` | End-to-end pipeline tests (15 tests) |

---

## Key Learnings & Bugs Fixed

### 1. MGraph JSON Format Mismatch

**Problem:** Phase B generator used compressed JSON, Phase C loader expected full JSON.

**Symptom:**
```python
mgraph_node_ids = collect_node_ids_from_mgraph(mgraph)
assert len(mgraph_node_ids) == 0  # Empty! Where did nodes go?
```

**Root Cause:**
```python
# Compressed format (wrong)
"edge_type": "@schema_mgraph_edge"

# Full format (correct)
"edge_type": "mgraph_db.mgraph.schemas.Schema__MGraph__Edge.Schema__MGraph__Edge"
```

**Fix:**
```python
# Before (compressed)
body_graph_json = doc.body_graph.to_json()

# After (full)
body_graph_json = doc.body_graph.mgraph.json()
```

**Loader simplification:**
```python
# Before - 50+ lines of manual reconstruction
def load_mgraph_from_json(graph_json: dict) -> MGraph:
    mgraph = MGraph()
    # ... complex manual node/edge creation
    return mgraph

# After - one line
def load_mgraph_from_json(graph_json: dict) -> MGraph:
    return MGraph.from_json(graph_json)
```

### 2. mgraph.copy() Doesn't Exist

**Problem:** Tests called `mgraph.copy()` which doesn't exist.

**Solution:** Remove the call - the loaded MGraph is already a new object. If copy is truly needed:
```python
MGraph.from_json(mgraph.json())
```

### 3. Substring Match Bug

**Problem:** Test assertion `'<b' not in output_html.lower()` was catching `<body>`.

**Solution:** Remove that assertion or use more specific matching:
```python
# Bad - catches <body>
assert '<b' not in output_html.lower()

# Good - removed, rely on other assertions
assert '<a'  not in output_html.lower()
assert '<i'  not in output_html.lower()
```

### 4. Placeholder IDs in Tests

**Problem:** Initial fixtures used `PLACEHOLDER_*` IDs which aren't valid `Obj_Id` values.

**Solution:** Generate real fixtures from Phase B with deterministic IDs:
```python
assert dict_node_ids == {'f0000001', 'f0000002', ...}
assert dict_node_ids != {'PLACEHOLDER_html_001', ...}  # Old invalid format
```

---

## Tracking Data Structures

### wrapper_mapping

Tracks inline elements that were unwrapped:

```python
wrapper_mapping = {
    'f0000005': {  # <a> element node_id
        'parent_id': 'f0000003',  # <p> parent
        'child_id': 'f0000006'    # text inside <a>
    },
    'f0000007': {  # <b> element node_id
        'parent_id': 'f0000003',
        'child_id': 'f0000008'
    }
}
```

### source_mapping

Tracks which original text nodes merged into new nodes:

```python
source_mapping = {
    'f0000020': [  # merged text node_id
        'f0000004',  # "Start "
        'f0000006',  # "link"
        'f0000009',  # " middle "
        'f0000008',  # "bold"
        'f0000010'   # " end"
    ]
}
```

---

## Html_Dict Helper Functions

Created reusable utilities for Html_Dict manipulation:

```python
from Html_Dict__Helpers import (
    find_node_by_id,              # Find node by node_id → (node, parent, index)
    unwrap_element_in_dict,       # Remove wrapper, keep children
    delete_node_by_id,            # Delete node entirely
    merge_adjacent_text_nodes,    # Combine adjacent TEXT nodes
    collect_node_ids,             # Get all node_ids in tree
    html_dict_to_html,            # Convert back to HTML string
    unwrap_all_inline_elements,   # Unwrap all from wrapper_mapping
    clean_html_from_tracking      # Full workflow in one call
)
```

---

## Test Coverage Summary

### By Category

| Category | Tests | Status |
|----------|-------|--------|
| Node_Id Flow (Tests 1-1d) | 4 | ✅ |
| Wrapper Mapping (Tests 2-2c) | 3 | ✅ |
| Source Mapping (Tests 3-3c) | 3 | ✅ |
| Traceability (Tests 4-4b) | 2 | ✅ |
| Unwrap Workflow (Tests 5-5c) | 3 | ✅ |
| **Total** | **15** | **✅** |

### By File

| Test File | Tests | Status |
|-----------|-------|--------|
| test_Html_Dict__Helpers.py | 20+ | ✅ |
| test_Html_Use_Case__3__Source_Tracking.py | ~10 | ✅ |
| test_Phase_C__Test_Fixtures.py | ~30 | ✅ |
| test_Phase_C__Test_Data_Loader.py | ~25 | ✅ |
| test_Phase_C__Full_Pipeline_Integration.py | 15 | ✅ |

---

## Workflow: Generating and Using Fixtures

### Step 1: Generate in Phase B

```bash
cd phase_B__reuse_node_ids_from_html_dict
python Phase_B__Test_Data_Generator.py

# Output:
# Generated: fixture__simple.json
# Generated: fixture__multiple_wrappers.json
# Generated: fixture__nested_structure.json
```

### Step 2: Copy to Phase C

```bash
cp fixture__*.json ../phase_C__source_node_tracking_in_transformations/
```

### Step 3: Run Phase C Tests

```bash
cd ../phase_C__source_node_tracking_in_transformations
pytest

# All tests pass!
```

### Diagnostic Helper

```python
from Phase_C__Test_Fixtures import print_fixtures_status

print_fixtures_status()
# Fixtures Directory: /path/to/phase_C
# Loaded Fixtures: ['simple', 'multiple_wrappers', 'nested_structure']
# 
# File Status:
#   ✓ simple: fixture__simple.json
#   ✓ multiple_wrappers: fixture__multiple_wrappers.json
#   ✓ nested_structure: fixture__nested_structure.json
```

---

## Full Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│ INPUT: "<div>This is a <a>link</a> with some <b>bold</b></div>"         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE A: Html__To__Html_Dict__With__Node_Ids                            │
│ • Parse HTML to dict structure                                          │
│ • Assign unique node_id to every node                                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE B: Html__To__Html_MGraph__Document__Node_Id_Reuse                 │
│ • Convert dict to MGraph                                                │
│ • Preserve node_ids from dict                                           │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
              ┌─────────────────────┴─────────────────────┐
              ▼                                           ▼
┌──────────────────────────────┐           ┌──────────────────────────────┐
│ PHASE C: Transform + Track   │           │ KEEP: Original Html_Dict     │
│ • Flatten structure          │           │ (unchanged, with node_ids)   │
│ • Track wrapper_mapping      │           │                              │
│ • Track source_mapping       │           │                              │
└──────────────────────────────┘           └──────────────────────────────┘
              │                                           │
              └─────────────────────┬─────────────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ REVERSE: Apply wrapper_mapping to Html_Dict                             │
│ • For each wrapper_id: unwrap_element_in_dict()                         │
│ • merge_adjacent_text_nodes()                                           │
│ • html_dict_to_html()                                                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ OUTPUT: "<div>This is a link with some bold</div>"                      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Next Steps

1. **Phase D** ✅ - Web Fetching (already complete)
2. **Phase E** - Formalize reverse operations into proper classes
3. **Phase F** - Text Classification Pipeline

---

## Key Takeaways

1. **Subclass pattern works beautifully** - Add functionality without touching core code
2. **Phase independence via fixtures** - JSON serialization enables clean phase boundaries
3. **Deterministic IDs are essential** - Makes debugging and testing much easier
4. **Full JSON format required** - Compressed JSON loses type information for deserialization
5. **MGraph.from_json() is the right tool** - Don't manually reconstruct, use the built-in method
6. **Test assertions need care** - Substring matches can have unintended consequences (`<b` vs `<body>`)
