# Performance Report Framework - LLM Usage Brief

**Version**: 1.0.0  
**Date**: January 2026  
**Location**: `phase_e/report/` (will migrate to `osbot_utils.helpers.performance.benchmark.report`)

---

## 1. Overview

The Performance Report Framework provides structured, type-safe performance reporting with:

- **Schema-based data** - Reports are `Schema__Perf_Report` objects, not strings
- **Automatic analysis** - Bottleneck detection, percentage calculations, insights
- **Multiple output formats** - txt, md, json from same data
- **Pluggable storage** - Abstract base with file system implementation

**Key Benefit**: User writes only benchmark definitions; framework handles everything else.

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER CODE                                       │
│   def benchmarks(self, timing):                                             │
│       timing.benchmark('A_01__name', lambda: ...)                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Perf_Report__Builder                                 │
│   - Runs benchmarks via Perf_Benchmark__Timing                              │
│   - Calculates categories, percentages                                      │
│   - Identifies bottleneck                                                   │
│   - Returns Schema__Perf_Report                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Schema__Perf_Report                                  │
│                        (SINGLE SOURCE OF TRUTH)                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              ▼                     ▼                     ▼
      Renderer__Text        Renderer__Markdown     Renderer__Json
              │                     │                     │
              └─────────────────────┼─────────────────────┘
                                    ▼
                    Perf_Report__Storage__File_System
```

---

## 3. Benchmark Naming Convention

### 3.1 Category Prefix Pattern

```
{CATEGORY}_{NUMBER}__{description}
    │          │           │
    │          │           └── Snake_case description
    │          └────────────── Two-digit sequence (01, 02, 03)
    └───────────────────────── Single letter category (A, B, C, ...)
```

**Examples:**
```python
'A_01__html_to_dict__full'           # Category A, benchmark 01
'A_02__dict_to_mgraph__full'         # Category A, benchmark 02
'B_01__converter_1_create'           # Category B, benchmark 01
'C_03__mgraph_to_html__convert_only' # Category C, benchmark 03
```

### 3.2 Category Detection

The framework extracts category from the first character before `_`:

```python
'A_01__html_to_dict__full' → Category 'A'
'B_02__converter_create'   → Category 'B'
```

### 3.3 Standard Category Pattern (A/B/C)

For isolation analysis, use this pattern:

| Category | Purpose | Measures |
|----------|---------|----------|
| **A_xx** | Full Operation | Create instance + call method |
| **B_xx** | Creation Only | Just instantiate object |
| **C_xx** | Method Only | Call method on pre-created instance |

**Analysis equation**: `A = B + C + Overhead`

This pattern answers: **"Is the bottleneck in object creation or method execution?"**

---

## 4. Core Components

### 4.1 Schemas (Pure Data)

```
Schema__Perf_Report                    # Main report container
├── metadata   : Schema__Perf_Report__Metadata
│   ├── timestamp       : Timestamp_Now
│   ├── version         : Safe_Str__Benchmark__Title
│   ├── title           : Safe_Str__Benchmark__Title
│   ├── description     : Safe_Str__Benchmark__Description
│   ├── test_input      : Safe_Str__Benchmark__Description
│   ├── measure_mode    : Enum__Measure_Mode
│   └── benchmark_count : Safe_UInt
│
├── benchmarks : List__Perf_Report__Benchmarks
│   └── Schema__Perf_Report__Benchmark
│       ├── benchmark_id : Safe_Str__Benchmark_Id
│       ├── time_ns      : Safe_UInt
│       ├── category_id  : Safe_Str__Benchmark__Section
│       └── pct_of_total : Safe_Float__Percentage_Change
│
├── categories : List__Perf_Report__Categories
│   └── Schema__Perf_Report__Category
│       ├── category_id     : Safe_Str__Benchmark__Section
│       ├── name            : Safe_Str__Benchmark__Title
│       ├── description     : Safe_Str__Benchmark__Description
│       ├── total_ns        : Safe_UInt
│       ├── pct_of_total    : Safe_Float__Percentage_Change
│       └── benchmark_count : Safe_UInt
│
├── analysis   : Schema__Perf_Report__Analysis
│   ├── bottleneck_id   : Safe_Str__Benchmark_Id
│   ├── bottleneck_ns   : Safe_UInt
│   ├── bottleneck_pct  : Safe_Float__Percentage_Change
│   ├── total_ns        : Safe_UInt
│   ├── overhead_ns     : Safe_Int
│   ├── overhead_pct    : Safe_Float__Percentage_Change
│   └── key_insight     : Safe_Str__Benchmark__Description
│
└── legend     : Dict__Perf_Report__Legend
    └── {category_id: description}
