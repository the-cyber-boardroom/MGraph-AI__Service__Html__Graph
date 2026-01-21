# PHASE_E_2__perf_8__debrief.md

## Performance Analysis: Graph Operations Breakdown

**Date:** 2026-01-10  
**Benchmark:** perf_8__benchmark__graph_operations__breakdown  
**Focus:** Breaking down the individual graph operations inside `_create_in_graph` and `_register_attrs`

---

## Executive Summary

Following perf_7 which identified the bottleneck as split between `_create_in_graph` (~206µs) and `_register_attrs` (~198µs), this analysis drills into the underlying graph operations. The key finding: **three MGraph operations account for 98% of per-element cost**:

| Operation | Per-element | % of total |
|-----------|-------------|------------|
| `attrs_graph.register_element()` | **182µs** | **45%** |
| `body_graph.create_element()` | **137µs** | **34%** |
| `body_graph.add_child()` | **78µs** | **19%** |
| `Node_Path()` creation | 1µs | 0% |

All three expensive operations are Type_Safe MGraph methods creating nodes and edges.

---

## Operations Under Analysis

### From `_process_body__create_in_graph`:

```python
def _process_body__create_in_graph(self, document, parent_id, node_id, position, node_path):
    document.body_graph.create_element(node_path=Node_Path(node_path), node_id=node_id)  # A_02 / B_02
    document.body_graph.add_child(parent_id, node_id, position)                          # A_03 / B_03
```

### From `_process_body__register_attrs`:

```python
def _process_body__register_attrs(self, document, node_id, tag, node):
    document.attrs_graph.register_element(node_id, tag)                                  # A_04 / B_04
    attrs = node.get('attrs', {})
    for attr_pos, (attr_name, attr_value) in enumerate(attrs.items()):
        document.attrs_graph.add_attribute(node_id, attr_name, attr_value, attr_pos)     # A_05
```

---

## Benchmark Structure

### Section A: Single Operation Measurements

| Benchmark | Measures | Adjustment |
|-----------|----------|------------|
| A_01 | `Node_Path('body.p[0]')` | None |
| A_02 | `body_graph.create_element()` | None (baseline) |
| A_03 | `body_graph.add_child()` | Subtract A_02 |
| A_04 | `attrs_graph.register_element()` | Subtract A_02 |
| A_05 | `attrs_graph.add_attribute()` | Subtract A_02 and A_04 |
| A_06 | Full `_create_in_graph` | Reference |
| A_07 | Full `_register_attrs` | Subtract A_06 |

### Section B: Full Loop Processing (N elements)

| Benchmark | Measures | Adjustment |
|-----------|----------|------------|
| B_01 | `Node_Path()` × N | None |
| B_02 | `create_element()` × N | None (baseline) |
| B_03 | `add_child()` × N | Subtract B_02 |
| B_04 | `register_element()` × N | Subtract B_02 |
| B_05 | Full `_create_in_graph` × N | Reference |
| B_06 | Full `_register_attrs` × N | Subtract B_05 |

---

## Results

### html_10 (10 elements)

```
│ A_01__node_path_creation         │ 700ns      │  0.0% │
│ A_02__create_element             │ 100.00µs   │  1.0% │
│ A_03__add_child                  │ 200.00µs   │  2.1% │
│ A_04__register_element           │ 200.00µs   │  2.1% │
│ A_05__add_attribute              │ 500.00µs   │  5.2% │
│ A_06__full_create_in_graph       │ 200.00µs   │  2.1% │
│ A_07__full_register_attrs        │ 200.00µs   │  2.1% │
│ ──────────────────────────────── │ ────────── │ ───── │
│ B_01__node_path_all              │ 8.00µs     │  0.1% │
│ B_02__create_element_all         │ 1.40ms     │ 14.6% │
│ B_03__add_child_all              │ 800.00µs   │  8.3% │
│ B_04__register_element_all       │ 1.90ms     │ 19.8% │
│ B_05__full_create_in_graph_all   │ 2.20ms     │ 22.9% │
│ B_06__full_register_attrs_all    │ 1.90ms     │ 19.8% │
```

