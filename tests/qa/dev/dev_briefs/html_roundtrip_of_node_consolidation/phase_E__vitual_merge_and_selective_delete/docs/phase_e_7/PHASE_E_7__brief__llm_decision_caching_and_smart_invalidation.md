# Phase E_7: LLM Decision Caching & Smart Invalidation

**Status**: 📋 Planning  
**Depends On**: Phase E_5 ✅ (Full Pipeline with L5 Transformations)

---

## Objective

> Extend the L5 transformation layer with granular caching of intermediate processing steps, enabling efficient LLM-based decision engines where expensive API calls are cached and only invalidated when inputs change.

**Key Value**: When using LLM-based content filtering (~500-2000ms per text block), decisions are cached so subsequent runs are instant. Changing the decision threshold only rebuilds decisions, not the entire pipeline.

---

## The Problem

Current L5 transformation runs the full Phase E_0 pipeline every time:

```
L3 (MGraph) → Extract Text → Merge → Decide → Delete → L5/c-phase-e0-filtered.json
                                       │
                                       └── With LLM: ~500ms × 50 text blocks = 25 seconds
```

**Issues:**
1. LLM decisions are expensive (~$0.001-0.01 per block + latency)
2. Re-running pipeline recalculates everything, even if only threshold changed
3. No way to inspect decisions without re-running
4. No audit trail of what was decided and why

---

## Solution: L5 Sub-Layer Architecture

```
L5/
├── a-original-reconstructed.json     ← Existing (final output)
├── b-body-only.json                  ← Existing (final output)
├── c-phase-e0-filtered.json          ← Existing (final output)
├── d-text-content.json               ← Existing (final output)
│
├── _analysis/                        ← NEW: Intermediate cache
│   ├── text-nodes.json               ← Extracted text nodes
│   ├── merged-texts.json             ← Virtual merge results
│   └── metadata.json                 ← Input hash, timestamps
│
├── _decisions/                       ← NEW: Decision cache
│   ├── results.json                  ← Keep/delete decisions per parent
│   ├── engine-config.json            ← Engine type, threshold, model
│   └── metadata.json                 ← Input hash, timestamps
│
└── _processed/                       ← NEW: Processed MGraph cache
    ├── mgraph-filtered.json          ← MGraph after deletions
    └── metadata.json                 ← Input hash, timestamps
```

---

## Cache Invalidation Strategy

### Content-Based Hashing

Each sub-layer tracks the hash of its inputs:

```python
# Analysis depends on L3 MGraph
analysis_hash = hash(L3_mgraph_json)

# Decisions depend on analysis + engine config
decisions_hash = hash(analysis_output + engine_config_json)

# Processed depends on decisions
processed_hash = hash(L3_mgraph_json + decisions_json)

# Final outputs depend on processed
output_hash = hash(processed_mgraph_json)
```

### Cascade Behavior

| If this changes... | These are invalidated | These remain cached |
|--------------------|----------------------|---------------------|
| L3 MGraph content | Analysis, Decisions, Processed, Outputs | L0, L1, L2 |
| Decision threshold | Decisions, Processed, Outputs | L0-L3, Analysis |
| Decision engine type | Decisions, Processed, Outputs | L0-L3, Analysis |
| LLM model version | Decisions, Processed, Outputs | L0-L3, Analysis |
| Nothing (re-run) | Nothing | Everything (full cache hit) |

---

## Data Structures

### Analysis Cache

```python
class Schema__L5__Analysis(Type_Safe):
    """Cached text extraction and merge results."""
    
    text_nodes: dict = None      # { node_id: { text, parent_id } }
    merged_texts: dict = None    # { parent_id: { merged_text, source_node_ids } }
    
    # Cache metadata
    input_hash: str = ''         # Hash of L3 MGraph
    created_at: str = ''         # ISO timestamp
    node_count: int = 0          # Number of text nodes
    merge_count: int = 0         # Number of merged groups
```

### Decision Cache

```python
class Schema__L5__Decisions(Type_Safe):
    """Cached decision results with engine configuration."""
    
    decisions: dict = None       # { parent_id: { keep, score, reason } }
    
    # Engine configuration (affects cache validity)
    engine_type: str = ''        # 'hash_based', 'llm_based', 'ml_based'
    engine_config: dict = None   # { threshold, model, prompt_version, etc. }
    
    # Cache metadata
    input_hash: str = ''         # Hash of analysis + engine_config
    created_at: str = ''         # ISO timestamp
    keep_count: int = 0          # Decisions to keep
    delete_count: int = 0        # Decisions to delete
    
    # LLM-specific (when engine_type == 'llm_based')
    llm_model: str = ''          # e.g., 'claude-3-haiku'
    llm_calls: int = 0           # Number of API calls made
    llm_cost_usd: float = 0.0    # Estimated cost
    llm_latency_ms: float = 0.0  # Total LLM time
```

