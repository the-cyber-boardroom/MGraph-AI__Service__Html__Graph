# Phase E_5: URL Fetching with Caching

**Status**: 📋 Ready to Implement  
**Depends On**: Phase E_4 ✅ (Cache Service Integration)  
**Updated**: January 12, 2026  
**Methodology**: LETS (Load, Extract, Transform, Save)

---

## Introduction

### What We're Building

Phase E_5 adds the **"front door"** to our HTML caching infrastructure: the ability to fetch real web pages from URLs and process them through our complete caching pipeline. While Phase E_4 gave us the foundation (L1-L3 caching with cache service storage), we could only process HTML strings that were provided directly. Now we're adding the crucial first step: **L0 - URL fetching with intelligent HTTP caching**.

```
                    PHASE E_5 ADDITION
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                      │
│    URL ──────► L0 ──────► L1 ──────► L2 ──────► L3                  │
│    │          │          │          │          │                     │
│    │          │          │          │          └─► MGraph Document   │
│    │          │          │          └─► Parsed HTML Dict             │
│    │          │          └─► Raw HTML String                         │
│    │          └─► URL Metadata + HTTP Headers                        │
│    └─► https://example.com/page                                      │
│                                                                      │
│    ◄──────────── NEW ──────────────►◄──── FROM PHASE E_4 ──────────►│
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### The Problem We're Solving

Before Phase E_5, using our HTML caching system required manually providing HTML:

```python
# Phase E_4 approach - must provide HTML directly
manager.cache_html(target='my-page', html='<html>...</html>')
document = manager.get_mgraph(target='my-page')
```

This works for testing and controlled scenarios, but real-world usage needs:

1. **Automatic URL fetching** - Give us a URL, we handle the rest
2. **HTTP caching semantics** - ETags, Last-Modified, Cache-Control headers
3. **Conditional requests** - Only re-download when content has changed
4. **Rate limiting** - Don't overwhelm servers with requests
5. **Retry logic** - Handle transient network failures gracefully
6. **Batch processing** - Process many URLs efficiently

After Phase E_5:

```python
# Phase E_5 approach - just provide the URL
session = session_factory.create_session('my-crawl')
document = session.process_url('https://example.com/page')

# Everything handled automatically:
# - URL fetched with retries and rate limiting
# - HTTP headers cached for conditional requests
# - HTML processed through L1 → L2 → L3 pipeline
# - All layers cached for instant subsequent access
```

### How It Fits Into MGraph-AI

MGraph-AI is a **memory-first graph database** designed for AI workloads. The HTML caching infrastructure we're building enables:

```
┌─────────────────────────────────────────────────────────────────────┐
│                      MGraph-AI HTML Processing                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  WEB PAGES                    STRUCTURED DATA                        │
│  ──────────                   ───────────────                        │
│                                                                      │
│  ┌─────────────┐              ┌─────────────────────────────────┐   │
│  │ HTML Page 1 │──────────────►│                                │   │
│  │ HTML Page 2 │──────────────►│      MGraph Documents          │   │
│  │ HTML Page 3 │──────────────►│                                │   │
│  │     ...     │──────────────►│  • Nodes for HTML elements     │   │
│  │ HTML Page N │──────────────►│  • Edges for relationships     │   │
│  └─────────────┘              │  • Queryable graph structure    │   │
│                               │  • AI-ready semantic data       │   │
│                               └─────────────────────────────────┘   │
│                                                                      │
│  Phase E_5 handles the LEFT side (fetching + caching)               │
│  Phases E_1-E_4 handle the RIGHT side (parsing + graphing)          │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### The LETS Methodology

We're implementing this using **LETS (Load, Extract, Transform, Save)**, a data pipeline architecture that ensures:

| Principle | What It Means |
|-----------|---------------|
| **Type_Safe schemas at every boundary** | Not raw dicts, but validated `Type_Safe` classes flowing between stages |
| **Every stage saves its output** | No hidden in-memory states; all data externalized to cache service |
| **Deterministic behavior** | Same input + same code = same output, always |
| **Replayability** | Can re-run any stage from cached intermediate data |
| **Minimum viable propagation** | Only process what changed, not everything |

Our four LETS stages map directly to cache layers:

| Stage | Layer | Input | Output | Action |
|-------|-------|-------|--------|--------|
| **Load** | L0 | URL | HTTP metadata | Fetch from network |
| **Extract** | L1 | HTTP response | Raw HTML | Store content |
| **Transform** | L2 | HTML string | Parsed dict | Parse structure |
| **Save** | L3 | Dict | MGraph document | Build graph |

### What We Learned from Phase E_4

Phase E_4 taught us several important lessons that shape Phase E_5:

1. **The `cache_id` Pattern**: All data operations require a parent entry's `cache_id` to ensure lightweight storage (1 file per operation instead of 5).

2. **One Storage Instance per Layer**: Since `Perf__Storage__Cache_Service` takes `file_id` as a constructor parameter, each layer needs its own storage instance.

3. **Layers Use Storage Directly**: Layers receive `storage` and `stats` via constructor, not through a `manager` reference.

4. **Factory Pattern Works Well**: Creating sessions/targets via factories makes the API clean and extensible.

5. **In-Memory Cache Service for Testing**: Using `client_cache_service()` gives us real API behavior without network overhead.

### Execution Modes: First Time vs. Cached vs. Selective

A key insight from the LETS methodology is supporting different **execution modes**:

