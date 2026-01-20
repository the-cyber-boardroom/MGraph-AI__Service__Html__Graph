// Speedscope Analyzer - Browser-compatible version
// Uses global React and Recharts from CDN

const { useState, useCallback, useMemo, useEffect } = React;
const { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } = Recharts;

const extractProfileKey = (filename) => {
  let name = filename.replace(/\.json$/, '').replace(/_json$/, '');
  name = name.replace(/^(speedscope)[_]+/, '');
  name = name.replace(/^_+|_+$/g, '');
  return name || filename;
};

const processSpeedscopeEvents = (profile, frames) => {
  const events = profile.events || [];
  const unit = profile.unit || 'microseconds';
  const unitMultiplier = unit === 'nanoseconds' ? 0.000001 : unit === 'microseconds' ? 0.001 : 1;
  
  const spans = [];
  const stack = [];
  
  events.forEach(event => {
    const frameName = frames[event.frame]?.name || `frame_${event.frame}`;
    const timeMs = event.at * unitMultiplier;
    
    if (event.type === 'O') {
      // Capture current stack path for this span
      const stackPath = stack.map(s => s.frame).concat(event.frame);
      stack.push({ frame: event.frame, name: frameName, startMs: timeMs, depth: stack.length, stackPath });
    } else if (event.type === 'C') {
      for (let i = stack.length - 1; i >= 0; i--) {
        if (stack[i].frame === event.frame) {
          const opened = stack.splice(i, 1)[0];
          spans.push({
            name: opened.name, frame: opened.frame, startMs: opened.startMs,
            endMs: timeMs, durationMs: timeMs - opened.startMs, depth: opened.depth,
            stackPath: opened.stackPath
          });
          break;
        }
      }
    }
  });
  return spans;
};

// Build Left Heavy aggregated tree from spans
const buildLeftHeavyTree = (spans, totalDurationMs) => {
  if (!spans.length) return [];
  
  // Build tree structure by aggregating spans with same stack path
  const root = { name: 'root', children: new Map(), totalMs: 0, frame: -1 };
  
  spans.forEach(span => {
    let current = root;
    const path = span.stackPath || [span.frame];
    
    path.forEach((frameId, depth) => {
      if (!current.children.has(frameId)) {
        current.children.set(frameId, {
          name: span.name,
          frame: frameId,
          children: new Map(),
          totalMs: 0,
          selfMs: 0,
          depth: depth
        });
      }
      current = current.children.get(frameId);
      // Only add duration at the leaf level (the actual span's depth)
      if (depth === path.length - 1) {
        current.totalMs += span.durationMs;
        current.name = span.name; // Ensure correct name
      }
    });
  });
  
  // Convert Map children to sorted arrays and calculate positions
  const convertNode = (node, parentTotalMs) => {
    const children = Array.from(node.children.values())
      .map(child => convertNode(child, node.totalMs || parentTotalMs))
      .sort((a, b) => b.totalMs - a.totalMs); // Sort by total time descending (heaviest left)
    
    return {
      name: node.name,
      frame: node.frame,
      totalMs: node.totalMs,
      depth: node.depth,
      children
    };
  };
  
  // Get root children and convert
  const rootChildren = Array.from(root.children.values())
    .map(child => convertNode(child, totalDurationMs))
    .sort((a, b) => b.totalMs - a.totalMs);
  
  return rootChildren;
};

// Flatten Left Heavy tree into renderable rectangles
const flattenLeftHeavyTree = (tree, totalDurationMs) => {
  const rects = [];
  
  const traverse = (node, xOffset, parentWidth, depth) => {
    const width = parentWidth * (node.totalMs / (depth === 0 ? totalDurationMs : node.totalMs));
    const actualWidth = depth === 0 ? (node.totalMs / totalDurationMs) : parentWidth;
    
    rects.push({
      name: node.name,
      frame: node.frame,
      depth: depth,
      totalMs: node.totalMs,
      xStart: xOffset,
      width: actualWidth
    });
    
    // Layout children
    let childX = xOffset;
    const childParentWidth = actualWidth;
    node.children.forEach(child => {
      const childWidth = childParentWidth * (child.totalMs / node.totalMs);
      traverse(child, childX, childWidth, depth + 1);
      childX += childWidth;
    });
  };
  
  let xOffset = 0;
  tree.forEach(rootNode => {
    const nodeWidth = rootNode.totalMs / totalDurationMs;
    traverse(rootNode, xOffset, nodeWidth, 0);
    xOffset += nodeWidth;
  });
  
  return rects;
};

const aggregateFrameStats = (spans) => {
  const byFrame = {};
  spans.forEach(span => {
    if (!byFrame[span.name]) {
      byFrame[span.name] = { name: span.name, frame: span.frame, calls: [], count: 0, totalMs: 0 };
    }
    byFrame[span.name].calls.push(span);
    byFrame[span.name].count++;
    byFrame[span.name].totalMs += span.durationMs;
  });
  
  return Object.values(byFrame)
    .map(f => ({
      ...f,
      avgMs: f.totalMs / f.count,
      minMs: Math.min(...f.calls.map(c => c.durationMs)),
      maxMs: Math.max(...f.calls.map(c => c.durationMs)),
      spread: f.calls.length > 1 ? Math.max(...f.calls.map(c => c.durationMs)) / Math.min(...f.calls.map(c => c.durationMs)) : 1
    }))
    .sort((a, b) => b.totalMs - a.totalMs);
};

