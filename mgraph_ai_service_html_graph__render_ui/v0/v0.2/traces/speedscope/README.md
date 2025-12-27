# Speedscope Analyzer

A browser-based visualization tool for Speedscope profiling data. Custom-built flame graph viewer with interactive features.

## Quick Start

```bash
cd speedscope-analyzer
python -m http.server 8080
# Open http://localhost:8080
```

Or use any static file server (Node's `npx serve`, PHP's built-in server, etc.)

## Features

### Flame Graph
- **Custom SVG implementation** - no D3 dependency
- **Click to zoom** into any span's time range
- **Double-click to focus** on a depth level (hides layers above)
- **Depth filter** - collapse top N layers to focus on deep calls
- **Hover** for detailed timing information
- **Maximize** button for full-screen analysis
- **Scrollable** for very deep call stacks

### Frame Stats
- Aggregated per-method statistics
- Total time, call count, avg/min/max per call
- Spread indicator (max/min ratio)
- Click bar chart or table to see call distribution

### Timeline
- Chronological call log
- Start/end/duration for each call

### Compare
- Multi-profile comparison (select 2+ profiles)
- Grouped bar charts
- Side-by-side statistics table

## Interactions

| Action | Result |
|--------|--------|
| Click span | Zoom to that span's time range |
| Click again | Reset zoom |
| Double-click span | Hide all levels above (focus) |
| Double-click again | Show all levels |
| Collapse top +/− | Incrementally hide/show top layers |
| ⊕ button | Maximize flame graph |
| ✕ or backdrop | Close maximized view |

## Speedscope Format

Expected JSON structure:

```json
{
  "shared": {
    "frames": [
      { "name": "method_name" }
    ]
  },
  "profiles": [{
    "type": "evented",
    "unit": "microseconds",
    "startValue": 0,
    "endValue": 1000,
    "events": [
      { "type": "O", "frame": 0, "at": 10 },
      { "type": "C", "frame": 0, "at": 100 }
    ]
  }]
}
```

- `O` = Open (method enter)
- `C` = Close (method exit)
- `frame` = Index into shared.frames array
- `at` = Timestamp in specified unit

## Dependencies (CDN)

- prop-types 15.8.1
- React 18
- ReactDOM 18
- Recharts 2.10.4
- Babel Standalone (for JSX transformation)
- Google Fonts: JetBrains Mono, Space Grotesk

## Generating Speedscope Files

Using `QA_Create_Html_Transformations`:

```python
with create_html_transformations as _:
    _.speedscope__for__html(html=html, html_type='my-test')
```

Or via `Timestamp_Collector`:

```python
_timestamp_collector_ = Timestamp_Collector(name="my_test")
with _timestamp_collector_:
    result = my_function()

speedscope_data = _timestamp_collector_.to_speedscope()
```

## File Naming

Files are identified by extracting a key from the filename:

| Filename | Key |
|----------|-----|
| `speedscope_____simple-html.json` | `simple-html` |
| `speedscope_____with_size__30.json` | `with_size__30` |

## Technical Notes

- Flame graph is pure SVG with React - no D3
- Colors assigned by frame index (consistent per method)
- All state managed in React hooks
- No build step required - Babel transforms JSX in browser
