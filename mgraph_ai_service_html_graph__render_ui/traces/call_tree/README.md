# Call Tree Visualizer

A Jaeger-style X-Ray visualization tool for call tree / execution trace data. Shows hierarchical method calls with timing bars.

## Quick Start

```bash
cd call-tree-visualizer
python -m http.server 8080
# Open http://localhost:8080
```

## Features

### Jaeger X-Ray Style View
- **Left column**: Expandable tree with method names
- **Right column**: Timeline bars showing relative timing
- **Duration labels**: Timing displayed next to each bar
- **Hotspot coloring**: Green→Yellow→Orange→Red based on self-time %

### Interactions
| Action | Result |
|--------|--------|
| Click ▶/▼ | Expand/collapse children |
| Hover row | Show detailed tooltip |
| Expand All | Show entire tree |
| Search | Filter methods by name |

### Hotspot Color Scale
| Color | Self-time % |
|-------|-------------|
| Teal | <1% |
| Green | 1-3% |
| Yellow | 3-8% |
| Orange | 8-15% |
| Red | >15% |

## Data Format

Expects `full_*.json` files with this structure:

```json
{
  "response_type": "full",
  "traces": {
    "metadata": {
      "total_duration_ms": 40.73,
      "entry_count": 468,
      "method_count": 30
    },
    "call_tree": [
      {
        "name": "method_name",
        "start_ns": 1000000,
        "end_ns": 2000000,
        "duration_ms": 1.0,
        "self_ms": 0.1,
        "depth": 0,
        "call_index": 0,
        "children": [...]
      }
    ]
  }
}
```

### Key Fields
| Field | Description |
|-------|-------------|
| `name` | Method identifier |
| `start_ns` / `end_ns` | Absolute timestamps in nanoseconds |
| `duration_ms` | Total time including children |
| `self_ms` | Time excluding children (hotspot indicator) |
| `depth` | Call stack depth |
| `call_index` | Execution order |
| `children` | Nested child calls |

## vs Flame Graph (Speedscope Analyzer)

| Aspect | Flame Graph | Call Tree Visualizer |
|--------|-------------|---------------------|
| Layout | Stacked by depth | One row per call |
| Labels | Inside bars | Separate column |
| Tree nav | None | Expand/collapse |
| Best for | "Where is time spent?" | "What is the exact call flow?" |

## Dependencies (CDN)

- prop-types 15.8.1
- React 18
- ReactDOM 18
- Babel Standalone
- Google Fonts: JetBrains Mono, Space Grotesk

## Technical Notes

- Pure React + CSS (no D3 or other chart libraries)
- Tree structure rendered recursively
- Filtering preserves tree structure (shows matching nodes + their children)
- Color based on self_ms percentage of total self time
