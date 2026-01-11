# Brief: Cache Service Storage Integration

**Phase**: E_3 Performance Analysis - Cache Service Integration  
**Version**: v0.4  
**Date**: 2025-01-10

---

## Overview

Add support for the MGraph-AI Cache Service as a storage backend for benchmark results and transformation artifacts. This enables persistent, visualizable caching of performance analysis artifacts using the cache service's `key_based` strategy with hierarchical child data files.

## Objectives

1. **Create `Perf__Storage__Cache_Service`** - New storage backend implementing `Perf__Storage__Base`
2. **Storage Abstraction** - Code should be agnostic to whether it's using local, memory, or cache service storage
3. **Hierarchical Artifact Storage** - Use `key_based` strategy + child data files to organize by session/target
4. **Environment-Based Configuration** - Cache service URL controlled via environment variable

---

## Architecture

### Storage Hierarchy

The cache service uses `key_based` strategy with child data files to create a semantic folder structure:

```
{namespace}/data/key-based/
└── sessions/{session-name}/targets/{target-name}/
    ├── perf-entry.json              # Main cache entry (session/target metadata)
    ├── perf-entry.json.config       # Cache service config
    ├── perf-entry.json.metadata     # Cache service metadata
    └── perf-entry/data/             # Child data files
        ├── results/
        │   ├── conversion__detailed.txt
        │   ├── conversion__detailed.json
        │   ├── scaling_analysis__quick.txt
        │   ├── scaling_analysis__quick.json
        │   └── scaling__quick__default.txt
        └── reports/
            └── DEBRIEF_3__data_analysis.md
```

### Class Structure

```
Perf__Storage__Base (existing - abstract)
    ├── Perf__Storage__Local (existing - local disk)
    ├── Perf__Storage__Memory (new - in-memory for tests)
    └── Perf__Storage__Cache_Service (new - remote cache service)

Perf__Storage__Factory (new - creates appropriate storage based on config)
Perf__Storage__Config (new - configuration management)
Cache_Service__Client (new - HTTP client wrapper)
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PERF_STORAGE_MODE` | Storage mode: `local`, `memory`, `cache_service` | `local` |
| `PERF_CACHE_SERVICE_URL` | Cache service base URL | `http://0.0.0.0:10017` |
| `PERF_CACHE_NAMESPACE` | Cache service namespace | `perf-results` |

---

## File Structure

```
phase_e/
├── core/
├── decision/
├── performance/
│   ├── Html_Generator__For_Benchmarks.py
│   ├── Perf__Phase_E__Conversion.py
│   └── Perf__Phase_E__Scalability.py
├── report/
│   ├── builder/
│   ├── collections/
│   ├── renderers/
│   ├── schemas/
│   ├── storage/
│   └── __init__.py
├── schemas/
├── storage/                                    # NEW - top-level storage module
│   ├── __init__.py
│   ├── base/
│   │   ├── __init__.py
│   │   └── Perf__Storage__Base.py              # MOVED from performance/
│   ├── backends/
│   │   ├── __init__.py
│   │   ├── Perf__Storage__Local.py             # MOVED from performance/
│   │   ├── Perf__Storage__Memory.py            # NEW
│   │   └── Perf__Storage__Cache_Service.py     # NEW
│   ├── cache_service/
│   │   ├── __init__.py
│   │   └── Cache_Service__Client.py            # NEW
│   ├── config/
│   │   ├── __init__.py
│   │   └── Perf__Storage__Config.py            # NEW
│   ├── factory/
│   │   ├── __init__.py
│   │   └── Perf__Storage__Factory.py           # NEW
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── Schema__Perf__Storage__Config.py    # NEW
│   │   └── Schema__Perf__Entry.py              # NEW
│   ├── safe_str/
│   │   ├── __init__.py
│   │   ├── Safe_Str__Session_Name.py           # NEW
│   │   ├── Safe_Str__Target_Name.py            # NEW
│   │   ├── Safe_Str__Data_Key.py               # NEW
│   │   └── Safe_Str__Data_File_Id.py           # NEW
│   └── enums/
│       ├── __init__.py
│       └── Enum__Storage_Mode.py               # NEW
├── __init__.py
└── Phase_E__Pipeline.py
```

