# Technical Debrief: Cache Entity Wrappers & FLeT Flow Data Storage

**Date**: January 19, 2026  
**Session Focus**: Bound client abstractions for cache operations and FLeT observability

---

## Executive Summary

This session extended the cache client with progressive abstraction layers ("bound clients") that simplify cache operations by binding identity parameters. We also integrated flow execution data storage into the FLeT base class for observability.

---

## 1. Problem Statement

### Cache Client Verbosity

Raw cache client calls required repetitive parameter passing:

```python
# Every call needs cache_id, namespace, data_key, data_file_id
html = cache_client.data().retrieve().data__string__with__id_and_key(
           cache_id=cache_id, namespace=namespace, data_key='html', data_file_id='raw')
flow = cache_client.data().retrieve().data__json__with__id_and_key(
           cache_id=cache_id, namespace=namespace, data_key='html/raw', data_file_id='flow')
```

### FLeT Observability

FLeTs needed a standard way to store flow execution data alongside the content they create.

---

## 2. Solution: Progressive Abstraction Layers

### Layer Architecture

```
Level 0: Raw Client (verbose)
    │
    ▼
Level 1: Cache__Entity (binds cache_id + namespace)
    │
    ▼
Level 2: Cache__Entity__Data_File (binds + data_key + data_file_id)
    │
    ▼
Level 2b: Cache__Entity__Json_File (JSON-focused API)
```

### Package Structure

```
mgraph_ai_service_cache_client/
└── client/
    ├── client_contract/                    # Raw FastAPI request wrappers
    │   ├── data/
    │   ├── data_store/
    │   └── ...
    └── client_entities/                    # Bound clients (identity pre-filled)
        ├── Cache__Entity.py                # Entity-level operations
        ├── Cache__Entity__Data_File.py     # Data file operations (string/JSON)
        └── Cache__Entity__Json_File.py     # JSON-focused operations
```

---

## 3. Implementation Details

### Cache__Entity

Binds `cache_id + namespace` for entity-level operations:

```python
entity = Cache__Entity(cache_client=client, cache_id=cache_id, namespace=namespace)

# Entry operations (Tier 1)
entry    = entity.entry__json()
metadata = entity.metadata()
refs     = entity.refs()

# Data operations (Tier 2)
html = entity.data__string('html', 'raw')
entity.data__store_json('config', 'settings', data)

# Factory to go deeper
data_file = entity.data_file('html', 'raw')
```

### Cache__Entity__Data_File

Binds `cache_id + namespace + data_key + data_file_id`:

```python
data_file = Cache__Entity__Data_File(cache_client=client, cache_id=id,
                                      namespace=ns, data_key='html', data_file_id='raw')

data_file.store_string(html)      # Store string
data_file.string()                # Get string
data_file.store_json(data)        # Store JSON
data_file.json()                  # Get JSON
data_file.exists__string()        # Check string exists
data_file.exists__json()          # Check JSON exists
```

### Cache__Entity__Json_File

JSON-focused wrapper with simplified API:

```python
class Cache__Entity__Json_File(Cache__Entity__Data_File):

    def exists(self) -> bool:
        return self.exists__json()

    def retrieve(self) -> dict:
        return self.json()

    def store(self, data: dict) -> Schema__Cache__Data__Store__Response:
        return self.store_json(data)

    def update(self, data: dict) -> bool:
        return self.update_json(data)

    def delete(self) -> bool:
        return super().delete(data_type=Enum__Cache__Data_Type.JSON)
```

**Key insight**: This class properly delegates to parent methods rather than duplicating implementation.

---

## 4. Naming Decisions

### Folder Naming

| Considered | Decision | Reasoning |
|------------|----------|-----------|
| `client/helpers/` | ❌ | Too generic |
| `client/bound/` | ❌ | Doesn't feel right |
| `client/wrappers/` | ❌ | Good but less specific |
| `client_factory/` | ❌ | Wrong pattern (factory creates, these wrap) |
| `client_entities/` | ✅ | Consistent with `client_contract`, domain-specific |

### Class Naming

| Original | Final | Reasoning |
|----------|-------|-----------|
| `Cache__Data__File` | `Cache__Entity__Data_File` | Shows hierarchy (entity → data file) |
| `FLeT__Data_File` | `Cache__Entity__Json_File` | Generic JSON wrapper belongs in cache client |

---

## 5. FLeT Flow Data Storage

### Design Decision

Initially, `FLeT__Data_File` had flow-specific methods (`flow__store()`, `flow__exists()`). This was refactored:

| Before | After |
|--------|-------|
| Cache client knows about "flow" concept | Cache client is generic |
| `flow__store()`, `flow()` methods | `store()`, `retrieve()` methods |
| Path computed inside class | Path controlled by caller |

### Integration in Html_FLeT__Base

