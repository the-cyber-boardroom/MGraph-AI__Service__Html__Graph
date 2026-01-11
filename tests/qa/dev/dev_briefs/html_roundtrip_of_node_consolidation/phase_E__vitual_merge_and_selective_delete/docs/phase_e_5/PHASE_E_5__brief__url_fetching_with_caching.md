# Phase E_5: URL Fetching with Caching

**Status**: 📋 Planned  
**Depends On**: Phase E_4 ✅ (HTML Caching Infrastructure)

---

## Objective

> Add URL fetching capabilities with intelligent caching, enabling real website processing while minimizing network requests through content-addressable storage and HTTP caching semantics.

---

## The Problem

### Current State (after Phase E_4)

We have a robust caching infrastructure for HTML processing:
- L1: Raw HTML caching
- L2: Parsed dict caching
- L3: MGraph document caching

But we can only process HTML strings that are provided directly. To work with real websites, we need:
- URL fetching
- Network response caching
- HTTP cache semantics (ETags, Last-Modified, etc.)

### Desired State

```
URL → [Check cache] → [Fetch if needed] → [Cache response] → L1 → L2 → L3
         ↓                   ↓
      Cache hit          Network request
      (~0ms)              (~100-500ms)
```

Full pipeline from URL to cached MGraph:

```python
manager = Html_Cache__Manager(storage).setup()
document = manager.get_mgraph_from_url('https://example.com/page1')

# First call: Fetch → Parse → Build → Cache all layers
# Subsequent calls: Instant cache hit
```

### Why This Matters

1. **Real website testing** - Process actual HTML from live sites
2. **Batch processing** - Crawl and process many pages efficiently
3. **Development workflow** - Work with cached pages offline
4. **Deduplication** - Same content from different URLs uses same cache entry

---

## Implementation Approach

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Html_Cache__Manager                           │
│                        (from E_4)                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐                                               │
│  │ L0: URL      │ ← NEW LAYER                                   │
│  │              │                                               │
│  │ URL → HTML   │                                               │
│  │ HTTP caching │                                               │
│  │ ETags, etc.  │                                               │
│  └──────────────┘                                               │
│         │                                                        │
│         ▼                                                        │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐         │
│  │ L1: HTML     │ ↔ │ L2: Dict     │ ↔ │ L3: MGraph   │         │
│  │ (from E_4)   │   │ (from E_4)   │   │ (from E_4)   │         │
│  └──────────────┘   └──────────────┘   └──────────────┘         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    Html_Fetcher                                  │
│                                                                  │
│  HTTP client wrapper with:                                       │
│  - Request/response handling                                     │
│  - HTTP cache semantics (ETag, Last-Modified, Cache-Control)    │
│  - Rate limiting                                                 │
│  - Retry logic                                                   │
│  - User-Agent configuration                                      │
└─────────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

1. **L0 Layer for URL Mapping**
   - Maps URLs to content hashes
   - Stores HTTP metadata (headers, status, fetched_at)
   - Enables same HTML from different URLs to share L1-L3 cache

2. **HTTP Cache Semantics**
   - Store ETag and Last-Modified from responses
   - Use conditional requests (If-None-Match, If-Modified-Since)
   - Respect Cache-Control headers (optional, configurable)

3. **Separate Fetcher Component**
   - `Html_Fetcher` handles all HTTP concerns
   - Pluggable (can mock for tests)
   - Configurable timeouts, retries, rate limiting

4. **Content-Addressable Deduplication**
   - Multiple URLs with same HTML share L1 cache entry
   - Saves storage and processing for templated sites
   - Hash-based lookup across targets

5. **Offline Mode**
   - Can work entirely from cache (no network)
   - Useful for development and testing
   - Configurable fallback behavior

---

## Interfaces

### Input

- **URLs**: HTTP/HTTPS URLs to fetch
- **Fetch options**: Timeout, headers, retry config
- **Cache options**: Force refresh, offline mode, max age

### Output

