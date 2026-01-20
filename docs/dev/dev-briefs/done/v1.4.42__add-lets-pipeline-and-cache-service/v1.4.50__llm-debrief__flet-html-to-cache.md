# Technical Debrief: FLeT__Html__To__Cache

**Date**: January 19, 2026  
**Component**: HTML to Cache FLeT Pipeline  
**Package**: `mgraph_ai_service_html_graph`

---

## 1. Purpose

`FLeT__Html__To__Cache` is a single-responsibility FLeT (Flow-Level Execution Task) that saves HTML content to the cache data layer. It operates within an already-established cache entity (cache_id provided by orchestrator).

### What It Does
- Receives HTML content as input
- Saves it to the cache data layer under a specified data_key
- Records flow execution data for observability

### What It Does NOT Do (Orchestrator Responsibility)
- Entity creation (cache_id must already exist)
- cache_key resolution
- cache_hash computation
- Deduplication checks

---

## 2. File Structure

```
mgraph_ai_service_html_graph/
└── service/
    └── flet_pipeline/
        └── flet/
            ├── base/
            │   ├── Html_FLeT__Base.py           # Base class for all FLeTs
            │   └── Html_FLeT__Flow.py           # Flow wrapper for observability
            ├── schemas/
            │   ├── Schema__FLeT__Config.py      # FLeT configuration
            │   └── Schema__FLeT__Execution__Result.py  # Execution result wrapper
            └── steps/
                └── html__to__cache/
                    ├── FLeT__Html__To__Cache.py       # Main FLeT class
                    ├── actions/
                    │   └── action__html_to_cache__save.py  # Single action
                    └── schemas/
                        ├── Schema__Html_To_Cache__Input.py   # Input schema
                        └── Schema__Html_To_Cache__Output.py  # Output schema
```

---

## 3. File Descriptions

### 3.1 FLeT__Html__To__Cache.py

**Purpose**: Main FLeT class that orchestrates HTML saving

**Responsibilities**:
- Configure the FLeT (name, description)
- Wire up the action with dependencies
- Provide type-safe execute override

```python
class FLeT__Html__To__Cache(Html_FLeT__Base):

    def setup(self) -> 'FLeT__Html__To__Cache':
        self.config = Schema__FLeT__Config(name        = 'html-to-cache',
                                           description = 'Save HTML content to cache data layer')
        return self

    def run_actions(self, input_data: Schema__Html_To_Cache__Input) -> Schema__Html_To_Cache__Output:
        return action__html_to_cache__save(input_data   = input_data,
                                           cache_client = self.cache_client,
                                           cache_id     = self.cache_id,
                                           namespace    = self.namespace)

    @type_safe
    def execute(self, input_data: Schema__Html_To_Cache__Input) -> Schema__FLeT__Execution__Result:
        return super().execute(input_data=input_data)
```

---

### 3.2 Html_FLeT__Base.py

**Purpose**: Base class providing common FLeT functionality

**Responsibilities**:
- Flow lifecycle management (setup, execute, teardown)
- Flow data storage for observability
- Cache entity access helpers
- Duration and log capture

**Key Attributes**:
```python
class Html_FLeT__Base(Type_Safe):
    config       : Schema__FLeT__Config = None    # FLeT configuration
    cache_client : Html_Cache__Client   = None    # Cache client for storage
    cache_id     : Cache_Id             = None    # Entity cache_id (from orchestrator)
    namespace    : Safe_Str__Namespace  = None    # Namespace for cache operations
    flow         : Html_FLeT__Flow      = None    # Flow instance for observability
    flow_output  : Type_Safe            = None    # Final output
```

**Key Methods**:
```python
def execute(self, input_data) -> Schema__FLeT__Execution__Result:
    # Wraps run_actions() in Flow context
    # Captures duration, handles errors
    # Saves flow data automatically

def save_flow_data(self):
    # Stores flow execution data to cache

def cache_entity(self) -> Cache__Entity:
    # Returns bound client for entity operations

def flow_data(self) -> Cache__Entity__Json_File:
    # Returns bound client for flow data file
```

---

### 3.3 Html_FLeT__Flow.py

**Purpose**: Flow wrapper that provides task-level observability

**Responsibilities**:
- Wrap action execution in Task context
- Capture start/end times, durations
- Record logs, events, results
- Store return values

**Usage**: Created internally by `Html_FLeT__Base.execute()`

---

### 3.4 action__html_to_cache__save.py

**Purpose**: Single action that performs the actual HTML storage

**Responsibilities**:
- Extract HTML string from input
- Call cache client to store content
- Return success/failure with metadata

