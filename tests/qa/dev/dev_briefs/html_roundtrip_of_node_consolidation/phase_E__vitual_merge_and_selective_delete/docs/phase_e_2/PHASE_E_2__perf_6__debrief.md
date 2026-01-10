# PHASE_E_2__perf_6__debrief.md

## Performance Analysis: _process_body_children Line-by-Line Breakdown

**Date:** 2026-01-10  
**Benchmark:** perf_6__benchmark__process_body_children__line_by_line  
**Focus:** Drilling into the recursive `_process_body_children` method

---

## Executive Summary

Following perf_5 which identified `_process_body_children()` as consuming 99%+ of processing time, this analysis breaks down that method line-by-line. The conclusive finding: **100% of the bottleneck is inside `_process_body__element()`**. When that single method call is commented out, processing 100,000 nodes takes only 35ms total. With it enabled, 100 nodes takes 45ms.

---

## Target Method Under Analysis

```python
def _process_body_children(self, document, parent_id, parent_dict, parent_path):
    nodes          = parent_dict.get('nodes', [])                           # A_01
    tag_counts     = self._count_tags(nodes)                                # A_02
    tag_occurrence = {}

    for position, node in enumerate(nodes):                                 # A_03a
        if not isinstance(node, dict):
            continue

        if self._is_text_node(node):                                        # A_03b
            self._process_body__text_node(document, parent_id, node, position)  # A_04
        elif 'tag' in node:                                                 # A_03c
            tag       = node.get('tag', '').lower()
            tag_index = tag_occurrence.get(tag, 0)
            tag_occurrence[tag] = tag_index + 1

            if tag_counts.get(tag, 0) > 1:
                node_path = f"{parent_path}.{tag}[{tag_index}]"
            else:
                node_path = f"{parent_path}.{tag}"

            self._process_body__element(document, parent_id, node,          # A_05 ← BOTTLENECK
                                        position, tag, node_path)
```

---

## Benchmark Structure

| Benchmark | What It Measures | Notes |
|-----------|------------------|-------|
| A_01 | `parent_dict.get('nodes', [])` | Dict access |
| A_02 | `self._count_tags(nodes)` | O(n) loop counting tags |
| A_03a | Pure loop (enumerate + isinstance) | Loop overhead only |
| A_03b | Loop + `_is_text_node()` | Adds N × dict lookups |
| A_03c | Full loop overhead (+ tag logic) | All iteration logic |
| A_04 | `_process_body__text_node` for all text nodes | Text node processing |
| A_05 | `_process_body__element` for all elements | **THE BOTTLENECK** |
| A_06 | Full `_process_body_children` | Reference |

---

## The TEXT Node Mystery

### Initial Confusion

A_04 (`process_all_text_nodes`) showed suspiciously low numbers:
```
│ A_04__process_all_text_nodes │ 7.00µs │
```

Added debug code:
```python
def stage_A_04__process_all_text_nodes():
    for position, node in enumerate(nodes):
        if converter._is_text_node(node):
            raise Exception("we never get here")  # Never triggered!
```

### Root Cause

The HTML structure:
```
body (f0000005)
  └── p (f0000006)         ← body's children are <p> elements
        └── TEXT (f0000007) ← TEXT is child of <p>, NOT body
```

When iterating `body_dict['nodes']`, we get `<p>` elements. `_is_text_node(<p>)` returns **False** because `<p>` has a `'tag'` key.

### Where TEXT Processing Actually Happens

The debugger confirmed TEXT nodes ARE processed, but **inside the recursive call**:

```
_process_body_children(body)
  └── for each <p> in body's children:
        └── _process_body__element(<p>)
              └── _process_body_children(<p>)    ← RECURSIVE
                    └── for each TEXT in <p>'s children:
                          └── _is_text_node(TEXT) → True
                          └── _process_body__text_node(TEXT)  ← HERE!
```

**Conclusion:** TEXT node processing cost is hidden inside A_05's recursive `_process_body__element` calls.

---

## Results: Full Pipeline

### html_100 (100 nodes)

