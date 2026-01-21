# Profile Analyzer

A web-based UI for analyzing performance profiling data from the `@timestamp` decorator system.

## Quick Start

### Option 1: Local Development Server (Recommended)

Due to browser security restrictions on loading local files, you need a simple HTTP server:

```bash
# Using Python 3
cd profile-analyzer
python -m http.server 8080

# Using Node.js
npx serve .

# Using PHP
php -S localhost:8080
```

Then open http://localhost:8080 in your browser.

### Option 2: Static Hosting

Upload both files to any static hosting service (GitHub Pages, Netlify, Vercel, S3, etc.) and access via the provided URL.

## Usage

1. **Select Mode**: Use the Summary/Full toggle in the header
   - **Summary**: For `summary_*.json` files (hotspot analysis)
   - **Full**: For `full_*.json` files (complete traces with call trees)

2. **Load Files**: Drag and drop your JSON profiling files onto the drop zone

3. **Analyze**:
   - **Method Stats**: View aggregated statistics per method
   - **Per-Call Scaling**: Detect O(n) behavior by plotting avg time per call vs entry count
   - **Call Tree**: Explore the hierarchical execution trace

## Features

- Click chart lines to toggle visibility
- Hover for detailed tooltips
- Maximize charts for full-screen view
- Sort tables by clicking column headers
- Compare multiple profiles side-by-side

## Files

- `index.html` - Main HTML entry point
- `app.jsx` - React component (transformed by Babel in browser)

## Dependencies (loaded from CDN)

- React 18
- Recharts 2.10
- Babel Standalone (for JSX transformation)