**Summary:**
- **Files to create:** 13 new files + 7 `__init__.py` files
- **Files to move:** 2 existing files (`Perf__Storage__Base.py`, `Perf__Storage__Local.py`)

---

## Type_Safe Implementation

### Required Imports

```python
# ═══════════════════════════════════════════════════════════════════════════════
# Core Type_Safe
# ═══════════════════════════════════════════════════════════════════════════════
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                  import type_safe

# ═══════════════════════════════════════════════════════════════════════════════
# Safe Primitives - NEVER use raw str, int, float
# ═══════════════════════════════════════════════════════════════════════════════
from osbot_utils.type_safe.primitives.core.Safe_Str                             import Safe_Str
from osbot_utils.type_safe.primitives.core.Safe_UInt                            import Safe_UInt
from osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id               import Safe_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id              import Cache_Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now import Timestamp_Now
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url        import Safe_Str__Url
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path import Safe_Str__File__Path

# ═══════════════════════════════════════════════════════════════════════════════
# Collections
# ═══════════════════════════════════════════════════════════════════════════════
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__Dict           import Type_Safe__Dict
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__List           import Type_Safe__List

# ═══════════════════════════════════════════════════════════════════════════════
# Utilities
# ═══════════════════════════════════════════════════════════════════════════════
from osbot_utils.utils.Files                                                    import file_exists, folder_create
from osbot_utils.utils.Json                                                     import json_load_file, json_save_file_pretty
from osbot_utils.utils.Env                                                      import get_env
```

### Custom Safe Primitives

```python
# ═══════════════════════════════════════════════════════════════════════════════
# phase_e/storage/safe_str/Safe_Str__Session_Name.py
# ═══════════════════════════════════════════════════════════════════════════════

import re
from osbot_utils.type_safe.primitives.core.Safe_Str                             import Safe_Str


class Safe_Str__Session_Name(Safe_Str):                                         # Performance session identifier
    max_length = 100
    regex      = re.compile(r'[^a-zA-Z0-9_\-]')                                  # Alphanumeric, underscore, hyphen
```

```python
# ═══════════════════════════════════════════════════════════════════════════════
# phase_e/storage/safe_str/Safe_Str__Target_Name.py
# ═══════════════════════════════════════════════════════════════════════════════

import re
from osbot_utils.type_safe.primitives.core.Safe_Str                             import Safe_Str


class Safe_Str__Target_Name(Safe_Str):                                          # Performance target identifier
    max_length = 100
    regex      = re.compile(r'[^a-zA-Z0-9_\-]')                                  # Alphanumeric, underscore, hyphen
```

```python
# ═══════════════════════════════════════════════════════════════════════════════
# phase_e/storage/safe_str/Safe_Str__Data_Key.py
# ═══════════════════════════════════════════════════════════════════════════════

import re
from osbot_utils.type_safe.primitives.core.Safe_Str                             import Safe_Str


class Safe_Str__Data_Key(Safe_Str):                                             # Child data path key
    max_length = 256
    regex      = re.compile(r'[^a-zA-Z0-9_\-/]')                                 # Allows path separators
```

```python
# ═══════════════════════════════════════════════════════════════════════════════
# phase_e/storage/safe_str/Safe_Str__Data_File_Id.py
# ═══════════════════════════════════════════════════════════════════════════════

import re
from osbot_utils.type_safe.primitives.core.Safe_Str                             import Safe_Str


class Safe_Str__Data_File_Id(Safe_Str):                                         # Child data file identifier
    max_length = 128
    regex      = re.compile(r'[^a-zA-Z0-9_\-\.]')                                # Allows dots for extensions
```

### Enums

```python
# ═══════════════════════════════════════════════════════════════════════════════
# phase_e/storage/enums/Enum__Storage_Mode.py
# ═══════════════════════════════════════════════════════════════════════════════

from enum                                                                       import Enum


class Enum__Storage_Mode(str, Enum):                                            # Storage backend mode
    LOCAL         = 'local'                                                     # Local disk storage
    MEMORY        = 'memory'                                                    # In-memory (tests)
    CACHE_SERVICE = 'cache_service'                                             # Remote cache service
```

