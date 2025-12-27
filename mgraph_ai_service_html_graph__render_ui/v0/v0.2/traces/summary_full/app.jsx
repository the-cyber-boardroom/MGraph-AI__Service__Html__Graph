// Browser-compatible version - uses global React and Recharts
const { useState, useCallback, useMemo } = React;
const { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line, ComposedChart, Area } = Recharts;


// Utility to extract profile key from filename
const extractProfileKey = (filename) => {
  // Remove file extension
  let name = filename.replace(/\.json$/, '');
  
  // Remove common prefixes (summary, create_stats, speedscope, full) with underscores
  name = name.replace(/^(summary|create_stats|speedscope|full)[_]+/, '');
  
  // Clean up any remaining leading/trailing underscores
  name = name.replace(/^_+|_+$/g, '');
  
  return name || filename;
};

// Parse size from key for scaling view
const parseSize = (key) => {
  const match = key.match(/with_size__(\d+)/);
  return match ? parseInt(match[1], 10) : null;
};

// Traverse call_tree and extract all method calls
const extractCallsFromTree = (node, calls = []) => {
  if (!node) return calls;
  
  calls.push({
    name: node.name,
    duration_ms: node.duration_ms,
    self_ms: node.self_ms,
    depth: node.depth,
    call_index: node.call_index
  });
  
  if (node.children) {
    node.children.forEach(child => extractCallsFromTree(child, calls));
  }
  
  return calls;
};

// Aggregate method stats from calls
const aggregateMethodStats = (calls) => {
  const byMethod = {};
  
  calls.forEach(call => {
    if (!byMethod[call.name]) {
      byMethod[call.name] = {
        name: call.name,
        calls: [],
        count: 0,
        total_ms: 0,
        total_self_ms: 0
      };
    }
    byMethod[call.name].calls.push(call);
    byMethod[call.name].count++;
    byMethod[call.name].total_ms += call.duration_ms;
    byMethod[call.name].total_self_ms += call.self_ms;
  });
  
  return Object.values(byMethod).map(m => ({
    name: m.name,
    count: m.count,
    total_ms: m.total_ms,
    total_self_ms: m.total_self_ms,
    avg_ms: m.total_ms / m.count,
    avg_self_ms: m.total_self_ms / m.count,
    min_ms: Math.min(...m.calls.map(c => c.duration_ms)),
    max_ms: Math.max(...m.calls.map(c => c.duration_ms)),
    min_self_ms: Math.min(...m.calls.map(c => c.self_ms)),
    max_self_ms: Math.max(...m.calls.map(c => c.self_ms)),
    calls: m.calls
  }));
};

// Merge files into unified profiles
const mergeProfiles = (files, type) => {
  const grouped = {};
  
  files.forEach(f => {
    const key = extractProfileKey(f.name);
    if (!grouped[key]) grouped[key] = { key, name: key };
    
    if (type === 'summary') {
      if (f.name.includes('summary') && f.data.response_type === 'summary') {
        grouped[key].summary = f.data;
      } else if (f.name.includes('create_stats')) {
        grouped[key].stats = f.data;
      }
    } else if (type === 'full') {
      if (f.name.includes('full') && f.data.response_type === 'full') {
        grouped[key].full = f.data;
        // Extract entry_count from metadata for scaling
        grouped[key].entryCount = f.data.traces?.metadata?.entry_count || 0;
        // Pre-process call tree
        const callTree = f.data.traces?.call_tree;
        if (callTree) {
          const allCalls = [];
          callTree.forEach(root => extractCallsFromTree(root, allCalls));
          grouped[key].allCalls = allCalls;
          grouped[key].methodStats = aggregateMethodStats(allCalls);
        }
      }
    }
  });
  
  if (type === 'summary') {
    return Object.values(grouped).filter(p => p.summary || p.stats);
  } else {
    return Object.values(grouped).filter(p => p.full);
  }
};

