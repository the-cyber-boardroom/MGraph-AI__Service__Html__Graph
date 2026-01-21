# Phase E_6: Caching Layer Architecture - Technical Debrief

## Executive Summary

Phase E_6 implemented a three-tier caching layer for the HTML-to-MGraph pipeline, enabling efficient storage and retrieval of intermediate processing results. The architecture follows a layered approach (L1/L2/L3) that caches progressively more processed representations of HTML content.

## Architecture Overview

### Layer Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                    Html_Cache__Manager                          │
│                 (Orchestration Layer)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │     L1      │  │     L2      │  │     L3      │             │
│  │  Raw HTML   │  │  HTML Dict  │  │   MGraph    │             │
│  │  (string)   │  │   (dict)    │  │ (document)  │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│              Perf__Storage__Cache_Service                       │
│                  (Storage Backend)                              │
└─────────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. Html_Cache__Layer__Base
Base class providing common functionality:
- Cache ID and hash management
- Key generation (`key_data()`, `key_metadata()`)
- Content hashing (SHA-256, truncated to 16 chars)
- Metadata save/load operations
- Storage abstraction

#### 2. Html_Cache__Layer__Html (L1)
- **Purpose**: Cache raw HTML strings
- **Storage**: String content via `save_string()`
- **Metadata**: Source, content hash, size in bytes
- **Key**: `L1/raw-html`

#### 3. Html_Cache__Layer__Html__Dict (L2)
- **Purpose**: Cache parsed HTML dictionary with node IDs
- **Storage**: JSON via `save()`
- **Build**: `Html__To__Html_Dict__With__Node_Ids.convert()`
- **Key**: `L2/html-dict`

#### 4. Html_Cache__Layer__MGraph (L3)
- **Purpose**: Cache MGraph document representation
- **Storage**: JSON via `save()` using `document.json()`
- **Build**: `Html__To__Html_MGraph__Document__Node_Id_Reuse.convert_from_dict()`
- **Metadata**: Content hash, node count, edge count
- **Key**: `L3/mgraph-document`

#### 5. Html_Cache__Manager
Orchestration layer providing:
- Layer lifecycle management
- Target-based context switching
- Cascade building (L1 → L2 → L3)
- Cache status queries
- Statistics tracking

### Storage Backend

```
Perf__Storage__Cache_Service
├── config: Schema__Perf__Storage__Config
├── client: Cache_Service__Client
├── session_name: Safe_Str__Session_Name
├── target_name: Safe_Str__Target_Name
└── file_id: Safe_Str__Data_File_Id
```

Key operations:
- `save()` / `load__json()` - JSON data
- `save_string()` / `load_string()` - Raw strings
- `create_file__perf_entry()` - Entry creation
- `file_exist()` / `file_delete()` - File management

## Performance Test Suite

### Test Structure

```
test_perf__Phase_E_6__1__Pipeline_Stages.py    # L1→L2→L3 conversion costs
test_perf__Phase_E_6__2__Phase_E0_Breakdown.py # Transform component costs
test_perf__Phase_E_6__3__Cache_Hit_Miss.py     # Cache save vs load
test_perf__Phase_E_6__4__Scaling.py            # 1-300 paragraph scaling
test_perf__Phase_E_6__5__Backend_Comparison.py # Backend + cost breakdown
```

### E_6_5 Benchmark Categories

| Section | Purpose | Benchmarks |
|---------|---------|------------|
| **A** | In-memory full pipelines | A_01 (save), A_02 (load) |
| **B** | In-memory cost breakdown | B_01-B_11 (serialization, requests, setup, pure ops) |
| **C** | Local server | C_01 (save), C_02 (load) |
| **D** | Live serverless | D_01 (save), D_02 (load) |

### Key Testing Patterns

#### 1. Pre-population for Load Tests
```python
# Setup outside measurement
storage = create_storage(...)
cache_id = storage.create_file__perf_entry()
layers = create_layers(storage)
layers[0].save(cache_id=cache_id, html=html_str)
layers[1].save(cache_id=cache_id, html_dict=html_dict)
layers[2].save(cache_id=cache_id, document=mgraph_doc)

# Benchmark only the load
def stage_load():
    return layers[0].load(cache_id=cache_id)
```

#### 2. Pure Operation Isolation
```python
# Pre-create everything OUTSIDE benchmark
storage_pure = create_storage(...)
cache_id_pure = storage_pure.create_file__perf_entry()
layer_html, layer_dict, layer_mgraph, _ = create_layers(storage_pure)

# Benchmark only the operation
def stage_pure_L1_save():
    return layer_html.save(cache_id=cache_id_pure, html=html_str)
```

#### 3. Incremental Target Counter
```python
target_counter = [0]
def next_target():
    target_counter[0] += 1
    return f'target-{target_counter[0]}'
```

## Type Safety

All components use OSBot's Type_Safe framework:
- `Safe_Str__File__Path` - File paths
- `Safe_Str__Cache_Hash` - Cache hashes
- `Cache_Id` - Cache identifiers
- `Safe_Str__Session_Name` / `Safe_Str__Target_Name` - Context identifiers
- `@type_safe` decorator for runtime validation

## Statistics Tracking

```python
class Schema__Html_Cache__Stats:
    l1_hits: int
    l1_misses: int
    l2_hits: int
    l2_misses: int
    l2_builds: int
    l3_hits: int
    l3_misses: int
    l3_builds: int
```

Stats are shared across layers and automatically updated on load operations.

## Key Design Decisions

1. **Layer Independence**: Each layer can operate independently with its own key namespace
2. **Shared Storage**: All layers share a single storage backend instance
3. **Cascade Building**: Manager can automatically build higher layers from lower ones
4. **Content Addressable**: Content hashing enables deduplication and validation
5. **Metadata Separation**: Each layer stores metadata separately from content
6. **Backend Agnostic**: Storage interface allows swapping backends (in-memory, local, serverless)

## Files Delivered

### Core Implementation
- `Html_Cache__Layer__Base.py`
- `Html_Cache__Layer__Html.py`
- `Html_Cache__Layer__Html__Dict.py`
- `Html_Cache__Layer__MGraph.py`
- `Html_Cache__Manager.py`

### Test Suite
- `test_Html_Cache__Layer__Base.py`
- `test_Html_Cache__Layer__Html.py`
- `test_Html_Cache__Layer__Dict.py`
- `test_Html_Cache__Layer__MGraph.py`
- `test_Html_Cache__Manager.py`

### Performance Tests
- `test_perf__Phase_E_6__1__Pipeline_Stages.py`
- `test_perf__Phase_E_6__2__Phase_E0_Breakdown.py`
- `test_perf__Phase_E_6__3__Cache_Hit_Miss.py`
- `test_perf__Phase_E_6__4__Scaling.py`
- `test_perf__Phase_E_6__5__Backend_Comparison.py`

## Usage Example

```python
# Setup
storage = Perf__Storage__Cache_Service(config=config, client=client)
manager = Html_Cache__Manager(storage=storage).setup()

# Cache HTML and build full pipeline
document = manager.build_full_pipeline(
    target='example.com/page',
    html=html_content,
    source='fetch'
)

# Later: retrieve from cache (fast)
cached_doc = manager.get_mgraph(target='example.com/page')

# Check cache status
status = manager.cache_status('example.com/page')
# {'target': 'example.com/page', 'L1': True, 'L2': True, 'L3': True}
```