```

### 4.2 Builder

```python
from phase_e.report.builder.Perf_Report__Builder import Perf_Report__Builder

builder = Perf_Report__Builder(
    metadata = Schema__Perf_Report__Metadata(...),
    legend   = Dict__Perf_Report__Legend({...})  ,
    config   = Schema__Perf_Benchmark__Timing__Config(...))

report = builder.run(benchmarks_fn)  # Returns Schema__Perf_Report
```

### 4.3 Renderers

```python
from phase_e.report.renderers import (Perf_Report__Renderer__Text    ,
                                      Perf_Report__Renderer__Markdown,
                                      Perf_Report__Renderer__Json    )

text_output = Perf_Report__Renderer__Text().render(report)      # → str
md_output   = Perf_Report__Renderer__Markdown().render(report)  # → str
json_output = Perf_Report__Renderer__Json().render(report)      # → str
```

### 4.4 Storage

```python
from phase_e.report.storage.Perf_Report__Storage__File_System import Perf_Report__Storage__File_System

storage = Perf_Report__Storage__File_System(storage_path='/path/to/reports')

storage.save(report, key='my_report', formats=['txt', 'md', 'json'])

loaded = storage.load('my_report')  # Returns Schema__Perf_Report
```

---

## 5. Complete Usage Example

### 5.1 Minimal Example

```python
from unittest                                                                        import TestCase
from osbot_utils.helpers.performance.benchmark.Perf_Benchmark__Timing                import Perf_Benchmark__Timing
from osbot_utils.helpers.performance.benchmark.schemas.enums.Enum__Measure_Mode      import Enum__Measure_Mode
from osbot_utils.helpers.performance.benchmark.schemas.timing.Schema__Perf_Benchmark__Timing__Config import Schema__Perf_Benchmark__Timing__Config
from phase_e.report.builder.Perf_Report__Builder                                     import Perf_Report__Builder
from phase_e.report.collections.Dict__Perf_Report__Legend                            import Dict__Perf_Report__Legend
from phase_e.report.schemas.Schema__Perf_Report__Metadata                            import Schema__Perf_Report__Metadata
from phase_e.report.storage.Perf_Report__Storage__File_System                        import Perf_Report__Storage__File_System
from phase_e.report.renderers.Perf_Report__Renderer__Text                            import Perf_Report__Renderer__Text