```
│ A_01__get_nodes                  │ 100ns   │ 0.0%  │
│ A_02__count_tags                 │ 9.00µs  │ 0.0%  │
│ A_03a__pure_loop                 │ 2.00µs  │ 0.0%  │
│ A_03b__loop_with_is_text_node    │ 7.00µs  │ 0.0%  │
│ A_03c__full_loop_overhead        │ 20.00µs │ 0.0%  │
│ A_04__process_all_text_nodes     │ 7.00µs  │ 0.0%  │
│ A_05__process_all_elements       │ 45.40ms │ 49.2% │ ← BOTTLENECK
│ A_06__full_process_body_children │ 46.80ms │ 50.7% │
```

**Key observation:** A_05 ≈ A_06, confirming all the time is in element processing.

---

## Results: With `_process_body__element` Commented Out

The smoking gun test - comment out the bottleneck:

```python
def stage_A_05__process_all_elements():
    tag_counts     = converter._count_tags(nodes)
    tag_occurrence = {}
    for position, node in enumerate(nodes):
        if not isinstance(node, dict):
            continue
        if 'tag' in node:
            tag       = node.get('tag', '').lower()
            tag_index = tag_occurrence.get(tag, 0)
            tag_occurrence[tag] = tag_index + 1
            if tag_counts.get(tag, 0) > 1:
                node_path = f"body.{tag}[{tag_index}]"
            else:
                node_path = f"body.{tag}"
            # converter._process_body__element(...)  ← COMMENTED OUT
```

### html_100 WITHOUT _process_body__element

```
│ A_01__get_nodes               │ 100ns   │  0.1% │
│ A_02__count_tags              │ 9.00µs  │ 11.7% │
│ A_03a__pure_loop              │ 2.00µs  │  2.6% │
│ A_03b__loop_with_is_text_node │ 8.00µs  │ 10.4% │
│ A_03c__full_loop_overhead     │ 20.00µs │ 25.9% │
│ A_04__process_all_text_nodes  │ 8.00µs  │ 10.4% │
│ A_05__process_all_elements    │ 30.00µs │ 38.9% │
```

**A_05 dropped from 45.40ms to 30.00µs = 1,500x faster!**

---

## Scaling Validation (Without _process_body__element)

To validate test data generation and confirm linear scaling:

| Size | A_02 count_tags | A_03a pure_loop | A_05 elements | Scaling |
|------|-----------------|-----------------|---------------|---------|
| 100 | 9µs | 2µs | 30µs | baseline |
| 1,000 | 90µs | 20µs | 300µs | 10x ✓ |
| 10,000 | 1.1ms | 200µs | 3.4ms | 10x ✓ |
| 100,000 | 10.8ms | 3.6ms | 34.8ms | 10x ✓ |

**Perfect linear O(n) scaling confirms:**
1. Test data generation is correct
2. All iteration/helper overhead scales linearly
3. The processing pipeline CAN handle 100,000 nodes efficiently

---

## Test Data Generation

Added larger test sizes:

```python
def generate__1_000(self) -> str:
    return self.generate_with_paragraphs(num_paragraphs=1_000, words_per_para=5)

def generate__10_000(self) -> str:
    return self.generate_with_paragraphs(num_paragraphs=10_000, words_per_para=5)

def generate__100_000(self) -> str:
    return self.generate_with_paragraphs(num_paragraphs=100_000, words_per_para=5)
```

With deterministic IDs for reproducibility:

```python
with graph_deterministic_ids():
    cls.html_1       = cls.generator.generate__1()
    cls.html_10      = cls.generator.generate__10()
    cls.html_100     = cls.generator.generate__100()
    cls.html_1_000   = cls.generator.generate__1_000()
    cls.html_10_000  = cls.generator.generate__10_000()
    cls.html_100_000 = cls.generator.generate__100_000()
    cls.html         = cls.html_100  # Change to test different sizes
```

---

## Key Methodology Refinements

### 1. Move Object Creation Outside Lambda

**Before (incorrect):**
```python
def stage_A_05():
    document  = create_fresh_document_with_body()  # Inside = measured!
    converter = Html__To__Html_MGraph__Document__Node_Id_Reuse()
    # ... processing
```

**After (correct):**
```python
document  = create_fresh_document_with_body()  # Outside = not measured
converter = Html__To__Html_MGraph__Document__Node_Id_Reuse()

def stage_A_05():
    # ... only processing measured
```

