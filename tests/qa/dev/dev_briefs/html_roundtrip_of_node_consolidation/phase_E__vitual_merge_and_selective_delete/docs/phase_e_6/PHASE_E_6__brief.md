# PHASE E_6: End-to-End Pipeline Performance Benchmarks

**Status**: Brief  
**Date**: January 2026  
**Predecessor**: Phase E_5 (URL Fetching + L5 Transformations)  
**Methodology**: Follow the Rabbit Hole (from Phase E_2)

---

## 1. Objective

Establish performance baselines for the complete LETS pipeline and identify optimization opportunities. This phase applies the systematic benchmarking methodology developed in E_2 to the full pipeline code built in E_5.

**Primary Goals:**
1. Measure time spent in each pipeline stage (L1, L2, L3, L5/c)
2. Break down `transform__phase_e0_filtered` (L5/c) into component costs
3. Quantify cache hit vs miss performance impact
4. Validate linear scaling behavior across HTML sizes
5. Compare performance across cache backends (in-memory, local, live)

---

## 2. Scope

### 2.1 Priority Order

| Priority | Area | Description |
|----------|------|-------------|
| **P1** | Pipeline Stages | Time spent in L1 (parse), L2 (graph), L3 (reconstruct), L5/c (filter) |
| **P2** | Phase E_0 Breakdown | Decompose `transform__phase_e0_filtered` into: extract → merge → classify → delete → reconstruct |
| **P3** | Cache Hit vs Miss | Compare first-request vs cached-request latency |
| **P4** | Scaling Analysis | Measure 10, 50, 100, 500, 1000 node HTML processing |
| **P5** | Cache Backend Comparison | In-memory vs local server vs live serverless |

### 2.2 Out of Scope

- L5/a, L5/b, L5/d transformations (covered implicitly in L5/c baseline)
- Network fetching (L0) - too variable for reproducible benchmarks
- ML/LLM decision engines - only hash-based for deterministic results

---

## 3. Test Infrastructure

### 3.1 Data Source

**Synthetic HTML** using `Html_Generator__For_Benchmarks`:

```python
from phase_e.performance.Html_Generator__For_Benchmarks import Html_Generator__For_Benchmarks

generator = Html_Generator__For_Benchmarks()

# Preset sizes available:
html_10    = generator.generate__10()      # ~10 paragraphs
html_50    = generator.generate__50()      # ~50 paragraphs  
html_100   = generator.generate__100()     # ~100 paragraphs
html_500   = generator.generate__500()     # ~500 paragraphs
html_1_000 = generator.generate__1_000()   # ~1,000 paragraphs
```

**Rationale:** Synthetic HTML provides reproducible benchmarks without network variability.

### 3.2 Cache Backends (Three Configurations)

| Backend | Use Case | Configuration |
|---------|----------|---------------|
| **In-Memory** | Fast, reproducible unit tests | `client_cache_service()` from `Phase_E__Fast_API__Test_Objs.py` |
| **Local Server** | Integration testing | `http://localhost:10017` |
| **Live Serverless** | Production baseline | `https://cache.dev.mgraph.ai` |

```python
# In-memory (start here)
from phase_e.test_fixtures.Phase_E__Fast_API__Test_Objs import client_cache_service
cache_client, cache_service = client_cache_service()

# Local server
from mgraph_ai_service_cache_client.client.Client__Cache__Service import Client__Cache__Service
client = Client__Cache__Service()
client.setup(base_url='http://localhost:10017')

# Live serverless
client = Client__Cache__Service()
client.setup(base_url='https://cache.dev.mgraph.ai')
```

### 3.3 Reporting Framework

Use existing `Perf_Report__Builder` infrastructure from Phase E_2:

```python
from phase_e.report.builder.Perf_Report__Builder import Perf_Report__Builder
from phase_e.report.storage.Perf_Report__Storage__File_System import Perf_Report__Storage__File_System
from phase_e.report.renderers.Perf_Report__Renderer__Text import Perf_Report__Renderer__Text
```