- **HTML content**: Raw HTML from URL (cached)
- **HTTP metadata**: Status, headers, timing
- **MGraph documents**: Full pipeline from URL to MGraph

---

## Storage Key Convention

```
session: phase-e-5
target:  example-com-page1  (normalized from URL)

Keys within target:
  L0/url.json                # {url, normalized_url, fetched_at}
  L0/response.json           # {status, headers, etag, last_modified}
  L0/content_hash.txt        # Points to L1 entry (may be shared)
  
  L1/raw.html                # (from E_4)
  L1/metadata.json           # (from E_4)
  
  L2/dict.json               # (from E_4)
  L2/metadata.json           # (from E_4)
  
  L3/document.json           # (from E_4)
  L3/metadata.json           # (from E_4)

URL index (cross-target):
  _urls/{url_hash}.json      # {url, target, content_hash, fetched_at}
```

---

## Files

| File | Purpose |
|------|---------|
| `cache/layers/Html_Cache__Layer__Url.py` | L0: URL to HTML mapping |
| `fetch/Html_Fetcher.py` | HTTP client wrapper |
| `fetch/Html_Fetcher__Config.py` | Fetch configuration |
| `fetch/Html_Fetcher__Response.py` | Response wrapper |
| `fetch/Html_Fetcher__Mock.py` | Mock fetcher for tests |
| `cache/schemas/Schema__Html_Cache__Url_Metadata.py` | URL layer metadata |
| `cache/schemas/Schema__Html_Fetcher__Config.py` | Fetcher configuration |

---

## Class Designs

### Html_Cache__Layer__Url (L0)

```python
class Html_Cache__Layer__Url(Html_Cache__Layer__Base):
    layer_name: str = 'L0'
    fetcher   : Html_Fetcher = None
    
    def fetch_and_cache(self, url: str, force_refresh: bool = False) -> Optional[str]:
        """Fetch URL and cache response, or return cached."""
        
        # Check if we have cached response
        if not force_refresh and self.exists():
            metadata = self.load_metadata()
            
            # Check if we should revalidate (conditional request)
            if self._should_revalidate(metadata):
                return self._conditional_fetch(url, metadata)
            
            # Return cached HTML via L1
            return self.manager.layer_html.load()
        
        # Fresh fetch
        response = self.fetcher.fetch(url)
        if response.ok:
            self._cache_response(url, response)
            return response.html
        
        return None
    
    def _conditional_fetch(self, url: str, metadata: dict) -> Optional[str]:
        """Fetch with If-None-Match / If-Modified-Since."""
        headers = {}
        if metadata.get('etag'):
            headers['If-None-Match'] = metadata['etag']
        if metadata.get('last_modified'):
            headers['If-Modified-Since'] = metadata['last_modified']
        
        response = self.fetcher.fetch(url, headers=headers)
        
        if response.status == 304:  # Not Modified
            self._update_revalidation_time(metadata)
            return self.manager.layer_html.load()
        
        if response.ok:
            self._cache_response(url, response)
            return response.html
        
        return None
    
    def _cache_response(self, url: str, response: Html_Fetcher__Response):
        """Cache the response and update L1."""
        # Save L0 metadata
        metadata = {
            'url'           : url,
            'normalized_url': self._normalize_url(url),
            'fetched_at'    : timestamp(),
            'status'        : response.status,
            'etag'          : response.headers.get('ETag'),
            'last_modified' : response.headers.get('Last-Modified'),
            'content_type'  : response.headers.get('Content-Type'),
            'content_hash'  : self.content_hash(response.html)
        }
        self.save_metadata(metadata)
        
        # Save to L1 (triggers L1 metadata)
        self.manager.layer_html.save(response.html, source=url)
```

### Html_Fetcher