const processSpeedscopeFiles = (files) => {
  return files
    .filter(f => f.data && (f.data.profiles || f.data.$schema?.includes('speedscope')))
    .map(f => {
      const key = extractProfileKey(f.name);
      const frames = f.data.shared?.frames || [];
      const profile = f.data.profiles?.[0] || {};
      const spans = processSpeedscopeEvents(profile, frames);
      const frameStats = aggregateFrameStats(spans);
      const totalDurationMs = profile.endValue 
        ? profile.endValue * (profile.unit === 'nanoseconds' ? 0.000001 : profile.unit === 'microseconds' ? 0.001 : 1)
        : (spans.length ? Math.max(...spans.map(s => s.endMs)) : 0);
      
      // Pre-compute Left Heavy tree
      const leftHeavyTree = buildLeftHeavyTree(spans, totalDurationMs);
      
      return {
        key, name: f.data.name || key, raw: f.data, frames, profile, spans, frameStats,
        totalDurationMs, eventCount: profile.events?.length || 0, frameCount: frames.length,
        leftHeavyTree
      };
    });
};

function SpeedscopeAnalyzer() {
  const [files, setFiles] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const [selectedKeys, setSelectedKeys] = useState(new Set());
  const [activeTab, setActiveTab] = useState('flame');
  const [expandedChart, setExpandedChart] = useState(false);
  const [depthOffset, setDepthOffset] = useState(0);
  const [flameMode, setFlameMode] = useState('timeOrder'); // 'timeOrder' or 'leftHeavy'
  const [autoCollapseOnZoom, setAutoCollapseOnZoom] = useState(true);
  const [zoomRange, setZoomRange] = useState(null);

  // =========================================================================
  // TRACE DATA RECEIVER - Listen for data from parent Sample Loader
  // =========================================================================
  useEffect(() => {
    const handleMessage = (event) => {
      if (event.data?.type === 'LOAD_TRACE_DATA') {
        const { name, data } = event.data.payload;
        console.log('[Speedscope] Received trace data:', name);

        // The API returns { graph, response_type, traces } where traces is a JSON string
        // We need to parse the traces string to get the actual speedscope data
        let speedscopeData = data;
        if (data.traces && typeof data.traces === 'string') {
          try {
            speedscopeData = JSON.parse(data.traces);
            console.log('[Speedscope] Parsed traces string');
          } catch (e) {
            console.error('[Speedscope] Failed to parse traces:', e);
          }
        }

        const fileName = `speedscope_${name}.json`;
        const newFile = { name: fileName, data: speedscopeData };
        console.log('[Speedscope] with data', speedscopeData);

        setFiles(prev => {
          const existing = new Set(prev.map(f => f.name));
          if (existing.has(fileName)) {
            return prev.map(f => f.name === fileName ? newFile : f);
          }
          return [...prev, newFile];
        });

        // Auto-select the new profile
        setTimeout(() => {
          const key = extractProfileKey(fileName);
          setSelectedKeys(new Set([key]));
        }, 50);
      }
    };

    window.addEventListener('message', handleMessage);

    // Notify parent we're ready
    if (window.parent !== window) {
      window.parent.postMessage({ type: 'VISUALIZER_READY', visualizer: 'speedscope' }, '*');
    }

    return () => window.removeEventListener('message', handleMessage);
  }, []);
  // =========================================================================

  const profiles = useMemo(() => processSpeedscopeFiles(files), [files]);
  
  useEffect(() => {
    if (profiles.length > 0 && selectedKeys.size === 0) {
      setSelectedKeys(new Set([profiles[0].key]));
    }
  }, [profiles]);

  // Reset depth offset and zoom when switching profiles
  useEffect(() => {
    setDepthOffset(0);
    setZoomRange(null);
  }, [selectedKeys]);

  const selectedProfiles = useMemo(() => 
    profiles.filter(p => selectedKeys.has(p.key)),
    [profiles, selectedKeys]
  );

  const handleDrop = useCallback(async (e) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFiles = Array.from(e.dataTransfer.files).filter(f => 
      f.name.endsWith('.json') || f.name.endsWith('_json')
    );
    const newFiles = await Promise.all(droppedFiles.map(async (file) => {
      const text = await file.text();
      try { return { name: file.name, data: JSON.parse(text) }; }
      catch { return null; }
    }));
    setFiles(prev => {
      const existing = new Set(prev.map(f => f.name));
      return [...prev, ...newFiles.filter(f => f && !existing.has(f.name))];
    });
  }, []);

  const handleProfileClick = (key) => {
    if (['flame', 'stats', 'timeline'].includes(activeTab)) {
      setSelectedKeys(new Set([key]));
    } else {
      setSelectedKeys(prev => {
        const next = new Set(prev);
        next.has(key) ? next.delete(key) : next.add(key);
        return next;
      });
    }
  };

  const colors = ['#4ecdc4', '#ff6b6b', '#ffe66d', '#95e1d3', '#f38181', '#aa96da', '#74b9ff', '#fd79a8', '#a29bfe', '#ffeaa7', '#dfe6e9', '#00b894'];

  // Flame Graph Component
  const FlameGraph = ({ profile, isExpanded = false }) => {
    const [hoveredSpan, setHoveredSpan] = useState(null);

    if (!profile || !profile.spans.length) {
      return React.createElement('div', { className: 'empty-state' }, 'No flame graph data available');
    }

    const spans = profile.spans;
    const maxDepth = Math.max(...spans.map(s => s.depth)) + 1;
    
    const rowHeight = isExpanded ? 26 : 24;
    const visibleMaxDepth = Math.max(1, maxDepth - depthOffset);
    const graphHeight = Math.min(isExpanded ? 800 : 600, Math.max(200, visibleMaxDepth * rowHeight + 50));
    const graphWidth = isExpanded ? window.innerWidth - 100 : window.innerWidth - 320;
    
    const getSpanColor = (span) => colors[span.frame % colors.length];

    // Time Order rendering
    const renderTimeOrder = () => {
      const effectiveRange = zoomRange || { start: 0, end: profile.totalDurationMs };
      const timeRange = effectiveRange.end - effectiveRange.start;
      
      const timeToX = (t) => ((t - effectiveRange.start) / timeRange) * graphWidth + 20;
      const durationToWidth = (d) => (d / timeRange) * graphWidth;

      const visibleSpans = spans.filter(s => 
        s.endMs > effectiveRange.start && 
        s.startMs < effectiveRange.end &&
        s.depth >= depthOffset
      );

      const handleSpanClick = (span, e) => {
        if (e.detail === 2) {
          e.stopPropagation();
          setDepthOffset(prev => prev === span.depth ? 0 : span.depth);
        } else {
          if (zoomRange && Math.abs(zoomRange.start - span.startMs) < 0.001 && Math.abs(zoomRange.end - span.endMs) < 0.001) {
            setZoomRange(null);
            if (autoCollapseOnZoom) setDepthOffset(0);
          } else {
            setZoomRange({ start: span.startMs, end: span.endMs });
            if (autoCollapseOnZoom) setDepthOffset(span.depth);
          }
        }
      };

      return (
        <>
          <g className="time-axis">
            {[0, 0.25, 0.5, 0.75, 1].map((pct, i) => {
              const x = 20 + pct * graphWidth;
              const time = effectiveRange.start + pct * timeRange;
              return (
                <g key={i}>
                  <line x1={x} y1={0} x2={x} y2={graphHeight - 25} stroke="#333" strokeDasharray="2,2" />
                  <text x={x} y={graphHeight - 8} fill="#666" fontSize="10" textAnchor="middle">
                    {time.toFixed(2)}ms
                  </text>
                </g>
              );
            })}
          </g>
          
          {visibleSpans.map((span, i) => {
            const x = Math.max(20, timeToX(span.startMs));
            const rawWidth = durationToWidth(span.durationMs);
            const width = Math.min(rawWidth, graphWidth + 20 - x);
            const y = (span.depth - depthOffset) * rowHeight;
            const isHovered = hoveredSpan === i;
            
            if (width < 0.5 || y < 0) return null;
            
            return (
              <g key={i} 
                 onMouseEnter={() => setHoveredSpan(i)}
                 onMouseLeave={() => setHoveredSpan(null)}
                 onClick={(e) => handleSpanClick(span, e)}
                 style={{ cursor: 'pointer' }}>
                <rect
                  x={x} y={y} width={Math.max(1, width)} height={rowHeight - 2}
                  fill={getSpanColor(span)}
                  opacity={isHovered ? 1 : 0.85}
                  stroke={isHovered ? '#fff' : '#0005'}
                  strokeWidth={isHovered ? 2 : 0.5}
                  rx={2}
                />
                {width > 35 && (
                  <text x={x + 4} y={y + rowHeight / 2 + 4} fill="#000" fontSize="11"
                    fontFamily="'JetBrains Mono', monospace" style={{ pointerEvents: 'none' }}>
                    {span.name.length > width / 6.5 ? span.name.slice(0, Math.floor(width / 6.5) - 2) + '..' : span.name}
                  </text>
                )}
              </g>
            );
          })}
        </>
      );
    };

    // Left Heavy rendering
    const renderLeftHeavy = () => {
      const leftHeavyRects = useMemo(() => 
        flattenLeftHeavyTree(profile.leftHeavyTree, profile.totalDurationMs),
        [profile.leftHeavyTree, profile.totalDurationMs]
      );

      const visibleRects = leftHeavyRects.filter(r => r.depth >= depthOffset);

      const handleRectClick = (rect, e) => {
        if (e.detail === 2) {
          e.stopPropagation();
          setDepthOffset(prev => prev === rect.depth ? 0 : rect.depth);
        }
      };

      return (
        <>
          <g className="time-axis">
            {[0, 0.25, 0.5, 0.75, 1].map((pct, i) => {
              const x = 20 + pct * graphWidth;
              const time = pct * profile.totalDurationMs;
              return (
                <g key={i}>
                  <line x1={x} y1={0} x2={x} y2={graphHeight - 25} stroke="#333" strokeDasharray="2,2" />
                  <text x={x} y={graphHeight - 8} fill="#666" fontSize="10" textAnchor="middle">
                    {time.toFixed(2)}ms
                  </text>
                </g>
              );
            })}
          </g>
          
          {visibleRects.map((rect, i) => {
            const x = 20 + rect.xStart * graphWidth;
            const width = rect.width * graphWidth;
            const y = (rect.depth - depthOffset) * rowHeight;
            const isHovered = hoveredSpan === i;
            
            if (width < 0.5 || y < 0) return null;
            
            return (
              <g key={i} 
                 onMouseEnter={() => setHoveredSpan(i)}
                 onMouseLeave={() => setHoveredSpan(null)}
                 onClick={(e) => handleRectClick(rect, e)}
                 style={{ cursor: 'pointer' }}>
                <rect
                  x={x} y={y} width={Math.max(1, width)} height={rowHeight - 2}
                  fill={colors[rect.frame % colors.length]}
                  opacity={isHovered ? 1 : 0.85}
                  stroke={isHovered ? '#fff' : '#0005'}
                  strokeWidth={isHovered ? 2 : 0.5}
                  rx={2}
                />
                {width > 35 && (
                  <text x={x + 4} y={y + rowHeight / 2 + 4} fill="#000" fontSize="11"
                    fontFamily="'JetBrains Mono', monospace" style={{ pointerEvents: 'none' }}>
                    {rect.name.length > width / 6.5 ? rect.name.slice(0, Math.floor(width / 6.5) - 2) + '..' : rect.name}
                  </text>
                )}
              </g>
            );
          })}
        </>
      );
    };

    // Get hovered data for tooltip
    const getHoveredData = () => {
      if (hoveredSpan === null) return null;
      
      if (flameMode === 'timeOrder') {
        const effectiveRange = zoomRange || { start: 0, end: profile.totalDurationMs };
        const visibleSpans = spans.filter(s => 
          s.endMs > effectiveRange.start && 
          s.startMs < effectiveRange.end &&
          s.depth >= depthOffset
        );
        return visibleSpans[hoveredSpan];
      } else {
        const leftHeavyRects = flattenLeftHeavyTree(profile.leftHeavyTree, profile.totalDurationMs);
        const visibleRects = leftHeavyRects.filter(r => r.depth >= depthOffset);
        return visibleRects[hoveredSpan];
      }
    };

    const hoveredData = getHoveredData();

    return (
      <div className="flame-graph-container">
        <div className="flame-graph-header">
          <div className="flame-graph-controls">
            <div className="view-toggle">
              <button 
                className={`toggle-btn ${flameMode === 'timeOrder' ? 'active' : ''}`}
                onClick={() => { setFlameMode('timeOrder'); setHoveredSpan(null); }}
              >
                Time Order
              </button>
              <button 
                className={`toggle-btn ${flameMode === 'leftHeavy' ? 'active' : ''}`}
                onClick={() => { setFlameMode('leftHeavy'); setHoveredSpan(null); setZoomRange(null); setDepthOffset(0); }}
              >
                Left Heavy
              </button>
            </div>
            <div className="depth-control">
              <span className="depth-label">Collapse top:</span>
              <button className="depth-btn" onClick={() => setDepthOffset(Math.max(0, depthOffset - 1))} disabled={depthOffset === 0}>−</button>
              <span className="depth-value">{depthOffset}</span>
              <button className="depth-btn" onClick={() => setDepthOffset(Math.min(maxDepth - 1, depthOffset + 1))} disabled={depthOffset >= maxDepth - 1}>+</button>
            </div>
            {depthOffset > 0 && (
              <button className="ctrl-btn" onClick={() => setDepthOffset(0)}>Show All ({depthOffset} hidden)</button>
            )}
            {flameMode === 'timeOrder' && zoomRange && (
              <button className="ctrl-btn" onClick={() => { setZoomRange(null); if (autoCollapseOnZoom) setDepthOffset(0); }}>Reset Zoom</button>
            )}
            <label className="auto-collapse-toggle" title="When enabled, clicking a span will collapse all parent levels">
              <input 
                type="checkbox" 
                checked={autoCollapseOnZoom} 
                onChange={(e) => setAutoCollapseOnZoom(e.target.checked)} 
              />
              <span>Auto-collapse</span>
            </label>
            <span className="flame-hint">
              {flameMode === 'timeOrder' ? 'Click=zoom · Double-click=focus level' : 'Double-click=focus level'}
            </span>
          </div>
          {!isExpanded && (
            <button className="expand-btn" onClick={() => setExpandedChart(true)} title="Maximize">⊕</button>
          )}
          {isExpanded && (
            <button className="expand-btn close" onClick={() => setExpandedChart(false)} title="Close">✕</button>
          )}
        </div>
        
        <div className="flame-graph-scroll">
          <svg width={graphWidth + 40} height={graphHeight} className="flame-graph-svg">
            {flameMode === 'timeOrder' ? renderTimeOrder() : renderLeftHeavy()}
          </svg>
        </div>
        
        <div className={`flame-tooltip ${hoveredData ? 'visible' : ''}`}>
          {hoveredData ? (
            <>
              <div className="tooltip-method">
                <span className="tooltip-color" style={{ background: colors[hoveredData.frame % colors.length] }} />
                <strong>{hoveredData.name}</strong>
              </div>
              <div className="tooltip-values">
                <span>
                  {flameMode === 'timeOrder' ? 'Duration' : 'Total Time'}: 
                  <strong> {(hoveredData.durationMs || hoveredData.totalMs).toFixed(3)}ms</strong>
                </span>
                {flameMode === 'timeOrder' && <span>Start: {hoveredData.startMs.toFixed(3)}ms</span>}
                {flameMode === 'leftHeavy' && <span>({((hoveredData.totalMs / profile.totalDurationMs) * 100).toFixed(1)}% of total)</span>}
                <span>Depth: {hoveredData.depth}</span>
              </div>
            </>
          ) : (
            <div className="tooltip-hint">Hover over a span to see details</div>
          )}
        </div>
      </div>
    );
  };

  // Fullscreen Overlay
  const renderExpandedOverlay = () => {
    if (!expandedChart) return null;
    const profile = selectedProfiles[0];
    
    return (
      <div className="chart-overlay" onClick={(e) => e.target.className === 'chart-overlay' && setExpandedChart(false)}>
        <div className="chart-overlay-content">
          <FlameGraph profile={profile} isExpanded={true} />
        </div>
      </div>
    );
  };

  // Frame Stats View
  const FrameStatsView = ({ profile }) => {
    const [sortField, setSortField] = useState('totalMs');
    const [sortAsc, setSortAsc] = useState(false);
    const [selectedFrame, setSelectedFrame] = useState(null);

    if (!profile) return <div className="empty-state">Select a profile to view frame statistics</div>;

    const stats = profile.frameStats;
    const sortedStats = [...stats].sort((a, b) => (sortAsc ? 1 : -1) * (a[sortField] - b[sortField]));
    const handleSort = (field) => {
      if (sortField === field) setSortAsc(!sortAsc);
      else { setSortField(field); setSortAsc(false); }
    };
    const selectedFrameData = selectedFrame ? stats.find(s => s.name === selectedFrame) : null;

    return (
      <div className="view-content">
        <h2>Frame Statistics</h2>
        <div className="metrics-row">
          <div className="metric-card"><span className="metric-value">{profile.totalDurationMs.toFixed(2)}</span><span className="metric-label">Total ms</span></div>
          <div className="metric-card"><span className="metric-value">{profile.frameCount}</span><span className="metric-label">Frames</span></div>
          <div className="metric-card"><span className="metric-value">{profile.eventCount}</span><span className="metric-label">Events</span></div>
          <div className="metric-card"><span className="metric-value">{profile.spans.length}</span><span className="metric-label">Calls</span></div>
        </div>

        <div className="chart-section">
          <h3>Top Frames by Total Time</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={sortedStats.slice(0, 15)} layout="vertical" margin={{ left: 180, right: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis type="number" stroke="#888" tickFormatter={v => `${v.toFixed(1)}ms`} />
              <YAxis type="category" dataKey="name" stroke="#888" tick={{ fontSize: 11 }} width={170} />
              <Tooltip contentStyle={{ background: '#1a1a1a', border: '1px solid #333' }} formatter={(v) => [`${v.toFixed(3)}ms`]} />
              <Bar animationDuration={150} dataKey="totalMs" fill="#4ecdc4" onClick={(data) => setSelectedFrame(data.name)} cursor="pointer" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {selectedFrameData && (
          <div className="chart-section">
            <h3>Call Distribution: {selectedFrameData.name}</h3>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={selectedFrameData.calls.map((c, i) => ({ index: i + 1, durationMs: c.durationMs }))}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis dataKey="index" stroke="#888" />
                <YAxis stroke="#888" tickFormatter={v => `${v.toFixed(2)}ms`} />
                <Tooltip contentStyle={{ background: '#1a1a1a', border: '1px solid #333' }} formatter={(v) => [`${v.toFixed(4)}ms`]} />
                <Line animationDuration={150} type="monotone" dataKey="durationMs" stroke="#4ecdc4" strokeWidth={2} dot={{ fill: '#4ecdc4', r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        <div className="table-section">
          <h3>Frame Statistics</h3>
          <table className="data-table">
            <thead>
              <tr>
                <th>Frame</th>
                <th className="sortable" onClick={() => handleSort('count')}>Calls {sortField === 'count' && (sortAsc ? '↑' : '↓')}</th>
                <th className="sortable" onClick={() => handleSort('totalMs')}>Total ms {sortField === 'totalMs' && (sortAsc ? '↑' : '↓')}</th>
                <th className="sortable" onClick={() => handleSort('avgMs')}>Avg ms {sortField === 'avgMs' && (sortAsc ? '↑' : '↓')}</th>
                <th>Min</th><th>Max</th>
                <th className="sortable" onClick={() => handleSort('spread')}>Spread {sortField === 'spread' && (sortAsc ? '↑' : '↓')}</th>
              </tr>
            </thead>
            <tbody>
              {sortedStats.map((stat, i) => (
                <tr key={i} onClick={() => setSelectedFrame(stat.name)} className={selectedFrame === stat.name ? 'row-selected' : ''} style={{ cursor: 'pointer' }}>
                  <td className="method-name"><span className="method-color-dot" style={{ background: colors[stat.frame % colors.length] }} />{stat.name}</td>
                  <td>{stat.count}</td><td>{stat.totalMs.toFixed(3)}</td><td>{stat.avgMs.toFixed(4)}</td>
                  <td>{stat.minMs.toFixed(4)}</td><td>{stat.maxMs.toFixed(4)}</td><td>{stat.spread.toFixed(1)}x</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  // Timeline View
  const TimelineView = ({ profile }) => {
    if (!profile) return <div className="empty-state">Select a profile to view timeline</div>;
    const events = profile.profile.events || [];
    const frames = profile.frames;
    const unit = profile.profile.unit || 'microseconds';
    const unitMultiplier = unit === 'nanoseconds' ? 0.000001 : unit === 'microseconds' ? 0.001 : 1;

    const timelineData = [];
    const openFrames = new Map();
    events.forEach((event) => {
      const frameName = frames[event.frame]?.name || `frame_${event.frame}`;
      const timeMs = event.at * unitMultiplier;
      if (event.type === 'O') openFrames.set(event.frame, { start: timeMs, name: frameName });
      else if (event.type === 'C' && openFrames.has(event.frame)) {
        const open = openFrames.get(event.frame);
        timelineData.push({ name: frameName, frame: event.frame, start: open.start, end: timeMs, duration: timeMs - open.start });
        openFrames.delete(event.frame);
      }
    });
    timelineData.sort((a, b) => a.start - b.start);

    return (
      <div className="view-content">
        <h2>Event Timeline</h2>
        <div className="metrics-row">
          <div className="metric-card"><span className="metric-value">{events.length}</span><span className="metric-label">Events</span></div>
          <div className="metric-card"><span className="metric-value">{timelineData.length}</span><span className="metric-label">Completed Calls</span></div>
          <div className="metric-card"><span className="metric-value">{profile.totalDurationMs.toFixed(2)}</span><span className="metric-label">Duration ms</span></div>
        </div>
        <div className="table-section">
          <h3>Call Log (First 50)</h3>
          <table className="data-table">
            <thead><tr><th>#</th><th>Frame</th><th>Start ms</th><th>End ms</th><th>Duration ms</th></tr></thead>
            <tbody>
              {timelineData.slice(0, 50).map((call, i) => (
                <tr key={i}>
                  <td>{i + 1}</td>
                  <td className="method-name"><span className="method-color-dot" style={{ background: colors[call.frame % colors.length] }} />{call.name}</td>
                  <td>{call.start.toFixed(3)}</td><td>{call.end.toFixed(3)}</td><td>{call.duration.toFixed(4)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  // Comparison View
  const ComparisonView = ({ profiles }) => {
    if (profiles.length < 2) return <div className="empty-state">Select 2+ profiles to compare</div>;
    const frameNames = new Set();
    profiles.forEach(p => p.frameStats.forEach(f => frameNames.add(f.name)));
    
    const comparisonData = Array.from(frameNames).map(name => {
      const row = { name };
      profiles.forEach(p => {
        const stat = p.frameStats.find(f => f.name === name);
        row[`${p.key}_total`] = stat?.totalMs || 0;
        row[`${p.key}_count`] = stat?.count || 0;
      });
      return row;
    }).sort((a, b) => Math.max(...profiles.map(p => b[`${p.key}_total`] || 0)) - Math.max(...profiles.map(p => a[`${p.key}_total`] || 0)));

    return (
      <div className="view-content">
        <h2>Profile Comparison</h2>
        <div className="metrics-row">
          {profiles.map((p, i) => (
            <div key={p.key} className="metric-card" style={{ borderColor: colors[i % colors.length] }}>
              <span className="metric-value">{p.totalDurationMs.toFixed(2)}</span><span className="metric-label">{p.key}</span>
            </div>
          ))}
        </div>
        <div className="chart-section">
          <h3>Total Time by Frame (Top 10)</h3>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={comparisonData.slice(0, 10)} layout="vertical" margin={{ left: 180, right: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis type="number" stroke="#888" tickFormatter={v => `${v.toFixed(1)}ms`} />
              <YAxis type="category" dataKey="name" stroke="#888" tick={{ fontSize: 11 }} width={170} />
              <Tooltip contentStyle={{ background: '#1a1a1a', border: '1px solid #333' }} />
              <Legend />
              {profiles.map((p, i) => <Bar key={p.key} animationDuration={150} dataKey={`${p.key}_total`} fill={colors[i % colors.length]} name={p.key} />)}
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="table-section">
          <h3>Comparison Table</h3>
          <table className="data-table">
            <thead>
              <tr><th>Frame</th>{profiles.map(p => <th key={p.key} colSpan={2}>{p.key}</th>)}</tr>
              <tr className="subheader"><th></th>{profiles.map(p => <React.Fragment key={p.key}><th>Total ms</th><th>Calls</th></React.Fragment>)}</tr>
            </thead>
            <tbody>
              {comparisonData.slice(0, 20).map((row, i) => (
                <tr key={i}>
                  <td className="method-name">{row.name}</td>
                  {profiles.map(p => <React.Fragment key={p.key}><td>{(row[`${p.key}_total`] || 0).toFixed(3)}</td><td>{row[`${p.key}_count`] || 0}</td></React.Fragment>)}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  const renderView = () => {
    const profile = selectedProfiles[0];
    switch (activeTab) {
      case 'flame': return <FlameGraph profile={profile} />;
      case 'stats': return <FrameStatsView profile={profile} />;
      case 'timeline': return <TimelineView profile={profile} />;
      case 'compare': return <ComparisonView profiles={selectedProfiles} />;
      default: return <FlameGraph profile={profile} />;
    }
  };

  const tabs = [
    { id: 'flame', label: 'Flame Graph' },
    { id: 'stats', label: 'Frame Stats' },
    { id: 'timeline', label: 'Timeline' },
    { id: 'compare', label: 'Compare' }
  ];

  return (
    <div className="analyzer">
      <style>{`
        * { box-sizing: border-box; }
        .analyzer {
          font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif;
          background: #0d0d0d;
          color: #e0e0e0;
          min-height: 100vh;
          display: grid;
          grid-template-columns: 240px 1fr;
          grid-template-rows: auto 1fr;
        }
        .header {
          grid-column: 1 / -1;
          display: flex;
          align-items: center;
          gap: 24px;
          padding: 16px 24px;
          background: #111;
          border-bottom: 1px solid #1a1a1a;
        }
        .logo {
          display: flex;
          align-items: center;
          gap: 8px;
          font-weight: 600;
          font-size: 18px;
          color: #4ecdc4;
        }
        .logo-icon {
          width: 24px;
          height: 24px;
          background: linear-gradient(135deg, #ff6b6b, #4ecdc4);
          border-radius: 4px;
        }
        .drop-zone {
          flex: 1;
          border: 2px dashed #333;
          border-radius: 8px;
          padding: 12px 24px;
          text-align: center;
          color: #666;
          transition: all 0.2s;
        }
        .drop-zone.dragging {
          border-color: #4ecdc4;
          background: rgba(78, 205, 196, 0.1);
          color: #4ecdc4;
        }
        .sidebar {
          background: #111;
          border-right: 1px solid #1a1a1a;
          padding: 16px;
          overflow-y: auto;
        }
        .sidebar-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 12px;
        }
        .sidebar-title {
          font-size: 11px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          color: #666;
        }
        .sidebar-actions { display: flex; gap: 4px; }
        .sidebar-btn, .ctrl-btn {
          background: #1a1a1a;
          border: 1px solid #333;
          color: #888;
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 11px;
          cursor: pointer;
          transition: all 0.15s;
        }
        .sidebar-btn:hover, .ctrl-btn:hover {
          background: #222;
          color: #4ecdc4;
          border-color: #4ecdc4;
        }
        .profile-list { display: flex; flex-direction: column; gap: 8px; }
        .profile-item {
          display: flex;
          align-items: flex-start;
          gap: 10px;
          padding: 10px 12px;
          background: #151515;
          border: 1px solid #2a2a2a;
          border-radius: 6px;
          cursor: pointer;
          transition: all 0.15s;
        }
        .profile-item:hover { border-color: #4ecdc4; }
        .profile-item.selected {
          background: rgba(78, 205, 196, 0.1);
          border-color: #4ecdc4;
        }
        .profile-checkbox {
          width: 18px;
          height: 18px;
          border-radius: 4px;
          border: 2px solid #444;
          background: transparent;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
          margin-top: 2px;
        }
        .profile-checkbox.checked {
          background: #4ecdc4;
          border-color: #4ecdc4;
        }
        .profile-checkbox.checked::after {
          content: '✓';
          color: #000;
          font-size: 12px;
          font-weight: bold;
        }
        .profile-info { flex: 1; min-width: 0; }
        .profile-name {
          font-weight: 500;
          font-size: 13px;
          color: #e0e0e0;
          word-break: break-word;
        }
        .profile-meta {
          font-size: 11px;
          color: #4ecdc4;
          margin-top: 2px;
        }
        .main {
          display: flex;
          flex-direction: column;
          overflow: hidden;
        }
        .tabs {
          display: flex;
          gap: 8px;
          padding: 16px 24px;
          border-bottom: 1px solid #1a1a1a;
          background: #0d0d0d;
        }
        .tab {
          padding: 8px 16px;
          background: transparent;
          border: none;
          color: #666;
          font-size: 13px;
          cursor: pointer;
          border-radius: 6px;
          transition: all 0.15s;
          font-family: inherit;
        }
        .tab:hover { color: #888; background: #1a1a1a; }
        .tab.active { color: #4ecdc4; background: rgba(78, 205, 196, 0.1); }
        .content {
          flex: 1;
          overflow-y: auto;
          padding: 24px;
        }
        .empty-state {
          display: flex;
          align-items: center;
          justify-content: center;
          height: 200px;
          color: #444;
          font-style: italic;
        }
        .view-content h2 { font-size: 18px; font-weight: 500; margin-bottom: 8px; }
        .view-content h3 {
          font-size: 13px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          color: #888;
          margin-bottom: 12px;
        }
        .metrics-row { display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }
        .metric-card {
          background: #151515;
          border: 1px solid #2a2a2a;
          border-radius: 8px;
          padding: 16px 20px;
          min-width: 100px;
        }
        .metric-value {
          display: block;
          font-size: 24px;
          font-weight: 600;
          color: #4ecdc4;
          font-family: 'JetBrains Mono', monospace;
        }
        .metric-label {
          display: block;
          font-size: 11px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          color: #666;
          margin-top: 4px;
        }
        .chart-section {
          background: #111;
          border: 1px solid #1a1a1a;
          border-radius: 8px;
          padding: 20px;
          margin-bottom: 24px;
        }
        .table-section { margin-bottom: 24px; }
        .data-table {
          width: 100%;
          border-collapse: collapse;
          font-size: 12px;
          font-family: 'JetBrains Mono', monospace;
        }
        .data-table th {
          text-align: left;
          padding: 10px 12px;
          background: #151515;
          border-bottom: 1px solid #2a2a2a;
          font-weight: 500;
          color: #888;
          font-size: 11px;
          text-transform: uppercase;
        }
        .data-table th.sortable { cursor: pointer; }
        .data-table th.sortable:hover { color: #4ecdc4; }
        .data-table td {
          padding: 10px 12px;
          border-bottom: 1px solid #1a1a1a;
          color: #ccc;
        }
        .data-table tr:hover { background: #151515; }
        .data-table tr.row-selected { background: rgba(78, 205, 196, 0.15); }
        .data-table .subheader th {
          font-size: 10px;
          padding: 6px 12px;
          background: #131313;
        }
        .method-name { display: flex; align-items: center; gap: 8px; color: #e0e0e0; }
        .method-color-dot { width: 8px; height: 8px; border-radius: 2px; flex-shrink: 0; }
        
        /* Flame Graph */
        .flame-graph-container {
          background: #111;
          border: 1px solid #1a1a1a;
          border-radius: 8px;
          padding: 16px;
        }
        .flame-graph-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 12px;
        }
        .flame-graph-controls {
          display: flex;
          align-items: center;
          gap: 12px;
          flex-wrap: wrap;
        }
        .view-toggle {
          display: flex;
          background: #1a1a1a;
          border-radius: 6px;
          padding: 2px;
          border: 1px solid #333;
        }
        .toggle-btn {
          padding: 6px 12px;
          background: transparent;
          border: none;
          color: #666;
          font-size: 12px;
          cursor: pointer;
          border-radius: 4px;
          transition: all 0.15s;
          font-family: inherit;
        }
        .toggle-btn:hover {
          color: #888;
        }
        .toggle-btn.active {
          background: #4ecdc4;
          color: #000;
          font-weight: 500;
        }
        .depth-control {
          display: flex;
          align-items: center;
          gap: 6px;
          background: #1a1a1a;
          padding: 4px 10px;
          border-radius: 4px;
          border: 1px solid #333;
        }
        .depth-label {
          font-size: 11px;
          color: #888;
        }
        .depth-btn {
          width: 22px;
          height: 22px;
          background: #222;
          border: 1px solid #444;
          color: #ccc;
          border-radius: 3px;
          cursor: pointer;
          font-size: 14px;
          line-height: 1;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .depth-btn:hover:not(:disabled) {
          background: #333;
          color: #4ecdc4;
          border-color: #4ecdc4;
        }
        .depth-btn:disabled {
          opacity: 0.3;
          cursor: not-allowed;
        }
        .depth-value {
          font-size: 12px;
          font-weight: 600;
          color: #4ecdc4;
          min-width: 16px;
          text-align: center;
        }
        .flame-hint { color: #555; font-size: 11px; font-style: italic; }
        .auto-collapse-toggle {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 11px;
          color: #888;
          cursor: pointer;
          padding: 4px 8px;
          background: #1a1a1a;
          border: 1px solid #333;
          border-radius: 4px;
          transition: all 0.15s;
        }
        .auto-collapse-toggle:hover {
          border-color: #4ecdc4;
          color: #aaa;
        }
        .auto-collapse-toggle input {
          accent-color: #4ecdc4;
          cursor: pointer;
        }
        .expand-btn {
          width: 32px;
          height: 32px;
          background: #1a1a1a;
          border: 1px solid #333;
          color: #888;
          border-radius: 6px;
          cursor: pointer;
          font-size: 18px;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.15s;
        }
        .expand-btn:hover {
          background: #222;
          color: #4ecdc4;
          border-color: #4ecdc4;
        }
        .expand-btn.close {
          background: #2a1a1a;
          border-color: #ff6b6b44;
        }
        .expand-btn.close:hover {
          background: #3a2a2a;
          color: #ff6b6b;
          border-color: #ff6b6b;
        }
        .flame-graph-scroll {
          overflow-x: auto;
          overflow-y: auto;
          max-height: 500px;
        }
        .flame-graph-svg { display: block; }
        .flame-tooltip {
          background: #1a1a1a;
          border: 1px solid #333;
          border-radius: 6px;
          padding: 12px 16px;
          margin-top: 12px;
          height: 72px;
          overflow: hidden;
        }
        .flame-tooltip.visible { border-color: #4ecdc4; }
        .tooltip-method { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
        .tooltip-color { width: 12px; height: 12px; border-radius: 2px; }
        .tooltip-method strong { color: #fff; font-family: 'JetBrains Mono', monospace; font-size: 13px; }
        .tooltip-values { display: flex; gap: 16px; font-size: 12px; color: #888; }
        .tooltip-values strong { color: #4ecdc4; }
        .tooltip-hint { color: #555; font-size: 12px; font-style: italic; line-height: 48px; }
        
        /* Fullscreen Overlay */
        .chart-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.9);
          z-index: 1000;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 24px;
        }
        .chart-overlay-content {
          background: #111;
          border: 1px solid #333;
          border-radius: 12px;
          width: 100%;
          height: 100%;
          padding: 24px;
          display: flex;
          flex-direction: column;
        }
        .chart-overlay-content .flame-graph-container {
          flex: 1;
          display: flex;
          flex-direction: column;
        }
        .chart-overlay-content .flame-graph-scroll {
          flex: 1;
          max-height: none;
        }
      `}</style>

      {renderExpandedOverlay()}

      <header className="header">
        <div className="logo">
          <div className="logo-icon" />
          Speedscope Analyzer
        </div>
        <div 
          className={`drop-zone ${isDragging ? 'dragging' : ''}`}
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
        >
          Drag & drop speedscope JSON files
        </div>
      </header>

      <aside className="sidebar">
        <div className="sidebar-header">
          <span className="sidebar-title">Profiles ({profiles.length})</span>
          <div className="sidebar-actions">
            <button className="sidebar-btn" onClick={() => setSelectedKeys(new Set(profiles.map(p => p.key)))}>All</button>
            <button className="sidebar-btn" onClick={() => setSelectedKeys(new Set())}>None</button>
            <button className="sidebar-btn" onClick={() => setFiles([])}>Clear</button>
          </div>
        </div>
        <div className="profile-list">
          {profiles.map(profile => (
            <div 
              key={profile.key}
              className={`profile-item ${selectedKeys.has(profile.key) ? 'selected' : ''}`}
              onClick={() => handleProfileClick(profile.key)}
            >
              <div className={`profile-checkbox ${selectedKeys.has(profile.key) ? 'checked' : ''}`} />
              <div className="profile-info">
                <div className="profile-name">{profile.key}</div>
                <div className="profile-meta">{profile.totalDurationMs.toFixed(1)}ms · {profile.spans.length} calls</div>
              </div>
            </div>
          ))}
        </div>
      </aside>

      <main className="main">
        <div className="tabs">
          {tabs.map(tab => (
            <button key={tab.id} className={`tab ${activeTab === tab.id ? 'active' : ''}`} onClick={() => setActiveTab(tab.id)}>
              {tab.label}
            </button>
          ))}
        </div>
        <div className="content">
          {profiles.length === 0 ? (
            <div className="empty-state">Drop speedscope JSON files to begin analysis</div>
          ) : selectedProfiles.length === 0 ? (
            <div className="empty-state">Select a profile from the sidebar</div>
          ) : renderView()}
        </div>
      </main>
    </div>
  );
}