**Output Location:** `phase_e/data/perf_results/`

---

## 4. Test Plan

### 4.1 Test File Sequence

Each test file builds on the previous, allowing incremental refinement:

| Order | File | Focus | Depends On |
|-------|------|-------|------------|
| 1 | `test_perf__Phase_E_6__1__Pipeline_Stages.py` | L1→L2→L3 breakdown | - |
| 2 | `test_perf__Phase_E_6__2__Phase_E0_Breakdown.py` | L5/c component costs | Test 1 |
| 3 | `test_perf__Phase_E_6__3__Cache_Hit_Miss.py` | Cache performance impact | Test 1 |
| 4 | `test_perf__Phase_E_6__4__Scaling.py` | Size-based scaling | Test 1 |
| 5 | `test_perf__Phase_E_6__5__Backend_Comparison.py` | In-memory vs local vs live | Tests 1-4 |

### 4.2 Test 1: Pipeline Stages Breakdown

**Goal:** Measure time in each pipeline stage independently.

```
Section A: Pipeline Stage Isolation (100 nodes)
───────────────────────────────────────────────
A_01: L1 - Html__To__Html_Dict__With__Node_Ids.convert()
A_02: L2 - Html__To__Html_MGraph__Document__Node_Id_Reuse.convert_from_dict()
A_03: L3 - Html_MGraph__Document__To__Html__With_Original_Head.convert()
A_04: Full L1→L2→L3 pipeline (reference - should ≈ A_01 + A_02 + A_03)
```

**Key Classes:**
- `Html__To__Html_Dict__With__Node_Ids` - L1 parsing
- `Html__To__Html_MGraph__Document__Node_Id_Reuse` - L2 graph construction
- `Html_MGraph__Document__To__Html__With_Original_Head` - L3 reconstruction

**Report Key:** `perf_6_1__pipeline_stages__100_nodes`

### 4.3 Test 2: Phase E_0 Filtered Breakdown

**Goal:** Decompose `transform__phase_e0_filtered` into component costs.

```
Section A: L5/c Component Breakdown (100 nodes)
───────────────────────────────────────────────
A_01: Fresh MGraph creation (Html__To__Html_MGraph__Document__Node_Id_Reuse)
A_02: Phase_E__Text_Extractor.extract()
A_03: Phase_E__Virtual_Merger.merge()
A_04: Phase_E__Decision_Engine__Hash_Based.classify_all()
A_05: Phase_E__Node_Deleter.delete()
A_06: Html_MGraph__Document__To__Html__With_Original_Head.convert()
A_07: Full transform__phase_e0_filtered() (reference)
```

**Key Classes:**
- `Phase_E__Text_Extractor`
- `Phase_E__Virtual_Merger`
- `Phase_E__Decision_Engine__Hash_Based`
- `Phase_E__Node_Deleter`

**Report Key:** `perf_6_2__phase_e0_breakdown__100_nodes`

### 4.4 Test 3: Cache Hit vs Miss

**Goal:** Quantify cache performance benefit.

```
Section A: Cache Miss (First Request)
─────────────────────────────────────
A_01: Create cache entry
A_02: Save L1 (raw HTML)
A_03: Save L2 (html_dict)
A_04: Save L3 (MGraph document)
A_05: Full save pipeline

Section B: Cache Hit (Subsequent Request)
─────────────────────────────────────────
B_01: Load L1 from cache
B_02: Load L2 from cache
B_03: Load L3 from cache
B_04: Full load pipeline
```

**Report Key:** `perf_6_3__cache_hit_miss__100_nodes`

### 4.5 Test 4: Scaling Analysis

**Goal:** Validate linear scaling and identify non-linear bottlenecks.