```
┌─────────────────────────────────────────────────────────────────────┐
│                       EXECUTION MODES                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  FULL MODE (First Time)                                             │
│  ──────────────────────                                             │
│  URL ──► L0 ──► L1 ──► L2 ──► L3                                    │
│      fetch   cache  parse  build                                     │
│                                                                      │
│  All stages execute. Network request made. Everything cached.        │
│  Use case: Initial crawl, force refresh                             │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  CACHED MODE (Second Time)                                          │
│  ─────────────────────────                                          │
│  URL ──► [L0 cached] ──► [L1 cached] ──► [L2 cached] ──► [L3 cached]│
│           skip           skip           skip           skip         │
│                                                                      │
│  All stages skip - data loaded from cache. No network. Instant.     │
│  Use case: Subsequent access, offline mode                          │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  SELECTIVE MODE (Rebuild Specific Layers)                           │
│  ────────────────────────────────────────                           │
│  URL ──► [L0 cached] ──► [L1 cached] ──► L2 ──► L3                  │
│           skip           skip         rebuild  rebuild               │
│                                                                      │
│  Choose which layers to reprocess. Useful when parser improves.     │
│  Use case: Schema changes, bug fixes, algorithm improvements        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

This is powerful because:
- **First time**: Pay the network cost once, cache everything
- **Second time**: Instant access from cache (~1ms vs ~500ms)
- **Selective rebuild**: When you improve L2 parsing, rebuild L2+L3 without re-fetching

### Why No Mocks?

Traditional testing uses mock objects to simulate HTTP responses. We're taking a different approach: **real HTTP against a local test server**.

```python
# Traditional approach (we're NOT doing this)
mock_response = Mock()
mock_response.status_code = 200
mock_response.text = '<html>...</html>'
requests.get = Mock(return_value=mock_response)

# Our approach (using Temp_Web_Server)
with Temp_Folder() as folder:
    folder.add_file('index.html', '<html>...</html>')
    with Temp_Web_Server(root_folder=folder.path()) as server:
        response = fetcher.fetch(server.url('index.html'))
        # Real HTTP request to real server!
```

**Why this matters:**
- Tests exercise actual HTTP code paths
- Edge cases (timeouts, redirects, headers) work identically to production
- No mock maintenance when HTTP library internals change
- Tests are more trustworthy

### The Type_Safe Foundation

Every piece of data in Phase E_5 uses **Type_Safe primitives** - never raw `str`, `int`, or `float`:

```python
# ✗ DANGEROUS - Raw primitives allow invalid data
class Bad_Config:
    url: str                    # Could be "not-a-url" or SQL injection
    timeout: int                # Could be -1 or 999999
    status: int                 # Could be 9999 (invalid HTTP status)

# ✓ SAFE - Domain primitives validate at construction
class Schema__Fetcher__Config(Type_Safe):
    url: Safe_Str__Url          # Must be valid http(s):// URL
    timeout: Safe_UInt__Seconds # Unsigned, max 3600
    status: Safe_UInt__Http__Status_Code  # Range 100-599
```

This catches bugs at the moment data enters the system, not deep in processing where the cause is hard to trace.

### What You'll Get After Phase E_5

```python
# Simple API for processing any URL
from phase_e.html_cache import Html_Cache__Session_Factory

# Create a session for your crawl
factory = Html_Cache__Session_Factory(cache_client, config)
session = factory.create_session('product-catalog-2026-01')

# Process URLs - everything cached automatically
for url in product_urls:
    document = session.process_url(url)
    # document is a full MGraph with:
    # - All HTML elements as nodes
    # - Parent-child relationships as edges
    # - Queryable graph structure
    # - Cached at L0, L1, L2, L3 for instant re-access

# Check stats
print(f"Fetched: {session.stats.l0_misses}")  # Network requests
print(f"Cached:  {session.stats.l0_hits}")     # Cache hits
```

---

## Key Design Principles

| Principle | Application |
|-----------|-------------|
| **No Raw Primitives** | Use `Safe_Str__Url`, `Safe_UInt`, etc. - never raw `str`, `int`, `float` |
| **LETS Methodology** | Type_Safe schemas in → Type_Safe schemas out at every stage |
| **Pure Data Schemas** | Schemas contain ONLY type annotations - NO methods |
| **Real HTTP Testing** | Use `Temp_Web_Server` - no mocks |
| **Factory Pattern** | Easy creation of sessions/targets via factories |
| **Execution Modes** | First-time, Cached, Selective execution support |

---

## 1. New Safe Primitives for Phase E_5

We need to create these custom primitives for the HTML caching domain:

### 1.1 Session/Target/File Primitives

```python
# ═══════════════════════════════════════════════════════════════════════════════
# phase_e/storage/primitives/Safe_Str__Session_Name.py
# ═══════════════════════════════════════════════════════════════════════════════
import re
from osbot_utils.type_safe.primitives.core.Safe_Str import Safe_Str

class Safe_Str__Session_Name(Safe_Str):                     # Session identifier
    max_length = 128
    regex      = re.compile(r'[^a-zA-Z0-9_\-]')             # Only: a-z A-Z 0-9 _ -
    # Examples: 'crawl-2026-01-12', 'dev-session', 'test-run-001'


class Safe_Str__Target_Name(Safe_Str):                      # Target (URL-derived) identifier
    max_length = 256
    regex      = re.compile(r'[^a-zA-Z0-9_\-]')             # Only: a-z A-Z 0-9 _ -
    # Examples: 'example-com-products-shoes', 'news-site-article-123'