```python
@task()
@type_safe
def action__html_to_cache__save(
    input_data   : Schema__Html_To_Cache__Input,
    cache_client : Html_Cache__Client,
    cache_id     : Cache_Id,
    namespace    : Safe_Str__Namespace
) -> Schema__Html_To_Cache__Output:

    html_str     = str(input_data.html)
    char_count   = len(html_str)
    data_key     = input_data.data_key
    data_file_id = input_data.data_file_id

    response = cache_client.data__store_string(
        namespace    = namespace,
        cache_id     = cache_id,
        data_key     = data_key,
        data_file_id = data_file_id,
        content      = html_str
    )

    if response:
        return Schema__Html_To_Cache__Output(
            success        = True,
            data_key       = data_key,
            data_file_id   = data_file_id,
            char_count     = char_count,
            store_response = response
        )
    else:
        return Schema__Html_To_Cache__Output(
            success      = False,
            data_key     = data_key,
            data_file_id = data_file_id,
            char_count   = char_count
        )
```

**Design Notes**:
- Decorated with `@task()` for Flow integration
- Decorated with `@type_safe` for parameter validation
- All dependencies passed as parameters (no hidden state)
- Returns typed output schema

---

### 3.5 Schema__Html_To_Cache__Input.py

**Purpose**: Input data contract for the FLeT

```python
class Schema__Html_To_Cache__Input(Type_Safe):
    html         : Safe_Str__Html                                    # HTML content to save
    data_key     : str = DEFAULT__HTML_TO_CACHE__DATA_KEY            # 'html'
    data_file_id : str = DEFAULT__HTML_TO_CACHE__DATA_FILE_ID        # 'raw'
```

**Defaults**:
- `data_key = 'html'`
- `data_file_id = 'raw'`
- Results in file: `{entity}/data/html/raw.txt`

---

### 3.6 Schema__Html_To_Cache__Output.py

**Purpose**: Output data contract for the FLeT

```python
class Schema__Html_To_Cache__Output(Type_Safe):
    success        : bool                                            # Whether save succeeded
    data_key       : str                                             # Data key used
    data_file_id   : str                                             # File ID used
    char_count     : int                                             # Character count of HTML
    store_response : Schema__Cache__Data__Store__Response = None     # Full response from cache
```

---

### 3.7 Schema__FLeT__Config.py

**Purpose**: Configuration for any FLeT

```python
class Schema__FLeT__Config(Type_Safe):
    name        : str = ''     # FLeT identifier (e.g., 'html-to-cache')
    description : str = ''     # Human-readable description
```

---

### 3.8 Schema__FLeT__Execution__Result.py

**Purpose**: Wrapper for FLeT execution results

```python
class Schema__FLeT__Execution__Result(Type_Safe):
    success     : bool       = False    # Whether execution succeeded
    duration    : float      = 0.0      # Execution time in seconds
    flow_output : Type_Safe  = None     # FLeT-specific output (e.g., Schema__Html_To_Cache__Output)
    message     : str        = ''       # Status message or error
```

---

## 4. Execution Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  1. CALLER (Orchestrator or Test)                                           │
│     flet = FLeT__Html__To__Cache(cache_client, cache_id, namespace).setup() │
│     result = flet.execute(Schema__Html_To_Cache__Input(html=html))          │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  2. FLeT__Html__To__Cache.execute()                                         │
│     → Calls super().execute(input_data)                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  3. Html_FLeT__Base.execute()                                               │
│     → Creates Html_FLeT__Flow                                               │
│     → Calls flow.setup(self.run_actions, input_data)                        │
│     → Calls flow.execute()                                                  │
│     → Captures duration, handles errors                                     │
│     → Calls save_flow_data()                                                │
│     → Returns Schema__FLeT__Execution__Result                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  4. Html_FLeT__Flow.execute()                                               │
│     → Calls run_actions(input_data) wrapped in Task context                 │
│     → Records timing, logs, results                                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  5. FLeT__Html__To__Cache.run_actions()                                     │
│     → Calls action__html_to_cache__save(input_data, cache_client, ...)      │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  6. action__html_to_cache__save()                                           │
│     → Extracts HTML string                                                  │
│     → Calls cache_client.data__store_string()                               │
│     → Returns Schema__Html_To_Cache__Output                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Storage Pattern

After execution, the cache contains:

```
{namespace}/data/key-based/{cache_key}/{file_id}/
├── root.json                              # Entry data (created by orchestrator)
├── root.json.config                       # Entry config
├── root.json.metadata                     # Entry metadata
└── root/data/
    ├── html/
    │   └── raw.txt                        # ← HTML content (from action)
    └── flows/
        └── html-to-cache/
            └── flow-data.json             # ← Flow execution data (from base)
```

### Example Paths

For `namespace='my-app'`, `cache_key='docs/readme'`, `file_id='root'`:

```
my-app/data/key-based/docs/readme/root/data/html/raw.txt
my-app/data/key-based/docs/readme/root/data/flows/html-to-cache/flow-data.json
```

---

## 6. Flow Data Structure

The `flow-data.json` file contains:

