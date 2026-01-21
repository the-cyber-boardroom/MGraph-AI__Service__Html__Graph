# Phase E_2: Performance Report Framework

**Status**: 📋 BRIEF  
**Date**: January 2026  
**Depends On**: Phase E_1 (Performance Benchmark Refactoring)  
**Target**: `phase_e/performance/report/`

---

## 1. Objective

Create a reusable framework for building structured performance reports that:

1. **Separates data from presentation** - Schema holds truth, renderers project to formats
2. **Follows Type_Safe patterns** - No raw primitives, schemas are pure data
3. **Enables rapid report creation** - User only writes the `benchmarks()` function
4. **Supports multiple output formats** - txt, md, html, json from same data
5. **Provides pluggable storage** - Abstract base with filesystem implementation

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER CODE                                       │
│                                                                             │
│   def benchmarks(self, timing):           # User writes ONLY this           │
│       timing.benchmark('A_01__...', ...)                                    │
│       timing.benchmark('A_02__...', ...)                                    │
│       ...                                                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Perf_Report__Builder                                 │
│                                                                             │
│   1. Creates Perf_Benchmark__Timing                                         │
│   2. Calls user's benchmarks(timing) function                               │
│   3. Collects timing.results                                                │
│   4. Calculates categories, percentages                                     │
│   5. Identifies bottleneck, generates insight                               │
│   6. Returns Schema__Perf_Report (structured data)                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Schema__Perf_Report                                  │
│                        (THE SINGLE SOURCE OF TRUTH)                          │
│                                                                             │
│   metadata   : Schema__Perf_Report__Metadata                                │
│   benchmarks : List__Perf_Report__Benchmarks                                │
│   categories : List__Perf_Report__Categories                                │
│   analysis   : Schema__Perf_Report__Analysis                                │
│   legend     : Dict__Perf_Report__Legend                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
            ┌───────────┐   ┌───────────┐   ┌───────────┐
            │ Renderer  │   │ Renderer  │   │ Renderer  │
            │   Text    │   │ Markdown  │   │   Json    │
            └───────────┘   └───────────┘   └───────────┘
                    │               │               │
                    ▼               ▼               ▼
            ┌─────────────────────────────────────────────┐
            │         Perf_Report__Storage__Base          │
            │              (Abstract)                     │
            ├─────────────────────────────────────────────┤
            │  Perf_Report__Storage__File_System          │
            │  (Future: __S3, __Database, etc.)           │
            └─────────────────────────────────────────────┘
```

---

## 3. Folder Structure

```
phase_e/
├── performance/
│   ├── report/                                    # NEW - Phase E_2
│   │   ├── __init__.py
│   │   │
│   │   ├── schemas/                               # Pure data containers
│   │   │   ├── __init__.py
│   │   │   ├── Schema__Perf_Report.py
│   │   │   ├── Schema__Perf_Report__Metadata.py
│   │   │   ├── Schema__Perf_Report__Benchmark.py
│   │   │   ├── Schema__Perf_Report__Category.py
│   │   │   └── Schema__Perf_Report__Analysis.py
│   │   │
│   │   ├── collections/                           # Typed collections
│   │   │   ├── __init__.py
│   │   │   ├── List__Perf_Report__Benchmarks.py
│   │   │   ├── List__Perf_Report__Categories.py
│   │   │   └── Dict__Perf_Report__Legend.py
│   │   │
│   │   ├── builder/                               # Report building logic
│   │   │   ├── __init__.py
│   │   │   └── Perf_Report__Builder.py
│   │   │
│   │   ├── renderers/                             # Output format renderers
│   │   │   ├── __init__.py
│   │   │   ├── Perf_Report__Renderer__Base.py
│   │   │   ├── Perf_Report__Renderer__Text.py
│   │   │   ├── Perf_Report__Renderer__Markdown.py
│   │   │   └── Perf_Report__Renderer__Json.py
│   │   │
│   │   └── storage/                               # Pluggable storage
│   │       ├── __init__.py
│   │       ├── Perf_Report__Storage__Base.py
│   │       └── Perf_Report__Storage__File_System.py
│   │
│   ├── Html_Generator__For_Benchmarks.py          # Existing
│   ├── Perf__Phase_E__Conversion.py               # Existing
│   ├── Perf__Phase_E__Scalability.py              # Existing
│   ├── Perf__Storage__Base.py                     # Existing (different purpose)
│   └── Perf__Storage__Local.py                    # Existing (different purpose)
│
└── tests/
    └── performance/
        └── report/                                # NEW - Phase E_2 tests
            ├── __init__.py
            ├── test_Schema__Perf_Report.py
            ├── test_Perf_Report__Builder.py
            ├── test_Perf_Report__Renderer__Text.py
            └── test_Perf_Report__Storage__File_System.py

