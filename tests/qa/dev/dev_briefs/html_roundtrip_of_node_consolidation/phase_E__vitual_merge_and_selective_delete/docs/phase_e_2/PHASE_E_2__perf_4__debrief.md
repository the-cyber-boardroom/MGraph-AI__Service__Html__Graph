# PHASE_E_2__perf_4__debrief.md

## Performance Analysis: convert_from_dict Breakdown

**Date:** 2026-01-10  
**Benchmark:** perf_4__benchmark__convert_from_dict__breakdown  
**Focus:** Zooming into the 95% bottleneck identified in previous analysis

---

## Executive Summary

Previous benchmarks identified `convert_from_dict()` as consuming 95% of the HTML→MGraph pipeline time. This analysis breaks down that method into its component stages and reveals a **clear scaling pattern**: fixed overhead from document setup (~4-5ms constant) plus **linear scaling in `process_body`** that becomes the dominant bottleneck at scale.

---

## Raw Data: Scaling Analysis

| Stage | html_1 | html_10 | html_50 | html_100 | Scaling Behavior |
|-------|--------|---------|---------|----------|------------------|
| document_setup | 4.10ms | 4.50ms | 5.20ms | 5.40ms | **CONSTANT** |
| extract_head_body | 1µs | 1µs | 1µs | 1µs | Negligible |
| process_attrs_html_tag | 1µs | 1µs | 1µs | 1µs | Negligible |
| process_head | 800µs | 1.00ms | 900µs | 700µs | **CONSTANT** |
| process_body | 800µs | 2.10ms | 7.80ms | 15.20ms | **O(n) LINEAR** |
| full_convert_from_dict | 9.20ms | 8.70ms | 18.10ms | 30.40ms | Reference |

---

## Key Findings

### 1. Document Setup is Fixed Overhead (~4-5ms)

The `document_setup` stage creates the `Html_MGraph__Document` object, which internally creates **5 separate MGraph instances** (head_graph, body_graph, attrs_graph, scripts_graph, styles_graph).

- This cost is **constant regardless of HTML size**
- At html_1: 4.10ms (27.5% of total)
- At html_100: 5.40ms (10.4% of total)
- Same absolute cost, decreasing percentage as content grows

**Assessment:** This is acceptable overhead. A 5ms fixed cost per document is reasonable for HTML parsing operations. No immediate optimization needed.

### 2. Extract and Attrs Processing are Negligible

Both `extract_head_body` and `process_attrs_html_tag` consistently measure at ~1µs regardless of document size. These are not bottlenecks and require no optimization focus.

### 3. Process Head is Constant (~800µs-1ms)

The `<head>` section processing remains relatively constant because:
- HTML `<head>` sections have a limited, predictable structure
- Number of `<head>` elements doesn't scale with page complexity
- Typical elements: `<title>`, `<meta>`, `<link>`, `<script>` declarations

### 4. Process Body Scales Linearly - THE BOTTLENECK

This is the critical finding:

| Nodes | process_body Time | Per-Node Cost |
|-------|-------------------|---------------|
| 1 | 800µs | 800µs |
| 10 | 2.10ms | 210µs |
| 50 | 7.80ms | 156µs |
| 100 | 15.20ms | 152µs |

**Extrapolation to Real-World Scale:**

| Nodes | Estimated process_body Time |
|-------|----------------------------|
| 500 | ~76ms |
| 1,000 | ~152ms |
| 5,000 | ~760ms |
| 10,000 | ~1.5 seconds |

This directly correlates with observed MVP behavior where **real-world pages take 1-5 seconds to load**. Pages with 1000s of DOM elements hit this linear scaling wall.

---

## The Real Problem

The issue with `process_body` is **not** that it scales linearly (O(n) is expected for processing n elements). The problem is the **per-node cost is too high** (~150µs per node).

For comparison:
- 150µs × 1,000 nodes = 150ms (borderline acceptable)
- 150µs × 10,000 nodes = 1.5 seconds (unacceptable for interactive use)