function ProfileAnalyzer() {
  const [files, setFiles] = useState([]);
  const [analysisMode, setAnalysisMode] = useState('summary'); // 'summary' or 'full'
  const [selectedKeys, setSelectedKeys] = useState(new Set());
  const [activeTab, setActiveTab] = useState('single');
  const [sortField, setSortField] = useState('total_self_ms');
  const [sortAsc, setSortAsc] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [baselineKey, setBaselineKey] = useState(null);
  const [selectedMethod, setSelectedMethod] = useState(null);
  const [expandedNodes, setExpandedNodes] = useState(new Set());

  const summaryProfiles = useMemo(() => mergeProfiles(files, 'summary'), [files]);
  const fullProfiles = useMemo(() => mergeProfiles(files, 'full'), [files]);
  
  const profiles = analysisMode === 'summary' ? summaryProfiles : fullProfiles;
  
  const selectedProfiles = useMemo(() => 
    profiles.filter(p => selectedKeys.has(p.key)),
    [profiles, selectedKeys]
  );

  const handleDrop = useCallback(async (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    // Accept files ending with .json OR _json (for URL-encoded filenames)
    const droppedFiles = Array.from(e.dataTransfer.files).filter(f => 
      f.name.endsWith('.json') || f.name.endsWith('_json')
    );
    
    const newFiles = await Promise.all(droppedFiles.map(async (file) => {
      const text = await file.text();
      try {
        return { name: file.name, data: JSON.parse(text) };
      } catch {
        return null;
      }
    }));
    
    setFiles(prev => {
      const existing = new Set(prev.map(f => f.name));
      const unique = newFiles.filter(f => f && !existing.has(f.name));
      return [...prev, ...unique];
    });
  }, []);

  const handleProfileClick = (key) => {
    if (activeTab === 'single' || activeTab === 'methods' || activeTab === 'tree') {
      setSelectedKeys(new Set([key]));
    } else {
      setSelectedKeys(prev => {
        const next = new Set(prev);
        if (next.has(key)) next.delete(key);
        else next.add(key);
        return next;
      });
    }
  };

  const selectAll = () => setSelectedKeys(new Set(profiles.map(p => p.key)));
  const selectNone = () => setSelectedKeys(new Set());
  const clearFiles = () => { setFiles([]); setSelectedKeys(new Set()); };

  // ============== SUMMARY VIEWS ==============
  
  const SummarySingleView = ({ profile }) => {
    if (!profile) return <div className="empty-state">Select a profile from the sidebar</div>;
    
    const summary = profile.summary?.traces;
    const stats = profile.stats;
    
    if (!summary) return <div className="empty-state">No summary data available</div>;
    
    const hotspots = [...(summary.hotspots || [])].sort((a, b) => 
      sortAsc ? a[sortField] - b[sortField] : b[sortField] - a[sortField]
    );

    return (
      <div className="view-content">
        <h2 className="profile-title">{profile.name}</h2>
        
        <div className="metrics-row">
          <div className="metric-card">
            <span className="metric-value">{summary.total_duration_ms?.toFixed(2)}</span>
            <span className="metric-label">Total ms</span>
          </div>
          <div className="metric-card">
            <span className="metric-value">{summary.method_count}</span>
            <span className="metric-label">Methods</span>
          </div>
          <div className="metric-card">
            <span className="metric-value">{summary.entry_count}</span>
            <span className="metric-label">Entries</span>
          </div>
          {stats && (
            <>
              <div className="metric-card">
                <span className="metric-value">{stats.html__size}</span>
                <span className="metric-label">HTML Size</span>
              </div>
              <div className="metric-card">
                <span className="metric-value">{(stats.duration__full * 1000).toFixed(1)}</span>
                <span className="metric-label">Full (ms)</span>
              </div>
            </>
          )}
        </div>

        <div className="chart-section">
          <h3>Hotspots by Self Time</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={hotspots} layout="vertical" margin={{ left: 150, right: 30 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis type="number" stroke="#888" tickFormatter={v => `${v}ms`} />
              <YAxis type="category" dataKey="name" stroke="#888" width={140} tick={{ fontSize: 11 }} />
              <Tooltip 
                contentStyle={{ background: '#1a1a1a', border: '1px solid #333' }}
                formatter={(v, n) => [n === 'self_ms' ? `${v.toFixed(2)}ms` : `${v}%`, n === 'self_ms' ? 'Self Time' : 'Percentage']}
              />
              <Bar animationDuration={150} dataKey="self_ms" fill="#4ecdc4" name="Self Time" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="table-section">
          <h3>Hotspot Details</h3>
          <table className="data-table">
            <thead>
              <tr>
                <th>Method</th>
                <th className="sortable" onClick={() => { setSortField('self_ms'); setSortAsc(sortField === 'self_ms' ? !sortAsc : false); }}>
                  Self ms {sortField === 'self_ms' && (sortAsc ? '↑' : '↓')}
                </th>
                <th className="sortable" onClick={() => { setSortField('percentage'); setSortAsc(sortField === 'percentage' ? !sortAsc : false); }}>
                  % {sortField === 'percentage' && (sortAsc ? '↑' : '↓')}
                </th>
                <th className="sortable" onClick={() => { setSortField('calls'); setSortAsc(sortField === 'calls' ? !sortAsc : false); }}>
                  Calls {sortField === 'calls' && (sortAsc ? '↑' : '↓')}
                </th>
                <th>ms/call</th>
              </tr>
            </thead>
            <tbody>
              {hotspots.map((h, i) => (
                <tr key={i}>
                  <td className="method-name">{h.name}</td>
                  <td>{h.self_ms.toFixed(2)}</td>
                  <td>{h.percentage.toFixed(1)}%</td>
                  <td>{h.calls}</td>
                  <td>{(h.self_ms / h.calls).toFixed(3)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  const SummaryComparisonView = ({ profiles }) => {
    if (profiles.length < 2) return <div className="empty-state">Select 2+ profiles to compare</div>;
    
    const validBaseline = profiles.find(p => p.key === baselineKey);
    const baseline = validBaseline || profiles[0];
    const otherProfiles = profiles.filter(p => p.key !== baseline.key);
    
    const methodSet = new Set();
    profiles.forEach(p => {
      (p.summary?.traces?.hotspots || []).forEach(h => methodSet.add(h.name));
    });
    
    const comparisonData = Array.from(methodSet).map(method => {
      const row = { method };
      profiles.forEach(p => {
        const h = (p.summary?.traces?.hotspots || []).find(x => x.name === method);
        row[p.key] = h?.self_ms || 0;
      });
      return row;
    }).sort((a, b) => {
      const maxA = Math.max(...profiles.map(p => a[p.key] || 0));
      const maxB = Math.max(...profiles.map(p => b[p.key] || 0));
      return maxB - maxA;
    }).slice(0, 15);

    const deltas = otherProfiles.map(p => {
      const baseHotspots = baseline.summary?.traces?.hotspots || [];
      const compHotspots = p.summary?.traces?.hotspots || [];
      
      return {
        name: p.key,
        baseName: baseline.key,
        totalDelta: (p.summary?.traces?.total_duration_ms || 0) - (baseline.summary?.traces?.total_duration_ms || 0),
        methods: Array.from(methodSet).map(method => {
          const baseH = baseHotspots.find(h => h.name === method);
          const compH = compHotspots.find(h => h.name === method);
          const baseMs = baseH?.self_ms || 0;
          const compMs = compH?.self_ms || 0;
          return {
            method,
            baseMs,
            compMs,
            delta: compMs - baseMs,
            pctChange: baseMs > 0 ? ((compMs - baseMs) / baseMs) * 100 : (compMs > 0 ? 100 : 0)
          };
        }).filter(m => m.baseMs > 0 || m.compMs > 0).sort((a, b) => Math.abs(b.delta) - Math.abs(a.delta))
      };
    });

    const colors = ['#4ecdc4', '#ff6b6b', '#ffe66d', '#95e1d3', '#f38181', '#aa96da'];

    return (
      <div className="view-content">
        <div className="comparison-header">
          <h2>Comparison</h2>
          <div className="baseline-selector">
            <label>Baseline:</label>
            <select 
              value={baseline.key} 
              onChange={(e) => setBaselineKey(e.target.value)}
              className="baseline-dropdown"
            >
              {profiles.map(p => (
                <option key={p.key} value={p.key}>{p.key}</option>
              ))}
            </select>
          </div>
        </div>
        
        <div className="chart-section">
          <h3>Method Times Comparison</h3>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={comparisonData} layout="vertical" margin={{ left: 150, right: 30 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis type="number" stroke="#888" tickFormatter={v => `${v}ms`} />
              <YAxis type="category" dataKey="method" stroke="#888" width={140} tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={{ background: '#1a1a1a', border: '1px solid #333' }} />
              <Legend />
              {profiles.map((p, i) => (
                <Bar animationDuration={150} key={p.key} dataKey={p.key} fill={colors[i % colors.length]} />
              ))}
            </BarChart>
          </ResponsiveContainer>
        </div>

        {deltas.map((delta, i) => (
          <div key={i} className="delta-section">
            <h3>
              Delta: {delta.baseName} → {delta.name}
              <span className={`total-delta ${delta.totalDelta > 0 ? 'regression' : 'improvement'}`}>
                {delta.totalDelta > 0 ? '+' : ''}{delta.totalDelta.toFixed(2)}ms total
              </span>
            </h3>
            <table className="data-table delta-table">
              <thead>
                <tr>
                  <th>Method</th>
                  <th>{delta.baseName}</th>
                  <th>{delta.name}</th>
                  <th>Δ ms</th>
                  <th>Δ %</th>
                </tr>
              </thead>
              <tbody>
                {delta.methods.slice(0, 10).map((m, j) => (
                  <tr key={j} className={m.delta > 0.1 ? 'regression' : m.delta < -0.1 ? 'improvement' : ''}>
                    <td className="method-name">{m.method}</td>
                    <td>{m.baseMs.toFixed(2)}</td>
                    <td>{m.compMs.toFixed(2)}</td>
                    <td className="delta-cell">{m.delta > 0 ? '+' : ''}{m.delta.toFixed(2)}</td>
                    <td className="delta-cell">{m.pctChange > 0 ? '+' : ''}{m.pctChange.toFixed(1)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ))}
      </div>
    );
  };

  const SummaryScalingView = ({ profiles }) => {
    const scalingProfiles = profiles.filter(p => parseSize(p.key) !== null);
    
    if (scalingProfiles.length < 2) {
      return <div className="empty-state">Select 2+ profiles with size data (with_size__N) to view scaling</div>;
    }

    const scalingData = scalingProfiles
      .map(p => ({
        size: parseSize(p.key),
        total_ms: p.summary?.traces?.total_duration_ms || 0,
        entry_count: p.summary?.traces?.entry_count || 0,
        name: p.key
      }))
      .sort((a, b) => a.size - b.size);

    const methodSet = new Set();
    scalingProfiles.forEach(p => {
      (p.summary?.traces?.hotspots || []).slice(0, 5).forEach(h => methodSet.add(h.name));
    });

    const methodScaling = Array.from(methodSet).map(method => {
      return {
        method,
        data: scalingProfiles.map(p => {
          const h = (p.summary?.traces?.hotspots || []).find(x => x.name === method);
          return {
            size: parseSize(p.key),
            ms: h?.self_ms ?? null
          };
        }).sort((a, b) => a.size - b.size)
      };
    });

    const colors = ['#4ecdc4', '#ff6b6b', '#ffe66d', '#95e1d3', '#f38181', '#aa96da'];

    return (
      <div className="view-content">
        <h2>Scaling Analysis</h2>
        
        <div className="chart-section">
          <h3>Total Duration vs Input Size</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={scalingData} margin={{ left: 20, right: 30 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="size" stroke="#888" label={{ value: 'Size', position: 'bottom', fill: '#888' }} />
              <YAxis stroke="#888" tickFormatter={v => `${v}ms`} />
              <Tooltip contentStyle={{ background: '#1a1a1a', border: '1px solid #333' }} />
              <Line animationDuration={150} type="monotone" dataKey="total_ms" stroke="#4ecdc4" strokeWidth={2} dot={{ fill: '#4ecdc4' }} name="Total ms" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-section">
          <h3>Top Methods Scaling (Total Self Time)</h3>
          <ResponsiveContainer width="100%" height={350}>
            <LineChart margin={{ left: 20, right: 30 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="size" type="number" stroke="#888" allowDuplicatedCategory={false} domain={['dataMin', 'dataMax']} />
              <YAxis stroke="#888" tickFormatter={v => `${v}ms`} />
              <Tooltip contentStyle={{ background: '#1a1a1a', border: '1px solid #333' }} />
              <Legend />
              {methodScaling.map((m, i) => (
                <Line 
                  animationDuration={150}
                  key={m.method}
                  data={m.data}
                  type="monotone"
                  dataKey="ms"
                  stroke={colors[i % colors.length]}
                  strokeWidth={2}
                  dot={{ fill: colors[i % colors.length] }}
                  name={m.method.length > 25 ? m.method.slice(0, 25) + '...' : m.method}
                  connectNulls={false}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    );
  };

  // ============== FULL VIEWS ==============
  
  const FullMethodsView = ({ profile }) => {
    if (!profile) return <div className="empty-state">Select a profile from the sidebar</div>;
    if (!profile.methodStats) return <div className="empty-state">No method stats available</div>;
    
    const stats = [...profile.methodStats].sort((a, b) => 
      sortAsc ? a[sortField] - b[sortField] : b[sortField] - a[sortField]
    );
    
    const metadata = profile.full?.traces?.metadata;

    return (
      <div className="view-content">
        <h2 className="profile-title">{profile.name}</h2>
        
        <div className="metrics-row">
          <div className="metric-card">
            <span className="metric-value">{metadata?.total_duration_ms?.toFixed(2)}</span>
            <span className="metric-label">Total ms</span>
          </div>
          <div className="metric-card">
            <span className="metric-value">{metadata?.method_count}</span>
            <span className="metric-label">Methods</span>
          </div>
          <div className="metric-card">
            <span className="metric-value">{metadata?.entry_count}</span>
            <span className="metric-label">Entries</span>
          </div>
          <div className="metric-card">
            <span className="metric-value">{profile.allCalls?.length}</span>
            <span className="metric-label">Total Calls</span>
          </div>
        </div>

        <div className="chart-section">
          <h3>Methods by Total Self Time</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stats.slice(0, 15)} layout="vertical" margin={{ left: 180, right: 30 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis type="number" stroke="#888" tickFormatter={v => `${v.toFixed(2)}ms`} />
              <YAxis type="category" dataKey="name" stroke="#888" width={170} tick={{ fontSize: 11 }} />
              <Tooltip 
                contentStyle={{ background: '#1a1a1a', border: '1px solid #333' }}
                formatter={(v) => [`${v.toFixed(3)}ms`]}
              />
              <Bar animationDuration={150} dataKey="total_self_ms" fill="#4ecdc4" name="Total Self Time" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="table-section">
          <h3>Method Statistics</h3>
          <table className="data-table">
            <thead>
              <tr>
                <th>Method</th>
                <th className="sortable" onClick={() => { setSortField('count'); setSortAsc(sortField === 'count' ? !sortAsc : false); }}>
                  Calls {sortField === 'count' && (sortAsc ? '↑' : '↓')}
                </th>
                <th className="sortable" onClick={() => { setSortField('total_self_ms'); setSortAsc(sortField === 'total_self_ms' ? !sortAsc : false); }}>
                  Total Self {sortField === 'total_self_ms' && (sortAsc ? '↑' : '↓')}
                </th>
                <th className="sortable" onClick={() => { setSortField('avg_self_ms'); setSortAsc(sortField === 'avg_self_ms' ? !sortAsc : false); }}>
                  Avg Self {sortField === 'avg_self_ms' && (sortAsc ? '↑' : '↓')}
                </th>
                <th className="sortable" onClick={() => { setSortField('min_self_ms'); setSortAsc(sortField === 'min_self_ms' ? !sortAsc : false); }}>
                  Min {sortField === 'min_self_ms' && (sortAsc ? '↑' : '↓')}
                </th>
                <th className="sortable" onClick={() => { setSortField('max_self_ms'); setSortAsc(sortField === 'max_self_ms' ? !sortAsc : false); }}>
                  Max {sortField === 'max_self_ms' && (sortAsc ? '↑' : '↓')}
                </th>
                <th>Spread</th>
              </tr>
            </thead>
            <tbody>
              {stats.map((m, i) => (
                <tr 
                  key={i} 
                  className={selectedMethod === m.name ? 'selected-row' : ''}
                  onClick={() => setSelectedMethod(selectedMethod === m.name ? null : m.name)}
                  style={{ cursor: 'pointer' }}
                >
                  <td className="method-name">{m.name}</td>
                  <td>{m.count}</td>
                  <td>{m.total_self_ms.toFixed(3)}</td>
                  <td>{m.avg_self_ms.toFixed(4)}</td>
                  <td>{m.min_self_ms.toFixed(4)}</td>
                  <td>{m.max_self_ms.toFixed(4)}</td>
                  <td>{(m.max_self_ms / Math.max(m.min_self_ms, 0.0001)).toFixed(1)}x</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {selectedMethod && (
          <div className="chart-section">
            <h3>Call Distribution: {selectedMethod}</h3>
            {(() => {
              const methodData = stats.find(m => m.name === selectedMethod);
              if (!methodData) return null;
              
              const callsByIndex = methodData.calls
                .sort((a, b) => a.call_index - b.call_index)
                .map((c, i) => ({ index: i + 1, self_ms: c.self_ms, call_index: c.call_index }));
              
              return (
                <ResponsiveContainer width="100%" height={250}>
                  <ComposedChart data={callsByIndex} margin={{ left: 20, right: 30 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                    <XAxis dataKey="index" stroke="#888" label={{ value: 'Call #', position: 'bottom', fill: '#666' }} />
                    <YAxis stroke="#888" tickFormatter={v => `${v.toFixed(2)}ms`} />
                    <Tooltip 
                      contentStyle={{ background: '#1a1a1a', border: '1px solid #333' }}
                      formatter={(v) => [`${v.toFixed(4)}ms`, 'Self Time']}
                    />
                    <Area animationDuration={150} type="monotone" dataKey="self_ms" fill="rgba(78, 205, 196, 0.2)" stroke="none" />
                    <Line animationDuration={150} type="monotone" dataKey="self_ms" stroke="#4ecdc4" strokeWidth={2} dot={{ fill: '#4ecdc4', r: 3 }} />
                  </ComposedChart>
                </ResponsiveContainer>
              );
            })()}
          </div>
        )}
      </div>
    );
  };

  const FullScalingView = ({ profiles }) => {
    const [visibleMethods, setVisibleMethods] = useState(null); // null = all visible initially
    const [hoveredMethod, setHoveredMethod] = useState(null);
    const [expandedChart, setExpandedChart] = useState(null); // null, 'overall', 'methods'
    
    // Filter to profiles that have method stats and sort by entry count
    const scalingProfiles = profiles
      .filter(p => p.methodStats && p.entryCount > 0)
      .sort((a, b) => a.entryCount - b.entryCount);
    
    if (scalingProfiles.length < 2) {
      return <div className="empty-state">Select 2+ full profiles to view scaling analysis</div>;
    }

    // Get all methods across profiles
    const methodSet = new Set();
    scalingProfiles.forEach(p => {
      p.methodStats.slice(0, 12).forEach(m => methodSet.add(m.name));
    });
    
    const allMethods = Array.from(methodSet);
    
    // Initialize visible methods on first render
    const effectiveVisible = visibleMethods || new Set(allMethods);

    // Build scaling data for avg_ms per call - use entryCount as X axis
    const avgMsScaling = allMethods.map(method => {
      return {
        method,
        data: scalingProfiles.map(p => {
          const m = p.methodStats.find(x => x.name === method);
          return {
            entryCount: p.entryCount,
            avg_ms: m?.avg_self_ms ?? null,
            count: m?.count ?? 0,
            total_self_ms: m?.total_self_ms ?? null,
            name: p.key
          };
        })
      };
    });

    // Overall scaling data
    const overallScaling = scalingProfiles
      .map(p => ({
        entryCount: p.entryCount,
        name: p.key,
        total_ms: p.full?.traces?.metadata?.total_duration_ms || 0,
        call_count: p.allCalls?.length || 0,
        avg_per_call: (p.full?.traces?.metadata?.total_duration_ms || 0) / (p.allCalls?.length || 1)
      }));

    const colors = ['#4ecdc4', '#ff6b6b', '#ffe66d', '#95e1d3', '#f38181', '#aa96da', '#74b9ff', '#fd79a8', '#a29bfe', '#ffeaa7', '#dfe6e9', '#00b894'];
    
    const toggleMethod = (method) => {
      setVisibleMethods(prev => {
        const current = prev || new Set(allMethods);
        const next = new Set(current);
        if (next.has(method)) {
          next.delete(method);
        } else {
          next.add(method);
        }
        return next;
      });
    };
    
    const selectAllMethods = () => setVisibleMethods(new Set(allMethods));
    const selectNoneMethods = () => setVisibleMethods(new Set());
    
    // Filter to only visible methods for the chart
    const visibleScaling = avgMsScaling.filter(m => effectiveVisible.has(m.method));
    
    // Get hovered method data for tooltip
    const hoveredData = hoveredMethod ? avgMsScaling.find(m => m.method === hoveredMethod) : null;

    const toggleExpand = (chartId) => {
      setExpandedChart(prev => prev === chartId ? null : chartId);
    };

    const ChartHeader = ({ title, chartId, note }) => (
      <div className="chart-header">
        <div>
          <h3>{title}</h3>
          {note && <p className="chart-note">{note}</p>}
        </div>
        <button 
          className="expand-btn" 
          onClick={() => toggleExpand(chartId)}
          title={expandedChart === chartId ? 'Minimize' : 'Maximize'}
        >
          {expandedChart === chartId ? '✕' : '⊕'}
        </button>
      </div>
    );

    const isExpanded = (chartId) => expandedChart === chartId;

    // Render expanded chart as overlay
    const renderExpandedOverlay = () => {
      if (!expandedChart) return null;
      
      return (
        <div className="chart-overlay" onClick={(e) => { if (e.target.className === 'chart-overlay') toggleExpand(null); }}>
          <div className="chart-overlay-content">
            {expandedChart === 'overall' && (
              <>
                <ChartHeader title="Overall: Avg ms per Call vs Entry Count" chartId="overall" />
                <div className="chart-overlay-body">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={overallScaling} margin={{ left: 20, right: 30, top: 20, bottom: 20 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                      <XAxis dataKey="entryCount" stroke="#888" tickFormatter={v => v >= 1000 ? `${(v/1000).toFixed(1)}k` : v} />
                      <YAxis stroke="#888" tickFormatter={v => `${v.toFixed(3)}ms`} />
                      <Tooltip 
                        contentStyle={{ background: '#1a1a1a', border: '1px solid #333' }} 
                        formatter={(v, name) => [name === 'avg_per_call' ? `${v.toFixed(4)}ms` : v, name === 'avg_per_call' ? 'Avg/Call' : name]}
                        labelFormatter={(v) => `Entries: ${v}`}
                      />
                      <Line animationDuration={150} type="monotone" dataKey="avg_per_call" stroke="#4ecdc4" strokeWidth={2} dot={{ fill: '#4ecdc4' }} name="Avg ms/call" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </>
            )}
            {expandedChart === 'methods' && (
              <>
                <ChartHeader 
                  title="Method Avg Self Time per Call vs Entry Count" 
                  chartId="methods"
                  note="Flat lines = O(1) per call (good). Rising lines = O(n) per call (investigate). Click a line to hide it."
                />
                <div className="chart-overlay-body">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart margin={{ left: 20, right: 30, top: 20, bottom: 20 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                      <XAxis dataKey="entryCount" type="number" stroke="#888" allowDuplicatedCategory={false} domain={['dataMin', 'dataMax']} tickFormatter={v => v >= 1000 ? `${(v/1000).toFixed(1)}k` : v} />
                      <YAxis stroke="#888" tickFormatter={v => `${v.toFixed(3)}ms`} />
                      <Tooltip content={() => null} />
                      <Legend />
                      {visibleScaling.map((m, i) => {
                        const colorIndex = allMethods.indexOf(m.method);
                        const isHovered = hoveredMethod === m.method;
                        const hasHover = hoveredMethod !== null;
                        return (
                          <Line 
                            animationDuration={150}
                            key={m.method}
                            data={m.data}
                            type="monotone"
                            dataKey="avg_ms"
                            stroke={colors[colorIndex % colors.length]}
                            strokeWidth={isHovered ? 4 : 2}
                            strokeOpacity={hasHover && !isHovered ? 0.25 : 1}
                            dot={{ fill: colors[colorIndex % colors.length], r: isHovered ? 5 : 3 }}
                            name={m.method.length > 30 ? m.method.slice(0, 30) + '...' : m.method}
                            connectNulls={false}
                            onMouseEnter={() => setHoveredMethod(m.method)}
                            onMouseLeave={() => setHoveredMethod(null)}
                            onClick={() => toggleMethod(m.method)}
                            style={{ cursor: 'pointer' }}
                          />
                        );
                      })}
                    </LineChart>
                  </ResponsiveContainer>
                </div>
                <div className={`chart-tooltip-below ${hoveredMethod ? 'visible' : ''}`}>
                  {hoveredData && (
                    <>
                      <div className="tooltip-method">
                        <span 
                          className="tooltip-color" 
                          style={{ background: colors[allMethods.indexOf(hoveredData.method) % colors.length] }}
                        />
                        <strong>{hoveredData.method}</strong>
                        <span className="tooltip-action">(click line to hide)</span>
                      </div>
                      <div className="tooltip-values">
                        {hoveredData.data.map((d, i) => (
                          <div key={i} className="tooltip-value-item">
                            <span className="tooltip-size">{d.entryCount}:</span>
                            <span className="tooltip-ms">{d.avg_ms !== null ? `${d.avg_ms.toFixed(4)}ms` : '-'}</span>
                            <span className="tooltip-calls">({d.count} calls)</span>
                          </div>
                        ))}
                      </div>
                    </>
                  )}
                  {!hoveredMethod && (
                    <div className="tooltip-hint">Hover over a line to see details, click to hide it</div>
                  )}
                </div>
              </>
            )}
          </div>
        </div>
      );
    };

    return (
      <div className="view-content">
        <h2>Per-Call Scaling Analysis</h2>
        <p className="view-description">This view shows average time per call vs entry count - useful for detecting O(n) behavior within methods.</p>
        
        {renderExpandedOverlay()}
        
        <div className="chart-section">
          <ChartHeader title="Overall: Avg ms per Call vs Entry Count" chartId="overall" />
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={overallScaling} margin={{ left: 20, right: 30 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="entryCount" stroke="#888" tickFormatter={v => v >= 1000 ? `${(v/1000).toFixed(1)}k` : v} />
              <YAxis stroke="#888" tickFormatter={v => `${v.toFixed(3)}ms`} />
              <Tooltip 
                contentStyle={{ background: '#1a1a1a', border: '1px solid #333' }} 
                formatter={(v, name) => [name === 'avg_per_call' ? `${v.toFixed(4)}ms` : v, name === 'avg_per_call' ? 'Avg/Call' : name]}
                labelFormatter={(v) => `Entries: ${v}`}
              />
              <Line animationDuration={150} type="monotone" dataKey="avg_per_call" stroke="#4ecdc4" strokeWidth={2} dot={{ fill: '#4ecdc4' }} name="Avg ms/call" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-section">
          <ChartHeader 
            title="Method Avg Self Time per Call vs Entry Count" 
            chartId="methods"
            note="Flat lines = O(1) per call (good). Rising lines = O(n) per call (investigate). Click a line to hide it."
          />
          <ResponsiveContainer width="100%" height={400}>
            <LineChart margin={{ left: 20, right: 30 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="entryCount" type="number" stroke="#888" allowDuplicatedCategory={false} domain={['dataMin', 'dataMax']} tickFormatter={v => v >= 1000 ? `${(v/1000).toFixed(1)}k` : v} />
              <YAxis stroke="#888" tickFormatter={v => `${v.toFixed(3)}ms`} />
              <Tooltip content={() => null} />
              <Legend />
              {visibleScaling.map((m, i) => {
                const colorIndex = allMethods.indexOf(m.method);
                const isHovered = hoveredMethod === m.method;
                const hasHover = hoveredMethod !== null;
                return (
                  <Line 
                    animationDuration={150}
                    key={m.method}
                    data={m.data}
                    type="monotone"
                    dataKey="avg_ms"
                    stroke={colors[colorIndex % colors.length]}
                    strokeWidth={isHovered ? 4 : 2}
                    strokeOpacity={hasHover && !isHovered ? 0.25 : 1}
                    dot={{ fill: colors[colorIndex % colors.length], r: isHovered ? 5 : 3 }}
                    name={m.method.length > 30 ? m.method.slice(0, 30) + '...' : m.method}
                    connectNulls={false}
                    onMouseEnter={() => setHoveredMethod(m.method)}
                    onMouseLeave={() => setHoveredMethod(null)}
                    onClick={() => toggleMethod(m.method)}
                    style={{ cursor: 'pointer' }}
                  />
                );
              })}
            </LineChart>
          </ResponsiveContainer>
          
          <div className={`chart-tooltip-below ${hoveredMethod ? 'visible' : ''}`}>
            {hoveredData && (
              <>
                <div className="tooltip-method">
                  <span 
                    className="tooltip-color" 
                    style={{ background: colors[allMethods.indexOf(hoveredData.method) % colors.length] }}
                  />
                  <strong>{hoveredData.method}</strong>
                  <span className="tooltip-action">(click line to hide)</span>
                </div>
                <div className="tooltip-values">
                  {hoveredData.data.map((d, i) => (
                    <div key={i} className="tooltip-value-item">
                      <span className="tooltip-size">{d.entryCount}:</span>
                      <span className="tooltip-ms">{d.avg_ms !== null ? `${d.avg_ms.toFixed(4)}ms` : '-'}</span>
                      <span className="tooltip-calls">({d.count} calls)</span>
                    </div>
                  ))}
                </div>
              </>
            )}
            {!hoveredMethod && (
              <div className="tooltip-hint">Hover over a line to see details, click to hide it</div>
            )}
          </div>
        </div>

        <div className="table-section">
          <div className="table-header-row">
            <h3>Method Scaling Data</h3>
            <div className="table-actions">
              <button className="sidebar-btn" onClick={selectAllMethods}>Show All</button>
              <button className="sidebar-btn" onClick={selectNoneMethods}>Hide All</button>
            </div>
          </div>
          <table className="data-table scaling-method-table">
            <thead>
              <tr>
                <th style={{ width: '40px' }}>Show</th>
                <th>Method</th>
                {scalingProfiles.map(p => (
                  <th key={p.key} colSpan={2} title={p.key}>{p.entryCount >= 1000 ? `${(p.entryCount/1000).toFixed(1)}k` : p.entryCount}</th>
                ))}
                <th>Trend</th>
              </tr>
              <tr className="subheader">
                <th></th>
                <th></th>
                {scalingProfiles.map(p => (
                  <React.Fragment key={p.key}>
                    <th>avg/call</th>
                    <th>calls</th>
                  </React.Fragment>
                ))}
                <th></th>
              </tr>
            </thead>
            <tbody>
              {avgMsScaling.map((m, i) => {
                const isVisible = effectiveVisible.has(m.method);
                const firstVal = m.data[0]?.avg_ms;
                const lastVal = m.data[m.data.length - 1]?.avg_ms;
                const trend = (firstVal && lastVal) ? ((lastVal - firstVal) / firstVal * 100) : 0;
                const trendClass = Math.abs(trend) < 20 ? 'flat' : trend > 0 ? 'rising' : 'falling';
                const isHovered = hoveredMethod === m.method;
                
                return (
                  <tr 
                    key={i} 
                    className={`${isVisible ? '' : 'row-hidden'} ${isHovered ? 'row-hovered' : ''}`}
                    style={{ opacity: isVisible ? 1 : 0.5 }}
                    onMouseEnter={() => setHoveredMethod(m.method)}
                    onMouseLeave={() => setHoveredMethod(null)}
                  >
                    <td style={{ textAlign: 'center' }}>
                      <input 
                        type="checkbox" 
                        checked={isVisible}
                        onChange={() => toggleMethod(m.method)}
                        className="method-toggle"
                      />
                    </td>
                    <td className="method-name">
                      <span 
                        className="method-color-dot" 
                        style={{ background: colors[allMethods.indexOf(m.method) % colors.length] }}
                      />
                      {m.method}
                    </td>
                    {m.data.map((d, j) => (
                      <React.Fragment key={j}>
                        <td>{d.avg_ms !== null ? d.avg_ms.toFixed(4) : '-'}</td>
                        <td className="calls-col">{d.count || '-'}</td>
                      </React.Fragment>
                    ))}
                    <td className={`trend-cell ${trendClass}`}>
                      {trendClass === 'flat' ? '→' : trendClass === 'rising' ? '↑' : '↓'}
                      {Math.abs(trend).toFixed(0)}%
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <div className="table-section">
          <h3>Overall Scaling Data</h3>
          <table className="data-table">
            <thead>
              <tr>
                <th>Profile</th>
                <th>Entry Count</th>
                <th>Total ms</th>
                <th>Call Count</th>
                <th>Avg ms/call</th>
              </tr>
            </thead>
            <tbody>
              {overallScaling.map((d, i) => (
                <tr key={i}>
                  <td className="method-name">{d.name}</td>
                  <td>{d.entryCount}</td>
                  <td>{d.total_ms.toFixed(2)}</td>
                  <td>{d.call_count}</td>
                  <td>{d.avg_per_call.toFixed(4)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  const FullTreeView = ({ profile }) => {
    if (!profile) return <div className="empty-state">Select a profile from the sidebar</div>;
    
    const callTree = profile.full?.traces?.call_tree;
    if (!callTree) return <div className="empty-state">No call tree data available</div>;

    const toggleNode = (path) => {
      setExpandedNodes(prev => {
        const next = new Set(prev);
        if (next.has(path)) next.delete(path);
        else next.add(path);
        return next;
      });
    };

    const renderNode = (node, path = '0', depth = 0) => {
      const hasChildren = node.children && node.children.length > 0;
      const isExpanded = expandedNodes.has(path);
      const selfPct = ((node.self_ms / (profile.full?.traces?.metadata?.total_duration_ms || 1)) * 100);
      
      return (
        <div key={path} className="tree-node">
          <div 
            className={`tree-row ${hasChildren ? 'expandable' : ''}`}
            style={{ paddingLeft: `${depth * 20 + 8}px` }}
            onClick={() => hasChildren && toggleNode(path)}
          >
            <span className="tree-toggle">
              {hasChildren ? (isExpanded ? '▼' : '▶') : '○'}
            </span>
            <span className="tree-name">{node.name}</span>
            <span className="tree-duration">{node.duration_ms.toFixed(3)}ms</span>
            <span className="tree-self">(self: {node.self_ms.toFixed(3)}ms)</span>
            <span className="tree-pct" style={{ 
              background: `rgba(78, 205, 196, ${Math.min(selfPct / 20, 1)})` 
            }}>
              {selfPct.toFixed(1)}%
            </span>
          </div>
          {hasChildren && isExpanded && (
            <div className="tree-children">
              {node.children.map((child, i) => renderNode(child, `${path}-${i}`, depth + 1))}
            </div>
          )}
        </div>
      );
    };

    return (
      <div className="view-content">
        <h2 className="profile-title">{profile.name} - Call Tree</h2>
        <div className="tree-actions">
          <button className="sidebar-btn" onClick={() => setExpandedNodes(new Set())}>Collapse All</button>
          <button className="sidebar-btn" onClick={() => {
            const allPaths = new Set();
            const collectPaths = (node, path = '0') => {
              allPaths.add(path);
              node.children?.forEach((c, i) => collectPaths(c, `${path}-${i}`));
            };
            callTree.forEach((root, i) => collectPaths(root, `${i}`));
            setExpandedNodes(allPaths);
          }}>Expand All</button>
        </div>
        <div className="tree-container">
          {callTree.map((root, i) => renderNode(root, `${i}`, 0))}
        </div>
      </div>
    );
  };

  // Determine which tabs to show based on mode
  const summaryTabs = [
    { key: 'single', label: 'Single Profile' },
    { key: 'compare', label: 'Comparison' },
    { key: 'scaling', label: 'Scaling' }
  ];

  const fullTabs = [
    { key: 'methods', label: 'Method Stats' },
    { key: 'scaling', label: 'Per-Call Scaling' },
    { key: 'tree', label: 'Call Tree' }
  ];

  const currentTabs = analysisMode === 'summary' ? summaryTabs : fullTabs;

  // Reset tab when switching modes
  const handleModeChange = (mode) => {
    setAnalysisMode(mode);
    setActiveTab(mode === 'summary' ? 'single' : 'methods');
    setSelectedKeys(new Set());
  };

  return (
    <div className="analyzer">
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Space+Grotesk:wght@400;500;600&display=swap');
        
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        .analyzer {
          font-family: 'Space Grotesk', sans-serif;
          background: #0d0d0d;
          color: #e0e0e0;
          min-height: 100vh;
          display: grid;
          grid-template-columns: 280px 1fr;
          grid-template-rows: auto 1fr;
        }
        
        .header {
          grid-column: 1 / -1;
          background: linear-gradient(180deg, #1a1a1a 0%, #0d0d0d 100%);
          border-bottom: 1px solid #2a2a2a;
          padding: 16px 24px;
          display: flex;
          align-items: center;
          gap: 24px;
        }
        
        .logo {
          font-family: 'JetBrains Mono', monospace;
          font-weight: 600;
          font-size: 18px;
          color: #4ecdc4;
          letter-spacing: -0.5px;
        }
        
        .mode-toggle {
          display: flex;
          background: #1a1a1a;
          border-radius: 6px;
          padding: 4px;
          gap: 4px;
        }
        
        .mode-btn {
          padding: 8px 16px;
          font-size: 12px;
          font-family: inherit;
          background: transparent;
          border: none;
          color: #888;
          cursor: pointer;
          border-radius: 4px;
          transition: all 0.15s;
        }
        
        .mode-btn:hover {
          color: #ccc;
        }
        
        .mode-btn.active {
          background: #4ecdc4;
          color: #0d0d0d;
          font-weight: 500;
        }
        
        .drop-zone {
          flex: 1;
          border: 2px dashed #333;
          border-radius: 8px;
          padding: 12px 20px;
          text-align: center;
          color: #666;
          font-size: 13px;
          transition: all 0.2s;
          cursor: pointer;
        }
        
        .drop-zone.dragging {
          border-color: #4ecdc4;
          background: rgba(78, 205, 196, 0.1);
          color: #4ecdc4;
        }
        
        .sidebar {
          background: #111;
          border-right: 1px solid #2a2a2a;
          padding: 16px;
          overflow-y: auto;
        }
        
        .sidebar-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
          padding-bottom: 12px;
          border-bottom: 1px solid #2a2a2a;
        }
        
        .sidebar-title {
          font-size: 11px;
          text-transform: uppercase;
          letter-spacing: 1px;
          color: #666;
        }
        
        .sidebar-actions {
          display: flex;
          gap: 8px;
        }
        
        .sidebar-btn {
          font-size: 10px;
          padding: 4px 8px;
          background: #1a1a1a;
          border: 1px solid #333;
          color: #888;
          border-radius: 4px;
          cursor: pointer;
          font-family: inherit;
        }
        
        .sidebar-btn:hover {
          background: #222;
          color: #ccc;
        }
        
        .profile-item {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 10px 12px;
          border-radius: 6px;
          cursor: pointer;
          transition: background 0.15s;
          margin-bottom: 4px;
        }
        
        .profile-item:hover {
          background: #1a1a1a;
        }
        
        .profile-item.selected {
          background: rgba(78, 205, 196, 0.15);
        }
        
        .profile-checkbox {
          width: 16px;
          height: 16px;
          accent-color: #4ecdc4;
        }
        
        .profile-info {
          flex: 1;
          min-width: 0;
        }
        
        .profile-name {
          font-family: 'JetBrains Mono', monospace;
          font-size: 12px;
          color: #ccc;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
        
        .profile-meta {
          font-size: 10px;
          color: #555;
          margin-top: 2px;
        }
        
        .main {
          display: flex;
          flex-direction: column;
          overflow: hidden;
        }
        
        .tabs {
          display: flex;
          gap: 0;
          background: #111;
          border-bottom: 1px solid #2a2a2a;
          padding: 0 24px;
        }
        
        .tab {
          padding: 14px 24px;
          font-size: 13px;
          color: #666;
          cursor: pointer;
          border-bottom: 2px solid transparent;
          transition: all 0.15s;
          font-family: inherit;
          background: none;
          border-top: none;
          border-left: none;
          border-right: none;
        }
        
        .tab:hover {
          color: #aaa;
        }
        
        .tab.active {
          color: #4ecdc4;
          border-bottom-color: #4ecdc4;
        }
        
        .content {
          flex: 1;
          overflow-y: auto;
          padding: 24px;
        }
        
        .view-content {
          max-width: 1200px;
        }
        
        .view-description {
          color: #888;
          font-size: 13px;
          margin-bottom: 24px;
        }
        
        .chart-note {
          color: #666;
          font-size: 12px;
          margin: -12px 0 16px 0;
          font-style: italic;
        }
        
        .empty-state {
          color: #444;
          font-size: 14px;
          text-align: center;
          padding: 60px 20px;
        }
        
        .profile-title {
          font-family: 'JetBrains Mono', monospace;
          font-size: 20px;
          color: #4ecdc4;
          margin-bottom: 24px;
        }
        
        h2 {
          font-size: 18px;
          margin-bottom: 24px;
          font-weight: 500;
        }
        
        h3 {
          font-size: 13px;
          color: #888;
          margin-bottom: 16px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          display: flex;
          align-items: center;
          gap: 12px;
        }
        
        .metrics-row {
          display: flex;
          gap: 16px;
          margin-bottom: 32px;
          flex-wrap: wrap;
        }
        
        .metric-card {
          background: #151515;
          border: 1px solid #2a2a2a;
          border-radius: 8px;
          padding: 16px 24px;
          display: flex;
          flex-direction: column;
          min-width: 120px;
        }
        
        .metric-value {
          font-family: 'JetBrains Mono', monospace;
          font-size: 24px;
          font-weight: 600;
          color: #fff;
        }
        
        .metric-label {
          font-size: 11px;
          color: #666;
          margin-top: 4px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
        
        .chart-section {
          background: #111;
          border: 1px solid #2a2a2a;
          border-radius: 8px;
          padding: 20px;
          margin-bottom: 24px;
        }
        
        .chart-section h3 {
          margin-bottom: 20px;
        }
        
        .table-section, .delta-section, .scaling-table {
          margin-bottom: 24px;
        }
        
        .data-table {
          width: 100%;
          border-collapse: collapse;
          font-size: 13px;
        }
        
        .data-table th {
          text-align: left;
          padding: 12px 16px;
          background: #151515;
          border-bottom: 1px solid #2a2a2a;
          font-weight: 500;
          color: #888;
          font-size: 11px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
        
        .data-table th.sortable {
          cursor: pointer;
        }
        
        .data-table th.sortable:hover {
          color: #4ecdc4;
        }
        
        .data-table td {
          padding: 10px 16px;
          border-bottom: 1px solid #1a1a1a;
          font-family: 'JetBrains Mono', monospace;
          font-size: 12px;
        }
        
        .data-table tr:hover {
          background: #151515;
        }
        
        .data-table tr.selected-row {
          background: rgba(78, 205, 196, 0.15);
        }
        
        .method-name {
          color: #4ecdc4;
          max-width: 280px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        
        .delta-table tr.improvement {
          background: rgba(78, 205, 196, 0.1);
        }
        
        .delta-table tr.regression {
          background: rgba(255, 107, 107, 0.1);
        }
        
        .delta-cell {
          font-weight: 500;
        }
        
        .improvement .delta-cell {
          color: #4ecdc4;
        }
        
        .regression .delta-cell {
          color: #ff6b6b;
        }
        
        .total-delta {
          font-family: 'JetBrains Mono', monospace;
          font-size: 12px;
          padding: 4px 10px;
          border-radius: 4px;
          margin-left: auto;
        }
        
        .total-delta.improvement {
          background: rgba(78, 205, 196, 0.2);
          color: #4ecdc4;
        }
        
        .total-delta.regression {
          background: rgba(255, 107, 107, 0.2);
          color: #ff6b6b;
        }
        
        .recharts-legend-item-text {
          font-size: 11px !important;
          color: #888 !important;
        }
        
        .comparison-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 24px;
        }
        
        .comparison-header h2 {
          margin-bottom: 0;
        }
        
        .baseline-selector {
          display: flex;
          align-items: center;
          gap: 10px;
        }
        
        .baseline-selector label {
          font-size: 12px;
          color: #888;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
        
        .baseline-dropdown {
          background: #1a1a1a;
          border: 1px solid #333;
          color: #e0e0e0;
          padding: 8px 12px;
          border-radius: 6px;
          font-family: 'JetBrains Mono', monospace;
          font-size: 12px;
          cursor: pointer;
          min-width: 160px;
        }
        
        .baseline-dropdown:hover {
          border-color: #4ecdc4;
        }
        
        .baseline-dropdown:focus {
          outline: none;
          border-color: #4ecdc4;
        }
        
        .baseline-dropdown option {
          background: #1a1a1a;
          color: #e0e0e0;
        }
        
        /* Tree View Styles */
        .tree-actions {
          display: flex;
          gap: 8px;
          margin-bottom: 16px;
        }
        
        .tree-container {
          background: #111;
          border: 1px solid #2a2a2a;
          border-radius: 8px;
          padding: 16px;
          font-family: 'JetBrains Mono', monospace;
          font-size: 12px;
          max-height: 600px;
          overflow-y: auto;
        }
        
        .tree-node {
          user-select: none;
        }
        
        .tree-row {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 6px 8px;
          border-radius: 4px;
          transition: background 0.1s;
        }
        
        .tree-row:hover {
          background: #1a1a1a;
        }
        
        .tree-row.expandable {
          cursor: pointer;
        }
        
        .tree-toggle {
          width: 16px;
          color: #666;
          font-size: 10px;
        }
        
        .tree-name {
          color: #4ecdc4;
          flex: 1;
        }
        
        .tree-duration {
          color: #fff;
          min-width: 80px;
          text-align: right;
        }
        
        .tree-self {
          color: #888;
          min-width: 100px;
        }
        
        .tree-pct {
          color: #fff;
          padding: 2px 6px;
          border-radius: 3px;
          font-size: 10px;
          min-width: 50px;
          text-align: center;
        }
        
        .tree-children {
          border-left: 1px solid #2a2a2a;
          margin-left: 16px;
        }
        
        .table-header-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }
        
        .table-header-row h3 {
          margin-bottom: 0;
        }
        
        .table-actions {
          display: flex;
          gap: 8px;
        }
        
        .scaling-method-table {
          font-size: 11px;
        }
        
        .scaling-method-table th {
          padding: 8px 10px;
          font-size: 10px;
        }
        
        .scaling-method-table td {
          padding: 6px 10px;
          font-size: 11px;
        }
        
        .scaling-method-table .subheader th {
          font-size: 9px;
          color: #555;
          font-weight: 400;
          padding-top: 0;
          background: #151515;
        }
        
        .scaling-method-table .calls-col {
          color: #666;
          border-right: 1px solid #2a2a2a;
        }
        
        .method-toggle {
          width: 14px;
          height: 14px;
          accent-color: #4ecdc4;
          cursor: pointer;
        }
        
        .row-hidden {
          opacity: 0.5;
        }
        
        .trend-cell {
          font-weight: 600;
          text-align: center;
        }
        
        .trend-cell.flat {
          color: #4ecdc4;
        }
        
        .trend-cell.rising {
          color: #ff6b6b;
        }
        
        .trend-cell.falling {
          color: #95e1d3;
        }
        
        /* Chart header with expand button */
        .chart-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 16px;
        }
        
        .chart-header h3 {
          margin-bottom: 4px;
        }
        
        .chart-header .chart-note {
          margin: 0;
        }
        
        .expand-btn {
          background: #1a1a1a;
          border: 1px solid #333;
          color: #888;
          width: 32px;
          height: 32px;
          border-radius: 6px;
          font-size: 18px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.15s;
          flex-shrink: 0;
        }
        
        .expand-btn:hover {
          background: #222;
          color: #4ecdc4;
          border-color: #4ecdc4;
        }
        
        .chart-section.expanded {
          position: relative;
        }
        
        /* Full screen chart overlay */
        .chart-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.85);
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
          display: flex;
          flex-direction: column;
          padding: 24px;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        }
        
        .chart-overlay-content .chart-header {
          flex-shrink: 0;
        }
        
        .chart-overlay-content .chart-header h3 {
          font-size: 16px;
        }
        
        .chart-overlay-body {
          flex: 1;
          min-height: 0;
        }
        
        .chart-overlay-content .chart-tooltip-below {
          flex-shrink: 0;
          margin-top: 16px;
        }
        
        .chart-overlay-content .expand-btn {
          width: 36px;
          height: 36px;
          font-size: 20px;
        }
        
        /* Custom tooltip below chart */
        .chart-tooltip-below {
          background: #1a1a1a;
          border: 1px solid #333;
          border-radius: 6px;
          padding: 12px 16px;
          margin-top: 16px;
          height: 72px;
          overflow: hidden;
          transition: border-color 0.15s;
        }
        
        .chart-tooltip-below.visible {
          border-color: #4ecdc4;
        }
        
        .tooltip-method {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 8px;
        }
        
        .tooltip-color {
          width: 12px;
          height: 12px;
          border-radius: 2px;
          flex-shrink: 0;
        }
        
        .tooltip-method strong {
          color: #fff;
          font-family: 'JetBrains Mono', monospace;
          font-size: 13px;
        }
        
        .tooltip-action {
          color: #666;
          font-size: 11px;
          margin-left: auto;
        }
        
        .tooltip-values {
          display: flex;
          gap: 24px;
          flex-wrap: wrap;
        }
        
        .tooltip-value-item {
          display: flex;
          align-items: center;
          gap: 6px;
          font-family: 'JetBrains Mono', monospace;
          font-size: 12px;
        }
        
        .tooltip-size {
          color: #888;
        }
        
        .tooltip-ms {
          color: #4ecdc4;
          font-weight: 500;
        }
        
        .tooltip-calls {
          color: #555;
          font-size: 10px;
        }
        
        .tooltip-hint {
          color: #555;
          font-size: 12px;
          font-style: italic;
          line-height: 48px;
        }
        
        /* Method color dot in table */
        .method-color-dot {
          display: inline-block;
          width: 8px;
          height: 8px;
          border-radius: 2px;
          margin-right: 8px;
          flex-shrink: 0;
        }
        
        /* Row hover highlight */
        .scaling-method-table tr.row-hovered {
          background: rgba(78, 205, 196, 0.15) !important;
        }
        
        .scaling-method-table tr {
          cursor: pointer;
        }
        
        /* Recharts line hover cursor */
        .recharts-line-curve {
          cursor: pointer;
        }
      `}</style>

      <header className="header">
        <div className="logo">◈ Profile Analyzer</div>
        <div className="mode-toggle">
          <button 
            className={`mode-btn ${analysisMode === 'summary' ? 'active' : ''}`}
            onClick={() => handleModeChange('summary')}
          >
            Summary
          </button>
          <button 
            className={`mode-btn ${analysisMode === 'full' ? 'active' : ''}`}
            onClick={() => handleModeChange('full')}
          >
            Full
          </button>
        </div>
        <div 
          className={`drop-zone ${isDragging ? 'dragging' : ''}`}
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
        >
          {isDragging ? 'Drop JSON files here' : `Drag & drop ${analysisMode} JSON files`}
        </div>
      </header>

      <aside className="sidebar">
        <div className="sidebar-header">
          <span className="sidebar-title">Profiles ({profiles.length})</span>
          <div className="sidebar-actions">
            <button className="sidebar-btn" onClick={selectAll}>All</button>
            <button className="sidebar-btn" onClick={selectNone}>None</button>
            <button className="sidebar-btn" onClick={clearFiles}>Clear</button>
          </div>
        </div>
        {profiles.length === 0 && (
          <div className="empty-state" style={{ padding: '20px 0', fontSize: '12px' }}>
            Drop {analysisMode} files to begin
          </div>
        )}
        {profiles.map(p => (
          <div 
            key={p.key} 
            className={`profile-item ${selectedKeys.has(p.key) ? 'selected' : ''}`}
            onClick={() => handleProfileClick(p.key)}
          >
            <input 
              type={['single', 'methods', 'tree'].includes(activeTab) ? 'radio' : 'checkbox'}
              className="profile-checkbox"
              checked={selectedKeys.has(p.key)}
              onChange={() => {}}
              name="profile-select"
            />
            <div className="profile-info">
              <div className="profile-name">{p.key}</div>
              <div className="profile-meta">
                {analysisMode === 'summary' && p.summary && `${p.summary.traces?.total_duration_ms?.toFixed(1)}ms`}
                {analysisMode === 'summary' && p.summary && p.stats && ' · '}
                {analysisMode === 'summary' && p.stats && `size: ${p.stats.html__size}`}
                {analysisMode === 'full' && p.full && `${p.full.traces?.metadata?.total_duration_ms?.toFixed(1)}ms · ${p.allCalls?.length} calls`}
              </div>
            </div>
          </div>
        ))}
      </aside>

      <main className="main">
        <nav className="tabs">
          {currentTabs.map(tab => (
            <button 
              key={tab.key}
              className={`tab ${activeTab === tab.key ? 'active' : ''}`} 
              onClick={() => setActiveTab(tab.key)}
            >
              {tab.label}
            </button>
          ))}
        </nav>
        <div className="content">
          {analysisMode === 'summary' && (
            <>
              {activeTab === 'single' && <SummarySingleView profile={selectedProfiles[0]} />}
              {activeTab === 'compare' && <SummaryComparisonView profiles={selectedProfiles} />}
              {activeTab === 'scaling' && <SummaryScalingView profiles={selectedProfiles} />}
            </>
          )}
          {analysisMode === 'full' && (
            <>
              {activeTab === 'methods' && <FullMethodsView profile={selectedProfiles[0]} />}
              {activeTab === 'scaling' && <FullScalingView profiles={selectedProfiles} />}
              {activeTab === 'tree' && <FullTreeView profile={selectedProfiles[0]} />}
            </>
          )}
        </div>
      </main>
    </div>
  );
}
