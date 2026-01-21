# Call Tree Visualizer: LLM Brief

**Version**: v1.4.12 (proposed)  
**Date**: December 2025  
**Purpose**: Requirements specification for advanced call tree visualization tool  
**Context**: Extends Profile Analyzer with interactive graph/3D visualizations  
**Companion To**: `v1_4_11__profile-analyzer__llm-brief.md`, `v3_59_2__timestamp-capture__llm-usage-brief.md`

---

## Overview

Build an advanced visualization tool for call tree / execution trace data. This extends the existing Profile Analyzer with more visual and intuitive representations of code execution flow, enabling developers to explore performance characteristics through interactive graph networks and 3D visualizations.

**Core Goal**: Transform JSON trace data into visual, explorable representations that reveal execution patterns, hotspots, and performance regressions in ways that tables and 2D charts cannot.

---

## Data Source

The visualizer consumes **Full Trace files** (`full_*.json`) which contain:

```json
{
  "response_type": "full",
  "traces": {
    "metadata": {
      "total_duration_ms": 61.49,
      "entry_count": 930,
      "method_count": 31
    },
    "call_tree": [
      {
        "name": "method_name",
        "call_index": 0,
        "depth": 0,
        "duration_ms": 100.0,
        "self_ms": 5.0,
        "children": [
          { "name": "child_method", "call_index": 1, "depth": 1, ... }
        ]
      }
    ]
  }
}
```

**Key fields for visualization**:
- `name`: Method identifier (node label)
- `duration_ms`: Total time including children (node size/color)
- `self_ms`: Time excluding children (hotspot indicator)
- `children`: Nested structure (edges/connections)
- `call_index`: Execution order (animation sequencing)
- `depth`: Call stack depth (layout layering)

**Optional**: Hotspots data from summary files may be integrated for color-coding.

---

## Three Visualization Modes

### Mode 1: X-Ray / Jaeger-Style Timeline

**Inspiration**: Jaeger distributed tracing UI, AWS X-Ray

**Concept**: Horizontal timeline with nested spans showing execution flow as boxes/bars.

```
┌─────────────────────────────────────────────────────────────────┐
│ process() ██████████████████████████████████████████████████████│
│   ├─ parse() ████████████████                                   │
│   │    └─ tokenize() ██████████                                 │
│   └─ transform() ████████████████████████████████               │
│        ├─ validate() ████████                                   │
│        └─ output() ██████████████████                           │
└─────────────────────────────────────────────────────────────────┘
         0ms        20ms        40ms        60ms        80ms
```

**Features**:
- Time flows left-to-right
- Bar width = duration
- Nesting shows call hierarchy
- Color intensity = self-time (hotspot indicator)
- Hover for details
- Click to zoom into subtree

**Use Case**: Understanding temporal execution flow and identifying where time is spent.

---

### Mode 2: Network Graph

**Inspiration**: D3 force-directed graphs, dependency visualizations

**Concept**: Nodes represent methods, edges represent calls, layout reveals structure.

```
                    ┌─────────┐
                    │ process │
                    └────┬────┘
              ┌─────────┼─────────┐
              ▼         ▼         ▼
         ┌────────┐ ┌────────┐ ┌────────┐
         │ parse  │ │transform│ │ output │
         └───┬────┘ └────┬───┘ └────────┘
             ▼          ▼
        ┌────────┐ ┌────────┐
        │tokenize│ │validate│
        └────────┘ └────────┘
```

**Features**:
- Node size = call count or total duration
- Node color = self-time percentage (hotspot heat map)
- Edge thickness = call frequency
- Force-directed or hierarchical layout options
- Zoom/pan navigation
- Click node to focus/expand
- Animated execution flow (particles along edges)

**Recommended Library**: D3.js (handles large datasets well)

**Use Case**: Understanding call relationships and identifying central/hot methods.

---

### Mode 3: 3D Visualization

**Inspiration**: Code city visualizations, 3D dependency graphs

**Concept**: Three-dimensional representation enabling spatial exploration of execution.

**Possible Metaphors**:

**Option A - 3D Tree/Forest**:
- Y-axis = call depth
- X/Z plane = method grouping
- Height/size = duration
- Color = performance (green→red gradient)

**Option B - Code City**:
- Buildings = methods
- Building height = duration or call count
- Building color = self-time
- Districts = call tree branches

**Option C - 3D Force Graph**:
- Nodes floating in 3D space
- Edges as connections
- Camera fly-through navigation

**Features**:
- Rotate, zoom, pan with mouse/touch
- Click to focus on method
- Isolate subtrees
- Performance heat map coloring
- Fly-through animation of execution order

**Recommended Library**: Three.js (or react-three-fiber for React integration)

**Use Case**: Exploring large call trees, finding patterns not visible in 2D, impressive demos.

---

## View Variants (All Modes)

Each visualization mode should support these view variants:

### 1. Overview
- Full call tree visible
- Zoomed out for structure comprehension
- Good starting point

### 2. Performance Heat Map
- Color-coded by timing metrics
- Options: self_ms, duration_ms, ms/call
- Gradient: green (fast) → yellow → red (slow)
- Highlights hotspots visually

### 3. Hotspot Focus
- Derived from self_ms percentages
- Top N methods emphasized
- Others faded/minimized
- Quick identification of optimization targets

### 4. Method Zoom
- Click to focus on specific method
- Shows that method's subtree only
- "View from this method's perspective"
- Breadcrumb navigation back up