docs/
└── phase_e_2/                                     # NEW - Phase E_2 docs
    ├── PHASE_E_2__brief.md                        # This file
    └── (debriefs added as work progresses)
```

---

## 4. Schema Definitions

### 4.1 Schema__Perf_Report__Metadata

```python
class Schema__Perf_Report__Metadata(Type_Safe):                   # Report metadata
    timestamp       : Timestamp_Now                               # Auto-generates on creation
    version         : Safe_Str__Version                           # Code version being tested
    title           : Safe_Str__Benchmark__Title                  # Report title
    description     : Safe_Str__Benchmark__Description            # What this report measures
    test_input      : Safe_Str__Benchmark__Description            # Description of input data
    measure_mode    : Enum__Measure_Mode                          # QUICK, FAST, DEFAULT
    benchmark_count : Safe_UInt                                   # Number of benchmarks
```

### 4.2 Schema__Perf_Report__Benchmark

```python
class Schema__Perf_Report__Benchmark(Type_Safe):                  # Single benchmark result
    benchmark_id    : Safe_Str__Benchmark_Id                      # e.g., A_01__html_to_dict__full
    time_ns         : Safe_UInt                                   # Measured time in nanoseconds
    category_id     : Safe_Str__Benchmark__Section                # Category ID (e.g., 'A')
    pct_of_total    : Safe_Float__Percentage_Change               # Percentage of total time
```

### 4.3 Schema__Perf_Report__Category

```python
class Schema__Perf_Report__Category(Type_Safe):                   # Category summary
    category_id     : Safe_Str__Benchmark__Section                # e.g., 'A', 'B', 'C'
    name            : Safe_Str__Benchmark__Title                  # e.g., 'Full Operation'
    description     : Safe_Str__Benchmark__Description            # From legend
    total_ns        : Safe_UInt                                   # Sum of all benchmarks
    pct_of_total    : Safe_Float__Percentage_Change               # Percentage of total time
    benchmark_count : Safe_UInt                                   # Number of benchmarks
```

### 4.4 Schema__Perf_Report__Analysis

```python
class Schema__Perf_Report__Analysis(Type_Safe):                   # Bottleneck analysis
    bottleneck_id   : Safe_Str__Benchmark_Id                      # Slowest benchmark
    bottleneck_ns   : Safe_UInt                                   # Time of bottleneck
    bottleneck_pct  : Safe_Float__Percentage_Change               # Percentage of total
    total_ns        : Safe_UInt                                   # Total time across all
    overhead_ns     : Safe_Int                                    # Can be negative
    overhead_pct    : Safe_Float__Percentage_Change               # Overhead percentage
    key_insight     : Safe_Str__Benchmark__Description            # Auto-generated insight
```

### 4.5 Schema__Perf_Report (Main Schema)

```python
class Schema__Perf_Report(Type_Safe):                             # Main report schema
    metadata        : Schema__Perf_Report__Metadata               # Report metadata
    benchmarks      : List__Perf_Report__Benchmarks               # All benchmark results
    categories      : List__Perf_Report__Categories               # Category summaries
    analysis        : Schema__Perf_Report__Analysis               # Bottleneck analysis
    legend          : Dict__Perf_Report__Legend                   # Category explanations
```

---

## 5. Collection Definitions

```python
# ═══════════════════════════════════════════════════════════════════════════════
# List__Perf_Report__Benchmarks
# ═══════════════════════════════════════════════════════════════════════════════

class List__Perf_Report__Benchmarks(Type_Safe__List):             # List of benchmark results
    expected_type = Schema__Perf_Report__Benchmark


# ═══════════════════════════════════════════════════════════════════════════════
# List__Perf_Report__Categories
# ═══════════════════════════════════════════════════════════════════════════════

class List__Perf_Report__Categories(Type_Safe__List):             # List of category summaries
    expected_type = Schema__Perf_Report__Category


