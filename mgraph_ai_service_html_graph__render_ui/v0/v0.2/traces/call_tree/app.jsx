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
  let maxDepth = 0;

  const walkTree = (nodes) => {
    nodes.forEach(node => {
      if (node.start_ns < minTime) minTime = node.start_ns;
      if (node.end_ns > maxTime) maxTime = node.end_ns;
      if (node.depth > maxDepth) maxDepth = node.depth;
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
    nodeCount,
    maxDepth
  };
};

// Color scale based on self_ms percentage
const getHotspotColor = (selfMs, totalSelfMs) => {
  if (!totalSelfMs || !selfMs) return '#4ecdc4';
  const pct = selfMs / totalSelfMs;

  if (pct > 0.15) return '#ff6b6b';
  if (pct > 0.08) return '#ffa502';
  if (pct > 0.03) return '#ffd93d';
  if (pct > 0.01) return '#6bcb77';
  return '#4ecdc4';
};

// Format duration nicely
const formatDuration = (ms) => {
  if (ms >= 1000) return `${(ms / 1000).toFixed(2)}s`;
  if (ms >= 1) return `${ms.toFixed(2)}ms`;
  return `${(ms * 1000).toFixed(1)}µs`;
};

// Tree Row Component - uses node.depth from data for indentation
const TreeRow = ({ node, profile, expandedNodes, toggleExpand, effectiveTimeRange, onBarClick, focusNode, onHover, colorMode, methodColors }) => {
  const hasChildren = node.children && node.children.length > 0;
  const isExpanded = expandedNodes.has(node.call_index);
  const indent = node.depth * 16; // Use node.depth from data
  const isFocused = focusNode && focusNode.call_index === node.call_index;
  const [isHovered, setIsHovered] = useState(false);

  // Calculate position relative to effective time range
  const startPct = Math.max(0, ((node.start_ns - effectiveTimeRange.minTime) / effectiveTimeRange.totalDurationNs) * 100);
  const endPct = Math.min(100, ((node.end_ns - effectiveTimeRange.minTime) / effectiveTimeRange.totalDurationNs) * 100);
  const widthPct = endPct - startPct;

  // Color based on mode
  const color = colorMode === 'method'
    ? (methodColors.get(node.name) || '#4ecdc4')
    : getHotspotColor(node.self_ms, profile.totalSelfMs);

  const handleMouseEnter = () => {
    setIsHovered(true);
    onHover(node);
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
  };

  return (
    <>
      <div
        style={{
          display: 'flex',
          borderBottom: '1px solid #1a1a1a',
          position: 'relative',
          minHeight: 32,
          background: isHovered ? '#1a1a1a' : 'transparent'
        }}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
      >
        {/* Left side: tree structure */}
        <div style={{
          width: 350,
          minWidth: 350,
          display: 'flex',
          alignItems: 'center',
          gap: 4,
          padding: '6px 8px',
          paddingLeft: indent + 8,
          borderRight: '1px solid #1a1a1a',
          overflow: 'hidden'
        }}>
          {hasChildren ? (
            <button
              onClick={() => toggleExpand(node.call_index, node)}
              style={{
                background: 'none',
                border: '1px solid #444',
                color: '#888',
                cursor: 'pointer',
                fontSize: 8,
                width: 14,
                height: 14,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
                borderRadius: 2
              }}
            >
              {isExpanded ? '▼' : '▶'}
            </button>
          ) : (
            <span style={{ color: '#333', fontSize: 10, width: 14, textAlign: 'center', flexShrink: 0 }}>│</span>
          )}
          <span
            title={node.name}
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: 11,
              color: '#e0e0e0',
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis'
            }}
          >
            {node.name}
          </span>
        </div>

        {/* Right side: timeline bar */}
        <div style={{ flex: 1, position: 'relative', padding: '4px 8px' }}>
          <div style={{ position: 'relative', height: '100%', minHeight: 24 }}>
            {widthPct > 0 && (
              <>
                <div
                  onClick={() => onBarClick(node)}
                  style={{
                    position: 'absolute',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    left: `${startPct}%`,
                    width: `${Math.max(widthPct, 0.3)}%`,
                    height: 18,
                    backgroundColor: color,
                    borderRadius: 3,
                    minWidth: 3,
                    opacity: isHovered ? 1 : 0.85,
                    cursor: 'pointer',
                    border: isFocused ? '2px solid #fff' : 'none',
                    boxSizing: 'border-box'
                  }}
                />
                <span
                  style={{
                    position: 'absolute',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    left: `${startPct + widthPct + 0.5}%`,
                    fontFamily: "'JetBrains Mono', monospace",
                    fontSize: 10,
                    color: '#888',
                    whiteSpace: 'nowrap',
                    paddingLeft: 6
                  }}
                >
                  {formatDuration(node.duration_ms)}
                </span>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Render children if expanded */}
      {hasChildren && isExpanded && node.children.map((child, idx) => (
        <TreeRow
          key={`${child.call_index}-${idx}`}
          node={child}
          profile={profile}
          expandedNodes={expandedNodes}
          toggleExpand={toggleExpand}
          effectiveTimeRange={effectiveTimeRange}
          onBarClick={onBarClick}
          focusNode={focusNode}
          onHover={onHover}
          colorMode={colorMode}
          methodColors={methodColors}
        />
      ))}
    </>
  );
};

