# Phase E_7: HTML Processing Pipeline with Full Caching

**Status**: 📋 Planning  
**Depends On**: Phase E_4 ✅ (Caching), Phase E_5 ✅ (URL Fetching), Phase E_0 ✅ (Processing)

---

## Objective

> Build a complete HTML processing pipeline that fetches URLs, processes content through virtual merge + selective delete, and caches results at every stage for maximum efficiency.

**Key Value**: When processing thousands of pages, expensive operations (parsing, MGraph creation, LLM-based decisions) only happen once. Subsequent runs are instant cache hits.

---

## The Problem

Processing HTML at scale involves multiple expensive operations:

| Operation | Cost | Frequency |
|-----------|------|-----------|
| HTTP Fetch | ~100-500ms | Per URL |
| HTML Parse | ~10ms | Per page |
| MGraph Creation | ~30ms | Per page |
| Text Extraction | ~5ms | Per page |
| Virtual Merge | ~2ms | Per page |
| **LLM Decision** | **~500-2000ms** | **Per text block** |
| Node Deletion | ~1ms | Per decision |
| HTML Output | ~5ms | Per page |

Without caching, processing 1000 pages with LLM decisions:
- **1000 × (100 + 10 + 30 + 5 + 2 + 500 + 1 + 5) = ~653 seconds = ~11 minutes**

With full caching (after first run):
- **1000 × ~1ms (cache lookup) = ~1 second**

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              PHASE E_7: HTML PROCESSING PIPELINE WITH CACHING               │
└─────────────────────────────────────────────────────────────────────────────┘

URL
 │
 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  L0: URL Layer (from E_5)                                                   │
│  Cache: URL metadata, ETag, Last-Modified                                   │
│  Key: {session}/{target}/L0/url_info.json                                   │
└─────────────────────────────────────────────────────────────────────────────┘
 │
 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  L1: Raw HTML Layer (from E_4)                                              │
│  Cache: HTML string                                                         │
│  Key: {session}/{target}/L1/raw.html                                        │
└─────────────────────────────────────────────────────────────────────────────┘
 │
 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  L2: Parsed Dict Layer (from E_4)                                           │
│  Cache: HTML dict with node_ids                                             │
│  Key: {session}/{target}/L2/dict.json                                       │
└─────────────────────────────────────────────────────────────────────────────┘
 │
 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  L3: MGraph Document Layer (from E_4)                                       │
│  Cache: Html_MGraph__Document (original, unprocessed)                       │
│  Key: {session}/{target}/L3/document.json                                   │
└─────────────────────────────────────────────────────────────────────────────┘
 │
 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  L4: Analysis Layer (NEW)                                                   │
│  Cache: text_nodes + merged_texts (lightweight, fast to recompute)          │
│  Key: {session}/{target}/L4/analysis.json                                   │
│                                                                             │
│  { text_nodes: { node_id: { text, parent_id } },                           │
│    merged_texts: { parent_id: { merged_text, source_node_ids } } }         │
└─────────────────────────────────────────────────────────────────────────────┘
 │
 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  L5: Decisions Layer (NEW) ⭐ CRITICAL FOR LLM CACHING                      │
│  Cache: Decision results per parent_id                                      │
│  Key: {session}/{target}/L5/decisions.json                                  │
│                                                                             │
│  { parent_id: { keep: bool, score: float, reason: str } }                  │
│                                                                             │
│  Also stores: decision_engine_type, threshold, model_version               │
│  Invalidation: Changes when decision engine config changes                  │
└─────────────────────────────────────────────────────────────────────────────┘
 │
 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  L6: Processed Document Layer (NEW)                                         │
│  Cache: Html_MGraph__Document (after node deletions)                        │
│  Key: {session}/{target}/L6/processed.json                                  │
│                                                                             │
│  Invalidation: Changes when L5 decisions change                             │
└─────────────────────────────────────────────────────────────────────────────┘
 │
 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  L7: Clean HTML Layer (NEW)                                                 │
│  Cache: Final HTML string output                                            │
│  Key: {session}/{target}/L7/clean.html                                      │
│                                                                             │
│  Invalidation: Changes when L6 document changes                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Cache Invalidation Strategy

### Content-Based Invalidation

Each layer stores a `content_hash` of its input. If the input hash changes, the cached output is invalid.

```
L1 hash = hash(HTML)
L2 hash = hash(L1_output)
L3 hash = hash(L2_output)
L4 hash = hash(L3_output)
L5 hash = hash(L4_output + decision_engine_config)  ← Config matters!
L6 hash = hash(L5_output)
L7 hash = hash(L6_output)
```