### Engine Configuration

```python
class Schema__L5__Engine_Config(Type_Safe):
    """Decision engine configuration for cache key."""
    
    engine_type: str = 'hash_based'
    threshold: float = 0.5
    
    # Hash-based specific
    hash_algorithm: str = 'md5'
    
    # LLM-based specific  
    llm_model: str = ''
    llm_prompt_version: str = ''
    llm_temperature: float = 0.0
    
    # ML-based specific
    ml_model_path: str = ''
    ml_model_version: str = ''
    
    def to_cache_key(self) -> str:
        """Generate deterministic cache key from config."""
        return hash(json.dumps(self.obj(), sort_keys=True))
```

### Processed MGraph Cache

```python
class Schema__L5__Processed(Type_Safe):
    """Cached MGraph after node deletions."""
    
    mgraph_json: dict = None     # Html_MGraph__Document as JSON
    
    # Cache metadata
    input_hash: str = ''         # Hash of L3 + decisions
    created_at: str = ''         # ISO timestamp
    nodes_deleted: int = 0       # Count of deleted nodes
    original_nodes: int = 0      # Original node count
    final_nodes: int = 0         # Final node count
```

---

## Class Design

### L5 Sub-Layer Classes

```python
class L5__Cache__Analysis(Type_Safe):
    """Cache manager for L5 analysis sub-layer."""
    
    storage: Perf__Storage__Cache_Service
    
    def save(self, cache_id: Cache_Id, analysis: Schema__L5__Analysis) -> bool
    def load(self, cache_id: Cache_Id) -> Optional[Schema__L5__Analysis]
    def is_valid(self, cache_id: Cache_Id, l3_hash: str) -> bool
    def invalidate(self, cache_id: Cache_Id) -> bool


class L5__Cache__Decisions(Type_Safe):
    """Cache manager for L5 decisions sub-layer."""
    
    storage: Perf__Storage__Cache_Service
    
    def save(self, cache_id: Cache_Id, decisions: Schema__L5__Decisions) -> bool
    def load(self, cache_id: Cache_Id) -> Optional[Schema__L5__Decisions]
    def is_valid(self, cache_id: Cache_Id, analysis_hash: str, engine_config: Schema__L5__Engine_Config) -> bool
    def invalidate(self, cache_id: Cache_Id) -> bool


class L5__Cache__Processed(Type_Safe):
    """Cache manager for L5 processed MGraph sub-layer."""
    
    storage: Perf__Storage__Cache_Service
    
    def save(self, cache_id: Cache_Id, processed: Schema__L5__Processed) -> bool
    def load(self, cache_id: Cache_Id) -> Optional[Schema__L5__Processed]
    def is_valid(self, cache_id: Cache_Id, decisions_hash: str) -> bool
    def invalidate(self, cache_id: Cache_Id) -> bool
```

### Smart Transformation Pipeline

```python
class L5__Transformation__Pipeline(Type_Safe):
    """L5 transformation with smart caching."""
    
    storage: Perf__Storage__Cache_Service
    decision_engine: Phase_E__Decision_Engine__Base
    
    # Sub-layer caches
    cache_analysis: L5__Cache__Analysis
    cache_decisions: L5__Cache__Decisions
    cache_processed: L5__Cache__Processed
    
    def transform(self, cache_id: Cache_Id, html_dict: dict, 
                  force_rebuild: bool = False) -> Schema__L5__Transform_Result:
        """
        Transform with smart caching.
        
        Steps:
        1. Check if analysis cache valid → use cached or rebuild
        2. Check if decisions cache valid for current engine config → use cached or rebuild
        3. Check if processed cache valid → use cached or rebuild
        4. Generate final outputs
        """
        pass
    
    def get_cache_status(self, cache_id: Cache_Id) -> dict:
        """Return which sub-layers are cached and valid."""
        pass
    
    def invalidate_decisions(self, cache_id: Cache_Id) -> bool:
        """Invalidate decisions and downstream (processed, outputs)."""
        pass
    
    def set_decision_engine(self, engine: Phase_E__Decision_Engine__Base):
        """Change engine - marks decisions cache as invalid."""
        pass
```

---

