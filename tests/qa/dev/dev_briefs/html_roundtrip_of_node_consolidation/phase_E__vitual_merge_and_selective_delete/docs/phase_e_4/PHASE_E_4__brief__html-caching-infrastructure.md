# Phase E_4: HTML Caching Infrastructure

**Status**: 🔄 In Progress  
**Depends On**: Phase E_3 ✅ (Storage abstraction layer)

---

## Objective

> Build a multi-layer caching infrastructure for HTML processing pipeline artifacts, enabling significant performance gains by caching intermediate results (raw HTML, parsed dicts, MGraph documents).

---

## The Problem

### Current State

Every time we process an HTML page, we perform the full pipeline:

```
HTML String → Parse to Dict → Create MGraph → Transform → Output
    ↓             ↓              ↓              ↓
  ~0ms         ~10ms          ~30ms*        ~varies
  (input)    (html5lib)    (now optimized)
```

*After Phase E_2 @type_safe optimization

For 100 pages processed 10 times each = 1000 pipeline runs = ~40 seconds just for MGraph creation.

### Desired State

Cache intermediate results so subsequent processing is near-instant:

```
First run:  HTML → Dict → MGraph → Cache all layers
Next runs:  Cache hit → MGraph ready instantly (~0ms)
```

For 100 pages processed 10 times: 100 first runs + 900 cache hits = ~4 seconds (10x faster).

### Why Existing Approaches Don't Work

1. **No persistence** - Current code recreates everything from scratch each run
2. **No content-addressability** - Same HTML from different sources isn't recognized
3. **No intermediate caching** - Must rebuild entire pipeline even if only transform changes

---

## Implementation Approach

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Html_Cache__Manager                           │
│                                                                  │
│  Orchestrates layers, provides cross-layer access                │
│  Handles cache cascade (L3 miss → build from L2 → build from L1) │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐         │
│  │ L1: HTML     │ ↔ │ L2: Dict     │ ↔ │ L3: MGraph   │         │
│  │              │   │              │   │              │         │
│  │ Raw HTML str │   │ Parsed dict  │   │ Document obj │         │
│  │ + metadata   │   │ + hash       │   │ + hash       │         │
│  └──────────────┘   └──────────────┘   └──────────────┘         │
│         │                  │                  │                  │
│         └──────────────────┴──────────────────┘                  │
│                           │                                      │
│                           ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Perf__Storage__Base                         │    │
│  │    (Memory for tests, Cache_Service for production)      │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

1. **Layer Independence with Cross-Access**
   - Each layer can be accessed independently
   - Manager provides cross-layer cascade on cache miss
   - Layers reference manager for accessing sibling layers when needed

2. **Content-Addressable Hashing**
   - Each layer stores content hash alongside data
   - Enables cross-target cache hits (same HTML from different URLs)
   - Hash stored in separate key for quick lookup

3. **Storage Abstraction**
   - Uses Phase E_3 `Perf__Storage__Base` interface
   - Tests use in-memory cache service via `client_cache_service()`
   - Production uses real cache service
   - Code is backend-agnostic

4. **Serialization via .json() / .from_json()**
   - All MGraph objects use standard serialization
   - Dict layer stores raw JSON
   - Consistent with existing codebase patterns

5. **Session/Target Organization**
   - Session: `phase-e-4` (or experiment identifier)
   - Target: specific HTML page or test case identifier
   - Follows Phase E_3 conventions

---

## Interfaces

### Input

- **HTML strings**: Raw HTML content to cache
- **Storage backend**: `Perf__Storage__Base` instance (injected)
- **Target identifier**: String identifying the HTML page/experiment

### Output

- **Cached artifacts**: HTML, Dict, MGraph available via manager
- **Cache statistics**: Hit/miss counts, storage sizes
- **Content hashes**: For cross-target lookups

---

## Storage Key Convention

```
session: phase-e-4
target:  test-simple-html  (or: example-com-page1)

Keys within target:
  L1/raw.html                # Raw HTML string
  L1/metadata.json           # {source, cached_at, content_hash, size_bytes}
  
  L2/dict.json               # Parsed HTML dict (full structure)
  L2/metadata.json           # {content_hash, node_count, cached_at}
  
  L3/document.json           # Html_MGraph__Document.json()
  L3/metadata.json           # {content_hash, node_count, edge_count, cached_at}

Shared keys (cross-target):
  _hashes/L1/{hash}.json     # {targets: ['target1', 'target2']}
  _hashes/L2/{hash}.json     # Same HTML dict from different sources
  _hashes/L3/{hash}.json     # Same MGraph from different sources
```

