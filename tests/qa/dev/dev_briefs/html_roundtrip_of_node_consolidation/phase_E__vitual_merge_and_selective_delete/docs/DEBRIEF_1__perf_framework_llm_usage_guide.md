# Performance Measurement Framework - LLM Usage Guide

**Version**: v1.0  
**Purpose**: Guide for LLMs on using the osbot_utils performance measurement framework  
**Applies To**: Any performance analysis, benchmarking, or optimization work

---

## Executive Summary

The osbot_utils performance framework provides **statistically robust, reproducible benchmarks** at nanosecond precision. The key principle is:

> **Every operation to measure must be isolated into a single callable that can be run through Fibonacci-based sampling.**

This eliminates noise from JIT compilation, GC pauses, and context switches that plague single-shot timing.

---

## Framework Layers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FRAMEWORK LAYERS                                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  Perf_Benchmark__Hypothesis                                                  │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Purpose: Compare BEFORE vs AFTER (A/B testing optimizations)               │
│  Use When: Testing if an optimization actually improves performance          │
│  Pattern: run_before(baseline_fn) → run_after(optimized_fn) → evaluate()    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Perf_Benchmark__Timing                                                      │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Purpose: Run multiple benchmarks in a session with structured IDs          │
│  Use When: Profiling multiple stages/components of a system                 │
│  Pattern: timing.benchmark('A_01__name', callable) for each operation       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Performance_Measure__Session (Perf)                                         │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Purpose: Measure a single callable with Fibonacci sampling                 │
│  Use When: Quick one-off measurements during development                    │
│  Pattern: session.measure(callable).print()                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## When to Use Each Layer

| Scenario | Use | Example |
|----------|-----|---------|
| "Is my optimization faster?" | `Perf_Benchmark__Hypothesis` | Testing `fast_create=True` vs default |
| "Where is time spent in my pipeline?" | `Perf_Benchmark__Timing` | Profiling HTML→Dict→MGraph→HTML stages |
| "How fast is this one function?" | `Perf` (Performance_Measure__Session) | Quick check during development |
| "How has performance changed over releases?" | `Perf_Benchmark__Diff` | Loading saved sessions and comparing |

---

## The Fundamental Rule

### ❌ WRONG: Single-Shot Timing

```python
import time

start = time.perf_counter_ns()
result = my_function()
elapsed = time.perf_counter_ns() - start  # Includes warmup, GC, noise
```

**Problems:**
- First call includes JIT compilation, import overhead
- GC pause can 10x the measurement
- Context switches add random noise
- Not reproducible

### ✅ CORRECT: Fibonacci-Based Sampling

```python
from osbot_utils.helpers.performance.benchmark.Perf_Benchmark__Timing import Perf_Benchmark__Timing

with Perf_Benchmark__Timing(config=config) as timing:
    timing.benchmark('A_01__my_function', my_function)  # Runs 87-1595 times
```

**Benefits:**
- Fibonacci sequence: [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610]
- Captures warmup effects in early iterations
- Outlier trimming removes GC spikes
- Weighted median-mean provides stable score
- Reproducible across runs

---

## Measurement Modes

| Mode | Iterations | Total Calls | Use When |
|------|------------|-------------|----------|
| `measure()` | Full Fibonacci | 1,595 | Fast operations (<1ms) |
| `measure__fast()` | Truncated | 87 | Medium operations (1-100ms) |
| `measure__quick()` | Minimal | 19 | Slow operations (>100ms) |

**Configuration in Perf_Benchmark__Timing:**

```python
config = Schema__Perf_Benchmark__Timing__Config(
    measure_fast  = True,   # Use 87-iteration mode
    measure_quick = False,  # Use 19-iteration mode (overrides fast)
)
```

---

## Benchmark ID Convention

```
{Section}_{Index}__{descriptive_name}

Examples:
  A_01__html_to_dict           # Section A, first benchmark
  A_02__dict_to_mgraph         # Section A, second benchmark
  B_01__converter_create       # Section B, first benchmark
  C_01__convert_only           # Section C, first benchmark
```

**Section meanings (suggested):**
- `A_xx__` - Primary/full operations
- `B_xx__` - Component creation/setup
- `C_xx__` - Isolated operations (no setup)
- `D_xx__` - Batch/bulk operations
- `S_xx__` - Scaling tests

