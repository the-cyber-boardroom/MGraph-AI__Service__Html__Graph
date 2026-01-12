# Cache Service Consumer Guide: Session-Target Storage Pattern

**Purpose**: Detailed explanation for LLM sessions that need to store multiple data files under a session/target hierarchy  
**Version**: Based on Cache Service v0.6.0+ and Client v0.10.1+

---

## Table of Contents

1. [Overview](#1-overview)
2. [Core Concepts](#2-core-concepts)
3. [The Two Storage Modes](#3-the-two-storage-modes)
4. [Key Hierarchy and Addressing](#4-key-hierarchy-and-addressing)
5. [File Structure Deep Dive](#5-file-structure-deep-dive)
6. [Data Schemas Reference](#6-data-schemas-reference)
7. [Operations Flow](#7-operations-flow)
8. [Code Patterns](#8-code-patterns)
9. [Data Portability](#9-data-portability)
10. [Best Practices](#10-best-practices)

---

## 1. Overview

### What This Pattern Solves

When building a caching layer that needs to:
- Organize data by **session** (e.g., "benchmark-run-2024-01-15") and **target** (e.g., "example-com-homepage")
- Store **multiple related files** under each session/target (e.g., L1/raw-html, L2/parsed-dict, L3/mgraph)
- **Efficiently store** lightweight data files without overhead
- **Lookup data** even when you don't have the UUID

The cache service provides a two-tier storage model:
1. **Entry Storage** (heavyweight): Creates the anchor point with full tracking
2. **Data Storage** (lightweight): Stores actual cache layer data under the entry

### The Key Insight

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ENTRY (perf-entry)                                                         │
│  - Created ONCE per session/target                                          │
│  - Has cache_id (UUID), cache_hash (deterministic), cache_key (semantic)    │
│  - Creates 3 files + 2 reference files (5 total)                           │
│  - This is the "anchor" that everything hangs off                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Parent cache_id
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  DATA FILES (L1, L2, L3, etc.)                                             │
│  - Created MANY TIMES under the entry                                       │
│  - Each creates only 1 file (no overhead)                                  │
│  - Accessed via parent's cache_id + data_key + data_file_id                │
│  - This is where your actual cached data lives                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Concepts

### 2.1 The Three Identifiers

| Identifier | Type | Deterministic? | Purpose |
|------------|------|----------------|---------|
| **cache_key** | Semantic path | ✅ Yes | Human-readable, derived from session/target |
| **cache_hash** | 16-char hex | ✅ Yes | Hash of cache_key, enables lookup without UUID |
| **cache_id** | UUID | ❌ No | Unique identifier, created on first store |

**Relationship:**
```
cache_key = "sessions/test-session/targets/my-target"
                    ↓ hash()
cache_hash = "b9fc56d4592ecb45"  (deterministic from cache_key)
                    ↓ lookup refs/by-hash/
cache_id = "a1b2c3d4-e5f6-..."   (UUID, non-deterministic)
```

### 2.2 Session and Target

These are **your application's concepts** mapped to the cache service:

```python
session_name = "benchmark-2024-01-15"    # Logical grouping (e.g., a test run, a date, a user)
target_name  = "example-com-homepage"    # Specific item being cached (e.g., a URL, a document)

# Combined into cache_key:
cache_key = f"sessions/{session_name}/targets/{target_name}"
# Result: "sessions/benchmark-2024-01-15/targets/example-com-homepage"
```

### 2.3 Namespace

The **namespace** provides multi-tenant isolation at the top level:

```
pytest/           ← namespace (isolates all data)
├── data/
├── refs/
└── ...
```

Common namespaces: `pytest`, `development`, `production`, `user-{id}`

---

## 3. The Two Storage Modes

### 3.1 Entry Storage (File Mode) - Heavyweight

**When to use**: Creating the anchor point for a session/target

**What happens**: Creates **5 files** total:

```
{namespace}/data/key-based/{cache_key}/
├── {file_id}.json              # Content: Your entry data (Schema__Perf__Entry)
├── {file_id}.json.config       # Config: How it was stored
└── {file_id}.json.metadata     # Metadata: Tracking info

{namespace}/refs/by-hash/{h[0:2]}/{h[2:4]}/{cache_hash}.json   # Hash → cache_ids
{namespace}/refs/by-id/{id[0:2]}/{id[2:4]}/{cache_id}.json     # ID → full refs
```

**Why 5 files?**
- **Content**: Your actual payload
- **Config**: Storage strategy, file type, paths
- **Metadata**: Timestamps, content hash, size
- **Hash ref**: Enables lookup by deterministic hash
- **ID ref**: Full path information for the entry

### 3.2 Data Storage (Data Mode) - Lightweight

**When to use**: Storing cached layer data (L1, L2, L3, etc.)

**What happens**: Creates **1 file** only:

```
{namespace}/data/key-based/{cache_key}/{file_id}/data/
└── {data_key}/{data_file_id}.json    # Just the content
```

**Why only 1 file?**
- Inherits config/metadata from parent entry
- No reference files needed (accessed via parent cache_id)
- **Performance**: Creating 5 files per cache layer would be extremely slow
- **Simplicity**: You know what you're storing and where

### 3.3 Performance Comparison

| Operation | Entry Mode | Data Mode | Ratio |
|-----------|------------|-----------|-------|
| Files created | 5 | 1 | 5x fewer |
| API calls | Multiple | 1 | Faster |
| Storage overhead | High | Minimal | ~80% less |
| Tracking/refs | Full | None (inherits) | Simpler |

**Example**: Caching 100 URLs with 3 layers each
- Entry mode for everything: 100 × 3 × 5 = **1,500 files**
- Mixed mode (entry + data): 100 × 5 + 100 × 3 × 1 = **800 files**
- Savings: **47% fewer files**

---

## 4. Key Hierarchy and Addressing

### 4.1 Full Path Breakdown

```python
# Configuration
namespace    = "pytest"
session_name = "test-html-cache"
target_name  = "layer-base"
file_id      = "perf-entry"           # The anchor file name
data_key     = "L2"                   # Layer folder
data_file_id = "html-dict"            # Data file name

# Derived values
cache_key  = f"sessions/{session_name}/targets/{target_name}"
           # "sessions/test-html-cache/targets/layer-base"

cache_hash = hash(cache_key)          # "b9fc56d4592ecb45" (deterministic)
cache_id   = "a1b2c3d4-..."           # UUID (from storage)
```

### 4.2 File Paths

```python
# Entry files (file mode - 3 files)
file_folder = f"{namespace}/data/key-based/sessions/{session_name}/targets/{target_name}"
           # "pytest/data/key-based/sessions/test-html-cache/targets/layer-base"

entry_content  = f"{file_folder}/{file_id}.json"
entry_config   = f"{file_folder}/{file_id}.json.config"
entry_metadata = f"{file_folder}/{file_id}.json.metadata"

# Data files (data mode - 1 file per layer)
data_folder = f"{namespace}/data/key-based/{cache_key}/{file_id}/data"
           # "pytest/data/key-based/sessions/test-html-cache/targets/layer-base/perf-entry/data"

data_file = f"{data_folder}/{data_key}/{data_file_id}.json"
         # "pytest/data/key-based/sessions/test-html-cache/targets/layer-base/perf-entry/data/L2/html-dict.json"

# Reference files (2 files, sharded)
cache_hash_sharded = f"{cache_hash[0:2]}/{cache_hash[2:4]}/{cache_hash}"
                  # "b9/fc/b9fc56d4592ecb45"

cache_id_sharded = f"{cache_id[0:2]}/{cache_id[2:4]}/{cache_id}"
                # "a1/b2/a1b2c3d4-..."

hash_ref = f"{namespace}/refs/by-hash/{cache_hash_sharded}.json"
id_ref   = f"{namespace}/refs/by-id/{cache_id_sharded}.json"
```

### 4.3 Complete File List

After creating an entry and one data file (L2/html-dict):

```python
all_files = [
    # Entry files (3)
    "pytest/data/key-based/sessions/test-html-cache/targets/layer-base/perf-entry.json",
    "pytest/data/key-based/sessions/test-html-cache/targets/layer-base/perf-entry.json.config",
    "pytest/data/key-based/sessions/test-html-cache/targets/layer-base/perf-entry.json.metadata",
    
    # Data file (1)
    "pytest/data/key-based/sessions/test-html-cache/targets/layer-base/perf-entry/data/L2/html-dict.json",
    
    # Reference files (2)
    "pytest/refs/by-hash/b9/fc/b9fc56d4592ecb45.json",
    "pytest/refs/by-id/a1/b2/a1b2c3d4-uuid.json"
]
```

---

## 5. File Structure Deep Dive

### 5.1 Entry Content (`perf-entry.json`)

The main entry file contains your application's anchor data:

```python
Schema__Perf__Entry = {
    "cache_key"   : "sessions/test-html-cache/targets/layer-base",
    "session_name": "test-html-cache",
    "target_name" : "layer-base",
    "timestamp"   : 1705312000.0,
    "config"      : {},           # Optional: Your custom config
    "summary"     : {}            # Optional: Summary data
}
```

**Key fields:**
- `cache_key`: The deterministic semantic path
- `session_name` / `target_name`: Your logical hierarchy
- `timestamp`: When created
- `config` / `summary`: Extension points for your data

### 5.2 Entry Config (`perf-entry.json.config`)

Storage configuration for the entry:

```python
Schema__Memory_FS__File__Config = {
    "file_id"        : "perf-entry",
    "exists_strategy": "first",
    "file_key"       : "sessions/test-html-cache/targets/layer-base",
    "file_paths"     : ["pytest/data/key-based/sessions/test-html-cache/targets/layer-base"],
    "file_type"      : {
        "name"          : "json",
        "content_type"  : "application/json; charset=utf-8",
        "file_extension": "json",
        "encoding"      : "utf-8",
        "serialization" : "json"
    }
}
```

### 5.3 Entry Metadata (`perf-entry.json.metadata`)

Tracking and versioning information:

```python
Schema__Memory_FS__File__Metadata = {
    "content__hash"        : "abc123...",        # SHA-256 of content
    "content__size"        : 195,                # Bytes
    "timestamp"            : 1705312000.0,
    "chain_hash"           : None,               # For versioning chains
    "previous_version_path": None,               # For versioning
    "tags"                 : [],
    "data"                 : {
        "cache_hash"      : "b9fc56d4592ecb45",
        "cache_key"       : "sessions_test-html-cache_targets_layer-base",  # Safe ID version
        "cache_id"        : "a1b2c3d4-...",
        "content_encoding": None,
        "file_id"         : "perf-entry",
        "file_type"       : "json",
        "json_field_path" : "cache_key",         # Field used for hashing
        "namespace"       : "pytest",
        "stored_at"       : "2024-01-15T10:00:00Z",
        "strategy"        : "key_based"
    }
}
```

### 5.4 Hash Reference (`refs/by-hash/{sharded_hash}.json`)

Maps deterministic hash to cache IDs (enables lookup without UUID):

```python
Schema__Cache__Hash__Reference = {
    "cache_hash"    : "b9fc56d4592ecb45",
    "cache_ids"     : [
        {"cache_id": "a1b2c3d4-...", "timestamp": 1705312000.0}
    ],
    "latest_id"     : "a1b2c3d4-...",
    "total_versions": 1
}
```

**Why this matters:**
- Given `session_name` + `target_name`, you can compute `cache_hash`
- Use hash to lookup `cache_id` without knowing the UUID
- `latest_id` gives you the most recent version if multiple exist

### 5.5 ID Reference (`refs/by-id/{sharded_id}.json`)

Complete path information for an entry:

```python
Schema__Cache__File__Refs = {
    "cache_id"  : "a1b2c3d4-...",
    "cache_hash": "b9fc56d4592ecb45",
    "namespace" : "pytest",
    "file_type" : "json",
    "strategy"  : "key_based",
    "timestamp" : 1705312000.0,
    
    "all_paths" : {
        "data"   : [
            "pytest/data/key-based/sessions/.../perf-entry.json",
            "pytest/data/key-based/sessions/.../perf-entry.json.config",
            "pytest/data/key-based/sessions/.../perf-entry.json.metadata"
        ],
        "by_hash": ["pytest/refs/by-hash/b9/fc/b9fc56d4592ecb45.json"],
        "by_id"  : ["pytest/refs/by-id/a1/b2/a1b2c3d4-....json"]
    },
    
    "file_paths": {
        "content_files": ["pytest/data/key-based/sessions/.../perf-entry.json"],
        "data_folders" : ["pytest/data/key-based/sessions/.../perf-entry/data"]
    }
}
```

**Key insight**: `file_paths.data_folders` tells you where child data files live.

### 5.6 Data File (`perf-entry/data/L2/html-dict.json`)

Just the raw content - no wrapper, no metadata:

```python
# Stored directly as-is
{
    "head": {"nodes": [{"tag": "title", "text": "Test"}]},
    "body": {"nodes": [
        {"tag": "h1", "text": "Hello"},
        {"tag": "p", "text": "World"}
    ]}
}
```

---

## 6. Data Schemas Reference

### 6.1 Your Application Schemas

```python
class Schema__Perf__Entry(Type_Safe):
    """Your anchor entry data"""
    cache_key   : str = ''
    session_name: str = ''
    target_name : str = ''
    timestamp   : float = 0.0
    config      : dict = None     # Custom config
    summary     : dict = None     # Summary data
```

### 6.2 Cache Service Schemas

```python
# From cache service - Entry config
class Schema__Memory_FS__File__Config(Type_Safe):
    file_id        : str
    exists_strategy: str
    file_key       : str
    file_paths     : List[str]
    file_type      : Schema__File_Type

# From cache service - Entry metadata
class Schema__Memory_FS__File__Metadata(Type_Safe):
    content__hash         : str
    content__size         : int
    timestamp             : float
    chain_hash            : Optional[str]
    previous_version_path : Optional[str]
    tags                  : List[str]
    data                  : Schema__Metadata__Data

# From cache service - Hash reference
class Schema__Cache__Hash__Reference(Type_Safe):
    cache_hash    : str
    cache_ids     : List[Schema__Cache__Hash__Entry]
    latest_id     : str
    total_versions: int

# From cache service - ID reference
class Schema__Cache__File__Refs(Type_Safe):
    cache_id   : str
    cache_hash : str
    namespace  : str
    file_type  : str
    strategy   : str
    timestamp  : float
    all_paths  : Schema__Cache__Store__Paths
    file_paths : Schema__Cache__File__Paths
```

---

## 7. Operations Flow

### 7.1 Creating an Entry (First Time)

```python
# 1. Compute cache_key from session/target
cache_key = f"sessions/{session_name}/targets/{target_name}"

# 2. Check if entry exists (via hash lookup)
cache_hash = hash_generator.from_string(cache_key)
cache_id   = client.find_entry_by_key(cache_key)  # Returns None if not exists

# 3. If not exists, create entry
if not cache_id:
    perf_entry = Schema__Perf__Entry(
        session_name = session_name,
        target_name  = target_name,
        cache_key    = cache_key
    )
    response = client.store_entry(
        cache_key       = cache_key,
        file_id         = "perf-entry",
        json_field_path = "cache_key",      # Field to hash for deterministic lookup
        perf_entry      = perf_entry
    )
    cache_id = response.cache_id

# 4. Now you have cache_id - save it or recompute via hash
```

### 7.2 Storing Data Files

```python
# Requires: cache_id from step 7.1

# Store L1 data
client.store_child_json(
    cache_id     = cache_id,
    data_key     = "L1",           # Layer folder
    data_file_id = "raw-html",     # File name
    data         = {"html": "<html>..."}
)

# Store L2 data
client.store_child_json(
    cache_id     = cache_id,
    data_key     = "L2",
    data_file_id = "html-dict",
    data         = {"head": {...}, "body": {...}}
)

# Store L3 data
client.store_child_json(
    cache_id     = cache_id,
    data_key     = "L3",
    data_file_id = "mgraph-document",
    data         = {"graph": {...}}
)
```

### 7.3 Retrieving Data

```python
# Option A: You have cache_id
html_dict = client.retrieve_child_json(
    cache_id     = cache_id,
    data_key     = "L2",
    data_file_id = "html-dict"
)

# Option B: You only have session_name + target_name
cache_key  = f"sessions/{session_name}/targets/{target_name}"
cache_id   = client.find_entry_by_key(cache_key)
if cache_id:
    html_dict = client.retrieve_child_json(...)
```

### 7.4 Checking Existence

```python
# Check if entry exists
cache_id = storage.cache_id()  # Returns None if not exists

# Check if data file exists
path = storage.data_file(key_data="L2/html-dict")
exists = storage.file_exist(path=path)
```

### 7.5 Deleting Data

```python
# Delete specific data file
storage.file_delete(
    cache_id = cache_id,
    path     = data_file_path,
    key_data = "L2/html-dict"
)

# Data file is gone, entry still exists
# Other layers (L1, L3) still accessible
```

---

## 8. Code Patterns

### 8.1 Storage Wrapper Pattern

```python
class Perf__Storage__Cache_Service(Perf__Storage__Base):
    """Wraps cache service with session/target semantics"""
    
    config       : Schema__Perf__Storage__Config
    client       : Cache_Service__Client
    session_name : str = "default-session"
    target_name  : str = "default-target"
    
    def cache_key(self) -> str:
        """Deterministic semantic key"""
        return f"sessions/{self.session_name}/targets/{self.target_name}"
    
    def cache_hash(self) -> str:
        """Deterministic hash for lookup"""
        return self.client.hash_generator.from_string(self.cache_key())
    
    def cache_id(self) -> Optional[str]:
        """UUID (requires lookup)"""
        return self.client.find_entry_by_key(self.cache_key())
    
    def create_file__perf_entry(self) -> str:
        """Create entry if not exists, return cache_id"""
        cache_id = self.cache_id()
        if not cache_id:
            # Create new entry
            perf_entry = Schema__Perf__Entry(...)
            response = self.client.store_entry(...)
            cache_id = response.cache_id
        return cache_id
    
    def save(self, cache_id: str, key: str, data: dict) -> bool:
        """Save data file under entry"""
        data_key, data_file_id = self.parse_key(key)  # "L2/html-dict" → ("L2", "html-dict")
        return self.client.store_child_json(
            cache_id     = cache_id,
            data_key     = data_key,
            data_file_id = data_file_id,
            data         = data
        )
    
    def load__json(self, cache_id: str, key: str) -> Optional[dict]:
        """Load data file"""
        data_key, data_file_id = self.parse_key(key)
        return self.client.retrieve_child_json(
            cache_id     = cache_id,
            data_key     = data_key,
            data_file_id = data_file_id
        )
```

### 8.2 Layer Pattern

```python
class Html_Cache__Layer__Base(Type_Safe):
    """Base class for cache layers"""
    
    storage    : Perf__Storage__Base
    stats      : Schema__Html_Cache__Stats
    layer_name : str = ''                    # 'L1', 'L2', 'L3'
    
    def cache_id(self):
        return self.storage.cache_id()
    
    def key_data(self) -> str:
        """Override in subclass: e.g., 'L2/html-dict'"""
        return f"{self.layer_name}/data"
    
    def data_file(self) -> str:
        return self.storage.data_file(key_data=self.key_data())
    
    def exists(self) -> bool:
        return self.storage.file_exist(path=self.data_file())
    
    def save(self, cache_id: str, data: dict) -> bool:
        return self.storage.save(cache_id=cache_id, key=self.key_data(), data=data)
    
    def load(self, cache_id: str) -> Optional[dict]:
        result = self.storage.load__json(cache_id=cache_id, key=self.key_data())
        if result:
            self.stats.hits += 1
        else:
            self.stats.misses += 1
        return result


class Html_Cache__Layer__Html__Dict(Html_Cache__Layer__Base):
    """L2: Parsed HTML dict"""
    
    layer_name = 'L2'
    
    def key_data(self) -> str:
        return "L2/html-dict"
    
    def build_from_html(self, html: str) -> dict:
        """Parse HTML to dict"""
        return Html__To__Html_Dict__With__Node_Ids(html=html).convert()
```

### 8.3 Manager Pattern

```python
class Html_Cache__Manager(Type_Safe):
    """Orchestrates multiple cache layers"""
    
    storage     : Perf__Storage__Base
    stats       : Schema__Html_Cache__Stats
    layer_html  : Html_Cache__Layer__Html       # L1
    layer_dict  : Html_Cache__Layer__Html__Dict # L2
    layer_mgraph: Html_Cache__Layer__MGraph     # L3
    
    def setup(self):
        # Ensure entry exists
        self.storage.create_file__perf_entry()
        
        # Initialize layers with shared storage
        self.layer_html   = Html_Cache__Layer__Html     (storage=self.storage, stats=self.stats)
        self.layer_dict   = Html_Cache__Layer__Html__Dict(storage=self.storage, stats=self.stats)
        self.layer_mgraph = Html_Cache__Layer__MGraph   (storage=self.storage, stats=self.stats)
        return self
    
    def get_dict(self, html: str) -> dict:
        cache_id = self.storage.cache_id()
        
        # Check L2 cache
        cached = self.layer_dict.load(cache_id=cache_id)
        if cached:
            return cached
        
        # Build and cache
        html_dict = self.layer_dict.build_from_html(html)
        self.layer_dict.save(cache_id=cache_id, data=html_dict)
        return html_dict
```

---

## 9. Data Portability

### 9.1 Everything Anchored to cache_id

The design ensures all data is portable via `cache_id`:

```python
# Given a cache_id, you can:

# 1. Get all paths
refs = storage.file__refs(cache_id)
# refs.all_paths.data     → [content, config, metadata files]
# refs.file_paths.data_folders → where child data lives

# 2. Get entry content
content = storage.file__contents__json(cache_id)

# 3. Get config and metadata
config   = storage.file__config(cache_id)
metadata = storage.file__metadata(cache_id)

# 4. Access any child data
for layer in ['L1', 'L2', 'L3']:
    data = storage.load__json(cache_id, f"{layer}/data")
```

### 9.2 Deterministic Lookup

Even without `cache_id`, you can find data:

```python
# From session/target → cache_key → cache_hash → cache_id

session_name = "my-session"
target_name  = "my-target"

cache_key  = f"sessions/{session_name}/targets/{target_name}"
cache_hash = hash_generator.from_string(cache_key)

# Hash reference gives you the cache_id
hash_ref = storage.file__hash(cache_hash)
cache_id = hash_ref.latest_id

# Now you have full access
```

### 9.3 Export/Import Pattern

```python
def export_session_target(storage, session_name, target_name) -> dict:
    """Export all data for a session/target"""
    cache_id = storage.cache_id()
    refs     = storage.file__refs(cache_id)
    
    return {
        'cache_id' : cache_id,
        'cache_hash': storage.cache_hash(),
        'cache_key': storage.cache_key(),
        'entry'    : storage.file__contents__json(cache_id),
        'config'   : storage.file__config(cache_id),
        'metadata' : storage.file__metadata(cache_id),
        'refs'     : refs,
        'data'     : {
            'L1': storage.load__json(cache_id, 'L1/raw-html'),
            'L2': storage.load__json(cache_id, 'L2/html-dict'),
            'L3': storage.load__json(cache_id, 'L3/mgraph-document'),
        }
    }
```

---

## 10. Best Practices

### 10.1 Entry Creation

- **Create once**: Entry creation is heavyweight (5 files)
- **Use `create_file__if_not_available`**: Idempotent creation
- **Choose meaningful session/target names**: They form the semantic path

### 10.2 Data Storage

- **Use data mode for layers**: Lightweight (1 file)
- **Consistent key naming**: `{layer}/{type}` pattern (e.g., `L2/html-dict`)
- **Don't create entries per data file**: Use child data under single entry

### 10.3 Lookup Strategy

```python
# Preferred: Cache the cache_id after first lookup
cache_id = storage.cache_id()  # Store this!

# Fallback: Compute via hash if needed
if not cache_id:
    cache_id = storage.create_file__perf_entry()
```

### 10.4 Error Handling

```python
def safe_load(storage, cache_id, key):
    """Load with proper error handling"""
    try:
        if not cache_id:
            return None
        return storage.load__json(cache_id=cache_id, key=key)
    except Exception:
        return None
```

### 10.5 Namespace Isolation

- Use different namespaces for different environments
- `pytest` for tests, `development`, `production`
- Namespaces provide complete isolation

---

## Summary

The cache service's two-tier storage model provides:

| Aspect | Entry (File Mode) | Data (Data Mode) |
|--------|------------------|------------------|
| Files created | 5 | 1 |
| Overhead | High | Minimal |
| References | Full tracking | None (via parent) |
| Use case | Anchor point | Layer data |
| Frequency | Once per session/target | Many per entry |

**Key takeaways:**

1. **Create entry once** per session/target combination
2. **Store layers as data files** under the entry
3. **Use cache_hash** for deterministic lookup without UUID
4. **All data portable** via cache_id anchoring
5. **Performance optimized** for high-volume layer caching