class Safe_Str__Data_File_Id(Safe_Str):                     # File ID for layer data
    max_length = 64
    regex      = re.compile(r'[^a-zA-Z0-9_\-]')             # Only: a-z A-Z 0-9 _ -
    # Examples: 'L0-url-metadata', 'L1-raw-html', 'L2-html-dict'


class Safe_Str__Data_Key(Safe_Str):                         # Data key within cache entry
    max_length = 256
    regex      = re.compile(r'[^a-zA-Z0-9_\-/]')            # Allows: a-z A-Z 0-9 _ - /
    # Examples: 'L1/raw-html', 'L2/metadata', 'L3/mgraph-document'
```

### 1.2 HTTP Primitives (Many Already Exist)

```python
# ═══════════════════════════════════════════════════════════════════════════════
# These already exist in osbot_utils - use them!
# ═══════════════════════════════════════════════════════════════════════════════
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url           import Safe_Str__Url
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html          import Safe_Str__Html
from osbot_utils.type_safe.primitives.domains.http.safe_str.Safe_Str__Http__ETag   import Safe_Str__Http__ETag
from osbot_utils.type_safe.primitives.domains.http.safe_str.Safe_Str__Http__Last_Modified import Safe_Str__Http__Last_Modified
from osbot_utils.type_safe.primitives.domains.http.safe_str.Safe_Str__Http__Cache_Control import Safe_Str__Http__Cache_Control
from osbot_utils.type_safe.primitives.domains.http.safe_str.Safe_Str__Http__Content_Type  import Safe_Str__Http__Content_Type
from osbot_utils.type_safe.primitives.domains.http.safe_str.Safe_Str__Http__User_Agent    import Safe_Str__Http__User_Agent
from osbot_utils.type_safe.primitives.domains.network.safe_uint.Safe_UInt__Port           import Safe_UInt__Port

# ═══════════════════════════════════════════════════════════════════════════════
# New HTTP primitives we need to create
# ═══════════════════════════════════════════════════════════════════════════════
class Safe_UInt__Http__Status_Code(Safe_UInt):              # HTTP status code
    min_value = 100
    max_value = 599

class Safe_UInt__Milliseconds(Safe_UInt):                   # Duration in ms
    min_value = 0
    max_value = 600_000                                     # Max 10 minutes

class Safe_UInt__Seconds(Safe_UInt):                        # Duration in seconds
    min_value = 0
    max_value = 3600                                        # Max 1 hour

class Safe_UInt__Bytes(Safe_UInt):                          # Content length in bytes
    min_value = 0
    max_value = 100_000_000                                 # Max 100MB
```

### 1.3 Content Hash Primitive

```python
class Safe_Str__Content_Hash(Safe_Str):                     # SHA-256 content hash
    max_length   = 64
    exact_length = True
    regex        = re.compile(r'[^a-f0-9]')                 # Only hex chars
```

---

## 2. Cache Service Hierarchy

### 2.1 The Complete Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         CACHE SERVICE HIERARCHY                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  NAMESPACE (environment-level)                                                   │
│  └── Type: Safe_Str__Id                                                         │
│  └── Purpose: Isolate environments (pytest, dev, prod)                          │
│  └── Examples: 'pytest', 'development', 'production'                            │
│                                                                                  │
│  SESSION (run-level grouping)                                                    │
│  └── Type: Safe_Str__Session_Name                                               │
│  └── Purpose: Isolate different runs/batches                                    │
│  └── Examples: 'crawl-2026-01-12', 'test-suite-001'                             │
│                                                                                  │
│  TARGET (URL/page-level grouping)                                                │
│  └── Type: Safe_Str__Target_Name                                                │
│  └── Purpose: Group all data for one URL/page                                   │
│  └── Examples: 'example-com-page1', 'news-site-article-123'                     │
│                                                                                  │
│  FILE_ID (layer-level storage)                                                   │
│  └── Type: Safe_Str__Data_File_Id                                               │
│  └── Purpose: Identify which layer data this is                                 │
│  └── Examples: 'L0-url-metadata', 'L1-raw-html', 'L2-html-dict'                 │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Storage Path Formula

```python
# Cache key formula:
cache_key = f'sessions/{session_name}/targets/{target_name}'

# Full path in cache service:
# {namespace}/data/key-based/{cache_key}/{file_id}/data/{data_key}

