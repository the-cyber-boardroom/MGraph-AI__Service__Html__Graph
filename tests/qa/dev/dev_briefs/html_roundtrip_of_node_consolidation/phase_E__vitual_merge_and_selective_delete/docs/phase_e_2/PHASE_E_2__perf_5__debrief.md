# PHASE_E_2__perf_5__debrief.md

## Performance Analysis: _process_body Line-by-Line Breakdown

**Date:** 2026-01-10  
**Benchmark:** perf_5__benchmark__process_body__line_by_line  
**Focus:** Isolating exact per-line costs inside `_process_body()` method

---

## Executive Summary

Following the findings from perf_4 (which identified `process_body` as the scaling bottleneck), this analysis developed a methodology to measure **exact line-by-line execution costs** within a method. After multiple iterations to eliminate measurement artifacts, we successfully isolated the cost of each code line and confirmed that **100% of the scaling cost occurs inside `_process_body_children()`**.

---

## The Challenge: Measuring Line-by-Line Performance

### Target Method Under Analysis

```python
def _process_body(self, document, body_dict):
    body_node_id = self._generate_node_id(body_dict)                    # Line 1

    document.body_graph.create_element(node_path=Node_Path('body'),     # Line 2
                                       node_id=body_node_id)
    document.body_graph.set_root(body_node_id)
    document.attrs_graph.register_element(body_node_id, 'body')

    for position, (key, value) in enumerate(body_dict.get('attrs', {}).items()):  # Line 3
        document.attrs_graph.add_attribute(body_node_id, key, value, position)

    self._process_body_children(document, body_node_id, body_dict, 'body')  # Line 4
```

### The Problem

How do you measure the cost of individual lines when:
- Each line depends on state from previous lines
- Object creation has overhead that pollutes measurements
- The benchmark framework measures lambdas that execute multiple times

---

## Iteration 1: Naive Approach (Failed)

### Approach

Create separate benchmarks for each operation in isolation:

```python
timing.benchmark('A_01__generate_node_id',
    lambda: Node_Id(Obj_Id()))

timing.benchmark('A_02__create_element',
    lambda: document.body_graph.create_element(...))
```

### Results

| Benchmark | Time | Problem |
|-----------|------|---------|
| A_01 | 1µs | OK |
| A_02 | 4.2ms | Includes document.setup()! |
| A_03 | 4.6ms | Includes document.setup()! |
| A_04 | 5.8ms | Includes document.setup()! |

### Why It Failed

Each lambda created fresh objects (`Html_MGraph__Document().setup()`) inside the measurement, adding ~4-5ms of document creation overhead to every benchmark. The actual operation costs were buried in noise.

---

## Iteration 2: State Factory Pattern (Partially Failed)

### Approach

Create a `State_Factory` class to pre-compute state at each line:

```python
class Process_Body__State_Factory:
    def state_after_line_1(self):
        document = Html_MGraph__Document().setup()
        converter = Html__To__Html_MGraph__Document__Node_Id_Reuse()
        body_node_id = converter._generate_node_id()
        return {'document': document, 'body_node_id': body_node_id}
```

Then use the state in benchmarks:

```python
def run_block_2():
    state = state_factory.state_after_line_1()
    code_block_2(state['document'], state['body_node_id'])

timing.benchmark('A_02', run_block_2)
```

### Results

| Benchmark | Time | Problem |
|-----------|------|---------|
| A_01 | 2µs | OK |
| A_02 | 4.8ms | Still includes state creation! |
| A_03 | 4.6ms | Still includes state creation! |
| A_04 | 7.0ms | Includes state creation + actual work |

### Why It Failed

The `state_factory.state_after_line_X()` call was **inside** the lambda, so we measured state creation on every iteration. The measurements were dominated by the state factory overhead, not the actual operations.

---

## Iteration 3: Cumulative Measurement (Partially Worked)

### Approach

Build cumulative benchmarks where each includes all previous code:

```python
def stage_01():
    document = Html_MGraph__Document().setup()
    return document

def stage_02():
    document = Html_MGraph__Document().setup()
    converter = Html__To__Html_MGraph__Document__Node_Id_Reuse()
    body_node_id = converter._generate_node_id()
    return document, body_node_id

# ... each stage adds one more operation
```

Then calculate incremental costs by subtraction:
- `node_id_cost = A_02 - A_01`
- `create_register_cost = A_03 - A_02`

### Results