### 2. Separate Loop Overhead Measurements

Split A_03 into three measurements:
- **A_03a**: Pure loop (enumerate + isinstance)
- **A_03b**: Loop + `_is_text_node` calls
- **A_03c**: Full loop with tag processing logic

This allows calculating:
```
_is_text_node cost per call = (A_03b - A_03a) / N
tag processing cost = (A_03c - A_03b) / N
```

### 3. Proving Bottleneck by Elimination

Comment out suspected bottleneck to prove causality:
```
WITH _process_body__element:     45.40ms
WITHOUT _process_body__element:  0.03ms (30µs)
                                 ────────
Difference:                      45.37ms = 99.93% of time
```

---

## Findings Summary

### What's Fast (scales linearly, acceptable performance)

| Operation | Time @ 100 nodes | Time @ 100,000 nodes | Per-call |
|-----------|------------------|----------------------|----------|
| `dict.get('nodes')` | 100ns | 100ns | ~100ns |
| `_count_tags()` | 9µs | 10.8ms | ~100ns/node |
| Loop iteration | 2µs | 3.6ms | ~36ns/node |
| `_is_text_node()` | 5µs (N calls) | 4.9ms | ~50ns/call |
| Tag processing logic | 12µs | 9.7ms | ~97ns/node |

### What's Slow (the entire bottleneck)

| Operation | Time @ 100 nodes | Per-call |
|-----------|------------------|----------|
| `_process_body__element()` | 45.40ms | **~454µs/element** |

---

## The Bottleneck Localized

```
_process_body (from perf_5)
    └── _process_body_children (from perf_6)
          └── _process_body__element  ← 100% OF BOTTLENECK IS HERE
```

Everything else combined (dict access, counting, looping, text node checks, path building) accounts for < 0.1% of total time.

---

## Next Steps: perf_7

Break down `_process_body__element`:

```python
def _process_body__element(self, document, parent_id, node, position, tag, node_path):
    node_id = self._generate_node_id()                                    # B_01
    
    self._process_body__create_in_graph(document, parent_id,              # B_02
                                        node_id, position, node_path)
    self._process_body__register_attrs(document, node_id, tag, node)      # B_03
    
    if tag in SCRIPT_TAGS:
        self._process_body__handle_script(document, node_id, node)
    else:
        self._process_body_children(document, node_id, node, node_path)   # B_04 (RECURSIVE)
```

Key questions for perf_7:
1. How much is `_generate_node_id()`?
2. How much is `_process_body__create_in_graph()` (create_element + add_child)?
3. How much is `_process_body__register_attrs()` (register + add attributes)?
4. How much is the recursive `_process_body_children()` call?

The recursive nature means B_04 will be dominant, but we need to measure B_01-B_03 to understand the per-element fixed cost.

---

## Connection to Previous Findings

| Benchmark | Key Finding | Status |
|-----------|-------------|--------|
| perf_1 | Converter creation is negligible | ✅ Confirmed |
| perf_2 | Dict→MGraph is 95% of pipeline | ✅ Confirmed |
| perf_3 | fast_create provides ~57% improvement | ✅ Validated |
| perf_4 | `process_body` is the scaling bottleneck | ✅ Confirmed |
| perf_5 | `_process_body_children()` is 99%+ of cost | ✅ Confirmed |
| perf_6 | `_process_body__element()` is 100% of that | ✅ **NEW** |

---

## Conclusion

The "Follow the Rabbit Hole" methodology continues to successfully narrow down the bottleneck. We've now proven that **100% of the scaling cost** is inside a single method: `_process_body__element()`.

The proof is definitive:
- Comment out `_process_body__element`: 100,000 nodes in 35ms
- Enable `_process_body__element`: 100 nodes in 45ms

That's a **1,285x slowdown** for processing **1,000x fewer nodes**.

The pipeline overhead (iteration, counting, path building) is negligible and scales perfectly. The problem is entirely within what `_process_body__element` does: creating graph nodes, registering attributes, and recursively processing children.

**Current per-element cost: ~454µs**  
**Target per-element cost: <20µs**  
**Required improvement: 95%+ reduction**