# ═══════════════════════════════════════════════════════════════════════════════
# Dict__Perf_Report__Legend
# ═══════════════════════════════════════════════════════════════════════════════

class Dict__Perf_Report__Legend(Type_Safe__Dict):                 # Category ID → Description
    expected_key_type   = Safe_Str__Benchmark__Section
    expected_value_type = Safe_Str__Benchmark__Description
```

---

## 6. Builder Implementation

### 6.1 Perf_Report__Builder

```python
class Perf_Report__Builder(Type_Safe):                            # Builds Schema__Perf_Report
    metadata : Schema__Perf_Report__Metadata                      # Metadata template
    legend   : Dict__Perf_Report__Legend                          # Legend definitions
    config   : Schema__Perf_Benchmark__Timing__Config             # Timing configuration

    @type_safe
    def run(self                                              ,   # Run benchmarks and build report
            benchmarks_fn : Callable                              # User's benchmark function
       ) -> Schema__Perf_Report:
        pass

    @type_safe
    def build_benchmarks(self                                 ,   # Convert timing results to schemas
                         results : Dict__Benchmark_Results    ,
                         total_ns: Safe_UInt
                    ) -> List__Perf_Report__Benchmarks:
        pass

    @type_safe
    def build_categories(self                                 ,   # Group and summarize categories
                         benchmarks: List__Perf_Report__Benchmarks,
                         total_ns  : Safe_UInt
                    ) -> List__Perf_Report__Categories:
        pass

    @type_safe
    def build_analysis(self                                   ,   # Identify bottleneck
                       benchmarks : List__Perf_Report__Benchmarks,
                       categories : List__Perf_Report__Categories,
                       total_ns   : Safe_UInt
                  ) -> Schema__Perf_Report__Analysis:
        pass

    @type_safe
    def extract_category_id(self                              ,   # Get category from benchmark ID
                            benchmark_id: Safe_Str__Benchmark_Id
                       ) -> Safe_Str__Benchmark__Section:
        pass  # Returns first char before '_'

    @type_safe
    def generate_insight(self                                 ,   # Create key insight text
                         analysis  : Schema__Perf_Report__Analysis,
                         categories: List__Perf_Report__Categories
                    ) -> Safe_Str__Benchmark__Description:
        pass
```

---

## 7. Renderer Implementations

### 7.1 Perf_Report__Renderer__Base (Abstract)

```python
class Perf_Report__Renderer__Base(Type_Safe):                     # Abstract renderer base
    
    @type_safe
    def render(self, report: Schema__Perf_Report) -> Safe_Str:    # Override in subclasses
        raise NotImplementedError()

    @type_safe
    def format_ns(self, ns: Safe_UInt) -> Safe_Str:               # Common helper
        pass  # Returns "14.50ms", "500ns", etc.

    @type_safe
    def format_pct(self, pct: Safe_Float__Percentage_Change) -> Safe_Str:
        pass  # Returns "95.8%", "-0.02%", etc.
```

### 7.2 Perf_Report__Renderer__Text

```python
class Perf_Report__Renderer__Text(Perf_Report__Renderer__Base):   # Renders to .txt
    
    @type_safe
    def render(self, report: Schema__Perf_Report) -> Safe_Str__Benchmark__Report:
        pass

    @type_safe
    def render_header(self, report: Schema__Perf_Report) -> Safe_Str:
        pass

    @type_safe
    def render_metadata_table(self, metadata: Schema__Perf_Report__Metadata) -> Safe_Str:
        pass

    @type_safe
    def render_description(self, metadata: Schema__Perf_Report__Metadata) -> Safe_Str:
        pass

    @type_safe
    def render_legend(self, legend: Dict__Perf_Report__Legend) -> Safe_Str:
        pass

    @type_safe
    def render_benchmarks_table(self                                    ,
                                benchmarks: List__Perf_Report__Benchmarks,
                                categories: List__Perf_Report__Categories
                           ) -> Safe_Str:
        pass

    @type_safe
    def render_category_summary(self, categories: List__Perf_Report__Categories) -> Safe_Str:
        pass

    @type_safe
    def render_analysis(self, analysis: Schema__Perf_Report__Analysis) -> Safe_Str:
        pass

    @type_safe
    def render_footer(self, metadata: Schema__Perf_Report__Metadata) -> Safe_Str:
        pass