---

## Schema Definitions

**CRITICAL: Schemas are PURE DATA containers - NO methods, NO business logic!**

```python
# ═══════════════════════════════════════════════════════════════════════════════
# phase_e/storage/schemas/Schema__Perf__Storage__Config.py
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Str                             import Safe_Str
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url        import Safe_Str__Url
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path import Safe_Str__File__Path
from phase_e.storage.enums.Enum__Storage_Mode                                   import Enum__Storage_Mode


class Schema__Perf__Storage__Config(Type_Safe):                                 # Storage configuration
    storage_mode       : Enum__Storage_Mode    = Enum__Storage_Mode.LOCAL       # Backend mode
    cache_service_url  : Safe_Str__Url         = 'http://0.0.0.0:10017'         # Cache service URL
    cache_namespace    : Safe_Str              = 'perf-results'                 # Cache namespace
    local_storage_path : Safe_Str__File__Path  = './perf_results'               # Local storage dir
```

```python
# ═══════════════════════════════════════════════════════════════════════════════
# phase_e/storage/schemas/Schema__Perf__Entry.py
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now import Timestamp_Now
from phase_e.storage.safe_str.Safe_Str__Session_Name                            import Safe_Str__Session_Name
from phase_e.storage.safe_str.Safe_Str__Target_Name                             import Safe_Str__Target_Name


class Schema__Perf__Entry(Type_Safe):                                           # Performance entry metadata
    session_name : Safe_Str__Session_Name                                       # Session identifier
    target_name  : Safe_Str__Target_Name                                        # Target identifier
    timestamp    : Timestamp_Now                                                # Auto-generated timestamp
    config       : dict                                                         # Test configuration
    summary      : dict                                                         # Summary metrics
```

---

## Implementation Details

### 1. `Perf__Storage__Config`

```python
# ═══════════════════════════════════════════════════════════════════════════════
# phase_e/storage/config/Perf__Storage__Config.py
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.utils.Env                                                      import get_env
from phase_e.storage.schemas.Schema__Perf__Storage__Config                      import Schema__Perf__Storage__Config


class Perf__Storage__Config(Type_Safe):                                         # Storage configuration manager
    config: Schema__Perf__Storage__Config                                       # Configuration schema
    
    def setup(self) -> 'Perf__Storage__Config':                                 # Load config from environment
        self.config = Schema__Perf__Storage__Config(
            storage_mode       = get_env('PERF_STORAGE_MODE'      , 'local'                 ),
            cache_service_url  = get_env('PERF_CACHE_SERVICE_URL' , 'http://0.0.0.0:10017'  ),
            cache_namespace    = get_env('PERF_CACHE_NAMESPACE'   , 'perf-results'          ),
            local_storage_path = get_env('PERF_LOCAL_STORAGE_PATH', './perf_results'        ))
        return self
```

### 2. `Perf__Storage__Memory`