---

## Pattern: Isolating Callable Targets

The most important skill is **isolating each operation into a pure callable**.

### Problem: Dependencies Between Stages

```python
# Stage 2 depends on Stage 1's output
html_dict = stage_1(html)      # Need this first
document  = stage_2(html_dict)  # Depends on html_dict
output    = stage_3(document)   # Depends on document
```

### Solution: Pre-Compute, Then Measure

```python
# 1. Pre-compute all intermediate values
html_dict = Html__To__Dict(html=html).convert()
document  = Dict__To__MGraph().convert(html_dict)

# 2. Now each benchmark is independent
with Perf_Benchmark__Timing(config=config) as timing:
    timing.benchmark('A_01__html_to_dict',
        lambda: Html__To__Dict(html=html).convert())
    
    timing.benchmark('A_02__dict_to_mgraph',
        lambda: Dict__To__MGraph().convert(html_dict))  # Uses pre-computed html_dict
    
    timing.benchmark('A_03__mgraph_to_html',
        lambda: MGraph__To__Html().convert(document))   # Uses pre-computed document
```

---

## Pattern: Separating Creation from Operation

When measuring a class method, you're often measuring **two things**:
1. Creating the class instance (Type_Safe `__init__`)
2. Calling the method

### Detailed Breakdown Pattern

```python
with Perf_Benchmark__Timing(config=config) as timing:
    
    # A: Full operation (create + call)
    timing.benchmark('A_01__full_operation',
        lambda: MyConverter(data=data).convert())
    
    # B: Creation only
    timing.benchmark('B_01__converter_create',
        lambda: MyConverter(data=data))
    
    # C: Method call only (using pre-created instance)
    converter = MyConverter(data=data)
    timing.benchmark('C_01__convert_only',
        converter.convert)
```

**This tells you:**
- If B is slow → Type_Safe object creation is expensive
- If C is slow → The method logic itself is expensive
- If A ≈ B + C → No hidden overhead
- If A > B + C → Something else happening (context, state)

---

## Pattern: Hypothesis Testing (A/B Comparison)

```python
from osbot_utils.helpers.performance.benchmark.Perf_Benchmark__Hypothesis import Perf_Benchmark__Hypothesis

def run_baseline(timing: Perf_Benchmark__Timing):
    timing.benchmark('A_01__operation', lambda: default_implementation())

def run_optimized(timing: Perf_Benchmark__Timing):
    with Type_Safe__Config(fast_create=True):
        timing.benchmark('A_01__operation', lambda: default_implementation())

hypothesis = Perf_Benchmark__Hypothesis(
    description        = 'Test fast_create optimization',
    target_improvement = 0.5,  # Expect 50%+ improvement
)

hypothesis.run_before(run_baseline)   # Warmup (discarded)
hypothesis.run_before(run_baseline)   # Actual baseline
hypothesis.run_after(run_optimized)   # Optimized version

result = hypothesis.evaluate()
hypothesis.print_report()
```

---

## Pattern: Multi-Size Scaling Analysis

```python
sizes = {
    '10'   : generator.generate_with_nodes(10)  ,
    '100'  : generator.generate_with_nodes(100) ,
    '1000' : generator.generate_with_nodes(1000),
}

results = {}
for name, html in sizes.items():
    results[name] = converter.benchmark_conversions(html)

# Analyze scaling behavior
# If time doubles when size doubles → O(n) linear ✅
# If time quadruples when size doubles → O(n²) quadratic ❌
```

---

## Common Mistakes

### Mistake 1: Measuring Object Creation Inside Loop

```python
# ❌ WRONG - measures Type_Safe creation 87 times
timing.benchmark('A_01__convert',
    lambda: MyConverter(data=data).convert())  # Creates new instance each iteration
```

This might be **intentional** (measuring real-world usage) or **accidental** (polluting conversion timing with creation overhead). Be explicit about which you want.

### Mistake 2: Closures with Mutable State

```python
# ❌ WRONG - result accumulates across iterations
result = None
def measure_me():
    nonlocal result
    result = expensive_operation()  # State persists!

timing.benchmark('A_01__test', measure_me)
```

**Fix**: Ensure each iteration is independent.

