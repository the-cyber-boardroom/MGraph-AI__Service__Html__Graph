# Phase E Debrief: Virtual Merge and Selective Delete

**Date**: January 2026  
**Status**: ✅ Complete  
**Tests**: All passing

---

## Executive Summary

Phase E implements a **read-only analysis + surgical delete** approach for HTML content filtering:

1. Extract text nodes with parent references
2. Virtually compute merged text per parent (no graph modification)
3. Make keep/discard decisions via pluggable engine
4. Delete unwanted parent nodes from original graph
5. Rebuild clean HTML

**Key Insight**: We never actually merge the graph - we compute what merged text *would be*, make decisions on that virtual result, then delete from the original unmodified graph.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PHASE E WORKFLOW                                          │
└─────────────────────────────────────────────────────────────────────────────┘

HTML String
    │
    ▼ (Phase A + B)
Html__To__Html_Dict__With__Node_Ids + Html__To__Html_MGraph__Document__Node_Id_Reuse
    │
    ▼
Html_MGraph__Document (with node_ids preserved)
    │
    ├──────────────────────────────────────────────────────────────────┐
    │                                                                  │
    ▼                                                                  │
Phase_E__Text_Extractor                                                │
    │                                                                  │
    │  { node_id: TextNodeInfo(text, parent_id) }                     │
    │                                                                  │
    ▼                                                                  │
Phase_E__Virtual_Merger (READ-ONLY)                                    │
    │                                                                  │
    │  { parent_id: MergedTextInfo(merged_text, source_node_ids) }    │
    │                                                                  │
    ▼                                                                  │
Phase_E__Decision_Engine (Pluggable)                                   │
    │                                                                  │
    │  { parent_id: DecisionResult(keep, score, reason) }             │
    │                                                                  │
    ▼                                                                  │
Phase_E__Node_Deleter ◄────────────────────────────────────────────────┘
    │                    (Deletes from ORIGINAL graph)
    ▼
Html_MGraph__Document (modified - unwanted nodes removed)
    │
    ▼
Html_MGraph__Document__To__Html
    │
    ▼
Clean HTML String
```

---

## Files Created

| File | Purpose |
|------|---------|
| `Phase_E__Text_Extractor.py` | Extract `{node_id: TextNodeInfo(text, parent_id)}` |
| `Phase_E__Virtual_Merger.py` | Compute merged text per parent (read-only) |
| `Phase_E__Decision_Engine__Base.py` | Abstract base with `should_keep()`, `classify()`, `classify_all()` |
| `Phase_E__Decision_Engine__Hash_Based.py` | Deterministic hash-based implementation |
| `Phase_E__Node_Deleter.py` | Delete parent nodes via `mgraph.edit().delete_node()` |
| `Phase_E__Pipeline.py` | Orchestrates full workflow with `process()` and `process_with_details()` |

### Test Files

| File | Tests |
|------|-------|
| `test_Phase_E__Text_Extractor.py` | Extraction from various HTML structures |
| `test_Phase_E__Virtual_Merger.py` | Merging logic and source tracking |
| `test_Phase_E__Decision_Engine__Hash_Based.py` | Hash determinism, thresholds, batch classification |
| `test_Phase_E__Node_Deleter.py` | Single/multiple deletion, safety |
| `test_Phase_E__Pipeline.py` | Full integration with `graph_deterministic_ids()` |

---

## Type_Safe Patterns Applied

### Data Classes (Pure Data, No Methods)

```python
class TextNodeInfo(Type_Safe):                                                  # Info about a text node
    text      : Safe_Str                                                        # Text content
    parent_id : Safe_Str                                                        # Parent element's node_id


class MergedTextInfo(Type_Safe):                                                # Info about merged text
    merged_text      : Safe_Str                                                 # Combined text content
    source_node_ids  : List[str]                                                # Original text node_ids


class DecisionResult(Type_Safe):                                                # Result of a keep/discard decision
    keep   : bool                                                               # True to keep, False to discard
    score  : Safe_Float                                                         # Confidence/relevance score
    reason : Safe_Str                                                           # Human-readable reason


class Process_Result(Type_Safe):                                                # Full result with intermediate data
    html             : Safe_Str
    text_nodes       : Dict[str, TextNodeInfo]
    merged_texts     : Dict[str, MergedTextInfo]
    decisions        : Dict[str, DecisionResult]
    parents_deleted  : List[str]
    deleted_count    : Safe_Int
    clean_html       : Safe_Str
```

### Code Formatting

- File headers with `═══` borders
- Aligned imports at column 85
- Section dividers for method groups
- Inline comments at column 70-80 (no docstrings)
- No underscore prefix on helper methods
- `@type_safe` decorator on public methods

---

## Bugs Fixed During Implementation

### Bug 1: Indexed Node Paths

**Symptom**: `find_nodes_by_tag(mgraph, 'p')` returned empty list

**Root Cause**: `node_path` includes index like `'body.div.p[0]'`, so splitting by `.` gives `'p[0]'` which doesn't match `'p'`

**Fix**:
```python
if '[' in tag:                                                      # Handle indexed tags like 'p[0]', 'p[1]'
    tag = tag[:tag.index('[')]