```python
# ═══════════════════════════════════════════════════════════════════════════════
# phase_e/storage/backends/Perf__Storage__Memory.py
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                     import Optional, List
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                  import type_safe
from osbot_utils.type_safe.primitives.core.Safe_Str                             import Safe_Str
from phase_e.storage.base.Perf__Storage__Base                                   import Perf__Storage__Base
from phase_e.storage.safe_str.Safe_Str__Session_Name                            import Safe_Str__Session_Name
from phase_e.storage.safe_str.Safe_Str__Target_Name                             import Safe_Str__Target_Name


class Perf__Storage__Memory(Perf__Storage__Base):                               # In-memory storage backend
    data         : dict                                                         # Storage dict (auto-init {})
    session_name : Safe_Str__Session_Name                                       # Current session
    target_name  : Safe_Str__Target_Name                                        # Current target
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Context Management
    # ═══════════════════════════════════════════════════════════════════════════
    
    @type_safe
    def set_context(self                                    ,                   # Set session/target context
                    session_name : Safe_Str__Session_Name   ,                   # Session identifier
                    target_name  : Safe_Str__Target_Name    ) -> None:          # Target identifier
        self.session_name = session_name
        self.target_name  = target_name
    
    def context_key(self) -> Safe_Str:                                          # Generate context prefix
        return f"{self.session_name}/{self.target_name}"
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Abstract Method Implementations
    # ═══════════════════════════════════════════════════════════════════════════
    
    @type_safe
    def save(self                  ,                                            # Save data with key
             key  : str            ,                                            # Data key
             data : dict           ) -> bool:                                   # Data to store
        full_key            = f"{self.context_key()}/{key}"
        self.data[full_key] = data
        return True
    
    @type_safe
    def save_string(self                  ,                                     # Save string content
                    key     : str         ,                                     # Data key
                    content : str         ) -> bool:                            # String content
        full_key            = f"{self.context_key()}/{key}"
        self.data[full_key] = content
        return True
    
    @type_safe
    def load(self             ,                                                 # Load data by key
             key : str        ) -> Optional[dict]:                              # Returns None if not found
        full_key = f"{self.context_key()}/{key}"
        return self.data.get(full_key)
    
    @type_safe
    def load_string(self             ,                                          # Load string content
                    key : str        ) -> Optional[str]:                        # Returns None if not found
        full_key = f"{self.context_key()}/{key}"
        return self.data.get(full_key)
    
    @type_safe
    def exists(self             ,                                               # Check if key exists
               key : str        ) -> bool:
        full_key = f"{self.context_key()}/{key}"
        return full_key in self.data
    
    @type_safe
    def delete(self             ,                                               # Delete data by key
               key : str        ) -> bool:
        full_key = f"{self.context_key()}/{key}"
        if full_key in self.data:
            del self.data[full_key]
            return True
        return False
    
    @type_safe
    def list_keys(self                  ,                                       # List all stored keys
                  prefix : str = ''     ) -> List[str]:                         # Optional prefix filter
        context = self.context_key()
        keys    = [k.replace(f"{context}/", '') 
                   for k in self.data.keys() 
                   if k.startswith(context)]
        if prefix:
            keys = [k for k in keys if k.startswith(prefix)]
        return sorted(keys)
```

### 3. `Cache_Service__Client`