### Decision Engine Config Tracking

L5 (Decisions) includes engine configuration in its hash:

```python
decision_config = {
    'engine_type' : 'hash_based',      # or 'llm_based', 'ml_based'
    'threshold'   : 0.5,
    'model'       : None,               # e.g., 'claude-3-haiku' for LLM
    'version'     : '1.0.0',
}

l5_hash = hash(l4_output + json.dumps(decision_config, sort_keys=True))
```

When you change decision engine settings, L5-L7 are invalidated but L0-L4 remain cached.

---

## Layer Dependencies

```
L0 ─► L1 ─► L2 ─► L3 ─► L4 ─► L5 ─► L6 ─► L7
URL   HTML  Dict  MGraph Analysis Decisions Processed Clean
                                     │
                                     └─ Depends on decision_engine_config
```

### Cascade Behavior

| If this changes... | These layers are invalidated |
|--------------------|------------------------------|
| URL content | L1, L2, L3, L4, L5, L6, L7 |
| Parse logic | L2, L3, L4, L5, L6, L7 |
| MGraph creation | L3, L4, L5, L6, L7 |
| Text extraction | L4, L5, L6, L7 |
| Decision engine config | L5, L6, L7 |
| Decision threshold | L5, L6, L7 |
| Nothing (re-run) | All cache hits! |

---

## Class Design

### Core Classes

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CLASS HIERARCHY                                    │
└─────────────────────────────────────────────────────────────────────────────┘

Html_Processing__Pipeline                       Main orchestrator
    │
    ├── Html_Cache__Manager__With_Processing    Extended cache manager
    │       │
    │       ├── layer_url      (L0)             From E_5
    │       ├── layer_html     (L1)             From E_4
    │       ├── layer_dict     (L2)             From E_4
    │       ├── layer_mgraph   (L3)             From E_4
    │       ├── layer_analysis (L4)             NEW
    │       ├── layer_decisions(L5)             NEW
    │       ├── layer_processed(L6)             NEW
    │       └── layer_clean    (L7)             NEW
    │
    ├── Phase_E__Text_Extractor                 From E_0
    ├── Phase_E__Virtual_Merger                 From E_0
    ├── Phase_E__Decision_Engine__Base          From E_0 (pluggable)
    │       ├── Phase_E__Decision_Engine__Hash_Based
    │       ├── Phase_E__Decision_Engine__ML_Based      (future)
    │       └── Phase_E__Decision_Engine__LLM_Based     (future)
    └── Phase_E__Node_Deleter                   From E_0
```

### New Layer Classes

```python
# L4: Analysis Layer
class Html_Cache__Layer__Analysis(Html_Cache__Layer__Base):
    layer_name: str = 'L4'
    
    def save(self, text_nodes: dict, merged_texts: dict) -> bool
    def load(self) -> Optional[Tuple[dict, dict]]
    def build_from_mgraph(self, document) -> Tuple[dict, dict]

# L5: Decisions Layer
class Html_Cache__Layer__Decisions(Html_Cache__Layer__Base):
    layer_name: str = 'L5'
    
    decision_engine: Phase_E__Decision_Engine__Base
    
    def save(self, decisions: dict, engine_config: dict) -> bool
    def load(self) -> Optional[dict]
    def build_from_analysis(self, merged_texts: dict) -> dict
    def is_valid_for_config(self, engine_config: dict) -> bool

# L6: Processed Document Layer
class Html_Cache__Layer__Processed(Html_Cache__Layer__Base):
    layer_name: str = 'L6'
    
    def save(self, document) -> bool
    def load(self) -> Optional[Html_MGraph__Document]
    def build_from_decisions(self, original_doc, decisions: dict) -> Html_MGraph__Document

# L7: Clean HTML Layer
class Html_Cache__Layer__Clean(Html_Cache__Layer__Base):
    layer_name: str = 'L7'
    
    def save(self, clean_html: str) -> bool
    def load(self) -> Optional[str]
    def build_from_processed(self, document) -> str