class test_perf__Example(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.storage = Perf_Report__Storage__File_System(storage_path='/tmp/reports')
        cls.config  = Schema__Perf_Benchmark__Timing__Config(
                          title            = 'Example Benchmark',
                          measure_fast     = True               ,
                          print_to_console = False              ,
                          asserts_enabled  = False              )

    def benchmarks(self, timing: Perf_Benchmark__Timing):
        # Section A: Full Operations
        timing.benchmark('A_01__operation_one', lambda: some_function())
        timing.benchmark('A_02__operation_two', lambda: other_function())

        # Section B: Setup Only
        timing.benchmark('B_01__setup_one', lambda: setup_only())

        # Section C: Execute Only
        timing.benchmark('C_01__execute_one', lambda: execute_only())

    def test__example_benchmark(self):
        builder = Perf_Report__Builder(
            metadata = Schema__Perf_Report__Metadata(
                           title        = 'Example Performance Analysis'         ,
                           version      = '1.0.0'                                 ,
                           description  = 'Demonstrates the reporting framework.',
                           test_input   = 'Sample input data'                    ,
                           measure_mode = Enum__Measure_Mode.FAST                ),
            legend   = Dict__Perf_Report__Legend({
                           'A': 'Full Operation = Setup + Execute'               ,
                           'B': 'Setup Only     = Just initialization'           ,
                           'C': 'Execute Only   = Run on pre-initialized'        }),
            config   = self.config                                                )

        report = builder.run(self.benchmarks)

        self.storage.save(report, key='example', formats=['txt', 'md', 'json'])

        print(Perf_Report__Renderer__Text().render(report))
```

### 5.2 Conversion Pipeline Example (A/B/C Pattern)

```python
def benchmarks(self, timing: Perf_Benchmark__Timing):

    # Section A: Full Operations (create + convert)
    timing.benchmark('A_01__html_to_dict__full',
        lambda: Html__To__Dict(html=self.html).convert())
    timing.benchmark('A_02__dict_to_graph__full',
        lambda: Dict__To__Graph().convert(self.dict_data))

    # Section B: Object Creation Only
    timing.benchmark('B_01__converter_1_create',
        lambda: Html__To__Dict(html=self.html))
    timing.benchmark('B_02__converter_2_create',
        Dict__To__Graph)

    # Section C: Conversion Only (pre-created objects)
    converter_1 = Html__To__Dict(html=self.html)
    timing.benchmark('C_01__html_to_dict__convert_only', converter_1.convert)

    converter_2 = Dict__To__Graph()
    timing.benchmark('C_02__dict_to_graph__convert_only',
        lambda: converter_2.convert(self.dict_data))
```

---

## 6. Report Output Sections

### 6.1 Text Report Structure

```
════════════════════════════════════════════════════════════════════════════════
TITLE (from metadata.title)
════════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────┐
│ BENCHMARK METADATA                                                  │
│   Date, Version, Test Input, Measurement Mode, Total Benchmarks     │
└─────────────────────────────────────────────────────────────────────┘

DESCRIPTION
  (from metadata.description)

LEGEND
  A_xx  (from legend['A'])
  B_xx  (from legend['B'])
  C_xx  (from legend['C'])

┌─────────────────────────────────────────────────────────────────────┐
│ DETAILED BREAKDOWN                                                  │
│   Table of all benchmarks with time and % of total                  │
└─────────────────────────────────────────────────────────────────────┘

CATEGORY SUMMARY
  Totals per category + overhead calculation

PERCENTAGE ANALYSIS (relative to Full Operations)
  B and C as percentage of A (answers: where is time spent?)

STAGE BREAKDOWN (Full Operations)
  Visual bar chart of A_xx benchmarks relative to A total

BOTTLENECK ANALYSIS
  Slowest benchmark in A_xx category

KEY INSIGHT
  Auto-generated insight about creation vs execution

════════════════════════════════════════════════════════════════════════════════
Footer with timestamp and version
════════════════════════════════════════════════════════════════════════════════
```

### 6.2 Key Analysis Calculations

| Metric | Formula | Purpose |
|--------|---------|---------|
| Overhead | `A_total - B_total - C_total` | Framework/measurement cost |
| Creation % | `B_total / A_total * 100` | % time in object creation |
| Execution % | `C_total / A_total * 100` | % time in method execution |
| Bottleneck % | `max(A_xx) / A_total * 100` | % of slowest operation |

---

## 7. Imports Reference

### 7.1 Schemas

```python
from phase_e.report.schemas.Schema__Perf_Report            import Schema__Perf_Report
from phase_e.report.schemas.Schema__Perf_Report__Metadata  import Schema__Perf_Report__Metadata
from phase_e.report.schemas.Schema__Perf_Report__Benchmark import Schema__Perf_Report__Benchmark
from phase_e.report.schemas.Schema__Perf_Report__Category  import Schema__Perf_Report__Category
from phase_e.report.schemas.Schema__Perf_Report__Analysis  import Schema__Perf_Report__Analysis
```

### 7.2 Collections

```python
from phase_e.report.collections.List__Perf_Report__Benchmarks import List__Perf_Report__Benchmarks
from phase_e.report.collections.List__Perf_Report__Categories import List__Perf_Report__Categories
from phase_e.report.collections.Dict__Perf_Report__Legend     import Dict__Perf_Report__Legend
```

### 7.3 Builder

```python
from phase_e.report.builder.Perf_Report__Builder import Perf_Report__Builder
```

### 7.4 Renderers

```python
from phase_e.report.renderers.Perf_Report__Renderer__Base     import Perf_Report__Renderer__Base
from phase_e.report.renderers.Perf_Report__Renderer__Text     import Perf_Report__Renderer__Text
from phase_e.report.renderers.Perf_Report__Renderer__Markdown import Perf_Report__Renderer__Markdown
from phase_e.report.renderers.Perf_Report__Renderer__Json     import Perf_Report__Renderer__Json
```

### 7.5 Storage

```python
from phase_e.report.storage.Perf_Report__Storage__Base        import Perf_Report__Storage__Base
from phase_e.report.storage.Perf_Report__Storage__File_System import Perf_Report__Storage__File_System
```

### 7.6 Supporting (from osbot_utils)

```python
from osbot_utils.helpers.performance.benchmark.Perf_Benchmark__Timing                        import Perf_Benchmark__Timing
from osbot_utils.helpers.performance.benchmark.schemas.enums.Enum__Measure_Mode              import Enum__Measure_Mode
from osbot_utils.helpers.performance.benchmark.schemas.timing.Schema__Perf_Benchmark__Timing__Config import Schema__Perf_Benchmark__Timing__Config
```

---

## 8. Extending the Framework

### 8.1 Custom Renderer

```python
class Perf_Report__Renderer__Html(Perf_Report__Renderer__Base):

    @type_safe
    def render(self, report: Schema__Perf_Report) -> str:
        # Build HTML with charts, styling, etc.
        html = ['<html><body>']
        html.append(f'<h1>{report.metadata.title}</h1>')
        # ... render sections ...
        html.append('</body></html>')
        return '\n'.join(html)
```

### 8.2 Custom Storage Backend

```python
class Perf_Report__Storage__S3(Perf_Report__Storage__Base):
    bucket_name : str
    s3_client   : Any

    @type_safe
    def save_content(self, key: str, content: str, format_type: str) -> bool:
        s3_key = f'reports/{key}.{format_type}'
        self.s3_client.put_object(Bucket=self.bucket_name, Key=s3_key, Body=content)
        return True

    @type_safe
    def load(self, key: str) -> Schema__Perf_Report:
        response = self.s3_client.get_object(Bucket=self.bucket_name, Key=f'reports/{key}.json')
        data = json_loads(response['Body'].read())
        return Schema__Perf_Report.from_json(data)
```

### 8.3 Custom Category Pattern

For non-A/B/C patterns, override analysis in Builder or create custom subclass:

```python
class Perf_Report__Builder__Custom(Perf_Report__Builder):

    @type_safe
    def calculate_overhead(self, categories: List__Perf_Report__Categories) -> int:
        # Custom overhead calculation for different category pattern
        # Example: X = setup, Y = process, Z = cleanup
        x_total = y_total = z_total = 0
        for category in categories:
            cat_id = str(category.category_id)
            if cat_id == 'X': x_total = int(category.total_ns)
            if cat_id == 'Y': y_total = int(category.total_ns)
            if cat_id == 'Z': z_total = int(category.total_ns)
        return x_total + y_total + z_total  # Different calculation
```

---

## 9. Common Patterns

### 9.1 Pre-compute Expensive Setup in setUpClass

```python
@classmethod
def setUpClass(cls):
    cls.html      = load_test_html()
    cls.html_dict = Html__To__Dict(html=cls.html).convert()      # Pre-compute
    cls.document  = Dict__To__Graph().convert(cls.html_dict)     # Pre-compute
```

### 9.2 Use Lambda for Parameterized Benchmarks

```python
# ✓ CORRECT - lambda captures self.html_dict
timing.benchmark('C_02__convert',
    lambda: converter.convert(self.html_dict))

# ✗ WRONG - would execute immediately
timing.benchmark('C_02__convert',
    converter.convert(self.html_dict))
```

### 9.3 Direct Method Reference for No-Argument Methods

```python
# ✓ Both work for no-argument methods
timing.benchmark('C_01__convert', converter.convert)
timing.benchmark('C_01__convert', lambda: converter.convert())
```

### 9.4 Class Reference for Constructor Benchmarks

```python
# Benchmark just calling the class (no arguments)
timing.benchmark('B_02__create', MyClass)

# Benchmark with arguments
timing.benchmark('B_01__create', lambda: MyClass(arg=value))
```

---

## 10. Troubleshooting

### 10.1 Category Not Detected

**Problem**: All benchmarks show as same category or "Unknown"

**Solution**: Ensure benchmark IDs follow pattern `{LETTER}_{NUMBER}__...`

```python
# ✗ Wrong patterns
'html_to_dict'           # No category prefix
'A-01-html_to_dict'      # Wrong separator
'AA_01__html_to_dict'    # Multi-letter category (not supported)

# ✓ Correct pattern
'A_01__html_to_dict'
```

### 10.2 Percentages Don't Add Up

**Problem**: Category percentages show ~50%/~50% instead of meaningful breakdown

**Solution**: This is correct for the main table (A+B+C=100%). Check "PERCENTAGE ANALYSIS (relative to Full Operations)" for B/A and C/A ratios.

### 10.3 Overhead is Negative

**Problem**: `Overhead: -500ns`

**Explanation**: Normal due to measurement variance. Small negative values indicate A ≈ B + C (no significant overhead).

### 10.4 JSON Round-Trip Fails

**Problem**: `Schema__Perf_Report.from_json(data)` raises error

**Solution**: Ensure all custom types have `json()` and `from_json()` methods. Check that Safe_* primitives are properly serialized.

---

## 11. Best Practices

| Practice | Reason |
|----------|--------|
| Use `measure_fast=True` for development | 87 iterations, faster feedback |
| Use `measure_fast=False` for final reports | 1000 iterations, more accurate |
| Pre-compute in `setUpClass` | Isolate benchmark from setup cost |
| Keep benchmark names descriptive | Appears in reports |
| Always include legend | Self-documenting reports |
| Save JSON format | Enables future comparison tooling |
| Use A/B/C pattern | Framework optimized for this analysis |

---

## 12. Migration Notes

When migrating from `phase_e.report` to `osbot_utils.helpers.performance.benchmark.report`:

1. Update all import paths
2. Verify Type_Safe primitives are available
3. Test JSON round-trip with production data
4. Update any custom renderers/storage backends

---

## 13. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01 | Initial release with Text, Markdown, JSON renderers |