---

## Comparison Features

### Scenario A: Different Input Sizes

**Use Case**: Comparing traces from `with_size__10` vs `with_size__50` vs `with_size__100`

**Characteristics**:
- Different node counts
- Different edge counts
- Goal: Understand how structure scales

**Visualization Approach**:
- Side-by-side views
- Synchronized zoom/pan
- Highlight methods present in all vs unique to larger inputs

---

### Scenario B: Before/After Optimization

**Use Case**: Same code path, before and after a fix

**Characteristics**:
- Same or very similar structure
- Different durations
- Goal: Identify improvements and regressions

**Visualization Approach**:
- Overlay or diff view
- Color by delta: green = faster, red = slower
- Numerical annotations showing % change
- Summary: "Total: -25% | Hotspot X: -80% | Method Y: +5%"

**UI Expectation**: Designed for equivalent graphs, focuses on duration comparison rather than structural differences.

---

## Architecture Recommendation

### Component Structure

Given the independence of each visualization mode, recommend **multiple smaller React components**:

```
CallTreeVisualizer/
├── index.jsx                    # Main container, mode switching, data loading
├── components/
│   ├── XRayTimeline.jsx         # Mode 1: Jaeger-style
│   ├── NetworkGraph.jsx         # Mode 2: D3 force graph
│   ├── ThreeDView.jsx           # Mode 3: Three.js
│   ├── ComparisonPanel.jsx      # Side-by-side/diff logic
│   └── shared/
│       ├── ColorLegend.jsx      # Reusable heat map legend
│       ├── MethodTooltip.jsx    # Hover details
│       ├── ViewControls.jsx     # Zoom, reset, layout options
│       └── DataLoader.jsx       # Drag-drop, file handling
├── hooks/
│   ├── useCallTreeData.js       # Data parsing/transformation
│   ├── useHotspots.js           # Hotspot calculation
│   └── useComparison.js         # Diff calculation
└── utils/
    ├── treeTransforms.js        # Flatten, filter, aggregate
    └── colorScales.js           # Performance gradients
```

**Rationale**:
- Each mode is visually and technically distinct
- Independent iteration on each visualization
- Easier testing and debugging
- Clear separation of D3 vs Three.js concerns
- Shared utilities prevent duplication

### Integration Options

**Option 1**: Standalone tool (like current Profile Analyzer)
- Separate `index.html` + components
- Independent deployment

**Option 2**: Tab in existing Profile Analyzer
- Add "Visualize" mode alongside Summary/Full
- Share file loading infrastructure
- Unified experience

**Recommendation**: Start as standalone, integrate later if valuable.

---

## Technical Considerations

### D3.js (Network Graph)
- Handles 1000s of nodes efficiently
- Force simulation for layout
- SVG or Canvas rendering
- Learning curve but very flexible

### Three.js (3D View)
- WebGL-based, hardware accelerated
- Camera controls (OrbitControls)
- Can handle complex scenes
- Consider react-three-fiber for React integration

### Performance
- Large traces may have 10,000+ nodes
- Consider:
  - Level-of-detail (collapse deep branches)
  - Virtualization (render visible only)
  - Web Workers for layout calculation
  - Canvas over SVG for very large graphs

---

## Data Requirements

### Minimum Viable
- Single `full_*.json` file with `call_tree`

### Enhanced
- Multiple files for comparison
- `summary_*.json` for pre-calculated hotspots
- `create_stats_*.json` for input metadata

### Derived Calculations
From call_tree, calculate:
- Total calls per method
- Aggregate self_ms per method
- Max depth reached
- Execution order sequence
- Hotspot rankings (top N by self_ms %)

---

## Interaction Patterns

| Action | Result |
|--------|--------|
| Hover node | Show tooltip with method details |
| Click node | Focus/zoom to that method's subtree |
| Double-click | Expand/collapse children |
| Scroll | Zoom in/out |
| Drag | Pan (2D) or rotate (3D) |
| Right-click | Context menu: isolate, hide, highlight |
| Keyboard `R` | Reset view to overview |
| Keyboard `H` | Toggle hotspot highlighting |

---

## Success Criteria

1. **Functional**: All three modes render call tree data correctly
2. **Performant**: Handles traces with 1000+ nodes smoothly
3. **Insightful**: Hotspots visually obvious without reading numbers
4. **Comparable**: Before/after differences immediately apparent
5. **Explorable**: Can zoom from overview to specific method easily
6. **Beautiful**: Visually impressive, suitable for demos and presentations

---

## Open Questions for Implementation

1. **Library choice for 3D**: Three.js directly vs react-three-fiber?
2. **Layout algorithm for network**: Force-directed vs hierarchical tree vs radial?
3. **Animation priority**: Execution flow animation (particles) vs static + hover?
4. **Comparison UX**: Side-by-side vs overlay vs toggle?
5. **Color scheme**: Match Profile Analyzer (teal accent) or distinct palette?

---

## Summary

Build a three-mode visualization tool for call tree data:

| Mode | Library | Strength |
|------|---------|----------|
| X-Ray Timeline | D3 / SVG | Temporal understanding |
| Network Graph | D3 | Relationship understanding |
| 3D View | Three.js | Exploration, wow factor |

Support both structural exploration (different sizes) and performance comparison (before/after).

Use modular React architecture for maintainability and independent iteration on each visualization mode.

---

*Brief generated from requirements discussion, December 2025*