function CallTreeVisualizer() {
  const [files, setFiles] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const [selectedKey, setSelectedKey] = useState(null);
  const [expandedNodes, setExpandedNodes] = useState(new Set());
  const [searchTerm, setSearchTerm] = useState('');
  const [expandDepth, setExpandDepth] = useState(1); // Current expansion depth
  const [isMaximized, setIsMaximized] = useState(false);
  const [focusNode, setFocusNode] = useState(null); // Node to use as root for timeline
  const [hoveredNode, setHoveredNode] = useState(null); // Currently hovered node for details panel
  const [colorMode, setColorMode] = useState('hotspot'); // 'hotspot' or 'method'
  const [showMethodStats, setShowMethodStats] = useState(false); // Accordion state

  const profiles = useMemo(() =>
    files.map(f => processCallTreeFile(f)).filter(Boolean),
    [files]
  );

  const selectedProfile = useMemo(() =>
    profiles.find(p => p.key === selectedKey) || profiles[0],
    [profiles, selectedKey]
  );

  // Compute method statistics (aggregate by method name)
  const methodStats = useMemo(() => {
    if (!selectedProfile) return [];

    const stats = new Map();

    const walkTree = (nodes) => {
      nodes.forEach(node => {
        const existing = stats.get(node.name) || { name: node.name, count: 0, totalMs: 0, selfMs: 0 };
        existing.count += 1;
        existing.totalMs += node.duration_ms || 0;
        existing.selfMs += node.self_ms || 0;
        stats.set(node.name, existing);
        if (node.children?.length) walkTree(node.children);
      });
    };
    walkTree(selectedProfile.callTree);

    // Sort by total time descending
    return Array.from(stats.values()).sort((a, b) => b.totalMs - a.totalMs);
  }, [selectedProfile]);

  // Generate consistent color for method name
  const methodColors = useMemo(() => {
    const colors = new Map();
    const palette = [
      '#4ecdc4', '#ff6b6b', '#ffd93d', '#6bcb77', '#ffa502',
      '#a55eea', '#45aaf2', '#fd9644', '#26de81', '#fc5c65',
      '#778ca3', '#f7b731', '#20bf6b', '#eb3b5a', '#2bcbba',
      '#fa8231', '#8854d0', '#3867d6', '#fed330', '#2d98da'
    ];

    methodStats.forEach((stat, index) => {
      colors.set(stat.name, palette[index % palette.length]);
    });

    return colors;
  }, [methodStats]);

  // Auto-select first profile
  useEffect(() => {
    if (profiles.length > 0 && !selectedKey) {
      setSelectedKey(profiles[0].key);
    }
  }, [profiles, selectedKey]);

  // Reset state when profile changes
  useEffect(() => {
    setExpandDepth(1);
    setFocusNode(null);
    setHoveredNode(null);
  }, [selectedKey]);

  // Expand nodes up to a certain depth
  const getNodesAtDepth = useCallback((profile, maxDepth) => {
    const ids = new Set();
    const walk = (nodes) => {
      nodes.forEach(n => {
        if (n.depth < maxDepth && n.children?.length) {
          ids.add(n.call_index);
          walk(n.children);
        }
      });
    };
    walk(profile.callTree);
    return ids;
  }, []);

  // Expand all nodes
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

  // Update expanded nodes when depth changes
  useEffect(() => {
    if (selectedProfile) {
      setExpandedNodes(getNodesAtDepth(selectedProfile, expandDepth));
    }
  }, [expandDepth, selectedProfile, getNodesAtDepth]);

  const toggleExpand = useCallback((callIndex, node) => {
    setExpandedNodes(prev => {
      const next = new Set(prev);
      if (next.has(callIndex)) {
        // Collapsing - also collapse all descendants
        next.delete(callIndex);
        if (node?.children) {
          const collapseDescendants = (nodes) => {
            nodes.forEach(n => {
              next.delete(n.call_index);
              if (n.children?.length) collapseDescendants(n.children);
            });
          };
          collapseDescendants(node.children);
        }
      } else {
        // Expanding - just expand this node (children stay collapsed)
        next.add(callIndex);
      }
      return next;
    });
  }, []);

  // Expand all handler
  const handleExpandAll = useCallback(() => {
    if (selectedProfile) {
      setExpandedNodes(expandAllNodes(selectedProfile));
      setExpandDepth(selectedProfile.maxDepth);
    }
  }, [selectedProfile, expandAllNodes]);

  // Collapse all handler
  const handleCollapseAll = useCallback(() => {
    setExpandedNodes(new Set());
    setExpandDepth(0);
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

  const filteredTree = useMemo(() => {
    if (!selectedProfile || !searchTerm.trim()) return selectedProfile?.callTree || [];

    const term = searchTerm.toLowerCase();
    const filterNodes = (nodes) => {
      return nodes.reduce((acc, node) => {
        const matches = node.name.toLowerCase().includes(term);
        const filteredChildren = node.children ? filterNodes(node.children) : [];

        if (matches || filteredChildren.length > 0) {
          acc.push({ ...node, children: filteredChildren });
        }
        return acc;
      }, []);
    };

    return filterNodes(selectedProfile.callTree);
  }, [selectedProfile, searchTerm]);

  // Calculate effective time range based on focus node
  const effectiveTimeRange = useMemo(() => {
    if (!selectedProfile) return null;
    if (focusNode) {
      return {
        minTime: focusNode.start_ns,
        maxTime: focusNode.end_ns,
        totalDurationNs: focusNode.end_ns - focusNode.start_ns,
        totalDurationMs: (focusNode.end_ns - focusNode.start_ns) / 1_000_000
      };
    }
    return {
      minTime: selectedProfile.minTime,
      maxTime: selectedProfile.maxTime,
      totalDurationNs: selectedProfile.totalDurationNs,
      totalDurationMs: selectedProfile.totalDurationMs
    };
  }, [selectedProfile, focusNode]);

  const timeMarkers = useMemo(() => {
    if (!effectiveTimeRange) return [];
    const markers = [];
    for (let i = 0; i <= 4; i++) {
      const pct = i * 25;
      const time = (pct / 100) * effectiveTimeRange.totalDurationMs;
      markers.push({ pct, time });
    }
    return markers;
  }, [effectiveTimeRange]);

  // Handle clicking on a bar to focus
  const handleBarClick = useCallback((node) => {
    if (focusNode && focusNode.call_index === node.call_index) {
      // Clicking same node again - reset
      setFocusNode(null);
    } else {
      setFocusNode(node);
      // Auto-expand the focused node
      if (node.children?.length) {
        setExpandedNodes(prev => {
          const next = new Set(prev);
          next.add(node.call_index);
          return next;
        });
      }
    }
  }, [focusNode]);

  const buttonStyle = {
    background: '#1a1a1a',
    border: '1px solid #333',
    color: '#888',
    padding: '6px 12px',
    borderRadius: 4,
    fontSize: 11,
    cursor: 'pointer'
  };

  return (
    <div style={{
      fontFamily: "'Space Grotesk', -apple-system, sans-serif",
      background: '#0d0d0d',
      color: '#e0e0e0',
      minHeight: '100vh',
      display: 'grid',
      gridTemplateColumns: '220px 1fr',
      gridTemplateRows: 'auto 1fr'
    }}>
      {/* Maximize Overlay */}
      {isMaximized && selectedProfile && (
        <div
          onClick={(e) => e.target === e.currentTarget && setIsMaximized(false)}
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.95)',
            zIndex: 1000,
            display: 'flex',
            flexDirection: 'column',
            padding: 20
          }}
        >
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            marginBottom: 16
          }}>
            {/* Depth control in overlay */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              background: '#1a1a1a',
              padding: '4px 10px',
              borderRadius: 4,
              border: '1px solid #333'
            }}>
              <span style={{ fontSize: 11, color: '#888' }}>Depth:</span>
              <button
                onClick={() => setExpandDepth(Math.max(0, expandDepth - 1))}
                disabled={expandDepth === 0}
                style={{
                  width: 22, height: 22, background: '#222', border: '1px solid #444',
                  color: expandDepth === 0 ? '#444' : '#ccc', borderRadius: 3,
                  cursor: expandDepth === 0 ? 'not-allowed' : 'pointer', fontSize: 14,
                  display: 'flex', alignItems: 'center', justifyContent: 'center'
                }}
              >−</button>
              <span style={{ fontSize: 12, fontWeight: 600, color: '#4ecdc4', minWidth: 16, textAlign: 'center' }}>
                {expandDepth}
              </span>
              <button
                onClick={() => setExpandDepth(Math.min(selectedProfile?.maxDepth || 20, expandDepth + 1))}
                style={{
                  width: 22, height: 22, background: '#222', border: '1px solid #444',
                  color: '#ccc', borderRadius: 3, cursor: 'pointer', fontSize: 14,
                  display: 'flex', alignItems: 'center', justifyContent: 'center'
                }}
              >+</button>
            </div>

            <button onClick={handleExpandAll} style={buttonStyle}>
              Expand All
            </button>

            <button onClick={handleCollapseAll} style={buttonStyle}>
              Collapse All
            </button>

            {/* Color mode toggle */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: 2,
              background: '#1a1a1a',
              padding: 2,
              borderRadius: 4,
              border: '1px solid #333'
            }}>
              <button
                onClick={() => setColorMode('hotspot')}
                style={{
                  padding: '4px 8px',
                  fontSize: 10,
                  border: 'none',
                  borderRadius: 3,
                  cursor: 'pointer',
                  background: colorMode === 'hotspot' ? '#4ecdc4' : 'transparent',
                  color: colorMode === 'hotspot' ? '#000' : '#888'
                }}
              >
                Hotspot
              </button>
              <button
                onClick={() => setColorMode('method')}
                style={{
                  padding: '4px 8px',
                  fontSize: 10,
                  border: 'none',
                  borderRadius: 3,
                  cursor: 'pointer',
                  background: colorMode === 'method' ? '#4ecdc4' : 'transparent',
                  color: colorMode === 'method' ? '#000' : '#888'
                }}
              >
                Method
              </button>
            </div>

            {focusNode && (
              <button
                onClick={() => setFocusNode(null)}
                style={{ ...buttonStyle, background: 'rgba(78, 205, 196, 0.15)', color: '#4ecdc4', borderColor: '#4ecdc4' }}
              >
                Reset Focus
              </button>
            )}

            <span style={{ fontSize: 11, color: '#555', fontStyle: 'italic' }}>
              Click bar to focus · Click again to reset
            </span>

            <div style={{ marginLeft: 'auto' }}>
              <button
                onClick={() => setIsMaximized(false)}
                style={{
                  width: 32, height: 32, background: '#2a1a1a', border: '1px solid #ff6b6b44',
                  color: '#888', borderRadius: 6, cursor: 'pointer', fontSize: 18,
                  display: 'flex', alignItems: 'center', justifyContent: 'center'
                }}
                title="Close"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Column headers */}
          <div style={{
            display: 'flex',
            background: '#151515',
            borderBottom: '1px solid #2a2a2a',
            fontSize: 10,
            textTransform: 'uppercase',
            letterSpacing: 0.5,
            color: '#666',
            borderRadius: '8px 8px 0 0'
          }}>
            <div style={{ width: 400, minWidth: 400, padding: '8px 12px', borderRight: '1px solid #2a2a2a' }}>
              Service & Operation
            </div>
            <div style={{ flex: 1, padding: '8px 12px', display: 'flex', justifyContent: 'space-between' }}>
              {timeMarkers.map((m, i) => (
                <span key={i} style={{ fontFamily: "'JetBrains Mono', monospace" }}>
                  {formatDuration(m.time)}
                </span>
              ))}
            </div>
          </div>

          {/* Tree rows in overlay */}
          <div style={{ flex: 1, overflow: 'auto', background: '#0d0d0d', borderRadius: '0 0 8px 8px' }}>
            {filteredTree.map((node, idx) => (
              <TreeRow
                key={`${node.call_index}-${idx}`}
                node={node}
                profile={selectedProfile}
                expandedNodes={expandedNodes}
                toggleExpand={toggleExpand}
                effectiveTimeRange={effectiveTimeRange}
                onBarClick={handleBarClick}
                focusNode={focusNode}
                onHover={setHoveredNode}
                colorMode={colorMode}
                methodColors={methodColors}
              />
            ))}
          </div>
        </div>
      )}
      {/* Header - spans both columns */}
      <header style={{
        gridColumn: '1 / -1',
        display: 'flex',
        alignItems: 'center',
        gap: 20,
        padding: '14px 20px',
        background: '#111',
        borderBottom: '1px solid #1a1a1a'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          fontWeight: 600,
          fontSize: 16,
          color: '#4ecdc4',
          whiteSpace: 'nowrap'
        }}>
          <div style={{
            width: 20,
            height: 20,
            background: 'linear-gradient(135deg, #ffa502, #ff6b6b)',
            borderRadius: 4
          }} />
          Call Tree Visualizer
        </div>
        <div
          style={{
            flex: 1,
            border: `2px dashed ${isDragging ? '#4ecdc4' : '#333'}`,
            borderRadius: 6,
            padding: '10px 20px',
            textAlign: 'center',
            color: isDragging ? '#4ecdc4' : '#666',
            background: isDragging ? 'rgba(78, 205, 196, 0.1)' : 'transparent',
            fontSize: 13
          }}
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
        >
          Drag & drop full_*.json files
        </div>
      </header>

      {/* Sidebar */}
      <aside style={{
        background: '#111',
        borderRight: '1px solid #1a1a1a',
        padding: 12,
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: 10
        }}>
          <span style={{ fontSize: 10, textTransform: 'uppercase', letterSpacing: 0.5, color: '#666' }}>
            Profiles ({profiles.length})
          </span>
          <div style={{ display: 'flex', gap: 4 }}>
            <button
              onClick={() => setFiles([])}
              style={{ ...buttonStyle, padding: '3px 8px', fontSize: 10 }}
            >
              Clear
            </button>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 6, flex: showMethodStats ? 0 : 1 }}>
          {profiles.map(profile => (
            <div
              key={profile.key}
              onClick={() => setSelectedKey(profile.key)}
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: 8,
                padding: '8px 10px',
                background: selectedKey === profile.key ? 'rgba(78, 205, 196, 0.1)' : '#151515',
                border: `1px solid ${selectedKey === profile.key ? '#4ecdc4' : '#2a2a2a'}`,
                borderRadius: 5,
                cursor: 'pointer',
                transition: 'all 0.15s'
              }}
            >
              <div style={{
                width: 14,
                height: 14,
                borderRadius: 3,
                border: `2px solid ${selectedKey === profile.key ? '#4ecdc4' : '#444'}`,
                background: selectedKey === profile.key ? '#4ecdc4' : 'transparent',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
                marginTop: 1,
                fontSize: 10,
                color: '#000',
                fontWeight: 'bold'
              }}>
                {selectedKey === profile.key && '✓'}
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{
                  fontWeight: 500,
                  fontSize: 12,
                  color: '#e0e0e0',
                  wordBreak: 'break-word'
                }}>
                  {profile.key}
                </div>
                <div style={{ fontSize: 10, color: '#4ecdc4', marginTop: 2 }}>
                  {formatDuration(profile.totalDurationMs)} · {profile.nodeCount} calls
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Method Stats Accordion */}
        <div style={{ marginTop: 12, borderTop: '1px solid #2a2a2a', paddingTop: 12 }}>
          <button
            onClick={() => setShowMethodStats(!showMethodStats)}
            style={{
              width: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              background: 'none',
              border: 'none',
              padding: '4px 0',
              cursor: 'pointer',
              color: '#888'
            }}
          >
            <span style={{ fontSize: 10, textTransform: 'uppercase', letterSpacing: 0.5 }}>
              Methods ({methodStats.length})
            </span>
            <span style={{ fontSize: 10 }}>{showMethodStats ? '▼' : '▶'}</span>
          </button>

          {showMethodStats && (
            <div style={{
              marginTop: 8,
              maxHeight: 300,
              overflowY: 'auto',
              background: '#0a0a0a',
              borderRadius: 4,
              border: '1px solid #222'
            }}>
              {methodStats.map((stat, idx) => (
                <div
                  key={stat.name}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 6,
                    padding: '6px 8px',
                    borderBottom: idx < methodStats.length - 1 ? '1px solid #1a1a1a' : 'none',
                    fontSize: 10
                  }}
                >
                  <div style={{
                    width: 8,
                    height: 8,
                    borderRadius: 2,
                    background: methodColors.get(stat.name) || '#4ecdc4',
                    flexShrink: 0
                  }} />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{
                      color: '#ccc',
                      whiteSpace: 'nowrap',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      fontFamily: "'JetBrains Mono', monospace",
                      fontSize: 9
                    }} title={stat.name}>
                      {stat.name}
                    </div>
                    <div style={{ color: '#666', marginTop: 2 }}>
                      <span style={{ color: '#4ecdc4' }}>{stat.count}×</span>
                      {' · '}
                      <span>{formatDuration(stat.totalMs)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Details Panel - shows hovered node info */}
        <div style={{
          marginTop: 'auto',
          paddingTop: 12,
          borderTop: '1px solid #2a2a2a'
        }}>
          <div style={{ fontSize: 10, textTransform: 'uppercase', letterSpacing: 0.5, color: '#666', marginBottom: 8 }}>
            Details
          </div>
          {hoveredNode ? (
            <div style={{
              background: '#151515',
              border: '1px solid #333',
              borderRadius: 5,
              padding: 10
            }}>
              <div style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: 11,
                color: '#fff',
                marginBottom: 8,
                wordBreak: 'break-all',
                lineHeight: 1.3
              }}>
                {hoveredNode.name}
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 4, fontSize: 10, color: '#888' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Duration:</span>
                  <strong style={{ color: '#4ecdc4' }}>{formatDuration(hoveredNode.duration_ms)}</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Self:</span>
                  <strong style={{ color: '#4ecdc4' }}>
                    {formatDuration(hoveredNode.self_ms)}
                    ({selectedProfile ? ((hoveredNode.self_ms / selectedProfile.totalSelfMs) * 100).toFixed(1) : 0}%)
                  </strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Depth:</span>
                  <span>{hoveredNode.depth}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Call Index:</span>
                  <span>#{hoveredNode.call_index}</span>
                </div>
              </div>
            </div>
          ) : (
            <div style={{
              color: '#444',
              fontSize: 10,
              fontStyle: 'italic',
              padding: '16px 0',
              textAlign: 'center'
            }}>
              Hover over a row to see details
            </div>
          )}
        </div>
      </aside>

      {/* Main content */}
      <main style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {/* Toolbar */}
        {profiles.length > 0 && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 10,
            padding: '10px 16px',
            background: '#0d0d0d',
            borderBottom: '1px solid #1a1a1a',
            flexWrap: 'wrap'
          }}>
            <input
              type="text"
              placeholder="Search methods..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{
                background: '#1a1a1a',
                border: '1px solid #333',
                color: '#e0e0e0',
                padding: '6px 10px',
                borderRadius: 4,
                fontSize: 12,
                width: 160
              }}
            />

            {/* Depth control */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              background: '#1a1a1a',
              padding: '4px 10px',
              borderRadius: 4,
              border: '1px solid #333'
            }}>
              <span style={{ fontSize: 11, color: '#888' }}>Depth:</span>
              <button
                onClick={() => setExpandDepth(Math.max(0, expandDepth - 1))}
                disabled={expandDepth === 0}
                style={{
                  width: 22,
                  height: 22,
                  background: '#222',
                  border: '1px solid #444',
                  color: expandDepth === 0 ? '#444' : '#ccc',
                  borderRadius: 3,
                  cursor: expandDepth === 0 ? 'not-allowed' : 'pointer',
                  fontSize: 14,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                −
              </button>
              <span style={{ fontSize: 12, fontWeight: 600, color: '#4ecdc4', minWidth: 16, textAlign: 'center' }}>
                {expandDepth}
              </span>
              <button
                onClick={() => setExpandDepth(Math.min(selectedProfile?.maxDepth || 20, expandDepth + 1))}
                disabled={expandDepth >= (selectedProfile?.maxDepth || 20)}
                style={{
                  width: 22,
                  height: 22,
                  background: '#222',
                  border: '1px solid #444',
                  color: expandDepth >= (selectedProfile?.maxDepth || 20) ? '#444' : '#ccc',
                  borderRadius: 3,
                  cursor: expandDepth >= (selectedProfile?.maxDepth || 20) ? 'not-allowed' : 'pointer',
                  fontSize: 14,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                +
              </button>
            </div>

            <button onClick={handleExpandAll} style={buttonStyle}>
              Expand All
            </button>

            <button onClick={handleCollapseAll} style={buttonStyle}>
              Collapse All
            </button>

            {/* Color mode toggle */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: 2,
              background: '#1a1a1a',
              padding: 2,
              borderRadius: 4,
              border: '1px solid #333'
            }}>
              <button
                onClick={() => setColorMode('hotspot')}
                style={{
                  padding: '4px 8px',
                  fontSize: 10,
                  border: 'none',
                  borderRadius: 3,
                  cursor: 'pointer',
                  background: colorMode === 'hotspot' ? '#4ecdc4' : 'transparent',
                  color: colorMode === 'hotspot' ? '#000' : '#888'
                }}
              >
                Hotspot
              </button>
              <button
                onClick={() => setColorMode('method')}
                style={{
                  padding: '4px 8px',
                  fontSize: 10,
                  border: 'none',
                  borderRadius: 3,
                  cursor: 'pointer',
                  background: colorMode === 'method' ? '#4ecdc4' : 'transparent',
                  color: colorMode === 'method' ? '#000' : '#888'
                }}
              >
                Method
              </button>
            </div>

            {focusNode && (
              <button
                onClick={() => setFocusNode(null)}
                style={{
                  ...buttonStyle,
                  background: 'rgba(78, 205, 196, 0.15)',
                  color: '#4ecdc4',
                  borderColor: '#4ecdc4'
                }}
              >
                Reset Focus
              </button>
            )}

            {selectedProfile && (
              <div style={{ marginLeft: 'auto', display: 'flex', gap: 12, fontSize: 11, color: '#888', alignItems: 'center' }}>
                <span>Duration: <strong style={{ color: '#4ecdc4' }}>{formatDuration(selectedProfile.totalDurationMs)}</strong></span>
                <span>Calls: <strong style={{ color: '#4ecdc4' }}>{selectedProfile.nodeCount}</strong></span>
                <button
                  onClick={() => setIsMaximized(true)}
                  style={{
                    width: 28,
                    height: 28,
                    background: '#1a1a1a',
                    border: '1px solid #333',
                    color: '#888',
                    borderRadius: 4,
                    cursor: 'pointer',
                    fontSize: 16,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                  title="Maximize"
                >
                  ⊕
                </button>
              </div>
            )}
          </div>
        )}

        {/* Tree view */}
        <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
          {!selectedProfile ? (
            <div style={{
              flex: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#444',
              fontStyle: 'italic'
            }}>
              Drop a full_*.json file to visualize the call tree
            </div>
          ) : (
            <>
              {/* Column headers */}
              <div style={{
                display: 'flex',
                background: '#151515',
                borderBottom: '1px solid #2a2a2a',
                fontSize: 10,
                textTransform: 'uppercase',
                letterSpacing: 0.5,
                color: '#666'
              }}>
                <div style={{
                  width: 350,
                  minWidth: 350,
                  padding: '8px 12px',
                  borderRight: '1px solid #2a2a2a',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}>
                  <span>Service & Operation</span>
                  <span style={{ fontSize: 9, fontStyle: 'italic', textTransform: 'none', color: '#555' }}>
                    Click bar to focus
                  </span>
                </div>
                <div style={{
                  flex: 1,
                  padding: '8px 12px',
                  display: 'flex',
                  justifyContent: 'space-between'
                }}>
                  {timeMarkers.map((m, i) => (
                    <span key={i} style={{ fontFamily: "'JetBrains Mono', monospace" }}>
                      {formatDuration(m.time)}
                    </span>
                  ))}
                </div>
              </div>

              {/* Tree rows */}
              <div style={{ flex: 1, overflow: 'auto' }}>
                {filteredTree.map((node, idx) => (
                  <TreeRow
                    key={`${node.call_index}-${idx}`}
                    node={node}
                    profile={selectedProfile}
                    expandedNodes={expandedNodes}
                    toggleExpand={toggleExpand}
                    effectiveTimeRange={effectiveTimeRange}
                    onBarClick={handleBarClick}
                    focusNode={focusNode}
                    onHover={setHoveredNode}
                    colorMode={colorMode}
                    methodColors={methodColors}
                  />
                ))}
              </div>
            </>
          )}
        </div>

        {/* Legend */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 14,
          padding: '10px 16px',
          background: '#111',
          borderTop: '1px solid #1a1a1a',
          fontSize: 10,
          color: '#888'
        }}>
          {colorMode === 'hotspot' ? (
            <>
              <span>Hotspot (self time %):</span>
              {[
                { color: '#4ecdc4', label: '<1%' },
                { color: '#6bcb77', label: '1-3%' },
                { color: '#ffd93d', label: '3-8%' },
                { color: '#ffa502', label: '8-15%' },
                { color: '#ff6b6b', label: '>15%' }
              ].map((item, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                  <div style={{ width: 10, height: 10, borderRadius: 2, background: item.color }} />
                  <span>{item.label}</span>
                </div>
              ))}
            </>
          ) : (
            <>
              <span>Color by method name</span>
              <span style={{ color: '#555', fontStyle: 'italic' }}>
                (see Methods list in sidebar for color key)
              </span>
            </>
          )}
        </div>
      </main>
    </div>
  );
}
