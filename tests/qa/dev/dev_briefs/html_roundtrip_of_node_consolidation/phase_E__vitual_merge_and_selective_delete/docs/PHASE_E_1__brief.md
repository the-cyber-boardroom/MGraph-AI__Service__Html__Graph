# Phase E_1 Brief: Performance Analysis and Benchmarks

**Date**: January 2026  
**Status**: Implementation  
**Builds On**: Phase E (Virtual Merge and Selective Delete)

---

## Objective

Add comprehensive performance analysis to Phase E measuring how each conversion stage scales with HTML complexity.

---

## Focus Areas

### Primary Timing Targets

| Stage | Class | Description |
|-------|-------|-------------|
| HTML → Dict | `Html__To__Html_Dict__With__Node_Ids` | Parse HTML, assign node_ids |
| Dict → MGraph | `Html__To__Html_MGraph__Document__Node_Id_Reuse` | Build graph (nodes + edges) |
| MGraph → HTML | `Html_MGraph__Document__To__Html` | Recreate HTML from graph |

### Secondary Timing Targets

| Stage | Class | Description |
|-------|-------|-------------|
| Text Extraction | `Phase_E__Text_Extractor` | Extract text nodes |
| Virtual Merge | `Phase_E__Virtual_Merger` | Compute merged text |
| Decision | `Phase_E__Decision_Engine__Hash_Based` | Hash-based classification |
| Deletion | `Phase_E__Node_Deleter` | Remove nodes from graph |

---

## Scaling Strategy

Test across sizes to detect bottlenecks:

| Size | Target Nodes | Represents |
|------|--------------|------------|
| Tiny | ~10 | Minimal fragment |
| Small | ~100 | Simple page |
| Medium | ~500 | Blog post |
| Large | ~1,000 | Article |
| XLarge | ~5,000 | Complex page |
| Massive | ~10,000 | Real-world SPA |

---

## File Structure

All files within existing `phase_e/` structure:

```
phase_e/
    core/
    decision/
    schemas/
    performance/                          # NEW
        Html_Generator__For_Benchmarks.py
        Perf__Phase_E__Conversion.py      # HTML↔Dict↔MGraph timings
        Perf__Phase_E__Pipeline.py        # Full pipeline timing
        Perf__Phase_E__Scalability.py     # Scaling analysis
    Phase_E__Pipeline.py

tests/
    core/
    decision/
    performance/                          # NEW
        test_Html_Generator__For_Benchmarks.py
        test_Perf__Phase_E__Conversion.py
        test_Perf__Phase_E__Pipeline.py
        test_Perf__Phase_E__Scalability.py
    test_Phase_E__Pipeline.py

docs/
    PHASE_E__brief.md
    PHASE_E__debrief.md
    PHASE_E_1__brief.md                   # This file
    PHASE_E_1__debrief.md                 # After implementation
```

---

## Benchmark ID Convention

```
A_xx__conversion__*     # HTML↔Dict↔MGraph conversions
B_xx__pipeline__*       # Full pipeline end-to-end
C_xx__component__*      # Individual Phase E components
S_xx__scale__*          # Scalability tests
```

---

## Key Metrics

### Per-Stage Breakdown

For each HTML size, capture:
```
Total Pipeline Time: 100%
├── HTML → Dict:      ??%
├── Dict → MGraph:    ??%
├── Phase E Process:  ??%
│   ├── Extract:      ??%
│   ├── Merge:        ??%
│   ├── Decision:     ??%
│   └── Delete:       ??%
└── MGraph → HTML:    ??%
```

### Scaling Behavior

Determine complexity class for each stage:
- O(n) linear - good
- O(n log n) - acceptable
- O(n²) quadratic - bottleneck

---

## Tooling

| Tool | Purpose |
|------|---------|
| `Perf` | Individual method timing with nanosecond precision |
| `Perf_Benchmark__Timing` | Structured benchmark suites |
| `measure__quick()` | For slow operations (>100ms) |

---

## Deliverables

1. **Html_Generator__For_Benchmarks** - Generate controlled test HTML
2. **Perf__Phase_E__Conversion** - Focus on the 3 main conversions
3. **Perf__Phase_E__Pipeline** - Full pipeline benchmarks
4. **Perf__Phase_E__Scalability** - Scaling analysis across sizes
5. **PHASE_E_1__debrief.md** - Results, findings, recommendations

---

## Success Criteria

- [ ] Measure all 3 conversion stages independently
- [ ] Test scaling from 10 to 10,000 nodes
- [ ] Identify bottlenecks (if any)
- [ ] Reproducible benchmark results
- [ ] Clear performance report