## Example Workflows

### First Run (Cold Cache)

```python
pipeline = L5__Transformation__Pipeline(
    storage         = storage,
    decision_engine = Phase_E__Decision_Engine__Hash_Based(threshold=0.5)
)

result = pipeline.transform(cache_id, html_dict)

# Steps executed:
# 1. Analysis: Extract + Merge         → 7ms   (BUILT)
# 2. Decisions: Hash-based scoring     → 2ms   (BUILT)
# 3. Processed: Delete nodes           → 1ms   (BUILT)
# 4. Outputs: Generate HTML            → 5ms   (BUILT)
# ────────────────────────────────────────────
# Total:                               → 15ms

print(result.cache_status)
# { 'analysis': 'built', 'decisions': 'built', 'processed': 'built' }
```

### Second Run (Full Cache Hit)

```python
result = pipeline.transform(cache_id, html_dict)

# Steps executed:
# 1. Analysis: Valid cache             → 0.5ms (HIT)
# 2. Decisions: Valid cache            → 0.5ms (HIT)
# 3. Processed: Valid cache            → 0.5ms (HIT)
# 4. Outputs: Already exist            → 0ms   (HIT)
# ────────────────────────────────────────────
# Total:                               → 1.5ms

print(result.cache_status)
# { 'analysis': 'hit', 'decisions': 'hit', 'processed': 'hit' }
```

### After Changing Threshold (Partial Rebuild)

```python
pipeline.decision_engine = Phase_E__Decision_Engine__Hash_Based(threshold=0.7)

result = pipeline.transform(cache_id, html_dict)

# Steps executed:
# 1. Analysis: Valid cache             → 0.5ms (HIT)
# 2. Decisions: Config changed!        → 2ms   (REBUILT)
# 3. Processed: Decisions changed!     → 1ms   (REBUILT)
# 4. Outputs: Regenerate               → 5ms   (REBUILT)
# ────────────────────────────────────────────
# Total:                               → 8.5ms

print(result.cache_status)
# { 'analysis': 'hit', 'decisions': 'rebuilt', 'processed': 'rebuilt' }
```

### With LLM Decision Engine (Expensive First Run)

```python
pipeline.decision_engine = Phase_E__Decision_Engine__LLM_Based(
    model     = 'claude-3-haiku',
    threshold = 0.6
)

# First run - 50 text blocks × 500ms per LLM call
result = pipeline.transform(cache_id, html_dict)

# Steps executed:
# 1. Analysis: Valid cache             → 0.5ms  (HIT)
# 2. Decisions: 50 LLM calls           → 25000ms (BUILT) ← Expensive!
# 3. Processed: Delete nodes           → 1ms    (BUILT)
# 4. Outputs: Generate HTML            → 5ms    (BUILT)
# ────────────────────────────────────────────
# Total:                               → ~25 seconds

print(result.decisions_meta)
# { 'llm_calls': 50, 'llm_cost_usd': 0.05, 'llm_latency_ms': 25000 }
```

### Second Run with LLM (Cache Hit!)

```python
result = pipeline.transform(cache_id, html_dict)

# Steps executed:
# 1. Analysis: Valid cache             → 0.5ms (HIT)
# 2. Decisions: Valid cache            → 0.5ms (HIT) ← No LLM calls!
# 3. Processed: Valid cache            → 0.5ms (HIT)
# 4. Outputs: Already exist            → 0ms   (HIT)
# ────────────────────────────────────────────
# Total:                               → 1.5ms (was 25 seconds!)

# Saved: 50 LLM calls, ~$0.05, 25 seconds
```

---

## Storage Structure

```
phase-e5-full-pipeline/
  data/key-based/sessions/full-pipeline-batch/targets/
    text_npr_org/
      perf-entry/
        data/
          L0/  ← URL metadata
          L1/  ← Raw HTML
          L2/  ← HTML dict
          L3/  ← Original MGraph
          L4/  ← Round-trip HTML
          L5/
            # Final outputs (existing)
            a-original-reconstructed.json
            b-body-only.json
            c-phase-e0-filtered.json
            d-text-content.json
            
            # Intermediate caches (NEW)
            _analysis/
              text-nodes.json
              merged-texts.json
              metadata.json
            _decisions/
              results.json
              engine-config.json
              metadata.json
            _processed/
              mgraph-filtered.json
              metadata.json
```

---

## Files to Create