```python
# ═══════════════════════════════════════════════════════════════════════════════
# phase_e/storage/cache_service/Cache_Service__Client.py
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                     import Optional
import requests
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                  import type_safe
from osbot_utils.type_safe.primitives.core.Safe_Str                             import Safe_Str
from osbot_utils.type_safe.primitives.core.Safe_UInt                            import Safe_UInt
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id              import Cache_Id
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url        import Safe_Str__Url
from phase_e.storage.safe_str.Safe_Str__Data_Key                                import Safe_Str__Data_Key
from phase_e.storage.safe_str.Safe_Str__Data_File_Id                            import Safe_Str__Data_File_Id


class Cache_Service__Client(Type_Safe):                                         # Cache service HTTP client
    base_url  : Safe_Str__Url  = 'http://0.0.0.0:10017'                         # Service base URL
    namespace : Safe_Str       = 'perf-results'                                 # Default namespace
    timeout   : Safe_UInt      = 30                                             # Request timeout seconds
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Main Entry Operations (key_based strategy)
    # ═══════════════════════════════════════════════════════════════════════════
    
    @type_safe
    def store_entry(self                               ,                        # Store main entry
                    cache_key : str                    ,                        # Semantic path key
                    file_id   : Safe_Str__Data_File_Id ,                        # File identifier
                    data      : dict                   ) -> dict:               # Entry data
        url      = f"{self.base_url}/{self.namespace}/key_based/store/json/{cache_key}/{file_id}"
        response = requests.post(url, json=data, timeout=self.timeout)
        return response.json()
    
    @type_safe
    def retrieve_entry(self                  ,                                  # Retrieve entry by ID
                       cache_id : Cache_Id   ) -> Optional[dict]:               # Returns None if not found
        url      = f"{self.base_url}/{self.namespace}/retrieve/{cache_id}/json"
        response = requests.get(url, timeout=self.timeout)
        if response.status_code == 404:
            return None
        return response.json()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Child Data Operations
    # ═══════════════════════════════════════════════════════════════════════════
    
    @type_safe
    def store_child_string(self                                ,                # Store string child data
                           cache_id     : Cache_Id             ,                # Parent cache ID
                           data_key     : Safe_Str__Data_Key   ,                # Data path key
                           data_file_id : Safe_Str__Data_File_Id,               # File identifier
                           content      : str                  ) -> dict:       # String content
        url      = f"{self.base_url}/{self.namespace}/cache/{cache_id}/data/store/string/{data_key}/{data_file_id}"
        response = requests.post(url, data=content, timeout=self.timeout)
        return response.json()
    
    @type_safe
    def store_child_json(self                                ,                  # Store JSON child data
                         cache_id     : Cache_Id             ,                  # Parent cache ID
                         data_key     : Safe_Str__Data_Key   ,                  # Data path key
                         data_file_id : Safe_Str__Data_File_Id,                 # File identifier
                         data         : dict                 ) -> dict:         # JSON data
        url      = f"{self.base_url}/{self.namespace}/cache/{cache_id}/data/store/json/{data_key}/{data_file_id}"
        response = requests.post(url, json=data, timeout=self.timeout)
        return response.json()
    
    @type_safe
    def retrieve_child_string(self                                ,             # Retrieve string child
                              cache_id     : Cache_Id             ,             # Parent cache ID
                              data_key     : Safe_Str__Data_Key   ,             # Data path key
                              data_file_id : Safe_Str__Data_File_Id) -> Optional[str]:
        url      = f"{self.base_url}/{self.namespace}/cache/{cache_id}/data/string/{data_key}/{data_file_id}"
        response = requests.get(url, timeout=self.timeout)
        if response.status_code == 404:
            return None
        return response.text
    
    @type_safe
    def retrieve_child_json(self                                ,               # Retrieve JSON child
                            cache_id     : Cache_Id             ,               # Parent cache ID
                            data_key     : Safe_Str__Data_Key   ,               # Data path key
                            data_file_id : Safe_Str__Data_File_Id) -> Optional[dict]:
        url      = f"{self.base_url}/{self.namespace}/cache/{cache_id}/data/json/{data_key}/{data_file_id}"
        response = requests.get(url, timeout=self.timeout)
        if response.status_code == 404:
            return None
        return response.json()
    
    @type_safe
    def delete_child(self                                ,                      # Delete child data file
                     cache_id     : Cache_Id             ,                      # Parent cache ID
                     data_type    : str                  ,                      # json | string
                     data_key     : Safe_Str__Data_Key   ,                      # Data path key
                     data_file_id : Safe_Str__Data_File_Id) -> bool:            # Success flag
        url      = f"{self.base_url}/{self.namespace}/cache/{cache_id}/data/delete/{data_type}/{data_key}/{data_file_id}"
        response = requests.delete(url, timeout=self.timeout)
        return response.status_code == 200
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Health Check
    # ═══════════════════════════════════════════════════════════════════════════
    
    def health_check(self) -> bool:                                             # Check service availability
        try:
            response = requests.get(f"{self.base_url}/info/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
```

### 4. `Perf__Storage__Cache_Service`