```

---

## Extended Cache Manager

```python
class Html_Cache__Manager__With_Processing(Html_Cache__Manager__With_Urls):
    """Full processing pipeline with caching at every layer."""
    
    # New layers
    layer_analysis  : Html_Cache__Layer__Analysis  = None
    layer_decisions : Html_Cache__Layer__Decisions = None
    layer_processed : Html_Cache__Layer__Processed = None
    layer_clean     : Html_Cache__Layer__Clean     = None
    
    # Decision engine (pluggable)
    decision_engine : Phase_E__Decision_Engine__Base = None
    
    # ═══════════════════════════════════════════════════════════════════════
    # High-Level API
    # ═══════════════════════════════════════════════════════════════════════
    
    def process_url(self, url: str, force_refresh: bool = False) -> str:
        """Full pipeline: URL → Clean HTML (with caching)."""
        pass
    
    def process_urls(self, urls: list, force_refresh: bool = False) -> dict:
        """Batch process multiple URLs."""
        pass
    
    def get_clean_html(self, target: str) -> Optional[str]:
        """Get cached clean HTML for target."""
        pass
    
    def get_decisions(self, target: str) -> Optional[dict]:
        """Get cached decisions for target."""
        pass
    
    # ═══════════════════════════════════════════════════════════════════════
    # Layer-Specific Access
    # ═══════════════════════════════════════════════════════════════════════
    
    def get_analysis(self, target: str) -> Optional[Tuple[dict, dict]]:
        """Get cached analysis (text_nodes, merged_texts)."""
        pass
    
    def get_processed_mgraph(self, target: str) -> Optional[Html_MGraph__Document]:
        """Get cached processed document."""
        pass
    
    # ═══════════════════════════════════════════════════════════════════════
    # Decision Engine Management
    # ═══════════════════════════════════════════════════════════════════════
    
    def set_decision_engine(self, engine: Phase_E__Decision_Engine__Base):
        """Set decision engine (invalidates L5-L7 cache)."""
        pass
    
    def get_decision_engine_config(self) -> dict:
        """Get current engine config for cache key."""
        pass
```

---

## Main Pipeline Class

```python
class Html_Processing__Pipeline(Type_Safe):
    """Orchestrates full HTML processing with caching."""
    
    cache_manager   : Html_Cache__Manager__With_Processing
    decision_engine : Phase_E__Decision_Engine__Base = None
    
    def setup(self) -> 'Html_Processing__Pipeline':
        """Initialize with default hash-based decision engine."""
        if self.decision_engine is None:
            self.decision_engine = Phase_E__Decision_Engine__Hash_Based()
        
        self.cache_manager.decision_engine = self.decision_engine
        return self
    
    # ═══════════════════════════════════════════════════════════════════════
    # Main Processing Methods
    # ═══════════════════════════════════════════════════════════════════════
    
    def process_url(self, url: str) -> Schema__Processing_Result:
        """Process single URL through full pipeline."""
        pass
    
    def process_urls(self, urls: list) -> Schema__Batch_Result:
        """Process multiple URLs with progress tracking."""
        pass
    
    def process_html(self, html: str, target: str) -> str:
        """Process raw HTML (no fetching)."""
        pass
    
    # ═══════════════════════════════════════════════════════════════════════
    # Inspection Methods
    # ═══════════════════════════════════════════════════════════════════════
    
    def get_pipeline_status(self, target: str) -> dict:
        """Get cache status for all layers."""
        pass
    
    def get_processing_details(self, target: str) -> dict:
        """Get full processing details (all intermediate results)."""
        pass
```

---

## Data Structures

### Schema Definitions

```python
class Schema__Phase_E_7__Analysis_Result(Type_Safe):
    text_nodes   : dict = None   # { node_id: { text, parent_id } }
    merged_texts : dict = None   # { parent_id: { merged_text, source_node_ids } }
    cached_at    : float = 0.0
    input_hash   : str = ''      # Hash of L3 document

class Schema__Phase_E_7__Decision_Cache(Type_Safe):
    decisions      : dict = None   # { parent_id: { keep, score, reason } }
    engine_type    : str = ''      # 'hash_based', 'llm_based', etc.
    engine_config  : dict = None   # Threshold, model, etc.
    cached_at      : float = 0.0
    input_hash     : str = ''      # Hash of L4 analysis + engine_config

class Schema__Phase_E_7__Processing_Result(Type_Safe):
    url            : str = ''
    target         : str = ''
    clean_html     : str = ''
    stats          : dict = None   # Processing statistics
    cache_hits     : dict = None   # Which layers were cache hits
    elapsed_ms     : float = 0.0

class Schema__Phase_E_7__Batch_Result(Type_Safe):
    total          : int = 0
    success        : int = 0
    failed         : int = 0
    cache_hits     : int = 0       # Full pipeline cache hits
    partial_hits   : int = 0       # Some layers cached
    fresh_builds   : int = 0       # Full pipeline builds
    details        : list = None   # Per-URL results
    elapsed_ms     : float = 0.0