# Example:
# pytest/data/key-based/sessions/crawl-2026-01-12/targets/example-com-page1/L1-raw-html/data/...
```

### 2.3 Layer File IDs

| Layer | File_ID | Data Key | Content |
|-------|---------|----------|---------|
| L0 | `L0-url-metadata` | `L0/url-metadata` | URL, HTTP headers, fetch timing |
| L1 | `L1-raw-html` | `L1/raw-html` | Raw HTML content |
| L2 | `L2-html-dict` | `L2/html-dict` | Parsed HTML structure |
| L3 | `L3-mgraph-document` | `L3/mgraph-document` | MGraph representation |

---

## 3. LETS Pipeline Stages

### 3.1 The Four Stages

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    LETS PIPELINE for HTML Processing                         │
│  ─────────────────────────────────────────────────────────────────────────── │
│                                                                              │
│  LOAD (L0)                                                                   │
│  ├── Input:  Safe_Str__Url                                                  │
│  ├── Output: Schema__Html_Cache__L0__Url_Metadata                           │
│  ├── Save:   L0/url-metadata.json                                           │
│  └── Action: Fetch URL, cache HTTP response metadata                        │
│                                                                              │
│  EXTRACT (L1)                                                                │
│  ├── Input:  HTTP response body                                             │
│  ├── Output: Schema__Html_Cache__L1__Html_Metadata                          │
│  ├── Save:   L1/raw-html.json                                               │
│  └── Action: Store raw HTML with content hash                               │
│                                                                              │
│  TRANSFORM (L2)                                                              │
│  ├── Input:  Safe_Str__Html                                                 │
│  ├── Output: Schema__Html_Cache__L2__Dict_Metadata                          │
│  ├── Save:   L2/html-dict.json                                              │
│  └── Action: Parse HTML to structured dict with node IDs                    │
│                                                                              │
│  SAVE (L3)                                                                   │
│  ├── Input:  Parsed dict                                                    │
│  ├── Output: Schema__Html_Cache__L3__MGraph_Metadata                        │
│  ├── Save:   L3/mgraph-document.json                                        │
│  └── Action: Build MGraph document, serialize with type preservation        │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Type_Safe Schemas at Every Boundary

```python
# ═══════════════════════════════════════════════════════════════════════════════
# L0: URL Metadata Schema (PURE DATA - NO METHODS)
# ═══════════════════════════════════════════════════════════════════════════════
class Schema__Html_Cache__L0__Url_Metadata(Type_Safe):
    # URL Information
    url            : Safe_Str__Url                          # Original URL
    normalized_url : Safe_Str__Url                          # Normalized for dedup
    final_url      : Safe_Str__Url                          # After redirects
    
    # HTTP Response
    status_code    : Safe_UInt__Http__Status_Code           # 200, 404, etc.
    content_type   : Safe_Str__Http__Content_Type           # text/html
    content_length : Safe_UInt__Bytes                       # Response size
    
    # Caching Headers
    etag           : Safe_Str__Http__ETag                   # For conditional requests
    last_modified  : Safe_Str__Http__Last_Modified          # For conditional requests
    cache_control  : Safe_Str__Http__Cache_Control          # Cache directives
    
    # Timing
    fetched_at     : Timestamp_Now                          # When fetched
    fetch_duration : Safe_UInt__Milliseconds                # How long fetch took
    
    # Content Reference
    content_hash   : Safe_Str__Content_Hash                 # Links to L1


# ═══════════════════════════════════════════════════════════════════════════════
# L1: HTML Metadata Schema (PURE DATA - NO METHODS)
# ═══════════════════════════════════════════════════════════════════════════════
class Schema__Html_Cache__L1__Html_Metadata(Type_Safe):
    source         : Safe_Str__Url                          # Where HTML came from
    size_bytes     : Safe_UInt__Bytes                       # HTML content size
    content_hash   : Safe_Str__Content_Hash                 # SHA-256 of content
    cached_at      : Timestamp_Now                          # When cached


# ═══════════════════════════════════════════════════════════════════════════════
# L2: Dict Metadata Schema (PURE DATA - NO METHODS)
# ═══════════════════════════════════════════════════════════════════════════════
class Schema__Html_Cache__L2__Dict_Metadata(Type_Safe):
    content_hash   : Safe_Str__Content_Hash                 # SHA-256 of dict
    cached_at      : Timestamp_Now                          # When cached
    node_count     : Safe_UInt                              # Number of HTML nodes


# ═══════════════════════════════════════════════════════════════════════════════
# L3: MGraph Metadata Schema (PURE DATA - NO METHODS)
# ═══════════════════════════════════════════════════════════════════════════════
class Schema__Html_Cache__L3__MGraph_Metadata(Type_Safe):
    content_hash   : Safe_Str__Content_Hash                 # SHA-256 of graph
    cached_at      : Timestamp_Now                          # When cached
    node_count     : Safe_UInt                              # Graph nodes
    edge_count     : Safe_UInt                              # Graph edges
```

---

## 4. Execution Modes

### 4.1 Three Execution Modes

```python
class Enum__Execution_Mode(Enum):
    FULL         = 'full'                                   # First time: fetch → cache all
    CACHED       = 'cached'                                 # 2nd time: read from cache only
    SELECTIVE    = 'selective'                              # Choose which layers to process
```

### 4.2 Mode Behavior

| Mode | L0 (Fetch) | L1 (HTML) | L2 (Dict) | L3 (MGraph) | Use Case |
|------|------------|-----------|-----------|-------------|----------|
| FULL | ✓ Execute | ✓ Execute | ✓ Execute | ✓ Execute | First run, force refresh |
| CACHED | ✗ Skip (use cache) | ✗ Skip | ✗ Skip | ✗ Skip | Subsequent runs |
| SELECTIVE | Configurable | Configurable | Configurable | Configurable | Rebuild specific layers |

### 4.3 Execution Config Schema

```python
class Schema__Html_Cache__Execution_Config(Type_Safe):
    mode           : Enum__Execution_Mode = Enum__Execution_Mode.FULL
    force_l0       : bool = False                           # Force re-fetch URL
    force_l1       : bool = False                           # Force re-cache HTML
    force_l2       : bool = False                           # Force rebuild dict
    force_l3       : bool = False                           # Force rebuild MGraph
    skip_on_cached : bool = True                            # Skip if already cached