```python
# ═══════════════════════════════════════════════════════════════════════════════
# phase_e/storage/backends/Perf__Storage__Cache_Service.py
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                     import Optional, List
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                  import type_safe
from osbot_utils.type_safe.primitives.core.Safe_Str                             import Safe_Str
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id              import Cache_Id
from phase_e.storage.base.Perf__Storage__Base                                   import Perf__Storage__Base
from phase_e.storage.schemas.Schema__Perf__Storage__Config                      import Schema__Perf__Storage__Config
from phase_e.storage.schemas.Schema__Perf__Entry                                import Schema__Perf__Entry
from phase_e.storage.cache_service.Cache_Service__Client                        import Cache_Service__Client
from phase_e.storage.safe_str.Safe_Str__Session_Name                            import Safe_Str__Session_Name
from phase_e.storage.safe_str.Safe_Str__Target_Name                             import Safe_Str__Target_Name
from phase_e.storage.safe_str.Safe_Str__Data_Key                                import Safe_Str__Data_Key
from phase_e.storage.safe_str.Safe_Str__Data_File_Id                            import Safe_Str__Data_File_Id


class Perf__Storage__Cache_Service(Perf__Storage__Base):                        # Cache service backend
    config       : Schema__Perf__Storage__Config                                # Configuration
    client       : Cache_Service__Client                                        # HTTP client
    session_name : Safe_Str__Session_Name                                       # Current session
    target_name  : Safe_Str__Target_Name                                        # Current target
    cache_id     : Cache_Id                                                     # Current entry ID
    
    def setup(self) -> 'Perf__Storage__Cache_Service':                          # Initialize client
        self.client = Cache_Service__Client(base_url  = self.config.cache_service_url,
                                            namespace = self.config.cache_namespace  )
        return self
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Context Management
    # ═══════════════════════════════════════════════════════════════════════════
    
    @type_safe
    def set_context(self                                    ,                   # Set session/target context
                    session_name : Safe_Str__Session_Name   ,                   # Session identifier
                    target_name  : Safe_Str__Target_Name    ) -> None:          # Target identifier
        self.session_name = session_name
        self.target_name  = target_name
        self.cache_id     = Cache_Id('')                                        # Reset cache ID
    
    def cache_key(self) -> str:                                                 # Generate cache key path
        return f"sessions/{self.session_name}/targets/{self.target_name}"
    
    @type_safe
    def ensure_entry(self                    ,                                  # Ensure perf-entry exists
                     metadata : dict = None  ) -> Cache_Id:                     # Create if needed
        if not self.cache_id:
            entry_data    = metadata or Schema__Perf__Entry(session_name = self.session_name,
                                                            target_name  = self.target_name ).json()
            result        = self.client.store_entry(cache_key = self.cache_key(),
                                                    file_id   = Safe_Str__Data_File_Id('perf-entry'),
                                                    data      = entry_data                          )
            self.cache_id = Cache_Id(result.get('cache_id', ''))
        return self.cache_id
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Abstract Method Implementations
    # ═══════════════════════════════════════════════════════════════════════════
    
    @type_safe
    def save(self                  ,                                            # Save JSON data
             key  : str            ,                                            # Data key path
             data : dict           ) -> bool:                                   # Data to store
        cache_id               = self.ensure_entry()
        data_key, data_file_id = self.parse_key(key)
        result                 = self.client.store_child_json(cache_id     = cache_id    ,
                                                              data_key     = data_key    ,
                                                              data_file_id = data_file_id,
                                                              data         = data        )
        return result.get('cache_id') is not None
    
    @type_safe
    def save_string(self                  ,                                     # Save string content
                    key     : str         ,                                     # Data key path
                    content : str         ) -> bool:                            # String content
        cache_id               = self.ensure_entry()
        data_key, data_file_id = self.parse_key(key)
        result                 = self.client.store_child_string(cache_id     = cache_id    ,
                                                                data_key     = data_key    ,
                                                                data_file_id = data_file_id,
                                                                content      = content     )
        return result.get('cache_id') is not None
    
    @type_safe
    def load(self             ,                                                 # Load JSON data
             key : str        ) -> Optional[dict]:                              # Returns None if not found
        if not self.cache_id:
            return None
        data_key, data_file_id = self.parse_key(key)
        return self.client.retrieve_child_json(cache_id     = self.cache_id,
                                               data_key     = data_key     ,
                                               data_file_id = data_file_id )
    
    @type_safe
    def load_string(self             ,                                          # Load string content
                    key : str        ) -> Optional[str]:                        # Returns None if not found
        if not self.cache_id:
            return None
        data_key, data_file_id = self.parse_key(key)
        return self.client.retrieve_child_string(cache_id     = self.cache_id,
                                                 data_key     = data_key     ,
                                                 data_file_id = data_file_id )
    
    @type_safe
    def exists(self             ,                                               # Check if key exists
               key : str        ) -> bool:
        return self.load(key) is not None or self.load_string(key) is not None
    
    @type_safe
    def delete(self             ,                                               # Delete data by key
               key : str        ) -> bool:
        if not self.cache_id:
            return False
        data_key, data_file_id = self.parse_key(key)
        return (self.client.delete_child(self.cache_id, 'json'  , data_key, data_file_id) or
                self.client.delete_child(self.cache_id, 'string', data_key, data_file_id))
    
    @type_safe
    def list_keys(self                  ,                                       # List child data files
                  prefix : str = ''     ) -> List[str]:                         # Requires refs endpoint
        pass                                                                    # TODO: implement via refs API
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Key Parsing
    # ═══════════════════════════════════════════════════════════════════════════
    
    @type_safe
    def parse_key(self            ,                                             # Parse key into parts
                  key : str       ) -> tuple:                                   # (data_key, data_file_id)
        parts = key.rsplit('/', 1)
        if len(parts) == 2:
            return Safe_Str__Data_Key(parts[0]), Safe_Str__Data_File_Id(parts[1])
        return Safe_Str__Data_Key(''), Safe_Str__Data_File_Id(parts[0])
```

