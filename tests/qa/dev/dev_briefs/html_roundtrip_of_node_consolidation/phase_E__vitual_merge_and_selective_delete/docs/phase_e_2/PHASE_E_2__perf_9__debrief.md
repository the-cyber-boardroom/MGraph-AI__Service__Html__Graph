# PHASE_E_2__perf_9__debrief.md

## Performance Analysis: MGraph new_node Internals Breakdown

**Date:** 2026-01-10  
**Benchmark:** perf_9__benchmark__mgraph_new_node__internals  
**Focus:** Breaking down the MGraph new_node/new_edge call chain internals

---

## Executive Summary

This benchmark revealed the **root cause** of the performance bottleneck: **`@type_safe` decorator overhead**.

By disabling `@type_safe` decorators on key methods, per-element cost dropped from ~137µs to ~32µs - a **4.3x improvement**. The `@type_safe` decorator was responsible for **77% of the total cost**.

With `@type_safe` disabled, the remaining costs are:
- `model.new_node()` (Schema creation): ~10µs (33%)
- `index.add_node()` (Index update): ~20µs (67%)

---

## Critical Finding: @type_safe Decorator Overhead

### Before vs After Comparison

| Operation | With @type_safe (perf_8) | Without @type_safe (perf_9) | Improvement |
|-----------|--------------------------|-----------------------------|----- -------|
| `create_element` | ~137µs | ~32µs | **4.3x faster** |
| `add_child` | ~78µs | ~30µs | **2.6x faster** |
| `register_element` | ~182µs | ~30-40µs (estimated) | **~5x faster** |

### The Math

```
WITH @type_safe:     ~137µs per create_element
WITHOUT @type_safe:  ~32µs per create_element
─────────────────────────────────────────────────
@type_safe overhead: ~105µs per call (77% of cost!)
```

### What Was Disabled

The following pattern was applied to key methods:

```python
#@type_safe # todo: re-enable this once we have add support for @type_safe to check Type_Safe__Config for method calling type safety
def new_node(self, node_path: Node_Path = None, **kwargs):
    ...
```

The `@type_safe` decorator performs:
1. **Input validation** - Type checking all parameters against annotations
2. **Return value validation** - Type checking the return value
3. **Runtime type coercion** - Converting values to expected types

Each of these operations involves reflection, isinstance checks, and potentially object creation - all of which add up significantly when called thousands of times.

---

## Results: Internal Breakdown (Without @type_safe)

### Section A: new_node Internals (Single Call)

```
│ A_01__get_edit                   │ 1.00µs     │  0.0% │  Cache hit
│ A_02__get_index                  │ 1.00µs     │  0.0% │  Cache hit
│ A_03__model_new_node             │ 10.00µs    │  0.2% │  Schema creation
│ A_04__mgraph_node_wrapper        │ 0ns        │  0.0% │  Negligible
│ A_05__index_add_node             │ 20.00µs    │  0.5% │  Index update
│ A_06__full_edit_new_node         │ 30.00µs    │  0.7% │  Reference
│ A_07__full_create_element        │ 30.00µs    │  0.7% │  High-level ref
```

**Breakdown:**
- Schema creation (`model.new_node`): **10µs (33%)**
- Index update (`index.add_node`): **20µs (67%)**
- Edit/graph wrappers: ~0µs (cached)

### Section B: new_edge Internals (Single Call)

```
│ B_01__model_new_edge             │ 10.00µs    │  0.2% │  Schema creation
│ B_02__index_add_edge             │ 10-20µs    │  0.2% │  Index update
│ B_03__full_edit_new_edge         │ 30.00µs    │  0.7% │  Reference
│ B_04__full_add_child             │ 30.00µs    │  0.7% │  High-level ref
```

### Section C: Full Loop (All Elements)

```
│ C_01__model_new_node_all         │ 1.00ms     │ 22.9% │  Model layer only
│ C_02__full_create_element_all    │ 3.20ms     │ 73.2% │  Full stack
```

**Per-element costs (html_100):**
- `model.new_node`: 1.00ms / 100 = **10µs/element**
- `full create_element`: 3.20ms / 100 = **32µs/element**
- Overhead: 32 - 10 = **22µs/element** (edit layer + index)

---

## Scaling Validation

| Size | C_01 (model only) | C_02 (full) | Per-element (model) | Per-element (full) |
|------|-------------------|-------------|---------------------|-------------------|
| 100 | 1.00ms | 3.20ms | 10.0µs | 32.0µs |
| 200 | 2.10ms | 7.00ms | 10.5µs | 35.0µs |
| 500 | 5.40ms | 16.40ms | 10.8µs | 32.8µs |
| 1000 | 10.20ms | 33.80ms | 10.2µs | 33.8µs |

**Perfect linear scaling** - per-element cost is consistent at ~10µs (model) and ~32-35µs (full).

---

## Cost Attribution (Without @type_safe)

### Per create_element Call (~32µs)