```python
class Html_FLeT__Base(Type_Safe):

    @cache_on_self
    def flow_data(self) -> Cache__Entity__Json_File:
        data_key     = f'flows/{self.config.name}'    # e.g., 'flows/html-to-cache'
        data_file_id = 'flow-data'
        return Cache__Entity__Json_File(cache_client = self.cache_client.cache_client,
                                        cache_id     = self.cache_id                 ,
                                        namespace    = self.namespace                ,
                                        data_key     = data_key                      ,
                                        data_file_id = data_file_id                  )

    def save_flow_data(self):
        if self.cache_client:
            self.flow_data().store(self.flow.json())
```

### Storage Pattern

```
{namespace}/data/key-based/{cache_key}/{file_id}/data/
├── html/
│   └── raw.txt                           ← Content created by FLeT
└── flows/
    └── html-to-cache/
        └── flow-data.json                ← Flow execution data
```

---

## 6. Bug Found & Fixed

### Issue: `exists()` returned `False` for existing JSON files

```python
with flet.flow_data() as _:
    assert _.exists() is False   # ← Bug! File exists but returns False
```

### Root Cause

`exists()` defaulted to `Enum__Cache__Data_Type.STRING`, looking for `.txt` instead of `.json`.

### Fix

Created `Cache__Entity__Json_File` that overrides `exists()` to use JSON type:

```python
def exists(self) -> bool:
    return self.exists__json()
```

---

## 7. Complete FLeT Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  FLeT__Html__To__Cache                                          │
│  ├── setup()         → Sets config (name, description)          │
│  ├── run_actions()   → Calls action__html_to_cache__save        │
│  └── execute()       → Calls super().execute()                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Html_FLeT__Base                                                │
│  ├── execute()       → Wraps in Flow, calls run_actions         │
│  ├── save_flow_data()→ Stores flow.json via Cache__Entity__Json_File
│  ├── cache_entity()  → Returns Cache__Entity                    │
│  └── flow_data()     → Returns Cache__Entity__Json_File         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  action__html_to_cache__save                                    │
│  └── Stores HTML string to cache data layer                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. Files Created/Modified

### New Files (cache_client)

| File | Purpose |
|------|---------|
| `client/client_entities/Cache__Entity.py` | Entity-bound client |
| `client/client_entities/Cache__Entity__Data_File.py` | Data file-bound client |
| `client/client_entities/Cache__Entity__Json_File.py` | JSON-focused data file |
| `tests/.../test_Cache__Entity.py` | Entity tests |
| `tests/.../test_Cache__Entity__Data_File.py` | Data file tests |
| `tests/.../test_Cache__Entity__Json_File.py` | JSON file tests |

### Modified Files (html_graph)

| File | Changes |
|------|---------|
| `Html_FLeT__Base.py` | Added `flow_data()`, `save_flow_data()`, `cache_entity()` |

---

## 9. Key Principles Applied

| Principle | Application |
|-----------|-------------|
| **Progressive abstraction** | Raw → Entity → Data File → JSON File |
| **Single responsibility** | Each class does one thing well |
| **Delegation over duplication** | `Cache__Entity__Json_File` calls parent methods |
| **Configuration over convention** | Flow path set by caller, not hardcoded |
| **Observability built-in** | Flow data automatically stored |

---

## 10. Next Steps

Potential future work:

1. **Cache__Entity__String_File** - String-focused counterpart to JSON file
2. **Additional FLeTs** - Html → MGraph, MGraph → Analysis, etc.
3. **Flow data querying** - Tools to analyze stored flow execution data
4. **Orchestrator integration** - Coordinate multiple FLeTs with shared observability

---

## 11. API Quick Reference

### Cache__Entity

```python
entity = Cache__Entity(cache_client, cache_id, namespace)

# Entry (Tier 1)
entity.entry__json()           # dict
entity.entry__with_metadata()  # Schema__Cache__Retrieve__Success
entity.metadata()              # Schema__Cache__File__Metadata
entity.refs()                  # Schema__Cache__File__Refs
entity.exists()                # bool
entity.delete()                # bool

# Data (Tier 2)
entity.data__string(data_key, data_file_id)        # str
entity.data__json(data_key, data_file_id)          # dict
entity.data__store_string(data_key, data_file_id, content)
entity.data__store_json(data_key, data_file_id, data)
entity.data__files(data_key?, recursive?)          # list
entity.data__files__paths()                        # list[str]

# Factory
entity.data_file(data_key, data_file_id)           # Cache__Entity__Data_File
```

### Cache__Entity__Json_File

```python
json_file = Cache__Entity__Json_File(cache_client, cache_id, namespace, data_key, data_file_id)

json_file.store(data)      # Schema__Cache__Data__Store__Response
json_file.retrieve()       # dict
json_file.exists()         # bool
json_file.update(data)     # bool
json_file.delete()         # bool
```
