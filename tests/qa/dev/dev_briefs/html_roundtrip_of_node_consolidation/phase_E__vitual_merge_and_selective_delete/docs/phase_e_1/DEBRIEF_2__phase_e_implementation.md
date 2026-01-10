# Phase E Performance Analysis - Implementation Debrief

**Date**: January 2026  
**Status**: ✅ Complete  
**Context**: Refactoring performance benchmarks for HTML→MGraph conversion pipeline

---

## Objective

Profile the Phase E HTML conversion pipeline to identify performance bottlenecks and measure the impact of Type_Safe optimizations (`fast_create`, `skip_validation`).

---

## The Problem We Solved

### Initial State

The original `Perf__Phase_E__Conversion.py` used raw `Perf` (Performance_Measure__Session) with a closure pattern:

```python
# Original approach
def benchmark_conversions(self, html: str) -> Schema__Conversion_Timing:
    html_dict = None
    document  = None

    def stage_html_to_dict():
        nonlocal html_dict
        html_dict = Html__To__Html_Dict__With__Node_Ids(html=html).convert()

    def stage_dict_to_mgraph():
        nonlocal document
        document = Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(html_dict)

    with self.session as _:
        result_1 = _.measure__fast(stage_html_to_dict  ).result
        result_2 = _.measure__fast(stage_dict_to_mgraph).result
        result_3 = _.measure__fast(stage_mgraph_to_html).result
```

**Issues identified:**
1. No structured benchmark IDs - results couldn't be compared over time
2. Closure pattern with `nonlocal` was fragile and hard to reason about
3. No separation of "full operation" vs "isolated stages"
4. Results schema was custom instead of using framework schemas
5. Couldn't leverage `Perf_Benchmark__Diff` for historical comparison

### Refactored State

```python
# Refactored approach using Perf_Benchmark__Timing
def benchmark_conversions(self, html: str) -> Schema__Conversion_Timing:
    # Pre-compute intermediate values for stage isolation
    html_dict = Html__To__Html_Dict__With__Node_Ids(html=html).convert()
    document  = Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(html_dict)

    with Perf_Benchmark__Timing(config=self.config) as timing:
        timing.benchmark('A_01__html_to_dict',
            lambda: Html__To__Html_Dict__With__Node_Ids(html=html).convert())

        timing.benchmark('A_02__dict_to_mgraph',
            lambda: Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(html_dict))

        timing.benchmark('A_03__mgraph_to_html',
            lambda: Html_MGraph__Document__To__Html().convert(document))

    # Extract from structured results
    html_to_dict_ns   = int(timing.results['A_01__html_to_dict'  ].final_score)
    dict_to_mgraph_ns = int(timing.results['A_02__dict_to_mgraph'].final_score)
    mgraph_to_html_ns = int(timing.results['A_03__mgraph_to_html'].final_score)
```

---

## Architecture

### File Structure

```
phase_e/
    performance/
        Perf__Phase_E__Conversion.py      # Main benchmark class
        Perf__Phase_E__Scalability.py     # Multi-size scaling analysis
        Perf__Storage__Local.py           # Save results to disk
        Html_Generator__For_Benchmarks.py # Generate controlled test HTML

tests/
    performance/
        test_Perf__Phase_E__Conversion.py # Benchmark tests with reports
```

### Class Responsibilities

| Class | Purpose |
|-------|---------|
| `Perf__Phase_E__Conversion` | Benchmark the 3 conversion stages |
| `Perf__Phase_E__Scalability` | Test scaling from 1 to 10,000 nodes |
| `Perf__Storage__Local` | Save reports and results to `/perf_results/` |
| `Html_Generator__For_Benchmarks` | Generate HTML with controlled node counts |

---

## Benchmark Design

### Three-Stage Pipeline

```
HTML String
    │
    ▼ [A_01__html_to_dict]
Html__To__Html_Dict__With__Node_Ids
    │
    ▼ [A_02__dict_to_mgraph]
Html__To__Html_MGraph__Document__Node_Id_Reuse
    │
    ▼ [A_03__mgraph_to_html]
Html_MGraph__Document__To__Html
    │
    ▼
HTML String (recreated)
```

### Benchmark ID Scheme