| File | Purpose |
|------|---------|
| **Schemas** | |
| `Schema__L5__Analysis.py` | Analysis cache schema |
| `Schema__L5__Decisions.py` | Decisions cache schema |
| `Schema__L5__Engine_Config.py` | Engine configuration schema |
| `Schema__L5__Processed.py` | Processed MGraph cache schema |
| **Cache Managers** | |
| `L5__Cache__Analysis.py` | Analysis sub-layer cache |
| `L5__Cache__Decisions.py` | Decisions sub-layer cache |
| `L5__Cache__Processed.py` | Processed sub-layer cache |
| **Pipeline** | |
| `L5__Transformation__Pipeline.py` | Smart transformation orchestrator |
| **Tests** | |
| `test_L5__Cache__Analysis.py` | Analysis cache tests |
| `test_L5__Cache__Decisions.py` | Decisions cache tests |
| `test_L5__Cache__Processed.py` | Processed cache tests |
| `test_L5__Transformation__Pipeline.py` | Pipeline integration tests |
| `test_L5__Cache_Invalidation.py` | Invalidation cascade tests |

---

## Test Cases

### Cache Validity Tests

| Test | Description |
|------|-------------|
| `test_analysis__valid_when_l3_unchanged` | Analysis cache valid if L3 same |
| `test_analysis__invalid_when_l3_changed` | Analysis cache invalid if L3 changes |
| `test_decisions__valid_when_config_unchanged` | Decisions valid if same config |
| `test_decisions__invalid_when_threshold_changed` | Decisions invalid if threshold changes |
| `test_decisions__invalid_when_engine_type_changed` | Decisions invalid if engine type changes |
| `test_processed__valid_when_decisions_unchanged` | Processed valid if decisions same |

### Pipeline Tests

| Test | Description |
|------|-------------|
| `test_pipeline__cold_cache_builds_all` | First run builds all sub-layers |
| `test_pipeline__warm_cache_hits_all` | Second run hits all caches |
| `test_pipeline__threshold_change_partial_rebuild` | Only rebuilds decisions+ |
| `test_pipeline__engine_swap_partial_rebuild` | Only rebuilds decisions+ |
| `test_pipeline__l3_change_full_rebuild` | Rebuilds everything |

### LLM Integration Tests (Future)

| Test | Description |
|------|-------------|
| `test_llm__decisions_cached` | LLM decisions cached correctly |
| `test_llm__no_calls_on_cache_hit` | No LLM calls when cached |
| `test_llm__cost_tracking` | Cost correctly tracked |

---

## Success Criteria

1. ✅ Analysis sub-layer caches text_nodes + merged_texts
2. ✅ Decisions sub-layer caches results + engine config
3. ✅ Processed sub-layer caches filtered MGraph
4. ✅ Cache invalidation cascades correctly
5. ✅ Threshold change only rebuilds decisions+
6. ✅ Engine type change only rebuilds decisions+
7. ✅ Full cache hit returns in <5ms
8. ✅ Ready for LLM decision engine integration

---

## Future Extensions (Phase E_8+)

| Extension | Description |
|-----------|-------------|
| `Phase_E__Decision_Engine__LLM_Based` | Claude/GPT-based content classification |
| `Phase_E__Decision_Engine__ML_Based` | Trained classifier model |
| Batch LLM calls | Group text blocks for efficiency |
| Decision explanations | Store LLM reasoning for audit |
| A/B testing | Compare engines on same content |
| Cost budgets | Stop LLM calls when budget exceeded |

---

## Dependencies

| Dependency | Source |
|------------|--------|
| `Perf__Storage__Cache_Service` | Phase E_4 |
| `Phase_E__Text_Extractor` | Phase E_0 |
| `Phase_E__Virtual_Merger` | Phase E_0 |
| `Phase_E__Decision_Engine__Base` | Phase E_0 |
| `Phase_E__Node_Deleter` | Phase E_0 |
| `Html_MGraph__Document` | Core |

---

## Relationship to Other Phases

| Phase | Relationship |
|-------|--------------|
| E_5 | Extends L5 layer with sub-layer caching |
| E_6 | Provides data for performance benchmarking |
| E_8+ | Enables efficient LLM decision engine |

---

## Summary

Phase E_7 adds **smart caching** to the L5 transformation layer:

- **Analysis cache**: Don't re-extract text if MGraph unchanged
- **Decisions cache**: Don't re-run LLM if config unchanged  
- **Processed cache**: Don't re-delete nodes if decisions unchanged
- **Cascade invalidation**: Changes only rebuild what's necessary

This prepares the system for **expensive LLM-based content filtering** where caching decisions saves significant time and cost.