### 5. `Perf__Storage__Factory`

```python
# ═══════════════════════════════════════════════════════════════════════════════
# phase_e/storage/factory/Perf__Storage__Factory.py
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                  import type_safe
from phase_e.storage.base.Perf__Storage__Base                                   import Perf__Storage__Base
from phase_e.storage.backends.Perf__Storage__Local                              import Perf__Storage__Local
from phase_e.storage.backends.Perf__Storage__Memory                             import Perf__Storage__Memory
from phase_e.storage.backends.Perf__Storage__Cache_Service                      import Perf__Storage__Cache_Service
from phase_e.storage.schemas.Schema__Perf__Storage__Config                      import Schema__Perf__Storage__Config
from phase_e.storage.enums.Enum__Storage_Mode                                   import Enum__Storage_Mode


class Perf__Storage__Factory(Type_Safe):                                        # Storage factory
    config: Schema__Perf__Storage__Config                                       # Configuration
    
    @type_safe
    def create(self) -> Perf__Storage__Base:                                    # Create storage backend
        mode = self.config.storage_mode
        
        if mode == Enum__Storage_Mode.LOCAL:
            return Perf__Storage__Local(storage_path=self.config.local_storage_path)
        
        if mode == Enum__Storage_Mode.MEMORY:
            return Perf__Storage__Memory()
        
        if mode == Enum__Storage_Mode.CACHE_SERVICE:
            storage = Perf__Storage__Cache_Service(config=self.config)
            return storage.setup()
        
        return None                                                             # Unknown mode
```

---

## Testing Strategy

**Following Type_Safe testing patterns with context managers and .obj() comparisons:**