```

---

## Storage Key Convention

```
session: phase-e-6
target:  example-com-page1

L0/url_info.json           # URL metadata (from E_5)
L1/raw.html                # Raw HTML (from E_4)
L2/dict.json               # Parsed dict (from E_4)
L3/document.json           # Original MGraph (from E_4)
L4/analysis.json           # Text nodes + merged texts (NEW)
L4/metadata.json           # { input_hash, cached_at }
L5/decisions.json          # Decision results (NEW)
L5/metadata.json           # { input_hash, engine_config, cached_at }
L6/processed.json          # Processed MGraph (NEW)
L6/metadata.json           # { input_hash, cached_at }
L7/clean.html              # Final clean HTML (NEW)
L7/metadata.json           # { input_hash, cached_at }
```

---

## Files to Create

| File | Purpose |
|------|---------|
| **Documentation** | |
| `PHASE_E_7__brief.md` | This document |
| **Schemas** | |
| `Schema__Phase_E_7__Analysis.py` | Analysis result schema |
| `Schema__Phase_E_7__Decisions.py` | Decision cache schema |
| `Schema__Phase_E_7__Processing.py` | Processing result schemas |
| **Layers** | |
| `Html_Cache__Layer__Analysis.py` | L4: Analysis caching |
| `Html_Cache__Layer__Decisions.py` | L5: Decision caching |
| `Html_Cache__Layer__Processed.py` | L6: Processed document caching |
| `Html_Cache__Layer__Clean.py` | L7: Clean HTML caching |
| **Manager** | |
| `Html_Cache__Manager__With_Processing.py` | Extended manager |
| **Pipeline** | |
| `Html_Processing__Pipeline.py` | Main orchestrator |
| **Tests** | |
| `test_Html_Cache__Layer__Analysis.py` | L4 tests |
| `test_Html_Cache__Layer__Decisions.py` | L5 tests |
| `test_Html_Cache__Layer__Processed.py` | L6 tests |
| `test_Html_Cache__Layer__Clean.py` | L7 tests |
| `test_Html_Cache__Manager__With_Processing.py` | Manager tests |
| `test_Html_Processing__Pipeline.py` | Pipeline integration tests |

---

## Example Walkthrough

### First Run (Cold Cache)

```python
pipeline = Html_Processing__Pipeline(
    cache_manager   = Html_Cache__Manager__With_Processing(storage=storage, fetcher=fetcher),
    decision_engine = Phase_E__Decision_Engine__Hash_Based(threshold=0.5)
).setup()

result = pipeline.process_url('https://example.com/article')

# Layers built:
# L0: Fetched URL         → 150ms
# L1: Cached HTML         → 0ms (just save)
# L2: Parsed to dict      → 10ms
# L3: Created MGraph      → 30ms
# L4: Extracted/merged    → 7ms
# L5: Made decisions      → 2ms (hash-based)
# L6: Deleted nodes       → 1ms
# L7: Generated HTML      → 5ms
# ─────────────────────────────────
# Total:                  → ~205ms

print(result.cache_hits)
# {'L0': False, 'L1': False, 'L2': False, 'L3': False, 
#  'L4': False, 'L5': False, 'L6': False, 'L7': False}
```

### Second Run (Full Cache Hit)

```python
result = pipeline.process_url('https://example.com/article')

# All layers cached:
# L7: Cache hit           → 1ms (just load clean HTML)
# ─────────────────────────────────
# Total:                  → ~1ms

print(result.cache_hits)
# {'L0': True, 'L1': True, 'L2': True, 'L3': True, 
#  'L4': True, 'L5': True, 'L6': True, 'L7': True}
```

### After Changing Decision Threshold

```python
pipeline.set_decision_engine(Phase_E__Decision_Engine__Hash_Based(threshold=0.7))

result = pipeline.process_url('https://example.com/article')

# L0-L4: Cache hits       → ~1ms
# L5: Rebuilt decisions   → 2ms (new threshold)
# L6: Rebuilt processed   → 1ms
# L7: Rebuilt clean HTML  → 5ms
# ─────────────────────────────────
# Total:                  → ~9ms

print(result.cache_hits)
# {'L0': True, 'L1': True, 'L2': True, 'L3': True, 
#  'L4': True, 'L5': False, 'L6': False, 'L7': False}
```

### With LLM Decision Engine (Expensive)

```python
pipeline.set_decision_engine(Phase_E__Decision_Engine__LLM_Based(
    model     = 'claude-3-haiku',
    threshold = 0.6
))