```

### 7.3 Perf_Report__Renderer__Markdown

```python
class Perf_Report__Renderer__Markdown(Perf_Report__Renderer__Base):  # Renders to .md
    
    @type_safe
    def render(self, report: Schema__Perf_Report) -> Safe_Str__Benchmark__Report:
        pass  # Uses markdown tables, headers, code blocks
```

### 7.4 Perf_Report__Renderer__Json

```python
class Perf_Report__Renderer__Json(Perf_Report__Renderer__Base):   # Renders to .json
    
    @type_safe
    def render(self, report: Schema__Perf_Report) -> Safe_Str:
        return json_dumps(report.json())                          # Direct serialization
```

---

## 8. Storage Implementations

### 8.1 Perf_Report__Storage__Base (Abstract)

```python
class Perf_Report__Storage__Base(Type_Safe):                      # Abstract storage base
    renderers : Dict[Safe_Str, Perf_Report__Renderer__Base]       # Format → Renderer mapping

    def __init__(self):
        self.renderers = {'txt' : Perf_Report__Renderer__Text()    ,
                          'md'  : Perf_Report__Renderer__Markdown(),
                          'json': Perf_Report__Renderer__Json()    }

    @type_safe
    def save(self                                             ,   # Save report in formats
             report  : Schema__Perf_Report                    ,
             key     : Safe_Str__Benchmark_Id                 ,
             formats : List[Safe_Str]
        ) -> bool:
        pass  # Calls save_content for each format

    @type_safe
    def save_content(self                                     ,   # Override in subclasses
                     key     : Safe_Str__Benchmark_Id         ,
                     content : Safe_Str                       ,
                     format  : Safe_Str
                ) -> bool:
        raise NotImplementedError()

    @type_safe
    def load(self, key: Safe_Str__Benchmark_Id) -> Schema__Perf_Report:
        raise NotImplementedError()                               # Override in subclasses

    @type_safe
    def list_reports(self) -> List[Safe_Str__Benchmark_Id]:
        raise NotImplementedError()                               # Override in subclasses
```

### 8.2 Perf_Report__Storage__File_System

```python
class Perf_Report__Storage__File_System(Perf_Report__Storage__Base):  # File system storage
    storage_path : Safe_Str__File__Path                           # Base path for reports

    @type_safe
    def save_content(self                                     ,   # Save to file
                     key     : Safe_Str__Benchmark_Id         ,
                     content : Safe_Str                       ,
                     format  : Safe_Str
                ) -> bool:
        pass  # Writes to {storage_path}/{key}.{format}

    @type_safe
    def load(self, key: Safe_Str__Benchmark_Id) -> Schema__Perf_Report:
        pass  # Reads from {storage_path}/{key}.json, deserializes

    @type_safe
    def list_reports(self) -> List[Safe_Str__Benchmark_Id]:
        pass  # Lists *.json files in storage_path

    @type_safe
    def build_file_path(self                                  ,   # Helper to construct path
                        key    : Safe_Str__Benchmark_Id       ,
                        format : Safe_Str
                   ) -> Safe_Str__File__Path:
        pass