```python
# ═══════════════════════════════════════════════════════════════════════════════
# tests/unit/phase_e/storage/backends/test_Perf__Storage__Memory.py
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                   import TestCase
from phase_e.storage.backends.Perf__Storage__Memory                             import Perf__Storage__Memory


class test_Perf__Storage__Memory(TestCase):
    
    @classmethod
    def setUpClass(cls):                                                        # Shared setup - expensive ops
        cls.storage = Perf__Storage__Memory()
        cls.storage.set_context('test_session', 'test_target')
    
    def test__init__(self):                                                     # Test auto-initialization
        with Perf__Storage__Memory() as _:
            assert type(_)      is Perf__Storage__Memory
            assert type(_.data) is dict
            assert _.data       == {}
    
    def test_save__json(self):                                                  # Test JSON save
        with self.storage as _:
            result = _.save('results/test.json', {'value': 42})
            assert result is True
            assert _.exists('results/test.json') is True
    
    def test_load__json(self):                                                  # Test JSON load
        with self.storage as _:
            _.save('results/load_test.json', {'key': 'value'})
            data = _.load('results/load_test.json')
            assert data == {'key': 'value'}
    
    def test_save_string(self):                                                 # Test string save
        with self.storage as _:
            result = _.save_string('results/test.txt', 'Hello World')
            assert result is True
    
    def test_load_string(self):                                                 # Test string load
        with self.storage as _:
            _.save_string('reports/report.md', '# Report')
            content = _.load_string('reports/report.md')
            assert content == '# Report'
    
    def test_delete(self):                                                      # Test delete
        with self.storage as _:
            _.save('results/delete_test.json', {'temp': True})
            assert _.exists('results/delete_test.json') is True
            assert _.delete('results/delete_test.json') is True
            assert _.exists('results/delete_test.json') is False
    
    def test_list_keys(self):                                                   # Test key listing
        with self.storage as _:
            _.save('results/a.json', {})
            _.save('results/b.json', {})
            _.save('reports/c.md'  , {})
            
            all_keys    = _.list_keys()
            result_keys = _.list_keys('results/')
            
            assert 'results/a.json' in all_keys
            assert 'results/b.json' in all_keys
            assert 'reports/c.md'   in all_keys
            assert len(result_keys) >= 2


# ═══════════════════════════════════════════════════════════════════════════════
# tests/unit/phase_e/storage/factory/test_Perf__Storage__Factory.py
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                   import TestCase
from phase_e.storage.factory.Perf__Storage__Factory                             import Perf__Storage__Factory
from phase_e.storage.backends.Perf__Storage__Memory                             import Perf__Storage__Memory
from phase_e.storage.backends.Perf__Storage__Local                              import Perf__Storage__Local
from phase_e.storage.schemas.Schema__Perf__Storage__Config                      import Schema__Perf__Storage__Config
from phase_e.storage.enums.Enum__Storage_Mode                                   import Enum__Storage_Mode


class test_Perf__Storage__Factory(TestCase):
    
    def test_create__memory(self):                                              # Test memory backend creation
        config  = Schema__Perf__Storage__Config(storage_mode=Enum__Storage_Mode.MEMORY)
        factory = Perf__Storage__Factory(config=config)
        storage = factory.create()
        
        assert type(storage) is Perf__Storage__Memory
    
    def test_create__local(self):                                               # Test local backend creation
        config  = Schema__Perf__Storage__Config(storage_mode=Enum__Storage_Mode.LOCAL)
        factory = Perf__Storage__Factory(config=config)
        storage = factory.create()
        
        assert type(storage) is Perf__Storage__Local
```

---

## Migration Path

1. **Phase 1**: Create folder structure under `phase_e/storage/`
2. **Phase 2**: Move existing files (`Perf__Storage__Base.py`, `Perf__Storage__Local.py`)
3. **Phase 3**: Create custom Safe_Str types and Enum__Storage_Mode
4. **Phase 4**: Create Schema__Perf__Storage__Config and Schema__Perf__Entry
5. **Phase 5**: Implement Perf__Storage__Memory with full test coverage
6. **Phase 6**: Implement Cache_Service__Client with health check
7. **Phase 7**: Implement Perf__Storage__Cache_Service
8. **Phase 8**: Implement Perf__Storage__Factory
9. **Phase 9**: Integration tests with cache service

---

## Success Criteria

1. ✅ All classes inherit from Type_Safe
2. ✅ No raw `str`, `int`, `float` - all use Safe_* primitives
3. ✅ Schemas are pure data containers - no methods
4. ✅ All methods decorated with `@type_safe`
5. ✅ Proper alignment and inline comments (no docstrings)
6. ✅ Tests use context managers with `_` pattern
7. ✅ Factory correctly creates backends based on config
8. ✅ Results stored in `sessions/{name}/targets/{target}/perf-entry/data/` structure
9. ✅ Both txt and json artifacts stored correctly
10. ✅ Reports (md) stored under `reports/` path
11. ✅ Uses `Cache_Id` from osbot_utils for cache identifiers

---

## Related Documentation

| Document | Purpose |
|----------|---------|
| `v3_63_4__for_llms__type_safe.md` | Type_Safe capabilities guide |
| `v3_63_4__for_llms__python_formatting_guide.md` | Python formatting rules |
| `v3_69_1__performance-schemas__type-safe-briefing.md` | Performance schema patterns |
| `v3_1_1__for_llms__type_safe__testing_guidance.md` | Testing patterns |
| `v3_28_0__osbot-utils-safe-primitives__reference-guide.md` | Safe primitives catalog |