### Mistake 3: Not Warming Up

```python
# ❌ WRONG - first measurement includes import/JIT overhead
timing.benchmark('A_01__cold_start', my_function)
```

**Fix**: Run a warmup iteration first:

```python
my_function()  # Warmup (discard)
timing.benchmark('A_01__warmed', my_function)
```

Or in Hypothesis tests, the first `run_before()` serves as warmup.

### Mistake 4: Ignoring Context Managers

```python
# ❌ WRONG - Type_Safe__Config only active outside benchmark
with Type_Safe__Config(fast_create=True):
    pass  # Context ends here

timing.benchmark('A_01__test', lambda: MyClass())  # fast_create NOT active!
```

**Fix**: Ensure context is active during measurement:

```python
with Type_Safe__Config(fast_create=True):
    timing.benchmark('A_01__test', lambda: MyClass())  # fast_create IS active
```

---

## Output and Reporting

### Using Perf_Benchmark__Timing__Reporter

```python
with Perf_Benchmark__Timing(config=config) as timing:
    timing.benchmark('A_01__test', my_function)
    timing.benchmark('A_02__test', other_function)
    
    # Get reporter
    reporter = timing.reporter()
    
    # Print to console
    reporter.print_summary()
    
    # Save in multiple formats
    reporter.save_json('/path/to/results.json')
    reporter.save_text('/path/to/results.txt')
    reporter.save_markdown('/path/to/results.md')
    reporter.save_html('/path/to/results.html')
```

### Custom Reports with Print_Table

```python
from osbot_utils.helpers.Print_Table import Print_Table

table = Print_Table()
table.set_title('MY CUSTOM REPORT')
table.add_headers('Benchmark', 'Time', 'Percentage')

for benchmark_id, result in timing.results.items():
    table.add_row([benchmark_id, format_ns(result.final_score), '...'])

table.set_footer('Summary info here')
print(table.text())
```

---

## Time Formatting Convention

```python
def format_ns(ns: int) -> str:
    if ns >= 1_000_000_000:
        return f"{ns / 1_000_000_000:.2f}s"
    elif ns >= 1_000_000:
        return f"{ns / 1_000_000:.2f}ms"
    elif ns >= 1_000:
        return f"{ns / 1_000:.2f}µs"
    else:
        return f"{ns}ns"
```

---

## Threshold Constants

Define readable constants for assertions:

```python
time_100_ns  =       100
time_500_ns  =       500
time_1_kns   =     1_000    # 1 µs
time_5_kns   =     5_000    # 5 µs
time_10_kns  =    10_000    # 10 µs
time_100_kns =   100_000    # 100 µs
time_1_mns   = 1_000_000    # 1 ms
```

---

## Summary Checklist

When doing performance analysis:

- [ ] Choose the right layer (Hypothesis vs Timing vs Perf)
- [ ] Use proper benchmark IDs (`A_01__descriptive_name`)
- [ ] Isolate each operation into a pure callable
- [ ] Pre-compute dependencies for stage isolation
- [ ] Consider separating creation from operation
- [ ] Use appropriate measurement mode (full/fast/quick)
- [ ] Ensure context managers are active during measurement
- [ ] Include warmup iterations
- [ ] Save results for future comparison
- [ ] Build clear reports with Print_Table

---

## Import Reference

```python
# Core timing
from osbot_utils.helpers.performance.benchmark.Perf_Benchmark__Timing import Perf_Benchmark__Timing
from osbot_utils.helpers.performance.benchmark.schemas.timing.Schema__Perf_Benchmark__Timing__Config import Schema__Perf_Benchmark__Timing__Config

# Hypothesis testing
from osbot_utils.helpers.performance.benchmark.Perf_Benchmark__Hypothesis import Perf_Benchmark__Hypothesis

# Session comparison
from osbot_utils.helpers.performance.benchmark.Perf_Benchmark__Diff import Perf_Benchmark__Diff

# Low-level measurement
from osbot_utils.helpers.performance.Performance_Measure__Session import Perf

# Reporting
from osbot_utils.helpers.Print_Table import Print_Table

# Type_Safe optimization context
from osbot_utils.type_safe.type_safe_core.config.Type_Safe__Config import Type_Safe__Config
```