```python
class Html_Fetcher(Type_Safe):
    config: Schema__Html_Fetcher__Config
    
    def fetch(self, url: str, headers: dict = None) -> Html_Fetcher__Response:
        """Fetch URL with configured settings."""
        import requests
        
        request_headers = {
            'User-Agent': self.config.user_agent,
            **(headers or {})
        }
        
        try:
            response = requests.get(
                url,
                headers = request_headers,
                timeout = self.config.timeout_seconds,
                allow_redirects = self.config.follow_redirects
            )
            
            return Html_Fetcher__Response(
                url     = url,
                status  = response.status_code,
                headers = dict(response.headers),
                html    = response.text if response.ok else None,
                ok      = response.ok,
                error   = None
            )
        except Exception as e:
            return Html_Fetcher__Response(
                url    = url,
                status = 0,
                ok     = False,
                error  = str(e)
            )
```

### Html_Fetcher__Mock

```python
class Html_Fetcher__Mock(Html_Fetcher):
    """Mock fetcher for testing without network."""
    
    responses: dict = {}  # url -> Html_Fetcher__Response
    
    def add_response(self, url: str, html: str, status: int = 200, headers: dict = None):
        """Register a mock response."""
        self.responses[url] = Html_Fetcher__Response(
            url     = url,
            status  = status,
            headers = headers or {},
            html    = html,
            ok      = 200 <= status < 300
        )
    
    def fetch(self, url: str, headers: dict = None) -> Html_Fetcher__Response:
        """Return mock response."""
        if url in self.responses:
            return self.responses[url]
        
        return Html_Fetcher__Response(
            url    = url,
            status = 404,
            ok     = False,
            error  = 'Mock: URL not registered'
        )
```

### Extended Html_Cache__Manager

```python
class Html_Cache__Manager(Type_Safe):
    # ... existing from E_4 ...
    
    # New L0 layer
    layer_url: Html_Cache__Layer__Url = None
    
    # New fetcher
    fetcher: Html_Fetcher = None
    
    def setup(self) -> 'Html_Cache__Manager':
        """Initialize all layers including L0."""
        # E_4 layers
        self.layer_html   = Html_Cache__Layer__Html  (manager=self)
        self.layer_dict   = Html_Cache__Layer__Dict  (manager=self)
        self.layer_mgraph = Html_Cache__Layer__MGraph(manager=self)
        
        # E_5 layer
        if self.fetcher:
            self.layer_url = Html_Cache__Layer__Url(manager=self, fetcher=self.fetcher)
        
        return self
    
    # New high-level operations
    def get_html_from_url(self, url: str, force_refresh: bool = False) -> Optional[str]:
        """Fetch URL (with caching) and return HTML."""
        target = self._url_to_target(url)
        self.set_target(target)
        return self.layer_url.fetch_and_cache(url, force_refresh)
    
    def get_mgraph_from_url(self, url: str, force_refresh: bool = False) -> Optional[Html_MGraph__Document]:
        """Full pipeline from URL to MGraph."""
        html = self.get_html_from_url(url, force_refresh)
        if html:
            return self.get_mgraph(self._url_to_target(url), build_if_missing=True)
        return None
    
    def _url_to_target(self, url: str) -> str:
        """Convert URL to target name."""
        # https://example.com/page/1 → example-com-page-1
        from urllib.parse import urlparse
        parsed = urlparse(url)
        target = f"{parsed.netloc}{parsed.path}".replace('/', '-').replace('.', '-')
        return target.strip('-')
```

---

## Test Plan

| Test | Description |
|------|-------------|
| `test_fetcher__basic_fetch` | Mock fetcher returns configured response |
| `test_fetcher__error_handling` | Network errors handled gracefully |
| `test_layer_url__cache_miss` | First fetch stores to L0 and L1 |
| `test_layer_url__cache_hit` | Second fetch returns cached (no network) |
| `test_layer_url__force_refresh` | Force refresh bypasses cache |
| `test_layer_url__conditional_fetch` | Uses ETag/If-None-Match |
| `test_layer_url__304_not_modified` | Handles 304 response correctly |
| `test_manager__get_html_from_url` | Full URL to HTML pipeline |
| `test_manager__get_mgraph_from_url` | Full URL to MGraph pipeline |
| `test_deduplication__same_content` | Same HTML from different URLs shares cache |
| `test_offline_mode` | Works without network when cached |
| `test_real_url__example_com` | Integration test with real URL (optional) |