# First run: Each text block → LLM call (~500ms each)
# 20 text blocks × 500ms = 10 seconds for decisions alone

result = pipeline.process_url('https://example.com/article')
# Total: ~10,500ms

# Second run: L5 cache hit, no LLM calls
result = pipeline.process_url('https://example.com/article')
# Total: ~1ms
```

---

## Batch Processing Example

```python
urls = [
    'https://example.com/article-1',
    'https://example.com/article-2',
    'https://example.com/article-3',
    # ... 997 more URLs
]

# First batch run
result = pipeline.process_urls(urls)

print(result)
# Schema__Phase_E_7__Batch_Result(
#     total       = 1000,
#     success     = 998,
#     failed      = 2,
#     cache_hits  = 0,
#     fresh_builds= 998,
#     elapsed_ms  = 205000  # ~205 seconds
# )

# Second batch run (all cached)
result = pipeline.process_urls(urls)

print(result)
# Schema__Phase_E_7__Batch_Result(
#     total       = 1000,
#     success     = 998,
#     failed      = 2,
#     cache_hits  = 998,
#     fresh_builds= 0,
#     elapsed_ms  = 1000    # ~1 second
# )
```

---

## Test Cases

### Layer Tests

| Test | Description |
|------|-------------|
| `test_layer_analysis__build_from_mgraph` | L4 builds correctly from L3 |
| `test_layer_analysis__roundtrip` | L4 save/load preserves data |
| `test_layer_decisions__with_hash_engine` | L5 works with hash engine |
| `test_layer_decisions__config_invalidation` | L5 invalidates on config change |
| `test_layer_processed__applies_deletions` | L6 correctly deletes nodes |
| `test_layer_clean__valid_html` | L7 produces valid HTML |

### Pipeline Tests

| Test | Description |
|------|-------------|
| `test_pipeline__full_cache_miss` | Cold cache builds all layers |
| `test_pipeline__full_cache_hit` | Warm cache returns L7 instantly |
| `test_pipeline__partial_cache_hit` | Config change rebuilds L5-L7 only |
| `test_pipeline__batch_processing` | Multiple URLs processed correctly |
| `test_pipeline__error_handling` | Failed URLs don't break batch |
| `test_pipeline__decision_engine_swap` | Engine swap invalidates correctly |

### Integration Tests

| Test | Description |
|------|-------------|
| `test_integration__real_html` | Process real-world HTML |
| `test_integration__cache_service` | Works with cache service backend |
| `test_integration__with_mock_fetcher` | Full pipeline with mock HTTP |

---

## Success Criteria

1. ✅ All 7 cache layers work independently
2. ✅ Cache invalidation cascades correctly
3. ✅ Decision engine config changes invalidate L5-L7 only
4. ✅ Batch processing handles errors gracefully
5. ✅ Full cache hit returns in <5ms
6. ✅ Pipeline produces valid, clean HTML
7. ✅ All tests pass with memory, local, and cache service backends

---

## Future Extensions

| Extension | Description |
|-----------|-------------|
| `Phase_E__Decision_Engine__ML_Based` | Trained classifier for content detection |
| `Phase_E__Decision_Engine__LLM_Based` | LLM prompt-based classification |
| Parallel batch processing | Process multiple URLs concurrently |
| Progress callbacks | Real-time progress for batch jobs |
| Incremental updates | Only reprocess changed pages |
| Site-wide deduplication | Share decisions across similar pages |
| Export to formats | JSON, Markdown, plain text output |

---

## Dependencies

- Phase E_4: `Html_Cache__Manager`, L1-L3 layers
- Phase E_5: `Html_Cache__Manager__With_Urls`, L0 layer, `Html_Fetcher`
- Phase E_0: `Phase_E__Text_Extractor`, `Phase_E__Virtual_Merger`, `Phase_E__Node_Deleter`, `Phase_E__Decision_Engine__*`
- Core: `MGraph`, `Html_MGraph__Document`

---

## Next Steps

1. Create schemas for L4-L7 metadata
2. Implement L4 (Analysis) layer with tests
3. Implement L5 (Decisions) layer with tests
4. Implement L6 (Processed) layer with tests
5. Implement L7 (Clean) layer with tests
6. Implement extended cache manager with tests
7. Implement main pipeline with tests
8. Write `PHASE_E_7__debrief.md`