### html_100 (100 elements)

```
│ A_01__node_path_creation         │ 700ns      │  0.0% │
│ A_02__create_element             │ 100.00µs   │  0.1% │
│ A_03__add_child                  │ 100.00µs   │  0.1% │
│ A_04__register_element           │ 200.00µs   │  0.2% │
│ A_05__add_attribute              │ 400.00µs   │  0.5% │
│ A_06__full_create_in_graph       │ 200.00µs   │  0.2% │
│ A_07__full_register_attrs        │ 200.00µs   │  0.2% │
│ ──────────────────────────────── │ ────────── │ ───── │
│ B_01__node_path_all              │ 80.00µs    │  0.1% │
│ B_02__create_element_all         │ 13.70ms    │ 16.8% │
│ B_03__add_child_all              │ 7.80ms     │  9.6% │
│ B_04__register_element_all       │ 18.20ms    │ 22.3% │
│ B_05__full_create_in_graph_all   │ 21.10ms    │ 25.9% │
```

### html_200 (200 elements)

```
│ B_01__node_path_all              │ 200.00µs   │  0.1% │
│ B_02__create_element_all         │ 27.40ms    │ 16.6% │
│ B_03__add_child_all              │ 15.50ms    │  9.4% │
│ B_04__register_element_all       │ 37.20ms    │ 22.6% │
│ B_05__full_create_in_graph_all   │ 43.20ms    │ 26.2% │
│ B_06__full_register_attrs_all    │ 39.70ms    │ 24.1% │
```

---

## Per-Element Cost Analysis

### html_100 Breakdown

| Operation | Total | Per-element | % of graph ops |
|-----------|-------|-------------|----------------|
| B_01 (Node_Path) | 80µs | **0.8µs** | 0.2% |
| B_02 (create_element) | 13.70ms | **137µs** | 34% |
| B_03 (add_child) | 7.80ms | **78µs** | 19% |
| B_04 (register_element) | 18.20ms | **182µs** | 45% |
| **TOTAL** | **39.78ms** | **~398µs** | **100%** |

### Verification

```
B_02 + B_03 = 13.70ms + 7.80ms = 21.50ms
B_05 (reference) = 21.10ms
Difference: 0.40ms (1.9%) ✓ Within measurement noise
```

---

## Visual Breakdown

```
┌─────────────────────────────────────────────────────────────┐
│           GRAPH OPERATIONS COST (~400µs/element)            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   attrs_graph.register_element  ███████████████████  182µs  │  45%
│   body_graph.create_element     █████████████        137µs  │  34%
│   body_graph.add_child          ████████              78µs  │  19%
│   Node_Path creation            ░                      1µs  │   0%
│                                                             │
├─────────────────────────────────────────────────────────────┤
│   TOTAL                                              398µs  │ 100%
└─────────────────────────────────────────────────────────────┘
```

---

## Scaling Validation

| Size | B_02 create | B_03 add_child | B_04 register | Scaling |
|------|-------------|----------------|---------------|---------|
| 10 | 1.40ms | 0.80ms | 1.90ms | baseline |
| 100 | 13.70ms | 7.80ms | 18.20ms | ~10x ✓ |
| 200 | 27.40ms | 15.50ms | 37.20ms | ~20x ✓ |

All operations scale linearly with element count. Per-element cost is consistent.

---

## Key Findings

### 1. `register_element` is the Most Expensive (45%)

At 182µs per call, `attrs_graph.register_element()` is the single most expensive operation. This is surprising because our test `<p>` elements have **no attributes** - yet registration alone costs 182µs.

### 2. `create_element` is Second (34%)

At 137µs per call, `body_graph.create_element()` creates a node in the body graph. This involves Type_Safe object creation.

### 3. `add_child` is Third (19%)