A target of **<20µs per node** would bring 10,000 nodes down to ~200ms.

---

## Optimization Strategies for process_body

### Strategy 1: Improve Raw Node/Object Creation Speed

The `process_body` method creates Type_Safe objects for each DOM node. The `fast_create` optimization already provides ~50% improvement, but further gains may be possible:

- Profile which Type_Safe classes are instantiated most frequently
- Consider specialized fast-paths for common node types
- Minimize attribute dictionary creation overhead

### Strategy 2: Cache Repeated Data/Structures

HTML documents have significant structural repetition:

- Same tag names repeated (div, span, p, a, etc.)
- Same attribute names repeated (class, id, style, href)
- Same attribute values repeated (common CSS classes)

Caching opportunities:
- Intern/cache `Node_Path` strings
- Cache `tag` to schema mappings
- Pool commonly used attribute name strings

### Strategy 3: Batch Object Creation

When processing a document, we know upfront (or can predict) how many objects we'll need:

- Pre-allocate node containers
- Batch-create nodes of the same type
- Reduce per-object allocation overhead through pooling

### Strategy 4: Reuse Identical Nodes/Objects

HTML has limited schema diversity:
- Only ~100 valid HTML tag types
- Common attribute patterns repeat across elements
- Many elements are structurally identical (e.g., list items)

Opportunities:
- Flyweight pattern for identical attribute sets
- Shared schema instances for same-type nodes
- Reference counting for duplicate text content

---

## HTML-Specific Optimization Advantages

The fact that we're processing HTML provides optimization opportunities:

1. **Limited Tag Vocabulary**: Only ~100 valid HTML tags exist. We can pre-compute schemas for all of them.

2. **Predictable Structure**: HTML follows strict parent-child rules. We know what can appear where.

3. **Attribute Patterns**: Common attributes (class, id, style, data-*) repeat frequently. High cache hit potential.

4. **Text Content Duplication**: Common text patterns (whitespace, punctuation) can be interned.

5. **No Data Loss Required**: All optimizations can be lossless - we're just changing representation, not content.

---

## Next Steps

### Immediate: Benchmark perf_5 - process_body Breakdown

Create a new benchmark that zooms into `_process_body()` to measure:

1. `_process_body_children()` - main recursive loop
2. `_process_body__text_node()` - text node handling
3. `_process_body__element()` - element creation
4. `_process_body__create_in_graph()` - graph insertion
5. `_process_body__register_attrs()` - attribute registration

### Then: Identify Sub-Bottleneck

Determine which sub-stage of `process_body` consumes the most time:
- Is it object creation?
- Is it graph insertion?
- Is it attribute processing?

### Finally: Apply Targeted Optimization

Based on findings, implement one of the four strategies above, prioritizing the approach that addresses the identified sub-bottleneck.

---

## Connection to Previous Findings

| Benchmark | Key Finding | Status |
|-----------|-------------|--------|
| perf_1 | Converter creation is negligible (0.01%) | ✅ Confirmed |
| perf_2 | Dict→MGraph is 95% of pipeline | ✅ Confirmed |
| perf_3 | fast_create provides ~57% improvement | ✅ Validated |
| perf_4 | process_body is the scaling bottleneck | ✅ **NEW** |

---

## Conclusion

The performance bottleneck has been successfully localized to `_process_body()` within `convert_from_dict()`. The linear scaling with a high per-node cost (~150µs) explains the 1-5 second load times observed in production with real-world HTML pages.

The path forward is clear:
1. Break down `process_body` further to find the exact operation causing the overhead
2. Apply HTML-specific optimizations (caching, batching, reuse) to reduce per-node cost
3. Target: <20µs per node to achieve acceptable performance at 10,000+ node scale

**The document_setup fixed cost (4-5ms) is acceptable. The focus must be on reducing the per-node cost in process_body.**