```
Section A: Full Pipeline at Different Sizes
───────────────────────────────────────────
A_01: 10 nodes   (L1→L2→L3)
A_02: 50 nodes   (L1→L2→L3)
A_03: 100 nodes  (L1→L2→L3)
A_04: 500 nodes  (L1→L2→L3)
A_05: 1000 nodes (L1→L2→L3)

Section B: L5/c at Different Sizes
──────────────────────────────────
B_01: 10 nodes   (transform__phase_e0_filtered)
B_02: 50 nodes   (transform__phase_e0_filtered)
B_03: 100 nodes  (transform__phase_e0_filtered)
B_04: 500 nodes  (transform__phase_e0_filtered)
B_05: 1000 nodes (transform__phase_e0_filtered)
```

**Expected:** Linear scaling (100 nodes ≈ 10x cost of 10 nodes)

**Report Key:** `perf_6_4__scaling__10_to_1000_nodes`

### 4.6 Test 5: Backend Comparison

**Goal:** Compare cache backend performance.

```
Section A: In-Memory Cache (100 nodes)
──────────────────────────────────────
A_01: Save pipeline
A_02: Load pipeline

Section B: Local Server Cache (100 nodes)
─────────────────────────────────────────
B_01: Save pipeline
B_02: Load pipeline

Section C: Live Serverless Cache (100 nodes)
────────────────────────────────────────────
C_01: Save pipeline
C_02: Load pipeline
```

**Report Key:** `perf_6_5__backend_comparison__100_nodes`

---

## 5. State Factory Pattern

Following E_2 methodology, each benchmark requires exact state from previous stages:

```python
class Pipeline__State_Factory:
    """Creates state at each pipeline stage for isolated measurement."""
    
    def __init__(self, html: str):
        self.html = html
    
    def state_for_L1(self) -> dict:
        """Before L1 - just raw HTML."""
        return {'html': self.html}
    
    def state_for_L2(self) -> dict:
        """After L1 - HTML parsed to dict."""
        html_dict = Html__To__Html_Dict__With__Node_Ids(html=self.html).convert()
        return {'html': self.html, 'html_dict': html_dict}
    
    def state_for_L3(self) -> dict:
        """After L2 - MGraph document created."""
        html_dict = Html__To__Html_Dict__With__Node_Ids(html=self.html).convert()
        document  = Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(html_dict)
        return {'html': self.html, 'html_dict': html_dict, 'document': document}
    
    def state_for_L5c(self) -> dict:
        """After L3 - ready for Phase E_0 filtering."""
        html_dict = Html__To__Html_Dict__With__Node_Ids(html=self.html).convert()
        document  = Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(html_dict)
        return {'html': self.html, 'html_dict': html_dict, 'document': document}
```

---

## 6. Expected Outputs

### 6.1 Report Files

Each test generates reports in multiple formats:

```
phase_e/data/perf_results/
├── perf_6_1__pipeline_stages__100_nodes.txt
├── perf_6_1__pipeline_stages__100_nodes.md
├── perf_6_1__pipeline_stages__100_nodes.json
├── perf_6_2__phase_e0_breakdown__100_nodes.txt
├── perf_6_2__phase_e0_breakdown__100_nodes.md
├── perf_6_2__phase_e0_breakdown__100_nodes.json
├── perf_6_3__cache_hit_miss__100_nodes.txt
├── perf_6_4__scaling__10_to_1000_nodes.txt
└── perf_6_5__backend_comparison__100_nodes.txt
```

### 6.2 Expected Metrics

Based on E_2 findings (~100µs per element after optimization):

| Stage | 100 Nodes (Expected) | Notes |
|-------|---------------------|-------|
| L1 (Parse) | ~5-10ms | BeautifulSoup parsing |
| L2 (Graph) | ~10-30ms | MGraph construction (was 76ms before E_2 fix) |
| L3 (Reconstruct) | ~5-10ms | HTML generation |
| L5/c (Filter) | ~20-50ms | Includes fresh L2 + Phase E_0 pipeline |