---

## Files

| File | Purpose |
|------|---------|
| `cache/Html_Cache__Manager.py` | Orchestrates all layers, cascade logic |
| `cache/layers/Html_Cache__Layer__Base.py` | Base class with common operations |
| `cache/layers/Html_Cache__Layer__Html.py` | L1: Raw HTML caching |
| `cache/layers/Html_Cache__Layer__Dict.py` | L2: Parsed dict caching |
| `cache/layers/Html_Cache__Layer__MGraph.py` | L3: MGraph document caching |
| `cache/schemas/Schema__Html_Cache__Metadata.py` | Metadata schemas for each layer |
| `cache/schemas/Schema__Html_Cache__Config.py` | Configuration options |
| `cache/schemas/Schema__Html_Cache__Stats.py` | Statistics tracking |

---

## Class Designs

### Html_Cache__Manager

```python
class Html_Cache__Manager(Type_Safe):
    storage      : Perf__Storage__Base              # Injected storage backend
    session_name : str = 'phase-e-4'                # Session identifier
    config       : Schema__Html_Cache__Config       # Configuration options
    stats        : Schema__Html_Cache__Stats        # Hit/miss tracking
    
    # Layers (created on setup)
    layer_html   : Html_Cache__Layer__Html   = None
    layer_dict   : Html_Cache__Layer__Dict   = None
    layer_mgraph : Html_Cache__Layer__MGraph = None
    
    def setup(self) -> 'Html_Cache__Manager':
        """Initialize layers with manager reference."""
        self.layer_html   = Html_Cache__Layer__Html  (manager=self)
        self.layer_dict   = Html_Cache__Layer__Dict  (manager=self)
        self.layer_mgraph = Html_Cache__Layer__MGraph(manager=self)
        return self
    
    def set_target(self, target_name: str) -> 'Html_Cache__Manager':
        """Set current target for all operations."""
        self.storage.set_context(self.session_name, target_name)
        return self
    
    # High-level operations
    def cache_html(self, target: str, html: str) -> bool
    def get_html(self, target: str) -> Optional[str]
    def get_dict(self, target: str, build_if_missing: bool = True) -> Optional[dict]
    def get_mgraph(self, target: str, build_if_missing: bool = True) -> Optional[Html_MGraph__Document]
    
    # Cascade operations
    def build_dict_from_html(self, target: str) -> Optional[dict]
    def build_mgraph_from_dict(self, target: str) -> Optional[Html_MGraph__Document]
    def build_full_pipeline(self, target: str, html: str) -> Optional[Html_MGraph__Document]
    
    # Cross-target operations
    def find_by_content_hash(self, layer: str, content_hash: str) -> List[str]
```

### Html_Cache__Layer__Base

```python
class Html_Cache__Layer__Base(Type_Safe):
    manager    : 'Html_Cache__Manager'              # Reference to manager
    layer_name : str                                # 'L1', 'L2', 'L3'
    
    def key_data(self) -> str:
        """Key for main data file."""
        return f"{self.layer_name}/data"
    
    def key_metadata(self) -> str:
        """Key for metadata file."""
        return f"{self.layer_name}/metadata.json"
    
    def exists(self) -> bool:
        """Check if layer data exists for current target."""
        return self.manager.storage.exists(self.key_data())
    
    def content_hash(self, content: str) -> str:
        """Generate hash for content-addressable lookup."""
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def save_metadata(self, metadata: dict) -> bool
    def load_metadata(self) -> Optional[dict]
```

### Html_Cache__Layer__Html (L1)

```python
class Html_Cache__Layer__Html(Html_Cache__Layer__Base):
    layer_name: str = 'L1'
    
    def save(self, html: str, source: str = 'unknown') -> bool:
        """Save raw HTML with metadata."""
        # Save HTML string
        self.manager.storage.save_string(f"{self.layer_name}/raw.html", html)
        
        # Save metadata
        metadata = {
            'source'       : source,
            'cached_at'    : timestamp(),
            'content_hash' : self.content_hash(html),
            'size_bytes'   : len(html.encode('utf-8'))
        }
        self.save_metadata(metadata)
        return True
    
    def load(self) -> Optional[str]:
        """Load raw HTML."""
        return self.manager.storage.load_string(f"{self.layer_name}/raw.html")
```

### Html_Cache__Layer__Dict (L2)

