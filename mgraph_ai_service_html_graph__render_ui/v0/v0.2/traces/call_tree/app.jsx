// Call Tree Visualizer - Jaeger X-Ray Style
// Browser-compatible version using global React from CDN

const { useState, useCallback, useMemo, useEffect, useRef } = React;

// Extract key from filename
const extractKey = (filename) => {
  let name = filename.replace(/\.json$/, '').replace(/_json$/, '');
  name = name.replace(/^full_+/, '');
  name = name.replace(/^_+|_+$/g, '');
  return name || filename;
};

// Process call tree data from file
const processCallTreeFile = (file) => {
  if (!file.data?.traces?.call_tree) return null;
  
  const traces = file.data.traces;
  const metadata = traces.metadata || {};
  const callTree = traces.call_tree || [];
  
  // Find global time range
  let minTime = Infinity;
  let maxTime = -Infinity;
  let totalSelfMs = 0;
  let nodeCount = 0;
  
  const walkTree = (nodes) => {
    nodes.forEach(node => {
      if (node.start_ns < minTime) minTime = node.start_ns;
      if (node.end_ns > maxTime) maxTime = node.end_ns;
      totalSelfMs += node.self_ms || 0;
      nodeCount++;
      if (node.children?.length) walkTree(node.children);
    });
  };
  walkTree(callTree);
  
  const totalDurationNs = maxTime - minTime;
  const totalDurationMs = totalDurationNs / 1_000_000;
  
  return {
    key: extractKey(file.name),
    name: metadata.name || file.name,
    callTree,
    metadata,
    minTime,
    maxTime,
    totalDurationNs,
    totalDurationMs,
    totalSelfMs,
    nodeCount
  };
};

// Color scale based on self_ms percentage
const getHotspotColor = (selfMs, totalSelfMs) => {
  if (!totalSelfMs || !selfMs) return '#4ecdc4'; // Default teal
  const pct = selfMs / totalSelfMs;
  
  if (pct > 0.15) return '#ff6b6b'; // Hot - red
  if (pct > 0.08) return '#ffa502'; // Warm - orange  
  if (pct > 0.03) return '#ffd93d'; // Medium - yellow
  if (pct > 0.01) return '#6bcb77'; // Cool - green
  return '#4ecdc4'; // Cold - teal
};

// Format duration nicely
const formatDuration = (ms) => {
  if (ms >= 1000) return `${(ms / 1000).toFixed(2)}s`;
  if (ms >= 1) return `${ms.toFixed(2)}ms`;
  return `${(ms * 1000).toFixed(1)}µs`;
};

// Tree Row Component
const TreeRow = ({ node, profile, expandedNodes, toggleExpand, depth = 0, rowHeight = 28 }) => {
  const [isHovered, setIsHovered] = useState(false);
  
  const hasChildren = node.children && node.children.length > 0;
  const isExpanded = expandedNodes.has(node.call_index);
  const indent = depth * 20;
  
  // Calculate bar position and width
  const startPct = ((node.start_ns - profile.minTime) / profile.totalDurationNs) * 100;
  const widthPct = ((node.end_ns - node.start_ns) / profile.totalDurationNs) * 100;
  
  const color = getHotspotColor(node.self_ms, profile.totalSelfMs);
  const selfPct = profile.totalSelfMs ? ((node.self_ms / profile.totalSelfMs) * 100).toFixed(1) : 0;
  
  return (
    <>
      <div 
        className={`tree-row ${isHovered ? 'hovered' : ''}`}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        {/* Left side: tree structure */}
        <div className="tree-label" style={{ paddingLeft: indent + 8 }}>
          {hasChildren ? (
            <button 
              className="expand-btn"
              onClick={() => toggleExpand(node.call_index)}
            >
              {isExpanded ? '▼' : '▶'}
            </button>
          ) : (
            <span className="expand-placeholder">│</span>
          )}
          <span className="method-name" title={node.name}>
            {node.name}
          </span>
        </div>
        
        {/* Right side: timeline bar */}
        <div className="timeline-cell">
          <div className="timeline-bar-container">
            <div 
              className="timeline-bar"
              style={{
                left: `${startPct}%`,
                width: `${Math.max(widthPct, 0.3)}%`,
                backgroundColor: color,
                opacity: isHovered ? 1 : 0.85
              }}
            />
            <span 
              className="duration-label"
              style={{ left: `${startPct + widthPct + 0.5}%` }}
            >
              {formatDuration(node.duration_ms)}
            </span>
          </div>
        </div>
        
        {/* Tooltip on hover */}
        {isHovered && (
          <div className="row-tooltip">
            <div className="tooltip-title">{node.name}</div>
            <div className="tooltip-stats">
              <span>Duration: <strong>{formatDuration(node.duration_ms)}</strong></span>
              <span>Self: <strong>{formatDuration(node.self_ms)}</strong> ({selfPct}%)</span>
              <span>Depth: {node.depth}</span>
              <span>Call #{node.call_index}</span>
            </div>
          </div>
        )}
      </div>
      
      {/* Render children if expanded */}
      {hasChildren && isExpanded && node.children.map((child, idx) => (
        <TreeRow
          key={`${child.call_index}-${idx}`}
          node={child}
          profile={profile}
          expandedNodes={expandedNodes}
          toggleExpand={toggleExpand}
          depth={depth + 1}
          rowHeight={rowHeight}
        />
      ))}
    </>
  );
};