```

---

## 9. Example Usage (Target State)

```python
class test_perf__Phase_E__Conversion__Detailed(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.html      = HTML_SIMPLE
        cls.html_dict = Html__To__Html_Dict__With__Node_Ids(html=cls.html).convert()
        cls.document  = Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(cls.html_dict)
        cls.storage   = Perf_Report__Storage__File_System(
                            storage_path=path_combine(phase_e.path, '../perf_results'))

    def benchmarks(self, timing: Perf_Benchmark__Timing):         # USER WRITES ONLY THIS
        # Section A: Full Operations
        timing.benchmark('A_01__html_to_dict__full',
            lambda: Html__To__Html_Dict__With__Node_Ids(html=self.html).convert())
        timing.benchmark('A_02__dict_to_mgraph__full',
            lambda: Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(self.html_dict))
        timing.benchmark('A_03__mgraph_to_html__full',
            lambda: Html_MGraph__Document__To__Html().convert(self.document))

        # Section B: Converter Creation
        timing.benchmark('B_01__converter_1_create',
            lambda: Html__To__Html_Dict__With__Node_Ids(html=self.html))
        timing.benchmark('B_02__converter_2_create',
            Html__To__Html_MGraph__Document__Node_Id_Reuse)
        timing.benchmark('B_03__converter_3_create',
            Html_MGraph__Document__To__Html)

        # Section C: Convert Only
        converter_1 = Html__To__Html_Dict__With__Node_Ids(html=self.html)
        timing.benchmark('C_01__html_to_dict__convert_only', converter_1.convert)

        converter_2 = Html__To__Html_MGraph__Document__Node_Id_Reuse()
        timing.benchmark('C_02__dict_to_mgraph__convert_only',
            lambda: converter_2.convert_from_dict(self.html_dict))

        converter_3 = Html_MGraph__Document__To__Html()
        timing.benchmark('C_03__mgraph_to_html__convert_only',
            lambda: converter_3.convert(self.document))

    def test__conversion_detailed_breakdown(self):
        builder = Perf_Report__Builder(
            metadata = Schema__Perf_Report__Metadata(
                title       = 'Phase E: Conversion Pipeline - Detailed Breakdown',
                version     = version__mgraph_ai_service_html_graph              ,
                description = 'Isolates converter creation from conversion logic',
                test_input  = HTML_SIMPLE[:50] + '...'                           ),
            legend = Dict__Perf_Report__Legend({
                'A': 'Full Operation      = Create converter instance + call convert()',
                'B': 'Converter Creation  = Only create converter instance (no conversion)',
                'C': 'Convert Only        = Call convert() on pre-created instance'}))

        report = builder.run(self.benchmarks)                     # Run and get structured data

        self.storage.save(report                    ,
                          key     = 'conversion__detailed',
                          formats = ['txt', 'md', 'json'] )
```

---

## 10. Implementation Order

### Phase E_2.1: Schemas & Collections
1. Create folder structure
2. Implement all Schema__* classes
3. Implement all List__* and Dict__* collections
4. Write unit tests for schemas

### Phase E_2.2: Builder
1. Implement Perf_Report__Builder
2. Test with simple benchmarks
3. Verify schema population

### Phase E_2.3: Renderers
1. Implement Perf_Report__Renderer__Base
2. Implement Perf_Report__Renderer__Text (match current output)
3. Implement Perf_Report__Renderer__Json
4. Implement Perf_Report__Renderer__Markdown
5. Test all renderers produce valid output

### Phase E_2.4: Storage
1. Implement Perf_Report__Storage__Base
2. Implement Perf_Report__Storage__File_System
3. Test save/load round-trip

### Phase E_2.5: Integration
1. Refactor test_perf__Phase_E__Conversion__Detailed to use new framework
2. Verify output matches current report
3. Document any differences

### Phase E_2.6: Migration Prep
1. Document what needs to change for osbot_utils migration
2. Identify any phase_e-specific code to remove
3. Write migration guide

---

## 11. Success Criteria

| Criteria | Measurement |
|----------|-------------|
| **Data structured** | Report stored as Schema__Perf_Report, not strings |
| **Multiple formats** | Same report renders to txt, md, json |
| **Round-trip** | Save to json, load back, data identical |
| **User simplicity** | Test file only needs benchmarks() function |
| **Type safety** | No raw primitives in schemas |
| **Output parity** | Text output matches current report format |

---

## 12. Future Extensions (Not in Phase E_2)

- `Perf_Report__Storage__S3` - Cloud storage
- `Perf_Report__Storage__Database` - SQLite/PostgreSQL
- `Perf_Report__Renderer__Html` - Interactive HTML with charts
- `Perf_Report__Comparator` - Compare two reports
- `Perf_Report__Aggregator` - Combine multiple reports
- Move to `osbot_utils.helpers.performance.benchmark.report.*`

---

## 13. Open Questions

1. **Category extraction** - Currently assumes first char before `_`. Should we support multi-char categories like `AA_01__...`?

2. **Insight generation** - Should insights be pluggable (different analyzers for different report types)?

3. **Renderer customization** - Should renderers accept configuration (column widths, colors, etc.)?

4. **Version tracking** - Should we store osbot_utils version in addition to project version?

---

## 14. References

- Phase E_1: Performance Benchmark Refactoring (completed)
- DEBRIEF_1: Perf Framework LLM Usage Guide
- DEBRIEF_2: Phase E Implementation
- DEBRIEF_3: Data Analysis
- DEBRIEF_4: Scalability Analysis
- v3_69_1__performance-schemas__type-safe-briefing.md
- v3_63_4__for_llms__type_safe.md
- v3_63_4__for_llms__python_formatting_guide.md