```python
class Html_Cache__Layer__Dict(Html_Cache__Layer__Base):
    layer_name: str = 'L2'
    
    def save(self, html_dict: dict) -> bool:
        """Save parsed HTML dict."""
        self.manager.storage.save(f"{self.layer_name}/dict.json", html_dict)
        
        # Calculate hash from serialized dict for consistency
        dict_str = json.dumps(html_dict, sort_keys=True)
        metadata = {
            'content_hash' : self.content_hash(dict_str),
            'node_count'   : self._count_nodes(html_dict),
            'cached_at'    : timestamp()
        }
        self.save_metadata(metadata)
        return True
    
    def load(self) -> Optional[dict]:
        """Load parsed HTML dict."""
        return self.manager.storage.load(f"{self.layer_name}/dict.json")
    
    def build_from_html(self, html: str) -> dict:
        """Parse HTML to dict using existing converter."""
        return Html__To__Html_Dict__With__Node_Ids(html=html).convert()
```

### Html_Cache__Layer__MGraph (L3)

```python
class Html_Cache__Layer__MGraph(Html_Cache__Layer__Base):
    layer_name: str = 'L3'
    
    def save(self, document: Html_MGraph__Document) -> bool:
        """Save MGraph document using .json() serialization."""
        doc_json = document.json()
        self.manager.storage.save(f"{self.layer_name}/document.json", doc_json)
        
        # Metadata
        doc_str = json.dumps(doc_json, sort_keys=True)
        stats = document.stats()  # If available
        metadata = {
            'content_hash' : self.content_hash(doc_str),
            'node_count'   : stats.total_nodes if stats else 0,
            'edge_count'   : stats.total_edges if stats else 0,
            'cached_at'    : timestamp()
        }
        self.save_metadata(metadata)
        return True
    
    def load(self) -> Optional[Html_MGraph__Document]:
        """Load MGraph document using .from_json() deserialization."""
        doc_json = self.manager.storage.load(f"{self.layer_name}/document.json")
        if doc_json:
            return Html_MGraph__Document.from_json(doc_json)
        return None
    
    def build_from_dict(self, html_dict: dict) -> Html_MGraph__Document:
        """Create MGraph from dict using existing converter."""
        converter = Html__To__Html_MGraph__Document__Node_Id_Reuse()
        return converter.convert_from_dict(html_dict)
```

---

## Test Plan

| Test | Description |
|------|-------------|
| `test_manager__setup` | Manager initializes all layers correctly |
| `test_manager__set_target` | Target switching updates storage context |
| `test_layer_html__save_load` | L1 round-trip for HTML strings |
| `test_layer_html__metadata` | L1 stores correct metadata |
| `test_layer_dict__save_load` | L2 round-trip for dicts |
| `test_layer_dict__build_from_html` | L2 can build from L1 cache |
| `test_layer_mgraph__save_load` | L3 round-trip for MGraph documents |
| `test_layer_mgraph__build_from_dict` | L3 can build from L2 cache |
| `test_cascade__full_pipeline` | Cache miss triggers full build |
| `test_cascade__partial_hit` | L2 hit skips HTML parsing |
| `test_content_hash__same_content` | Same HTML produces same hash |
| `test_stats__hit_miss_tracking` | Statistics count correctly |
| `test_cache_service__integration` | Full test with cache service backend |

### Test Data Strategy

Use `Html_Generator__For_Benchmarks` from Phase E_2:

```python
@classmethod
def setUpClass(cls):
    cls.cache_client, cls.cache_service = client_cache_service()
    cls.generator = Html_Generator__For_Benchmarks()
    
    # Pre-generate test HTML at various sizes
    with graph_deterministic_ids():
        cls.html_10  = cls.generator.generate__10()
        cls.html_100 = cls.generator.generate__100()
```

---

## Performance Targets

| Scenario | Without Cache | With Cache | Improvement |
|----------|---------------|------------|-------------|
| First run (100 nodes) | ~30ms | ~35ms (build + cache) | -17% (overhead) |
| Subsequent runs | ~30ms | ~1ms (cache hit) | **30x faster** |
| 10 runs same page | ~300ms | ~35ms | **8.5x faster** |

Note: First run has small overhead for caching. Payoff is on subsequent runs.

---

## Success Criteria

- [ ] All three layers (L1, L2, L3) save and load correctly
- [ ] Cache cascade works (L3 miss → build from L2 → build from L1)
- [ ] MGraph serialization/deserialization via .json()/.from_json() works
- [ ] Content hashing produces consistent results
- [ ] Works with both memory and cache service backends
- [ ] Statistics track hits and misses
- [ ] Performance improvement measurable on repeated access

---

## Next Phase

Phase E_5 will add:
- URL fetching with HTTP client
- Network response caching
- Real website testing
- Deduplication across pages (same template detection)