| ID | Stage | Measures |
|----|-------|----------|
| `A_01__html_to_dict` | Stage 1 | Parse HTML, assign node_ids |
| `A_02__dict_to_mgraph` | Stage 2 | Build MGraph (nodes + edges) |
| `A_03__mgraph_to_html` | Stage 3 | Recreate HTML from graph |

### Detailed Breakdown IDs

For diagnostic purposes, we added granular benchmarks:

| ID | Category | Measures |
|----|----------|----------|
| `A_01__html_to_dict__full` | Full Operation | Create converter + convert |
| `B_01__converter_1_create` | Creation Only | Just create converter instance |
| `C_01__html_to_dict__convert_only` | Convert Only | Call .convert() on pre-created instance |

This pattern isolates **Type_Safe object creation** from **conversion logic**.

---

## Test Suite Design

### Key Test Methods

```python
class test_Perf__Phase_E__Conversion(TestCase):

    def test__benchmark_conversions(self):
        # Basic 3-stage benchmark
        # Saves: conversion__basic.txt

    def test__benchmark_conversions_detailed(self):
        # Granular breakdown (A/B/C sections)
        # Saves: conversion__detailed.txt

    def test__benchmark_multiple_sizes__default(self):
        # Multi-size in default Type_Safe mode
        # Saves: conversion__multi__default.txt

    def test__benchmark_multiple_sizes__fast_create(self):
        # Multi-size with fast_create optimization
        # Saves: conversion__multi__fast_create.txt

    def test__benchmark_comparison__default_vs_fast_create(self):
        # Side-by-side comparison with improvement %
        # Saves: conversion__comparison__default_vs_fast_create.txt

    def test__benchmark_detailed_comparison(self):
        # Shows WHERE time is saved
        # Saves: conversion__detailed_comparison.txt
```

### Storage Pattern

```python
@classmethod
def setUpClass(cls):
    cls.storage_path = path_combine(phase_e.path, '../perf_results')
    cls.storage      = Perf__Storage__Local(storage_path=cls.storage_path)

# In tests:
self.storage.save_report(key='conversion__basic', report=report)
```

Reports are saved as `.txt` files in `/perf_results/`:
- `conversion__basic.txt`
- `conversion__detailed.txt`
- `conversion__multi__default.txt`
- `conversion__multi__fast_create.txt`
- `conversion__comparison__default_vs_fast_create.txt`

---

## Schema Design

### Timing Result Schema

```python
class Schema__Conversion_Timing(Type_Safe):
    html_to_dict_ns   : Safe_Int    # HTML → Dict time in nanoseconds
    dict_to_mgraph_ns : Safe_Int    # Dict → MGraph time in nanoseconds
    mgraph_to_html_ns : Safe_Int    # MGraph → HTML time in nanoseconds
    total_ns          : Safe_Int    # Total time
    html_size_bytes   : Safe_Int    # Size of input HTML
    node_count        : Safe_Int    # Approximate node count
```

### Breakdown Schema

```python
class Schema__Conversion_Breakdown(Type_Safe):
    html_to_dict_pct   : Safe_Float  # % time in HTML → Dict
    dict_to_mgraph_pct : Safe_Float  # % time in Dict → MGraph
    mgraph_to_html_pct : Safe_Float  # % time in MGraph → HTML
```

---

## Report Format

### Single Timing Report

```
┌───────────────────────────────────────────┐
│ CONVERSION TIMING REPORT                  │
├───────────────────────────────────────────┤
│ Stage         │ Time     │ Percentage     │
├───────────────────────────────────────────┤
│ HTML → Dict   │ 20.00µs  │ 0.1%           │
│ Dict → MGraph │ 14.80ms  │ 95.4%          │
│ MGraph → HTML │ 700.00µs │ 4.5%           │
│ TOTAL         │ 15.52ms  │ 100%           │
├───────────────────────────────────────────┤
│ HTML Size: 55 bytes | Est. Nodes: 4       │
└───────────────────────────────────────────┘
```

### Multi-Size Report