```

### 4.4 Pipeline Execution Logic

```python
class Html_Cache__Pipeline(Type_Safe):                      # Pipeline orchestrator
    manager        : Html_Cache__Manager
    config         : Schema__Html_Cache__Execution_Config
    
    def process_url(self, url: Safe_Str__Url) -> Schema__Html_Cache__Pipeline_Result:
        """LETS pipeline: URL → L0 → L1 → L2 → L3"""
        target = self._url_to_target(url)
        
        # L0: LOAD - Fetch URL
        if self._should_execute_l0(target):
            l0_result = self._execute_l0(url, target)
            self._save_stage('L0', target, l0_result)
        
        # L1: EXTRACT - Store HTML
        if self._should_execute_l1(target):
            l1_result = self._execute_l1(target)
            self._save_stage('L1', target, l1_result)
        
        # L2: TRANSFORM - Parse to dict
        if self._should_execute_l2(target):
            l2_result = self._execute_l2(target)
            self._save_stage('L2', target, l2_result)
        
        # L3: SAVE - Build MGraph
        if self._should_execute_l3(target):
            l3_result = self._execute_l3(target)
            self._save_stage('L3', target, l3_result)
        
        return self._build_result(target)
    
    def _should_execute_l0(self, target: Safe_Str__Target_Name) -> bool:
        if self.config.force_l0:
            return True
        if self.config.mode == Enum__Execution_Mode.CACHED:
            return False
        if self.config.skip_on_cached and self.manager.has_l0(target):
            return False
        return True
```

---

## 5. Factory Pattern for Easy Session/Target Creation

### 5.1 Storage Factory

```python
class Html_Cache__Storage_Factory(Type_Safe):
    """Factory for creating per-layer storage instances."""
    
    config         : Schema__Perf__Storage__Config
    cache_client   : Cache_Service__Client
    session_name   : Safe_Str__Session_Name
    
    def create_for_layer(self, 
                         layer_name  : Safe_Str__Id,
                         target_name : Safe_Str__Target_Name
                        ) -> Perf__Storage__Cache_Service:
        """Create storage instance for specific layer and target."""
        file_id = self._layer_to_file_id(layer_name)
        return Perf__Storage__Cache_Service(
            config       = self.config,
            client       = self.cache_client,
            session_name = self.session_name,
            target_name  = target_name,
            file_id      = file_id
        )
    
    def _layer_to_file_id(self, layer_name: Safe_Str__Id) -> Safe_Str__Data_File_Id:
        mapping = {
            'L0': 'L0-url-metadata',
            'L1': 'L1-raw-html',
            'L2': 'L2-html-dict',
            'L3': 'L3-mgraph-document',
        }
        return Safe_Str__Data_File_Id(mapping.get(layer_name, f'{layer_name}-data'))
```

### 5.2 Session Factory

```python
class Html_Cache__Session_Factory(Type_Safe):
    """Factory for creating cache sessions with all layers configured."""
    
    cache_client   : Cache_Service__Client
    config         : Schema__Perf__Storage__Config
    
    def create_session(self, session_name: Safe_Str__Session_Name) -> 'Html_Cache__Session':
        """Create a new cache session."""
        return Html_Cache__Session(
            session_name   = session_name,
            storage_factory = Html_Cache__Storage_Factory(
                config       = self.config,
                cache_client = self.cache_client,
                session_name = session_name
            )
        )


class Html_Cache__Session(Type_Safe):
    """A cache session that can process multiple targets."""
    
    session_name    : Safe_Str__Session_Name
    storage_factory : Html_Cache__Storage_Factory
    stats           : Schema__Html_Cache__Stats
    fetcher         : Html_Fetcher
    targets         : Dict__Targets                         # target_name → manager
    
    def get_manager_for_target(self, target_name: Safe_Str__Target_Name) -> Html_Cache__Manager:
        """Get or create manager for a target."""
        if target_name not in self.targets:
            self.targets[target_name] = self._create_manager(target_name)
        return self.targets[target_name]
    
    def process_url(self, url: Safe_Str__Url) -> Html_MGraph__Document:
        """Process URL through full LETS pipeline."""
        target_name = self._url_to_target(url)
        manager     = self.get_manager_for_target(target_name)
        return manager.get_mgraph_from_url(url)
    
    def _create_manager(self, target_name: Safe_Str__Target_Name) -> Html_Cache__Manager:
        return Html_Cache__Manager(
            storage_l0 = self.storage_factory.create_for_layer('L0', target_name),
            storage_l1 = self.storage_factory.create_for_layer('L1', target_name),
            storage_l2 = self.storage_factory.create_for_layer('L2', target_name),
            storage_l3 = self.storage_factory.create_for_layer('L3', target_name),
            stats      = self.stats,
            fetcher    = self.fetcher
        )
```

### 5.3 Usage Example

```python
# ═══════════════════════════════════════════════════════════════════════════════
# Easy session/target creation via factories
# ═══════════════════════════════════════════════════════════════════════════════

# Create session factory (once at startup)
cache_client, cache_service = client_cache_service()
session_factory = Html_Cache__Session_Factory(
    cache_client = Cache_Service__Client(cache_client=cache_client),
    config       = Schema__Perf__Storage__Config(storage_mode=Enum__Storage_Mode.CACHE_SERVICE)
)

# Create session for this crawl run
session = session_factory.create_session(Safe_Str__Session_Name('crawl-2026-01-12'))

# Process URLs - factory handles all storage setup
doc1 = session.process_url(Safe_Str__Url('https://example.com/page1'))
doc2 = session.process_url(Safe_Str__Url('https://example.com/page2'))
doc3 = session.process_url(Safe_Str__Url('https://example.com/page3'))