```json
{
  "flow_data": {
    "flow_id": "flow_id___abc123",
    "flow_name": "run_actions",
    "start_time": "2026-01-19T12:00:00",
    "end_time": "2026-01-19T12:00:01",
    "status": "completed",
    "error": null,
    "tasks": [
      {
        "task_id": "task_id___xyz789",
        "task_name": "action__html_to_cache__save",
        "start_time": "...",
        "end_time": "...",
        "status": "completed",
        "return_value": { ... }
      }
    ],
    "logs": [
      {"timestamp": "...", "level": 10, "message": "Task started", "task_id": "..."},
      {"timestamp": "...", "level": 10, "message": "Task completed", "task_id": "..."}
    ],
    "return_value": {
      "success": true,
      "data_key": "html",
      "data_file_id": "raw",
      "char_count": 45,
      "store_response": { ... }
    }
  },
  "flow_events": []
}
```

---

## 7. Usage Example

### Basic Usage

```python
# Setup
cache_client = Html_Cache__Client(...)
cache_id     = 'existing-entity-id'
namespace    = 'my-namespace'

# Create and configure FLeT
flet = FLeT__Html__To__Cache(
    cache_client = cache_client,
    cache_id     = cache_id,
    namespace    = namespace
).setup()

# Execute
html = '<html><body><p>Hello World</p></body></html>'
result = flet.execute(Schema__Html_To_Cache__Input(html=Safe_Str__Html(html)))

# Check result
assert result.success is True
assert result.flow_output.char_count == 45
assert result.flow_output.data_key == 'html'
assert result.flow_output.data_file_id == 'raw'
```

### Accessing Flow Data After Execution

```python
# Get flow execution data
with flet.flow_data() as flow_file:
    assert flow_file.exists() is True
    flow_json = flow_file.retrieve()
    print(f"Flow status: {flow_json['flow_data']['status']}")

# Get cache entity
with flet.cache_entity() as entity:
    html_content = entity.data__string('html', 'raw')
    all_files = entity.data__files__paths()
```

### Custom Data Key

```python
# Store HTML under different path
result = flet.execute(Schema__Html_To_Cache__Input(
    html         = Safe_Str__Html(html),
    data_key     = 'rendered',
    data_file_id = 'output'
))
# Creates: {entity}/data/rendered/output.txt
```

---

## 8. Design Principles

| Principle | Application |
|-----------|-------------|
| **Single Responsibility** | FLeT only saves HTML; entity creation is orchestrator's job |
| **Explicit Dependencies** | Action receives all dependencies as parameters |
| **Type Safety** | All inputs/outputs are typed schemas with `@type_safe` |
| **Observability** | Flow data automatically captured and stored |
| **Separation of Concerns** | FLeT → Base → Action layers |
| **Testability** | Each layer independently testable |

---

## 9. Error Handling

```python
# In Html_FLeT__Base.execute()
try:
    flow.setup(self.run_actions, input_data)
    flow.execute()
    self.flow_output = flow.flow_return_value
    success = True
    message = 'Flow executed ok'
except Exception as error:
    success = False
    message = str(error)

# Always save flow data (even on failure)
self.save_flow_data()

return Schema__FLeT__Execution__Result(
    success     = success,
    message     = message,
    duration    = duration.seconds,
    flow_output = self.flow_output
)
```

---

## 10. Dependencies

### External Packages
- `osbot_utils` - Type_Safe, decorators, Flow/Task system
- `mgraph_ai_service_cache_client` - Cache client and entity wrappers

### Internal Dependencies
```
FLeT__Html__To__Cache
    ├── Html_FLeT__Base
    │   ├── Html_FLeT__Flow
    │   ├── Cache__Entity
    │   └── Cache__Entity__Json_File
    ├── Schema__FLeT__Config
    ├── Schema__FLeT__Execution__Result
    ├── Schema__Html_To_Cache__Input
    ├── Schema__Html_To_Cache__Output
    └── action__html_to_cache__save
        └── Html_Cache__Client
```

---

## 11. Testing

```python
class test_FLeT__Html__To__Cache(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cache_client, cls.cache_service = create_html_cache_client()
        cls.namespace   = 'test-html-to-cache'
        cls.cache_key   = 'test/entity'
        cls.cache_id    = cls.create_test_entity()

    def test_execute__with_dependencies(self):
        flet = FLeT__Html__To__Cache(
            cache_client = self.cache_client,
            cache_id     = self.cache_id,
            namespace    = self.namespace
        ).setup()

        result = flet.execute(Schema__Html_To_Cache__Input(
            html = Safe_Str__Html('<html><body>Test</body></html>')
        ))

        assert result.success is True
        assert result.flow_output.char_count == 29

        # Verify flow data stored
        with flet.flow_data() as _:
            assert _.exists() is True
            assert _.retrieve()['flow_data']['status'] == 'completed'

        # Verify HTML stored
        with flet.cache_entity() as _:
            assert _.data__string('html', 'raw') == '<html><body>Test</body></html>'
```

---

## 12. Summary

`FLeT__Html__To__Cache` is a focused, single-responsibility component that:

1. **Receives** HTML content via typed input schema
2. **Saves** it to the cache data layer via a single action
3. **Records** flow execution data for observability
4. **Returns** typed result with success status and metadata

The three-layer architecture (FLeT → Base → Action) provides clean separation of concerns while the automatic flow data storage enables debugging and monitoring of all FLeT executions.