```
┌────────────────────────────────────────────────────────────────────────┐
│ CONVERSION TIMING BY SIZE                                              │
├────────────────────────────────────────────────────────────────────────┤
│ Size │ Total   │ HTML→Dict     │ Dict→MGraph   │ MGraph→HTML   │ Bytes │
├────────────────────────────────────────────────────────────────────────┤
│ 1    │ 7.62ms  │ 20.00µs (0%)  │ 7.40ms (97%)  │ 200.00µs (3%) │ 161   │
│ 10   │ 8.93ms  │ 30.00µs (0%)  │ 8.50ms (95%)  │ 400.00µs (4%) │ 277   │
│ 100  │ 33.70ms │ 200.00µs (1%) │ 31.10ms (92%) │ 2.40ms (7%)   │ 2,040 │
├────────────────────────────────────────────────────────────────────────┤
│ Primary Bottleneck: Dict→MGraph                                        │
└────────────────────────────────────────────────────────────────────────┘
```

### Detailed Breakdown Report

```
┌────────────────────────────────────────────────────────────────────┐
│ DETAILED CONVERSION BREAKDOWN                                      │
├────────────────────────────────────────────────────────────────────┤
│ Benchmark                          │ Time     │ Category           │
├────────────────────────────────────────────────────────────────────┤
│ A_01__html_to_dict__full           │ 100.00µs │ Full Operation     │
│ A_02__dict_to_mgraph__full         │ 70.80ms  │ Full Operation     │
│ A_03__mgraph_to_html__full         │ 3.40ms   │ Full Operation     │
│ B_01__converter_1_create           │ 3.00µs   │ Converter Creation │
│ B_02__converter_2_create           │ 4.00µs   │ Converter Creation │
│ B_03__converter_3_create           │ 4.00µs   │ Converter Creation │
│ C_01__html_to_dict__convert_only   │ 50.00µs  │ Convert Only       │
│ C_02__dict_to_mgraph__convert_only │ 71.40ms  │ Convert Only       │
│ C_03__mgraph_to_html__convert_only │ 3.60ms   │ Convert Only       │
├────────────────────────────────────────────────────────────────────┤
│ Overhead (full - create - convert): 47.00µs                        │
└────────────────────────────────────────────────────────────────────┘
```

---

## Key Implementation Decisions

| Decision | Rationale |
|----------|-----------|
| Pre-compute intermediate values | Ensures each stage can be measured independently |
| Use `measure_fast=True` | Operations take 5-70ms, full Fibonacci would be too slow |
| Separate A/B/C benchmark sections | Isolates full operation, creation, and convert-only |
| Custom schemas for timing | Preserves domain semantics while using Perf internals |
| Print_Table for reports | Consistent with osbot_utils formatting conventions |
| Save to `/perf_results/` | Persistent storage for historical comparison |

---

## Lessons Learned

### 1. The Original Measurements Were Accurate

The original code showed 7.2ms for `Dict→MGraph` on a single node. We initially suspected measurement error, but **the detailed breakdown confirmed this is real**:

- Converter creation: 4µs (negligible)
- Convert only: 71.4ms (the actual work)

The bottleneck is inside `convert_from_dict()`, not in measurement methodology.

### 2. Context Managers Must Wrap the Benchmark

```python
# ❌ WRONG - fast_create not active during measurement
with Type_Safe__Config(fast_create=True):
    converter = Perf__Phase_E__Conversion()
    
timing = converter.benchmark_conversions(html)  # Outside context!

# ✅ CORRECT - fast_create active during measurement
with Type_Safe__Config(fast_create=True):
    timing = converter.benchmark_conversions(html)  # Inside context
```

### 3. Pre-Computation vs Real-World

Pre-computing `html_dict` and `document` gives us **isolated stage timings**, but in real-world usage, stages run sequentially. Both perspectives are valuable:

- **Isolated**: Where can we optimize?
- **Sequential**: What does the user actually experience?

### 4. Structured IDs Enable Historical Tracking

By using `A_01__html_to_dict` instead of ad-hoc names, we can:
- Compare results across runs
- Use `Perf_Benchmark__Diff` for evolution analysis
- Build automated regression detection

---

## Files Created

| File | Purpose |
|------|---------|
| `Perf__Phase_E__Conversion.py` | Refactored benchmark class |
| `test_Perf__Phase_E__Conversion.py` | Comprehensive test suite |
| `/perf_results/conversion__*.txt` | Saved reports |

---

## Next Steps

1. **Profile inside `convert_from_dict()`** - The 7ms+ baseline needs deeper investigation
2. **Measure MGraph object creation** - How many nodes/edges are created? What's the per-object cost?
3. **Test with larger HTML** - Does the bottleneck shift at 1000+ nodes?
4. **Automate regression detection** - Use `Perf_Benchmark__Diff` in CI