### Test Strategy

```python
class test_Html_Cache__With_Url_Fetching(TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.cache_client, cls.cache_service = client_cache_service()
        cls.generator = Html_Generator__For_Benchmarks()
        
        # Create mock fetcher with test HTML
        cls.mock_fetcher = Html_Fetcher__Mock()
        cls.mock_fetcher.add_response(
            url  = 'https://example.com/page1',
            html = cls.generator.generate__10()
        )
        cls.mock_fetcher.add_response(
            url  = 'https://example.com/page2',
            html = cls.generator.generate__100()
        )
    
    def test_full_pipeline_from_url(self):
        storage = self._create_storage()
        manager = Html_Cache__Manager(
            storage = storage,
            fetcher = self.mock_fetcher
        ).setup()
        
        # First call - "fetches" from mock
        document = manager.get_mgraph_from_url('https://example.com/page1')
        assert document is not None
        
        # Second call - cache hit (no fetch)
        document2 = manager.get_mgraph_from_url('https://example.com/page1')
        assert document2 is not None
        
        # Verify mock was only called once
        # (would need call tracking in mock)
```

---

## Performance Targets

| Scenario | Time |
|----------|------|
| First URL fetch (network) | 100-500ms (network dependent) |
| First URL fetch (mock) | ~35ms (parse + build + cache) |
| Cached URL access | ~1ms (cache hit) |
| Same content, different URL | ~1ms (content-hash hit) |

---

## HTTP Caching Strategy

### Cache-Control Handling (Optional)

```python
class Html_Cache__Layer__Url:
    
    def _should_revalidate(self, metadata: dict) -> bool:
        """Check if cached response needs revalidation."""
        
        if not self.config.respect_cache_control:
            # Always use cache if available
            return False
        
        # Check max-age
        if max_age := metadata.get('cache_control_max_age'):
            age = time.time() - metadata['fetched_at']
            if age < max_age:
                return False  # Still fresh
        
        # Check if we have validation headers
        if metadata.get('etag') or metadata.get('last_modified'):
            return True  # Can do conditional request
        
        # No validation possible, use cache anyway
        return False
```

### Rate Limiting

```python
class Html_Fetcher:
    last_request_time: float = 0
    
    def fetch(self, url: str, headers: dict = None) -> Html_Fetcher__Response:
        # Rate limiting
        if self.config.min_request_interval_seconds:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.config.min_request_interval_seconds:
                time.sleep(self.config.min_request_interval_seconds - elapsed)
        
        self.last_request_time = time.time()
        # ... rest of fetch logic
```

---

## Success Criteria

- [ ] Mock fetcher works for all tests (no network required)
- [ ] L0 layer correctly maps URLs to L1 content
- [ ] HTTP metadata (ETag, Last-Modified) stored and used
- [ ] Conditional requests work (304 handling)
- [ ] Content deduplication works across URLs
- [ ] Full URL-to-MGraph pipeline functional
- [ ] Offline mode works with cached data
- [ ] Rate limiting prevents request flooding
- [ ] At least one real URL test passes (manual/optional)

---

## Future Enhancements (Phase E_6+)

1. **Crawling** - Follow links, build site graph
2. **Robots.txt** - Respect crawl rules
3. **JavaScript rendering** - Handle SPAs (via Playwright/Selenium)
4. **Parallel fetching** - Concurrent requests with rate limiting
5. **Site templates** - Detect and deduplicate common page structures
6. **Incremental updates** - Only re-fetch changed pages

---

## Dependencies

### Python Packages

```
requests>=2.28.0    # HTTP client (or httpx for async)
```

### Internal Dependencies

```
Phase E_3: Perf__Storage__Base, Perf__Storage__Cache_Service
Phase E_4: Html_Cache__Manager, Html_Cache__Layer__*
```
