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

### Flame Graph Views

**Time Order** (default)
- Spans positioned by actual execution time
- Click to zoom into a span's time range
- Double-click to focus on a depth level

**Left Heavy** (aggregated)
- Spans aggregated by stack path
- Sorted by total time (heaviest on left)
- Great for identifying where time is actually spent
- Double-click to focus on a depth level

### Auto-collapse on Zoom

Enable the **Auto-collapse** checkbox for a powerful workflow:
- Click any span to zoom AND collapse all parent levels
- The clicked span becomes the visual "root"
- Only see that span and its descendants
- Click again or "Reset Zoom" to restore

### Other Features

- **Depth filter** - Collapse top N layers to focus on deep calls
- **Maximize** button for full-screen analysis
- **Scrollable** for very deep call stacks
- **Hover** for detailed timing information

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
| Click span (Time Order) | Zoom to that span's time range |
| Click same span again | Reset zoom |
| Double-click span | Hide all levels above (focus) |
| Double-click again | Show all levels |
| Auto-collapse + Click | Zoom AND collapse parents |
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

## File Naming

Files are identified by extracting a key from the filename:

| Filename | Key |
|----------|-----|
| `speedscope_____simple-html.json` | `simple-html` |
| `speedscope_____with_size__30.json` | `with_size__30` |

## Technical Notes

- Flame graph is pure SVG with React - no D3
- Left Heavy view aggregates by stack path, sorts by total time
- Colors assigned by frame index (consistent per method)
- All state managed in React hooks
- No build step required - Babel transforms JSX in browser