At 78µs per call, `body_graph.add_child()` creates an edge between parent and child nodes.

### 4. `Node_Path` Creation is NOT the Problem

At ~1µs per call, `Node_Path()` creation is negligible. This was a potential suspect (string parsing, object creation) but is now ruled out.

### 5. `add_attribute` Was Not Measured at Scale

Since our test `<p>` elements have no attributes, `add_attribute` isn't called in the loop. A_05 shows single-call cost of ~400µs, but this needs HTML with attributes to measure at scale.

---

## What These Operations Do

### `body_graph.create_element(node_path, node_id)`

Creates a node in the MGraph representing an HTML element:
- Creates Type_Safe node object
- Adds to graph's node collection
- Associates node_path and node_id

### `body_graph.add_child(parent_id, child_id, position)`

Creates an edge representing parent-child relationship:
- Creates Type_Safe edge object
- Validates parent and child exist
- Adds to graph's edge collection

### `attrs_graph.register_element(node_id, tag)`

Registers an element in the attributes graph:
- Creates element registration node
- Associates node_id with tag name
- Sets up structure for attributes

---

## The Rabbit Hole Path

```
convert_from_dict (perf_2: 95% of pipeline)
  └── _process_body (perf_5: 99%+ of convert)
        └── _process_body_children (perf_6: 100% of _process_body)
              └── _process_body__element (perf_7: 100% of children)
                    ├── _create_in_graph (perf_7: 44%)
                    │     ├── create_element (perf_8: 34%)  ← TYPE_SAFE MGRAPH
                    │     └── add_child (perf_8: 19%)       ← TYPE_SAFE MGRAPH
                    │
                    └── _register_attrs (perf_7: 42%)
                          └── register_element (perf_8: 45%) ← TYPE_SAFE MGRAPH
```

---

## Connection to Previous Findings

| Benchmark | Key Finding | Status |
|-----------|-------------|--------|
| perf_1 | Converter creation is negligible | ✅ Confirmed |
| perf_2 | Dict→MGraph is 95% of pipeline | ✅ Confirmed |
| perf_3 | fast_create provides ~57% improvement | ✅ Validated |
| perf_4 | `process_body` is the scaling bottleneck | ✅ Confirmed |
| perf_5 | `_process_body_children()` is 99%+ of cost | ✅ Confirmed |
| perf_6 | `_process_body__element()` is 100% of that | ✅ Confirmed |
| perf_7 | Split: `_create_in_graph` (44%) + `_register_attrs` (42%) | ✅ Confirmed |
| perf_8 | Three MGraph ops: register (45%) + create (34%) + add_child (19%) | ✅ **NEW** |

---

## Next Steps: perf_9

Need to look **inside** these three MGraph methods:

### `create_element` internals:
- Type_Safe node object creation
- Schema instantiation
- Graph data structure insertion

### `add_child` internals:
- Edge object creation
- Node validation
- Edge collection insertion

### `register_element` internals:
- What makes this the most expensive?
- Why 182µs for an element with no attributes?

**Key question:** Are these costs from:
1. Type_Safe object creation overhead?
2. Schema/validation overhead?
3. Data structure operations?
4. Something else?

---

## Conclusion

We've successfully broken down the bottleneck to three specific MGraph operations:

| Operation | Per-element | Cumulative % |
|-----------|-------------|--------------|
| `register_element` | 182µs | 45% |
| `create_element` | 137µs | 79% |
| `add_child` | 78µs | 98% |
| Other | ~3µs | 100% |

The optimization target is now clear: **improve the performance of Type_Safe MGraph node/edge creation**. These three methods together account for ~397µs of the ~460µs per-element cost identified in perf_7.

**Current per-element cost: ~400µs** (graph operations only)  
**Target per-element cost: <20µs**  
**Required improvement: 95%+ reduction**

The next step (perf_9) should examine what happens inside these MGraph methods to understand why Type_Safe object creation is so expensive.