# Stats accumulated across all targets
print(session.stats.l0_hits)                                # Cache hits at L0
print(session.stats.l1_hits)                                # Cache hits at L1
```

---

## 6. HTML Fetcher (Real HTTP Client)

### 6.1 Fetcher Config Schema

```python
class Schema__Html_Fetcher__Config(Type_Safe):
    timeout_seconds         : Safe_UInt__Seconds = 30
    max_retries             : Safe_UInt          = 3
    retry_delay_seconds     : Safe_UInt__Seconds = 1
    min_request_interval_ms : Safe_UInt__Milliseconds = 100     # Rate limiting
    user_agent              : Safe_Str__Http__User_Agent = 'MGraph-AI Html_Fetcher/1.0'
    follow_redirects        : bool = True
    max_redirects           : Safe_UInt = 5
```

### 6.2 Fetcher Response Schema

```python
class Schema__Html_Fetcher__Response(Type_Safe):
    url            : Safe_Str__Url                          # Original URL
    final_url      : Safe_Str__Url                          # After redirects
    status_code    : Safe_UInt__Http__Status_Code           # HTTP status
    headers        : Dict__Http_Headers                     # Response headers
    html           : Safe_Str__Html                         # Response body
    ok             : bool                                   # 200 <= status < 300
    error          : Safe_Str__Text                         # Error message if failed
    duration_ms    : Safe_UInt__Milliseconds                # Request duration
```

### 6.3 Fetcher Implementation

```python
class Html_Fetcher(Type_Safe):
    """HTTP client with retries and rate limiting."""
    
    config              : Schema__Html_Fetcher__Config
    last_request_time   : Safe_UInt__Milliseconds = 0
    
    def fetch(self, 
              url     : Safe_Str__Url, 
              headers : Dict__Http_Headers = None
             ) -> Schema__Html_Fetcher__Response:
        """Fetch URL with retries and rate limiting."""
        import requests
        import time
        
        self._apply_rate_limit()
        
        start_time      = time.time()
        request_headers = self._build_headers(headers)
        
        for attempt in range(self.config.max_retries):
            try:
                response = requests.get(
                    str(url),                               # Convert Safe_Str to str for requests
                    headers         = dict(request_headers) if request_headers else {},
                    timeout         = int(self.config.timeout_seconds),
                    allow_redirects = self.config.follow_redirects
                )
                
                duration_ms = Safe_UInt__Milliseconds(int((time.time() - start_time) * 1000))
                
                return Schema__Html_Fetcher__Response(
                    url         = url,
                    final_url   = Safe_Str__Url(response.url),
                    status_code = Safe_UInt__Http__Status_Code(response.status_code),
                    headers     = self._parse_headers(response.headers),
                    html        = Safe_Str__Html(response.text) if response.ok else Safe_Str__Html(''),
                    ok          = response.ok,
                    duration_ms = duration_ms
                )
                
            except requests.RequestException as e:
                if attempt < self.config.max_retries - 1:
                    time.sleep(int(self.config.retry_delay_seconds))
                    continue
                
                return Schema__Html_Fetcher__Response(
                    url     = url,
                    ok      = False,
                    error   = Safe_Str__Text(str(e))
                )
        
        return Schema__Html_Fetcher__Response(
            url   = url,
            ok    = False,
            error = Safe_Str__Text('Max retries exceeded')
        )
```

---

## 7. Testing with Temp_Web_Server (No Mocks)

### 7.1 Test Setup Pattern

```python
from unittest                                    import TestCase
from osbot_utils.testing.Temp_Folder             import Temp_Folder
from osbot_utils.testing.Temp_Web_Server         import Temp_Web_Server
from tests.Phase_E__Fast_API__Test_Objs          import client_cache_service

# Test HTML content
HTML_SIMPLE = Safe_Str__Html('''<!DOCTYPE html>
<html><head><title>Test</title></head>
<body><h1>Hello World</h1></body></html>''')

HTML_WITH_LINKS = Safe_Str__Html('''<!DOCTYPE html>
<html><head><title>Links</title></head>
<body><a href="/page2">Link</a></body></html>''')