// Main Component
function CallTreeVisualizer() {
  const [files, setFiles] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const [selectedKey, setSelectedKey] = useState(null);
  const [expandedNodes, setExpandedNodes] = useState(new Set());
  const [expandAll, setExpandAll] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  
  const profiles = useMemo(() => 
    files.map(f => processCallTreeFile(f)).filter(Boolean),
    [files]
  );
  
  const selectedProfile = useMemo(() => 
    profiles.find(p => p.key === selectedKey) || profiles[0],
    [profiles, selectedKey]
  );
  
  // Auto-select first profile
  useEffect(() => {
    if (profiles.length > 0 && !selectedKey) {
      setSelectedKey(profiles[0].key);
    }
  }, [profiles, selectedKey]);
  
  // Expand all nodes for a profile
  const expandAllNodes = useCallback((profile) => {
    const allIds = new Set();
    const walk = (nodes) => {
      nodes.forEach(n => {
        if (n.children?.length) {
          allIds.add(n.call_index);
          walk(n.children);
        }
      });
    };
    walk(profile.callTree);
    return allIds;
  }, []);
  
  // Toggle expand all
  useEffect(() => {
    if (selectedProfile) {
      if (expandAll) {
        setExpandedNodes(expandAllNodes(selectedProfile));
      } else {
        // Collapse to just first level
        const firstLevel = new Set();
        selectedProfile.callTree.forEach(n => {
          if (n.children?.length) firstLevel.add(n.call_index);
        });
        setExpandedNodes(firstLevel);
      }
    }
  }, [expandAll, selectedProfile, expandAllNodes]);
  
  const toggleExpand = useCallback((callIndex) => {
    setExpandedNodes(prev => {
      const next = new Set(prev);
      if (next.has(callIndex)) {
        next.delete(callIndex);
      } else {
        next.add(callIndex);
      }
      return next;
    });
  }, []);
  
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
  
  // Filter nodes by search term
  const filteredTree = useMemo(() => {
    if (!selectedProfile || !searchTerm.trim()) return selectedProfile?.callTree || [];
    
    const term = searchTerm.toLowerCase();
    const filterNodes = (nodes) => {
      return nodes.reduce((acc, node) => {
        const matches = node.name.toLowerCase().includes(term);
        const filteredChildren = node.children ? filterNodes(node.children) : [];
        
        if (matches || filteredChildren.length > 0) {
          acc.push({
            ...node,
            children: filteredChildren
          });
        }
        return acc;
      }, []);
    };
    
    return filterNodes(selectedProfile.callTree);
  }, [selectedProfile, searchTerm]);
  
  // Time axis markers
  const timeMarkers = useMemo(() => {
    if (!selectedProfile) return [];
    const markers = [];
    for (let i = 0; i <= 4; i++) {
      const pct = i * 25;
      const time = (pct / 100) * selectedProfile.totalDurationMs;
      markers.push({ pct, time });
    }
    return markers;
  }, [selectedProfile]);

  return (
    <div className="visualizer">
      <style>{`
        * { box-sizing: border-box; }
        
        .visualizer {
          font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif;
          background: #0d0d0d;
          color: #e0e0e0;
          min-height: 100vh;
          display: flex;
          flex-direction: column;
        }
        
        .header {
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
          white-space: nowrap;
        }
        
        .logo-icon {
          width: 24px;
          height: 24px;
          background: linear-gradient(135deg, #ffa502, #ff6b6b);
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
        
        .toolbar {
          display: flex;
          align-items: center;
          gap: 16px;
          padding: 12px 24px;
          background: #111;
          border-bottom: 1px solid #1a1a1a;
        }
        
        .profile-select {
          background: #1a1a1a;
          border: 1px solid #333;
          color: #e0e0e0;
          padding: 8px 12px;
          border-radius: 6px;
          font-size: 13px;
          min-width: 200px;
        }
        
        .search-input {
          background: #1a1a1a;
          border: 1px solid #333;
          color: #e0e0e0;
          padding: 8px 12px;
          border-radius: 6px;
          font-size: 13px;
          width: 250px;
        }
        
        .search-input::placeholder {
          color: #666;
        }
        
        .toolbar-btn {
          background: #1a1a1a;
          border: 1px solid #333;
          color: #888;
          padding: 8px 16px;
          border-radius: 6px;
          font-size: 12px;
          cursor: pointer;
          transition: all 0.15s;
        }
        
        .toolbar-btn:hover {
          background: #222;
          color: #4ecdc4;
          border-color: #4ecdc4;
        }
        
        .toolbar-btn.active {
          background: rgba(78, 205, 196, 0.15);
          color: #4ecdc4;
          border-color: #4ecdc4;
        }
        
        .stats {
          margin-left: auto;
          display: flex;
          gap: 16px;
          font-size: 12px;
          color: #888;
        }
        
        .stats strong {
          color: #4ecdc4;
        }
        
        .main-content {
          flex: 1;
          overflow: hidden;
          display: flex;
          flex-direction: column;
        }
        
        .tree-header {
          display: flex;
          background: #151515;
          border-bottom: 1px solid #2a2a2a;
          font-size: 11px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          color: #666;
        }
        
        .tree-header-label {
          width: 400px;
          min-width: 400px;
          padding: 10px 16px;
          border-right: 1px solid #2a2a2a;
        }
        
        .tree-header-timeline {
          flex: 1;
          padding: 10px 16px;
          display: flex;
          justify-content: space-between;
        }
        
        .time-marker {
          font-family: 'JetBrains Mono', monospace;
          font-size: 10px;
        }
        
        .tree-container {
          flex: 1;
          overflow: auto;
        }
        
        .tree-row {
          display: flex;
          border-bottom: 1px solid #1a1a1a;
          position: relative;
          min-height: 32px;
        }
        
        .tree-row:hover {
          background: #151515;
        }
        
        .tree-row.hovered {
          background: #1a1a1a;
        }
        
        .tree-label {
          width: 400px;
          min-width: 400px;
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 6px 8px;
          border-right: 1px solid #1a1a1a;
          overflow: hidden;
        }
        
        .expand-btn {
          background: none;
          border: none;
          color: #666;
          cursor: pointer;
          font-size: 10px;
          width: 16px;
          height: 16px;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
        }
        
        .expand-btn:hover {
          color: #4ecdc4;
        }
        
        .expand-placeholder {
          color: #333;
          font-size: 10px;
          width: 16px;
          text-align: center;
          flex-shrink: 0;
        }
        
        .method-name {
          font-family: 'JetBrains Mono', monospace;
          font-size: 12px;
          color: #e0e0e0;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
        
        .timeline-cell {
          flex: 1;
          position: relative;
          padding: 4px 8px;
        }
        
        .timeline-bar-container {
          position: relative;
          height: 100%;
          min-height: 24px;
        }
        
        .timeline-bar {
          position: absolute;
          top: 50%;
          transform: translateY(-50%);
          height: 20px;
          border-radius: 3px;
          min-width: 3px;
        }
        
        .duration-label {
          position: absolute;
          top: 50%;
          transform: translateY(-50%);
          font-family: 'JetBrains Mono', monospace;
          font-size: 11px;
          color: #888;
          white-space: nowrap;
          padding-left: 6px;
        }
        
        .row-tooltip {
          position: absolute;
          top: 100%;
          left: 200px;
          z-index: 100;
          background: #1a1a1a;
          border: 1px solid #4ecdc4;
          border-radius: 6px;
          padding: 12px 16px;
          min-width: 300px;
          box-shadow: 0 4px 12px rgba(0,0,0,0.5);
        }
        
        .tooltip-title {
          font-family: 'JetBrains Mono', monospace;
          font-size: 13px;
          color: #fff;
          margin-bottom: 8px;
          word-break: break-all;
        }
        
        .tooltip-stats {
          display: flex;
          flex-wrap: wrap;
          gap: 12px;
          font-size: 12px;
          color: #888;
        }
        
        .tooltip-stats strong {
          color: #4ecdc4;
        }
        
        .empty-state {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #444;
          font-style: italic;
        }
        
        .legend {
          display: flex;
          align-items: center;
          gap: 16px;
          padding: 12px 24px;
          background: #111;
          border-top: 1px solid #1a1a1a;
          font-size: 11px;
          color: #888;
        }
        
        .legend-item {
          display: flex;
          align-items: center;
          gap: 6px;
        }
        
        .legend-color {
          width: 12px;
          height: 12px;
          border-radius: 2px;
        }
      `}</style>
      
      <header className="header">
        <div className="logo">
          <div className="logo-icon" />
          Call Tree Visualizer
        </div>
        <div 
          className={`drop-zone ${isDragging ? 'dragging' : ''}`}
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
        >
          Drag & drop full_*.json files
        </div>
      </header>
      
      {profiles.length > 0 && (
        <div className="toolbar">
          <select 
            className="profile-select"
            value={selectedKey || ''}
            onChange={(e) => setSelectedKey(e.target.value)}
          >
            {profiles.map(p => (
              <option key={p.key} value={p.key}>{p.key}</option>
            ))}
          </select>
          
          <input
            type="text"
            className="search-input"
            placeholder="Search methods..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          
          <button 
            className={`toolbar-btn ${expandAll ? 'active' : ''}`}
            onClick={() => setExpandAll(!expandAll)}
          >
            {expandAll ? 'Collapse All' : 'Expand All'}
          </button>
          
          <button 
            className="toolbar-btn"
            onClick={() => setFiles([])}
          >
            Clear
          </button>
          
          {selectedProfile && (
            <div className="stats">
              <span>Duration: <strong>{formatDuration(selectedProfile.totalDurationMs)}</strong></span>
              <span>Calls: <strong>{selectedProfile.nodeCount}</strong></span>
              <span>Methods: <strong>{selectedProfile.metadata.method_count || '?'}</strong></span>
            </div>
          )}
        </div>
      )}
      
      <div className="main-content">
        {!selectedProfile ? (
          <div className="empty-state">Drop a full_*.json file to visualize the call tree</div>
        ) : (
          <>
            <div className="tree-header">
              <div className="tree-header-label">Service & Operation</div>
              <div className="tree-header-timeline">
                {timeMarkers.map((m, i) => (
                  <span key={i} className="time-marker">{formatDuration(m.time)}</span>
                ))}
              </div>
            </div>
            
            <div className="tree-container">
              {filteredTree.map((node, idx) => (
                <TreeRow
                  key={`${node.call_index}-${idx}`}
                  node={node}
                  profile={selectedProfile}
                  expandedNodes={expandedNodes}
                  toggleExpand={toggleExpand}
                  depth={0}
                />
              ))}
            </div>
          </>
        )}
      </div>
      
      <div className="legend">
        <span>Hotspot (self time %):</span>
        <div className="legend-item">
          <div className="legend-color" style={{ background: '#4ecdc4' }} />
          <span>&lt;1%</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ background: '#6bcb77' }} />
          <span>1-3%</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ background: '#ffd93d' }} />
          <span>3-8%</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ background: '#ffa502' }} />
          <span>8-15%</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ background: '#ff6b6b' }} />
          <span>&gt;15%</span>
        </div>
      </div>
    </div>
  );
}