```
┌─────────────────────────────────────────────────────────────┐
│         create_element COST BREAKDOWN (~32µs)               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   index.add_node        ██████████████████████████  20µs    │  63%
│   model.new_node        ██████████████             10µs    │  31%
│   Edit layer overhead   ██                          2µs    │   6%
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Per add_child Call (~30µs)

```
┌─────────────────────────────────────────────────────────────┐
│           add_child COST BREAKDOWN (~30µs)                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   index.add_edge        ██████████████████████████  15µs    │  50%
│   model.new_edge        ██████████████             10µs    │  33%
│   Edit layer overhead   █████                       5µs    │  17%
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## The Index as New Bottleneck

With `@type_safe` removed, **index operations are now the dominant cost**:

| Operation | Time | % of new_node |
|-----------|------|---------------|
| `index.add_node()` | 20µs | 67% |
| `model.new_node()` | 10µs | 33% |

The index maintains multiple data structures for fast lookups:
- Node ID → Node mapping
- Node path → Node ID mapping
- Edge relationships
- Type indexes

Each `add_node` call updates several of these indexes.

---

## Observations and Fixes

### 1. @type_safe Decorator Impact (CRITICAL)

**Finding:** `@type_safe` decorator adds ~105µs overhead per call, representing 77% of total cost.

**Recommendation:** Implement `Type_Safe__Config` option for method-level type safety control, similar to `fast_create`:

```python
# Proposed API
with type_safe_disabled():
    # Bulk operations without per-call type checking
    for node in nodes:
        graph.new_node(...)

# Or via config
Type_Safe__Config.method_type_checking = False
```

**Impact:** Would reduce per-element cost from ~137µs to ~32µs (4.3x improvement).

### 2. Index Update Overhead

**Finding:** `index.add_node()` is 67% of remaining cost at 20µs per call.

**Potential optimizations:**
- Batch index updates (add many nodes, then index once)
- Lazy indexing (index on first query, not on insert)
- Simpler index structures for bulk operations

### 3. Benchmark Value for Regression Testing

These benchmarks will be invaluable for:
- Detecting performance regressions when re-enabling `@type_safe`
- Validating that `Type_Safe__Config` options work correctly
- Comparing different indexing strategies
- Measuring impact of future optimizations

---

## The Complete Picture

### Full Pipeline Cost (html_100, without @type_safe)

From perf_8 we know each element needs:
- `create_element`: ~32µs (was 137µs)
- `add_child`: ~30µs (was 78µs)
- `register_element`: ~30-40µs (was 182µs, estimated improvement)

**Total per element: ~90-100µs** (was ~400µs)

For 100 elements: ~9-10ms (was ~40ms) - **4x improvement**

### With @type_safe Re-enabled via Config

If `Type_Safe__Config` can selectively disable method-level checking during bulk operations:

```python
with type_safe_fast_method_calls():
    for element in elements:
        document.body_graph.create_element(...)
        document.body_graph.add_child(...)
        document.attrs_graph.register_element(...)
```

Expected: Same ~100µs per element performance while maintaining type safety for other code paths.

---

## The Rabbit Hole Path - Complete

```
convert_from_dict (perf_2: 95% of pipeline)
  └── _process_body (perf_5: 99%+ of convert)
        └── _process_body_children (perf_6: 100%)
              └── _process_body__element (perf_7: 100%)
                    ├── _create_in_graph (perf_7: 44%)
                    │     ├── create_element (perf_8: 34%)
                    │     │     ├── @type_safe overhead: 77% ← ROOT CAUSE
                    │     │     ├── index.add_node: 15%
                    │     │     └── model.new_node: 8%
                    │     └── add_child (perf_8: 19%)
                    │           └── Similar breakdown
                    │
                    └── _register_attrs (perf_7: 42%)
                          └── register_element (perf_8: 45%)
                                └── Similar breakdown
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
| perf_7 | Split: create_in_graph (44%) + register_attrs (42%) | ✅ Confirmed |
| perf_8 | Three MGraph ops: register + create + add_child | ✅ Confirmed |
| perf_9 | **@type_safe is 77% of cost; index is 67% of remainder** | ✅ **ROOT CAUSE FOUND** |

---

## Conclusion

**Root cause identified:** The `@type_safe` decorator is responsible for 77% of per-element processing cost.

**Solution path:**
1. Implement `Type_Safe__Config` option for bulk operation mode
2. Similar to `fast_create`, allow disabling per-method type checking during performance-critical loops
3. Maintain type safety for API boundaries while optimizing internal operations

**Performance targets:**

| Metric | Before | After @type_safe optimization | Improvement |
|--------|--------|-------------------------------|-------------|
| Per-element cost | ~460µs | ~100µs | **4.6x** |
| html_100 total | ~46ms | ~10ms | **4.6x** |
| html_1000 total | ~460ms | ~100ms | **4.6x** |

**Current state:**
- Without @type_safe: **~32µs per create_element** ✅
- Target achieved for raw operations
- Need `Type_Safe__Config` feature to make this production-ready

The benchmarks created in this investigation will serve as regression tests when implementing the `@type_safe` configuration feature.