class test_Html_Cache__Full_Pipeline(TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Cache service (in-memory)
        cls.cache_client, cls.cache_service = client_cache_service()
        cls.cache_client_wrapper = Cache_Service__Client(cache_client=cls.cache_client)
        
        # Temp folder with HTML files
        cls.temp_folder = Temp_Folder()
        cls.temp_folder.__enter__()
        cls.temp_folder.add_file('index.html', str(HTML_SIMPLE))
        cls.temp_folder.add_file('page2.html', str(HTML_WITH_LINKS))
        
        # Real HTTP server
        cls.server = Temp_Web_Server(root_folder=cls.temp_folder.path())
        cls.server.__enter__()
        
        # Session factory
        cls.session_factory = Html_Cache__Session_Factory(
            cache_client = cls.cache_client_wrapper,
            config       = Schema__Perf__Storage__Config()
        )
    
    @classmethod
    def tearDownClass(cls):
        cls.server.__exit__(None, None, None)
        cls.temp_folder.__exit__(None, None, None)
    
    def test_full_pipeline__first_fetch(self):
        """LETS pipeline: URL → L0 → L1 → L2 → L3 (first time)"""
        with self.session_factory.create_session(Safe_Str__Session_Name('test-001')) as session:
            url      = Safe_Str__Url(self.server.url('index.html'))
            document = session.process_url(url)
            
            assert document is not None
            assert session.stats.l0_misses == 1             # Network fetch happened
            assert session.stats.l1_misses == 1             # HTML cached
    
    def test_full_pipeline__cached_fetch(self):
        """LETS pipeline: All cached (second time)"""
        with self.session_factory.create_session(Safe_Str__Session_Name('test-002')) as session:
            url = Safe_Str__Url(self.server.url('index.html'))
            
            # First fetch
            session.process_url(url)
            
            # Reset stats
            session.stats = Schema__Html_Cache__Stats()
            
            # Second fetch - should hit cache
            document = session.process_url(url)
            
            assert document is not None
            assert session.stats.l0_hits == 1               # Cache hit at L0
            assert session.stats.l1_hits == 1               # Cache hit at L1
```

### 7.2 Testing Conditional Requests (ETag/304)

```python
class test_Html_Fetcher__Conditional(TestCase):
    
    def test_conditional_fetch__304_not_modified(self):
        """Test ETag conditional request returns 304."""
        # Custom handler that returns ETag
        def etag_handler(request):
            if_none_match = request.headers.get('If-None-Match')
            if if_none_match == '"abc123"':
                request.send_response(304)
                request.end_headers()
                return
            
            request.send_response(200)
            request.send_header('Content-Type', 'text/html')
            request.send_header('ETag', '"abc123"')
            request.end_headers()
            request.wfile.write(b'<html>Test</html>')
        
        with Temp_Web_Server(http_handler=etag_handler) as server:
            fetcher = Html_Fetcher()
            
            # First request - get ETag
            response1 = fetcher.fetch(Safe_Str__Url(server.url('/')))
            assert response1.status_code == 200
            
            # Second request with If-None-Match
            headers = Dict__Http_Headers()
            headers['If-None-Match'] = '"abc123"'
            response2 = fetcher.fetch(Safe_Str__Url(server.url('/')), headers=headers)
            
            assert response2.status_code == 304
```

---

## 8. Type_Safe Collections

### 8.1 Collection Definitions

```python
# ═══════════════════════════════════════════════════════════════════════════════
# Collections for cache infrastructure
# ═══════════════════════════════════════════════════════════════════════════════
from typing                                                   import Dict
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__Dict import Type_Safe__Dict

class Dict__Http_Headers(Type_Safe__Dict[Safe_Str__Http__Header__Name, Safe_Str__Http__Header__Value]):
    """HTTP headers dictionary."""
    pass

class Dict__Targets(Type_Safe__Dict[Safe_Str__Target_Name, Html_Cache__Manager]):
    """Target name to manager mapping."""
    pass

class Dict__Cache_Ids(Type_Safe__Dict[Safe_Str__Target_Name, Cache_Id]):
    """Target name to cache_id mapping."""
    pass
```

---

## 9. Files to Create

### 9.1 New Primitives

| File | Purpose |
|------|---------|
| `phase_e/storage/primitives/Safe_Str__Session_Name.py` | Session name primitive |
| `phase_e/storage/primitives/Safe_Str__Target_Name.py` | Target name primitive |
| `phase_e/storage/primitives/Safe_Str__Data_File_Id.py` | File ID primitive |
| `phase_e/storage/primitives/Safe_Str__Data_Key.py` | Data key primitive |
| `phase_e/storage/primitives/Safe_Str__Content_Hash.py` | Content hash primitive |
| `phase_e/storage/primitives/Safe_UInt__Http__Status_Code.py` | HTTP status code |
| `phase_e/storage/primitives/Safe_UInt__Milliseconds.py` | Duration in ms |
| `phase_e/storage/primitives/Safe_UInt__Bytes.py` | Size in bytes |

### 9.2 Core Components

| File | Purpose |
|------|---------|
| `phase_e/html_cache/Html_Fetcher.py` | HTTP client with retries |
| `phase_e/html_cache/layers/Html_Cache__Layer__Url.py` | L0 URL layer |
| `phase_e/html_cache/Html_Cache__Storage_Factory.py` | Per-layer storage factory |
| `phase_e/html_cache/Html_Cache__Session_Factory.py` | Session factory |
| `phase_e/html_cache/Html_Cache__Session.py` | Session with multiple targets |
| `phase_e/html_cache/Html_Cache__Pipeline.py` | LETS pipeline orchestrator |

### 9.3 Schemas (Pure Data)

| File | Purpose |
|------|---------|
| `phase_e/html_cache/schemas/Schema__Html_Fetcher__Config.py` | Fetcher config |
| `phase_e/html_cache/schemas/Schema__Html_Fetcher__Response.py` | Fetcher response |
| `phase_e/html_cache/schemas/Schema__Html_Cache__L0__Url_Metadata.py` | L0 metadata |
| `phase_e/html_cache/schemas/Schema__Html_Cache__Execution_Config.py` | Execution mode config |
| `phase_e/html_cache/schemas/Schema__Html_Cache__Pipeline_Result.py` | Pipeline result |

### 9.4 Collections

| File | Purpose |
|------|---------|
| `phase_e/html_cache/collections/Dict__Http_Headers.py` | HTTP headers dict |
| `phase_e/html_cache/collections/Dict__Targets.py` | Targets dict |

### 9.5 Enums

| File | Purpose |
|------|---------|
| `phase_e/html_cache/enums/Enum__Execution_Mode.py` | Pipeline execution mode |

### 9.6 Tests (Real HTTP, No Mocks)

| File | Purpose |
|------|---------|
| `tests/test_Html_Fetcher.py` | Fetcher with Temp_Web_Server |
| `tests/test_Html_Cache__Layer__Url.py` | L0 layer tests |
| `tests/test_Html_Cache__Session.py` | Session tests |
| `tests/test_Html_Cache__Pipeline.py` | Full LETS pipeline tests |

---

## 10. Success Criteria

### Type_Safe Requirements
- [ ] **No raw primitives** - All `str`/`int`/`float` replaced with Safe_* types
- [ ] **Pure data schemas** - Schemas have NO methods
- [ ] **Type_Safe collections** - `Dict__*`, `List__*` for typed containers
- [ ] **Enums for modes** - `Enum__Execution_Mode`, not strings

### LETS Requirements
- [ ] **Schema at every boundary** - Type_Safe in → Type_Safe out
- [ ] **Save after each stage** - L0 → L1 → L2 → L3 all persisted
- [ ] **Deterministic** - Same input = same output
- [ ] **Replayable** - Can re-run any stage from cached data

### Execution Mode Requirements
- [ ] **FULL mode** - Fetch and process everything
- [ ] **CACHED mode** - Use cache only, no network
- [ ] **SELECTIVE mode** - Choose which layers to process/rebuild

### Factory Pattern Requirements
- [ ] **Storage factory** - Creates per-layer storage instances
- [ ] **Session factory** - Easy session creation
- [ ] **Target management** - Automatic target creation per URL

### Testing Requirements
- [ ] **Real HTTP** - Use Temp_Web_Server
- [ ] **No mocks** - All tests against real (local) HTTP
- [ ] **Context managers** - `with` pattern throughout
- [ ] **Inline comments** - No docstrings

---

## 11. Import Reference

```python
# ═══════════════════════════════════════════════════════════════════════════════
# Core Type_Safe
# ═══════════════════════════════════════════════════════════════════════════════
from osbot_utils.type_safe.Type_Safe import Type_Safe

# ═══════════════════════════════════════════════════════════════════════════════
# Core Primitives
# ═══════════════════════════════════════════════════════════════════════════════
from osbot_utils.type_safe.primitives.core.Safe_Str   import Safe_Str
from osbot_utils.type_safe.primitives.core.Safe_UInt  import Safe_UInt

# ═══════════════════════════════════════════════════════════════════════════════
# Domain Primitives (Existing)
# ═══════════════════════════════════════════════════════════════════════════════
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url                      import Safe_Str__Url
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html                     import Safe_Str__Html
from osbot_utils.type_safe.primitives.domains.http.safe_str.Safe_Str__Http__ETag              import Safe_Str__Http__ETag
from osbot_utils.type_safe.primitives.domains.http.safe_str.Safe_Str__Http__Last_Modified     import Safe_Str__Http__Last_Modified
from osbot_utils.type_safe.primitives.domains.http.safe_str.Safe_Str__Http__Cache_Control     import Safe_Str__Http__Cache_Control
from osbot_utils.type_safe.primitives.domains.http.safe_str.Safe_Str__Http__Content_Type      import Safe_Str__Http__Content_Type
from osbot_utils.type_safe.primitives.domains.http.safe_str.Safe_Str__Http__User_Agent        import Safe_Str__Http__User_Agent
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now              import Timestamp_Now
from osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id                             import Safe_Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id               import Safe_Str__Id
from osbot_utils.type_safe.primitives.domains.text.safe_str.Safe_Str__Text                    import Safe_Str__Text

# ═══════════════════════════════════════════════════════════════════════════════
# Testing Utilities
# ═══════════════════════════════════════════════════════════════════════════════
from osbot_utils.testing.Temp_Folder     import Temp_Folder
from osbot_utils.testing.Temp_Web_Server import Temp_Web_Server
from osbot_utils.testing.Temp_File       import Temp_File

# ═══════════════════════════════════════════════════════════════════════════════
# New Primitives (To Create)
# ═══════════════════════════════════════════════════════════════════════════════
from phase_e.storage.primitives.Safe_Str__Session_Name       import Safe_Str__Session_Name
from phase_e.storage.primitives.Safe_Str__Target_Name        import Safe_Str__Target_Name
from phase_e.storage.primitives.Safe_Str__Data_File_Id       import Safe_Str__Data_File_Id
from phase_e.storage.primitives.Safe_Str__Content_Hash       import Safe_Str__Content_Hash
from phase_e.storage.primitives.Safe_UInt__Http__Status_Code import Safe_UInt__Http__Status_Code
from phase_e.storage.primitives.Safe_UInt__Milliseconds      import Safe_UInt__Milliseconds
from phase_e.storage.primitives.Safe_UInt__Bytes             import Safe_UInt__Bytes
```

---

## 12. Summary

Phase E_5 implements **URL fetching with intelligent caching** using:

1. **Type_Safe Primitives** - No raw `str`/`int`/`float` anywhere
2. **LETS Methodology** - Load → Extract → Transform → Save with Type_Safe schemas at every boundary
3. **Factory Pattern** - Easy session/target creation via `Html_Cache__Session_Factory`
4. **Execution Modes** - FULL (first time), CACHED (fast), SELECTIVE (rebuild specific layers)
5. **Real HTTP Testing** - `Temp_Web_Server` from OSBot_Utils, no mocks
6. **Per-Layer Storage** - Each layer (L0, L1, L2, L3) has its own `Perf__Storage__Cache_Service` instance