| Benchmark | Time |
|-----------|------|
| A_01 setup | 4.90ms |
| A_02 +node_id | 5.20ms |
| A_03 +create/register | 4.70ms |
| A_04 +attrs | 4.50ms |
| A_05 +children | 27.80ms |

### Why It Partially Failed

The measurements for A_01-A_04 showed **variance within the document.setup() noise** (~4.5-5.2ms). We could see that A_05 was the jump, but the individual line costs were lost in measurement noise.

However, this DID confirm: `_process_body_children()` = A_05 - A_04 ≈ 23ms

---

## Iteration 4: Reuse Objects + Deterministic IDs (SUCCESS)

### Key Insights

1. **Reuse objects across benchmarks** - Create `document` and `converter` ONCE, before the timing lambdas
2. **Use deterministic IDs** - Allows assertions to validate correctness
3. **Measure only the exact code** - No object creation inside the lambda

### Implementation

```python
def benchmarks(self, timing: Perf_Benchmark__Timing):
    body_dict           = self.body_dict
    html_to_html_mgraph = Html__To__Html_MGraph__Document__Node_Id_Reuse()  # Created ONCE
    document            = Html_MGraph__Document().setup()                   # Created ONCE

    def stage_A_01__generate_node_id():
        body_node_id = html_to_html_mgraph._generate_node_id(body_dict)
        assert body_node_id == 'f0000005'  # Deterministic!

    timing.benchmark('A_01__generate_node_id', stage_A_01__generate_node_id)

    def stage_A_02__register_element():
        body_node_id = 'f0000005'  # Use known ID
        document.body_graph.create_element(node_path=Node_Path('body'),
                                           node_id=body_node_id)
        document.body_graph.set_root(body_node_id)
        document.attrs_graph.register_element(body_node_id, 'body')

    timing.benchmark('A_02__register_element', stage_A_02__register_element)
    # ... etc
```

### Deterministic ID Setup

```python
with graph_deterministic_ids():
    cls.html_10  = cls.generator.generate__10()
    cls.html_100 = cls.generator.generate__100()
    cls.html     = cls.html_100
    cls.html_dict = Html__To__Html_Dict__With__Node_Ids(html=cls.html).convert()
```

This produces predictable node IDs (`f0000005`, `f0000006`, etc.) that can be used in assertions and hardcoded in benchmarks.

---

## Final Results

### html_10 (10 nodes)

| Benchmark | Time | Notes |
|-----------|------|-------|
| A_01 `_generate_node_id()` | 800ns | Negligible |
| A_02 `create + set_root + register` | 300µs | Constant |
| A_03 `attrs for loop` | 200ns | Negligible |
| A_04 `_process_body_children()` | 4.40ms | **SCALES** |
| A_05 `full _process_body` | 5.00ms | Reference |
| A_06 `full (new objects)` | 5.30ms | Control |

### html_50 (50 nodes)

| Benchmark | Time | Notes |
|-----------|------|-------|
| A_01 `_generate_node_id()` | 900ns | Negligible |
| A_02 `create + set_root + register` | 400µs | Constant |
| A_03 `attrs for loop` | 200ns | Negligible |
| A_04 `_process_body_children()` | 24.70ms | **SCALES** |
| A_05 `full _process_body` | 23.80ms | Reference |
| A_06 `full (new objects)` | 23.60ms | Control |

### html_100 (100 nodes)

| Benchmark | Time | Notes |
|-----------|------|-------|
| A_01 `_generate_node_id()` | ~1µs | Negligible |
| A_02 `create + set_root + register` | ~400µs | Constant |
| A_03 `attrs for loop` | ~200ns | Negligible |
| A_04 `_process_body_children()` | 45.30ms | **SCALES** |
| A_05 `full _process_body` | 46.30ms | Reference |
| A_06 `full (new objects)` | 48.10ms | Control |

---

## Key Findings

### 1. The Numbers Add Up

A_04 ≈ A_05 ≈ A_06 confirms our measurement methodology is correct. The small variations (~1-3ms) are CPU timing noise, not measurement errors.

### 2. Fixed vs Scaling Costs

| Operation | Cost | Scales? |
|-----------|------|---------|
| `_generate_node_id()` | ~1µs | NO |
| `create_element + set_root + register` | ~400µs | NO |
| `attrs for loop` | ~200ns | NO |
| `_process_body_children()` | **45ms @ 100 nodes** | **YES** |

### 3. Per-Node Cost Analysis