### 6.3 Validation Checks

Each test should validate:

1. **Sum of Parts ≈ Whole**: `A_01 + A_02 + A_03 ≈ A_04`
2. **Linear Scaling**: `500 nodes ≈ 5x × 100 nodes`
3. **Cache Hit < Cache Miss**: Loading should be faster than saving
4. **Reproducibility**: Same inputs produce consistent timings (within 10%)

---

## 7. Implementation Sequence

### Phase 1: Foundation (Test 1)
1. Create `test_perf__Phase_E_6__1__Pipeline_Stages.py`
2. Implement state factory
3. Run benchmarks with in-memory cache
4. Capture baseline metrics
5. Review results, adjust if needed

### Phase 2: Deep Dive (Test 2)
1. Create `test_perf__Phase_E_6__2__Phase_E0_Breakdown.py`
2. Break down L5/c into components
3. Identify dominant cost within Phase E_0
4. Document findings

### Phase 3: Cache Analysis (Test 3)
1. Create `test_perf__Phase_E_6__3__Cache_Hit_Miss.py`
2. Measure save vs load operations
3. Calculate cache benefit ratio

### Phase 4: Scaling Validation (Test 4)
1. Create `test_perf__Phase_E_6__4__Scaling.py`
2. Test 10 → 1000 nodes
3. Plot scaling curve
4. Identify any non-linear behavior

### Phase 5: Backend Comparison (Test 5)
1. Create `test_perf__Phase_E_6__5__Backend_Comparison.py`
2. Test all three backends
3. Document latency differences

---

## 8. Success Criteria

1. **Baseline Established**: All pipeline stages have documented timing baselines
2. **Bottlenecks Identified**: Clear identification of which stage(s) dominate total time
3. **Linear Scaling Confirmed**: No O(n²) or worse behavior detected
4. **Cache Benefit Quantified**: Know the speedup from cache hits vs misses
5. **Reports Generated**: All benchmark reports saved to `perf_results/`

---

## 9. Dependencies

### Required Packages
```python
# HTML Processing
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_Dict__With__Node_Ids import Html__To__Html_Dict__With__Node_Ids
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document__Node_Id_Reuse import Html__To__Html_MGraph__Document__Node_Id_Reuse

# Phase E_0 Components
from phase_e.core.Phase_E__Text_Extractor import Phase_E__Text_Extractor
from phase_e.core.Phase_E__Virtual_Merger import Phase_E__Virtual_Merger
from phase_e.core.Phase_E__Node_Deleter import Phase_E__Node_Deleter
from phase_e.decision.Phase_E__Decision_Engine__Hash_Based import Phase_E__Decision_Engine__Hash_Based
from phase_e.mgraph.Html_MGraph__Document__To__Html__With_Original_Head import Html_MGraph__Document__To__Html__With_Original_Head

# Performance Infrastructure
from phase_e.performance.Html_Generator__For_Benchmarks import Html_Generator__For_Benchmarks
from phase_e.report.builder.Perf_Report__Builder import Perf_Report__Builder
from phase_e.report.storage.Perf_Report__Storage__File_System import Perf_Report__Storage__File_System

# Cache Service
from phase_e.test_fixtures.Phase_E__Fast_API__Test_Objs import client_cache_service
```

### External Services (for Tests 5)
- Local cache server: `http://localhost:10017`
- Live cache server: `https://cache.dev.mgraph.ai`

---

## 10. Notes

- Start with **in-memory cache** for reproducibility
- Use **`@type_safe_fast_create`** decorator on test methods (from E_2 learnings)
- Use **`graph_deterministic_ids()`** context manager for reproducible node IDs
- Save reports in **`.txt` format first** for quick iteration, add `.md` and `.json` once stable
- Each test file should be **self-contained** and runnable independently

---

*Brief complete. Ready to implement Test 1.*