```

### Bug 2: Missing HTML Structure

**Symptom**: Tests failing with empty `text_nodes`

**Root Cause**: HTML strings like `"<div>Hello</div>"` don't create a body_graph

**Fix**: All test HTML strings need `<html><body>` wrapper:
```python
html = "<html><body><div>Hello</div></body></html>"
```

---

## Testing Patterns

### Deterministic IDs with `graph_deterministic_ids()`

```python
def test_process_with_details__text_nodes_extracted(self):
    with self.pipeline as _:
        html = "<html><body><div>Hello World</div></body></html>"
        with graph_deterministic_ids():
            result = _.process_with_details(html)

        assert result.obj() == __(html='<html><body><div>Hello World</div></body></html>',
                                  text_nodes=__(f0000004=__(text='Hello World', parent_id='f0000003')),
                                  merged_texts=__(f0000003=__(merged_text='Hello World',
                                                              source_node_ids=['f0000004'])),
                                  decisions=__(f0000003=__(keep=False,
                                                           score=0.0721,
                                                           reason='hash_below_threshold')),
                                  parents_deleted=['f0000003'],
                                  deleted_count=1,
                                  clean_html='<!DOCTYPE html>\n<html>\n    <body></body>\n</html>')
```

### Context Manager with `_`

```python
def test__init__(self):
    with self.extractor as _:
        assert type(_).__name__ == 'Phase_E__Text_Extractor'
```

### `setUpClass` for Shared Objects

```python
@classmethod
def setUpClass(cls):
    cls.pipeline = Phase_E__Pipeline()
```

---

## Usage Examples

### Simple Usage

```python
from Phase_E__Pipeline import Phase_E__Pipeline

pipeline   = Phase_E__Pipeline()
clean_html = pipeline.process(html)
```

### Custom Threshold

```python
from Phase_E__Decision_Engine__Hash_Based import Phase_E__Decision_Engine__Hash_Based
from Phase_E__Pipeline import Phase_E__Pipeline

engine   = Phase_E__Decision_Engine__Hash_Based(threshold=0.3)  # Keep more content
pipeline = Phase_E__Pipeline(decision_engine=engine)
clean_html = pipeline.process(html)
```

### With Details for Debugging

```python
result = pipeline.process_with_details(html)

print(result.text_nodes)       # Extracted text
print(result.merged_texts)     # Virtual merge
print(result.decisions)        # Keep/discard decisions
print(result.parents_deleted)  # What was removed
print(result.clean_html)       # Output HTML
```

---

## Hash-Based Decision Engine

The `Phase_E__Decision_Engine__Hash_Based` provides deterministic decisions based on MD5 hash of text content:

```python
def hash_score(self, text: str) -> float:
    if not text:
        return 0.0

    full_hash = md5(text.encode()).hexdigest()
    hash_int  = int(full_hash[:16], 16)
    score     = (hash_int % 10000) / 10000.0

    return score
```

**Example scores** (deterministic):
- `"Hello World"` → 0.0721 (below 0.5 threshold → delete)
- `"Test"` → 0.1712 (below 0.5 threshold → delete)

This pattern matches `Semantic_Text__Engine__Hash_Based` from the semantic text service.

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Virtual merge (read-only)** | Avoid complex reverse mapping; analyze without modifying |
| **Delete parent nodes** | Removes entire subtree cleanly |
| **Pluggable decision engine** | Ready for ML/LLM replacement |
| **Type_Safe throughout** | Runtime type safety, clean serialization |
| **`Process_Result` schema** | Full visibility into pipeline state for debugging |

---

## Future Extensions

| Extension | Description |
|-----------|-------------|
| `Phase_E__Decision_Engine__ML_Based` | Trained classifier for content detection |
| `Phase_E__Decision_Engine__LLM_Based` | LLM prompt-based classification |
| Block-level parent resolution | Walk up tree to find block-level ancestor |
| Attribute-aware decisions | Use attrs_graph for class/id in decisions |
| Cascade delete empty parents | Remove parents that become empty after deletion |

---

## Dependencies

- Phase A: `Html__To__Html_Dict__With__Node_Ids`
- Phase B: `Html__To__Html_MGraph__Document__Node_Id_Reuse`
- Existing: `Html_MGraph__Document__To__Html`
- Core: `MGraph` from `mgraph_db`
- Testing: `graph_deterministic_ids`, `__` from `osbot_utils.testing`

---

## Summary

Phase E successfully implements a clean separation between:
1. **Analysis** (extract + virtual merge) - read-only
2. **Decision** (pluggable engine) - policy
3. **Action** (delete) - mutation

This architecture makes it easy to swap decision logic without touching the extraction or deletion code, and the `Process_Result` schema provides full transparency into the pipeline state at each step.