| HTML Size | A_04 Time | Per-Node Cost |
|-----------|-----------|---------------|
| 10 nodes | 4.4ms | ~440µs/node |
| 50 nodes | 24.7ms | ~494µs/node |
| 100 nodes | 45.3ms | ~453µs/node |

**Average: ~450µs per node**

### 4. The Bottleneck is 100% Inside _process_body_children()

- Fixed overhead (A_01 + A_02 + A_03): ~400µs total
- Scaling cost (A_04): ~45ms @ 100 nodes
- **Ratio: 99.1% of time is in `_process_body_children()`**

---

## Methodology: "Follow the Rabbit Hole" Pattern

### Pattern Description

When analyzing performance of a method line-by-line:

1. **Create shared objects BEFORE the benchmark lambdas**
   ```python
   converter = Html__To__Html_MGraph__Document__Node_Id_Reuse()
   document  = Html_MGraph__Document().setup()
   ```

2. **Use deterministic IDs for reproducibility**
   ```python
   with graph_deterministic_ids():
       cls.html_dict = Html__To__Html_Dict__With__Node_Ids(html=cls.html).convert()
   ```

3. **Hardcode known values in benchmarks**
   ```python
   def stage_A_02():
       body_node_id = 'f0000005'  # Known from deterministic generation
       document.body_graph.create_element(...)
   ```

4. **Measure exact code, nothing more**
   - No object creation inside lambdas
   - No state factory calls inside lambdas
   - Just the exact lines from the original method

5. **Add control benchmarks**
   - A_05: Full method using shared objects
   - A_06: Full method using fresh objects
   - These should be approximately equal, validating no hidden side effects

### When to Use This Pattern

- Analyzing a method known to be a bottleneck
- Need to identify which specific line/operation is costly
- Validating that optimizations target the right code

---

## HTML Generator Fix

During this analysis, we discovered the HTML generator was producing fewer nodes than expected:

### Problem
```python
def generate_with_target_nodes(self, target_nodes: int = 100) -> str:
    num_paragraphs = max(1, target_nodes // 3)  # Wrong: 10 // 3 = 3 paragraphs
```

`generate__10()` was producing only 3 paragraphs (6-9 nodes) instead of 10.

### Fix
```python
def generate__10(self) -> str:
    return self.generate_with_paragraphs(num_paragraphs=10, words_per_para=5)
```

Now produces exactly 10 `<p>` elements with text nodes.

---

## Next Steps

### Immediate: perf_6 - _process_body_children Breakdown

The bottleneck is now localized to `_process_body_children()`. Need to break down:

```python
def _process_body_children(self, document, parent_id, parent_dict, parent_path):
    nodes = parent_dict.get('nodes', [])
    tag_counts = self._count_tags(nodes)                    # Measure this
    tag_occurrence = {}

    for position, node in enumerate(nodes):
        if not isinstance(node, dict):
            continue

        if self._is_text_node(node):                        # Measure this
            self._process_body__text_node(...)              # Measure this
        elif 'tag' in node:
            # ... path building ...
            self._process_body__element(...)                # Measure this (recursive)
```

### Target Operations to Measure

1. `_count_tags()` - Should be O(n) but fast
2. `_is_text_node()` - Simple dict check
3. `_process_body__text_node()` - Text node creation
4. `_process_body__element()` - Element creation + recursive call

The recursive nature of `_process_body__element()` → `_process_body_children()` is likely where the ~450µs per node is being spent.

---

## Connection to Previous Findings

| Benchmark | Key Finding | Status |
|-----------|-------------|--------|
| perf_1 | Converter creation is negligible | ✅ Confirmed |
| perf_2 | Dict→MGraph is 95% of pipeline | ✅ Confirmed |
| perf_3 | fast_create provides ~57% improvement | ✅ Validated |
| perf_4 | `process_body` is the scaling bottleneck | ✅ Confirmed |
| perf_5 | `_process_body_children()` is 99%+ of cost | ✅ **NEW** |

---

## Conclusion

Through iterative refinement of our measurement methodology, we successfully developed the **"Follow the Rabbit Hole" pattern** for line-by-line performance analysis. This pattern eliminates measurement artifacts by:

- Reusing objects across benchmarks
- Using deterministic IDs for validation
- Measuring exact code without hidden overhead

The analysis conclusively shows that **100% of the scaling cost** in `_process_body()` comes from the recursive `_process_body_children()` call. The next step is to apply the same methodology to break down what happens inside that recursive loop.

**Current per-node cost: ~450µs**  
**Target per-node cost: <20µs**  
**Required improvement: 95%+ reduction**
