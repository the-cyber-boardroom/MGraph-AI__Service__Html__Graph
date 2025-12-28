const { useState, useCallback, useMemo, useEffect, useRef } = React;

const extractKey = (filename) => {
  let name = filename.replace(/\.json$/, '').replace(/_json$/, '');
  name = name.replace(/^full_+/, '').replace(/^_+|_+$/g, '');
  return name || filename;
};

const processCallTreeFile = (file) => {
  if (!file.data?.traces?.call_tree) return null;
  const { metadata = {}, call_tree: callTree = [] } = file.data.traces;
  let minTime = Infinity, maxTime = -Infinity, totalSelfMs = 0, nodeCount = 0, maxDepth = 0, maxDuration = 0;
  const walk = (nodes) => nodes.forEach(n => {
    if (n.start_ns < minTime) minTime = n.start_ns;
    if (n.end_ns > maxTime) maxTime = n.end_ns;
    if (n.depth > maxDepth) maxDepth = n.depth;
    if (n.duration_ms > maxDuration) maxDuration = n.duration_ms;
    totalSelfMs += n.self_ms || 0;
    nodeCount++;
    if (n.children?.length) walk(n.children);
  });
  walk(callTree);
  return { key: extractKey(file.name), callTree, metadata, totalDurationMs: (maxTime - minTime) / 1e6, totalSelfMs, nodeCount, maxDepth, maxDuration };
};

const getHotspotColor = (s, t) => { if (!t || !s) return 0x4ecdc4; const p = s / t; return p > .15 ? 0xff6b6b : p > .08 ? 0xffa502 : p > .03 ? 0xffd93d : p > .01 ? 0x6bcb77 : 0x4ecdc4; };
const getHotspotColorCSS = (s, t) => { if (!t || !s) return '#4ecdc4'; const p = s / t; return p > .15 ? '#ff6b6b' : p > .08 ? '#ffa502' : p > .03 ? '#ffd93d' : p > .01 ? '#6bcb77' : '#4ecdc4'; };
const formatDuration = (ms) => ms >= 1000 ? `${(ms / 1000).toFixed(2)}s` : ms >= 1 ? `${ms.toFixed(2)}ms` : `${(ms * 1000).toFixed(1)}µs`;
const flattenTree = (nodes, result = []) => { nodes.forEach(n => { result.push(n); if (n.children?.length) flattenTree(n.children, result); }); return result; };

const Slider = ({ label, value, min, max, onChange, unit = '' }) => (
  <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
    <span style={{ fontSize: 12, color: '#888', minWidth: 70 }}>{label}</span>
    <input type="range" min={min} max={max} value={value} onChange={(e) => onChange(Number(e.target.value))} style={{ flex: 1, accentColor: '#4ecdc4', height: 4, background: '#333', borderRadius: 2 }} />
    <span style={{ fontSize: 11, color: '#4ecdc4', minWidth: 45, textAlign: 'right', fontFamily: "'JetBrains Mono', monospace" }}>{value}{unit}</span>
  </div>
);

const NavButton = ({ onClick, children, title }) => (
  <button onClick={onClick} title={title} style={{ width: 32, height: 32, background: '#1a1a1a', border: '1px solid #333', color: '#888', borderRadius: 4, cursor: 'pointer', fontSize: 14, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
    onMouseEnter={(e) => { e.target.style.background = '#252525'; e.target.style.color = '#4ecdc4'; e.target.style.borderColor = '#4ecdc4'; }}
    onMouseLeave={(e) => { e.target.style.background = '#1a1a1a'; e.target.style.color = '#888'; e.target.style.borderColor = '#333'; }}>
    {children}
  </button>
);

const ThreeJSVisualization = React.memo(({ profile, layoutMode, sizeBy, selectedNode, onNodeClick, setHoveredNode, fitTrigger, showEdges, graphSettings, highlightMode, navAction, setNavAction, hoverEnabled }) => {
  const containerRef = useRef(null);
  const sceneRef = useRef(null);
  const rendererRef = useRef(null);
  const cameraRef = useRef(null);
  const controlsRef = useRef(null);
  const nodesRef = useRef([]);
  const edgesRef = useRef([]);
  const animationIdRef = useRef(null);
  const raycasterRef = useRef(null);
  const mouseRef = useRef(new THREE.Vector2());

  useEffect(() => {
    if (!containerRef.current || !profile) return;
    const container = containerRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0d0d0d);
    sceneRef.current = scene;

    const camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 2000);
    camera.position.set(0, 50, 100);
    cameraRef.current = camera;

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.innerHTML = '';
    container.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.rotateSpeed = 0.3;
    controls.panSpeed = 0.5;
    controls.minDistance = 5;
    controls.maxDistance = 800;
    controlsRef.current = controls;

    raycasterRef.current = new THREE.Raycaster();

    scene.add(new THREE.AmbientLight(0xffffff, 0.4));
    const dl = new THREE.DirectionalLight(0xffffff, 0.8);
    dl.position.set(50, 100, 50);
    scene.add(dl);
    const dl2 = new THREE.DirectionalLight(0x4ecdc4, 0.3);
    dl2.position.set(-50, -50, -50);
    scene.add(dl2);

    const grid = new THREE.GridHelper(200, 40, 0x222222, 0x1a1a1a);
    grid.position.y = -1;
    scene.add(grid);

    const animate = () => {
      animationIdRef.current = requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };
    animate();

    const handleResize = () => {
      const w = container.clientWidth, h = container.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener('resize', handleResize);

    const handleMouseMove = (e) => {
      const rect = container.getBoundingClientRect();
      mouseRef.current.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouseRef.current.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
      raycasterRef.current.setFromCamera(mouseRef.current, camera);
      const hit = raycasterRef.current.intersectObjects(nodesRef.current);
      container.style.cursor = hit.length ? 'pointer' : 'grab';
    };

    // Use pointerdown/up to handle node selection without interfering with orbit controls
    let clickedNode = null;
    const handlePointerDown = (e) => {
      if (e.button !== 0) return;
      const rect = container.getBoundingClientRect();
      mouseRef.current.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouseRef.current.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
      raycasterRef.current.setFromCamera(mouseRef.current, camera);
      const hit = raycasterRef.current.intersectObjects(nodesRef.current);
      if (hit.length) {
        clickedNode = hit[0].object.userData.node;
        controls.enabled = false; // Disable orbit controls when clicking a node
      } else {
        clickedNode = null;
      }
    };

    const handlePointerUp = (e) => {
      if (e.button !== 0) return;
      controls.enabled = true; // Re-enable orbit controls
      if (clickedNode) {
        const rect = container.getBoundingClientRect();
        mouseRef.current.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        mouseRef.current.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
        raycasterRef.current.setFromCamera(mouseRef.current, camera);
        const hit = raycasterRef.current.intersectObjects(nodesRef.current);
        if (hit.length && hit[0].object.userData.node.call_index === clickedNode.call_index) {
          onNodeClick(clickedNode);
        }
        clickedNode = null;
      }
    };

    const handleKeydown = (e) => {
      const keys = { ArrowLeft: 'rotateLeft', ArrowRight: 'rotateRight', ArrowUp: 'rotateUp', ArrowDown: 'rotateDown', Equal: 'zoomIn', Minus: 'zoomOut', KeyW: 'up', KeyS: 'down', KeyA: 'left', KeyD: 'right', KeyR: 'reset' };
      if (keys[e.code]) { e.preventDefault(); setNavAction(keys[e.code]); }
    };

    container.addEventListener('mousemove', handleMouseMove);
    container.addEventListener('pointerdown', handlePointerDown);
    container.addEventListener('pointerup', handlePointerUp);
    container.setAttribute('tabindex', '0');
    container.addEventListener('keydown', handleKeydown);

    return () => {
      cancelAnimationFrame(animationIdRef.current);
      window.removeEventListener('resize', handleResize);
      container.removeEventListener('mousemove', handleMouseMove);
      container.removeEventListener('pointerdown', handlePointerDown);
      container.removeEventListener('pointerup', handlePointerUp);
      container.removeEventListener('keydown', handleKeydown);
      renderer.dispose();
      controls.dispose();
    };
  }, [profile?.key, onNodeClick, setNavAction]);

  useEffect(() => {
    if (!navAction || !cameraRef.current || !controlsRef.current) return;
    const camera = cameraRef.current;
    const controls = controlsRef.current;
    
    // Simulate mouse movement amounts
    const rotateAmount = 0.05; // radians
    const panAmount = 2; // world units
    const zoomAmount = 0.9; // multiplier

    const actions = {
      up: () => {
        const panOffset = new THREE.Vector3();
        panOffset.setFromMatrixColumn(camera.matrix, 1).multiplyScalar(panAmount);
        controls.target.add(panOffset);
        camera.position.add(panOffset);
      },
      down: () => {
        const panOffset = new THREE.Vector3();
        panOffset.setFromMatrixColumn(camera.matrix, 1).multiplyScalar(-panAmount);
        controls.target.add(panOffset);
        camera.position.add(panOffset);
      },
      left: () => {
        const panOffset = new THREE.Vector3();
        panOffset.setFromMatrixColumn(camera.matrix, 0).multiplyScalar(-panAmount);
        controls.target.add(panOffset);
        camera.position.add(panOffset);
      },
      right: () => {
        const panOffset = new THREE.Vector3();
        panOffset.setFromMatrixColumn(camera.matrix, 0).multiplyScalar(panAmount);
        controls.target.add(panOffset);
        camera.position.add(panOffset);
      },
      zoomIn: () => {
        const direction = new THREE.Vector3().subVectors(controls.target, camera.position);
        camera.position.add(direction.multiplyScalar(1 - zoomAmount));
      },
      zoomOut: () => {
        const direction = new THREE.Vector3().subVectors(camera.position, controls.target);
        camera.position.add(direction.multiplyScalar(1 - zoomAmount));
      },
      rotateLeft: () => {
        const offset = new THREE.Vector3().subVectors(camera.position, controls.target);
        const spherical = new THREE.Spherical().setFromVector3(offset);
        spherical.theta += rotateAmount;
        offset.setFromSpherical(spherical);
        camera.position.copy(controls.target).add(offset);
        camera.lookAt(controls.target);
      },
      rotateRight: () => {
        const offset = new THREE.Vector3().subVectors(camera.position, controls.target);
        const spherical = new THREE.Spherical().setFromVector3(offset);
        spherical.theta -= rotateAmount;
        offset.setFromSpherical(spherical);
        camera.position.copy(controls.target).add(offset);
        camera.lookAt(controls.target);
      },
      rotateUp: () => {
        const offset = new THREE.Vector3().subVectors(camera.position, controls.target);
        const spherical = new THREE.Spherical().setFromVector3(offset);
        spherical.phi = Math.max(0.1, spherical.phi - rotateAmount);
        offset.setFromSpherical(spherical);
        camera.position.copy(controls.target).add(offset);
        camera.lookAt(controls.target);
      },
      rotateDown: () => {
        const offset = new THREE.Vector3().subVectors(camera.position, controls.target);
        const spherical = new THREE.Spherical().setFromVector3(offset);
        spherical.phi = Math.min(Math.PI - 0.1, spherical.phi + rotateAmount);
        offset.setFromSpherical(spherical);
        camera.position.copy(controls.target).add(offset);
        camera.lookAt(controls.target);
      },
      reset: () => { 
        camera.position.set(0, 50, 100); 
        controls.target.set(0, 0, 0); 
      }
    };
    actions[navAction]?.();
    controls.update();
    setNavAction(null);
  }, [navAction, setNavAction]);

  useEffect(() => {
    if (!sceneRef.current || !profile) return;
    const scene = sceneRef.current;

    nodesRef.current.forEach(m => { scene.remove(m); m.geometry.dispose(); m.material.dispose(); });
    nodesRef.current = [];
    edgesRef.current.forEach(l => { scene.remove(l); l.geometry.dispose(); l.material.dispose(); });
    edgesRef.current = [];

    const flatNodes = flattenTree(profile.callTree);
    const nodePositions = new Map();
    const { linkDistance, repulsion, collision, minNodeSize, maxNodeSize } = graphSettings;

    if (layoutMode === 'tree') {
      const layoutNode = (node, x, z, depth, si, sc) => {
        const y = -depth * (linkDistance * 0.2);
        const spread = Math.max(100, sc * 15);
        const ox = sc > 1 ? (si - (sc - 1) / 2) * (spread / sc) : 0;
        nodePositions.set(node.call_index, { x: x + ox, y, z, node });
        node.children?.forEach((c, i) => layoutNode(c, x + ox, z + linkDistance * 0.3, depth + 1, i, node.children.length));
      };
      profile.callTree.forEach((r, i) => layoutNode(r, i * 80 - (profile.callTree.length - 1) * 40, 0, 0, i, profile.callTree.length));
    } else if (layoutMode === 'city') {
      const mm = new Map();
      flatNodes.forEach(n => { if (!mm.has(n.name)) mm.set(n.name, []); mm.get(n.name).push(n); });
      const methods = [...mm.entries()].sort((a, b) => b[1].reduce((s, n) => s + (n.self_ms || 0), 0) - a[1].reduce((s, n) => s + (n.self_ms || 0), 0));
      const gs = Math.ceil(Math.sqrt(methods.length)), sp = 8 + collision;
      methods.forEach(([, nodes], i) => {
        const gx = (i % gs) - gs / 2, gz = Math.floor(i / gs) - gs / 2;
        nodes.forEach((n, j) => nodePositions.set(n.call_index, { x: gx * sp + (j % 3) * (2 + collision * 0.5), y: 0, z: gz * sp + Math.floor(j / 3) * (2 + collision * 0.5), node: n }));
      });
    } else {
      const positions = flatNodes.map(n => ({ x: (Math.random() - 0.5) * 100, y: (Math.random() - 0.5) * 100, z: (Math.random() - 0.5) * 100, vx: 0, vy: 0, vz: 0, node: n }));
      for (let iter = 0; iter < 100; iter++) {
        for (let i = 0; i < positions.length; i++) {
          for (let j = i + 1; j < positions.length; j++) {
            const dx = positions[j].x - positions[i].x, dy = positions[j].y - positions[i].y, dz = positions[j].z - positions[i].z;
            const dist = Math.sqrt(dx * dx + dy * dy + dz * dz) + 0.1;
            const f = repulsion / (dist * dist);
            positions[i].vx -= (dx / dist) * f; positions[i].vy -= (dy / dist) * f; positions[i].vz -= (dz / dist) * f;
            positions[j].vx += (dx / dist) * f; positions[j].vy += (dy / dist) * f; positions[j].vz += (dz / dist) * f;
          }
        }
        flatNodes.forEach((n, i) => {
          if (n.depth > 0) {
            const pp = positions.find(p => p.node.children?.some(c => c.call_index === n.call_index));
            if (pp) {
              const dx = pp.x - positions[i].x, dy = pp.y - positions[i].y, dz = pp.z - positions[i].z;
              positions[i].vx += dx * 0.01; positions[i].vy += dy * 0.01; positions[i].vz += dz * 0.01;
            }
          }
        });
        positions.forEach(p => {
          p.vx -= p.x * 0.001; p.vy -= p.y * 0.001; p.vz -= p.z * 0.001;
          p.x += p.vx * 0.5; p.y += p.vy * 0.5; p.z += p.vz * 0.5;
          p.vx *= 0.9; p.vy *= 0.9; p.vz *= 0.9;
        });
      }
      positions.forEach(p => nodePositions.set(p.node.call_index, { x: p.x, y: p.y, z: p.z, node: p.node }));
    }

    nodePositions.forEach((pos) => {
      const node = pos.node;
      const color = getHotspotColor(node.self_ms, profile.totalSelfMs);
      let size = sizeBy === 'duration' ? minNodeSize + Math.sqrt(node.duration_ms / profile.maxDuration) * (maxNodeSize - minNodeSize) : sizeBy === 'self' ? minNodeSize + Math.sqrt((node.self_ms / profile.totalSelfMs) * 100) * (maxNodeSize - minNodeSize) * 0.5 : (minNodeSize + maxNodeSize) / 2;
      size = Math.max(minNodeSize, Math.min(maxNodeSize, size));

      let mesh;
      if (layoutMode === 'city') {
        const h = Math.max(2, (node.duration_ms / profile.maxDuration) * 30);
        mesh = new THREE.Mesh(new THREE.BoxGeometry(size, h, size), new THREE.MeshPhongMaterial({ color, transparent: true, opacity: 0.9 }));
        mesh.position.set(pos.x, h / 2, pos.z);
      } else {
        mesh = new THREE.Mesh(new THREE.SphereGeometry(size, 16, 16), new THREE.MeshPhongMaterial({ color, transparent: true, opacity: 0.9 }));
        mesh.position.set(pos.x, pos.y, pos.z);
      }
      mesh.userData = { node, originalColor: color };
      scene.add(mesh);
      nodesRef.current.push(mesh);
    });

    if (showEdges) {
      const mat = new THREE.LineBasicMaterial({ color: 0x333333, transparent: true, opacity: 0.5 });
      flatNodes.forEach(node => {
        if (node.children?.length) {
          const pp = nodePositions.get(node.call_index);
          if (!pp) return;
          node.children.forEach(child => {
            const cp = nodePositions.get(child.call_index);
            if (!cp) return;
            const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(pp.x, pp.y, pp.z), new THREE.Vector3(cp.x, cp.y, cp.z)]), mat.clone());
            line.userData = { parentCallIndex: node.call_index, childCallIndex: child.call_index };
            scene.add(line);
            edgesRef.current.push(line);
          });
        }
      });
    }
  }, [profile, layoutMode, sizeBy, showEdges, graphSettings]);

  useEffect(() => {
    nodesRef.current.forEach(m => { m.material.color.setHex(m.userData.originalColor); m.material.emissive = new THREE.Color(0); m.material.opacity = 0.9; });
    edgesRef.current.forEach(l => { l.material.color.setHex(0x333333); l.material.opacity = 0.5; });
    if (!selectedNode) return;

    const connected = new Set(), sameName = new Set();
    if (highlightMode === 'connections' || highlightMode === 'both') {
      edgesRef.current.forEach(l => {
        if (l.userData.childCallIndex === selectedNode.call_index) connected.add(l.userData.parentCallIndex);
        if (l.userData.parentCallIndex === selectedNode.call_index) connected.add(l.userData.childCallIndex);
      });
    }
    if (highlightMode === 'sameName' || highlightMode === 'both') {
      nodesRef.current.forEach(m => { if (m.userData.node.name === selectedNode.name) sameName.add(m.userData.node.call_index); });
    }

    nodesRef.current.forEach(m => {
      const isSel = m.userData.node.call_index === selectedNode.call_index;
      const isCon = connected.has(m.userData.node.call_index);
      const isSame = sameName.has(m.userData.node.call_index);
      if (isSel) { m.material.emissive = new THREE.Color(0xffffff); m.material.emissiveIntensity = 0.4; }
      else if (isCon) { m.material.emissive = new THREE.Color(0x4ecdc4); m.material.emissiveIntensity = 0.3; }
      else if (isSame) { m.material.emissive = new THREE.Color(0xff6b6b); m.material.emissiveIntensity = 0.3; }
      else if (highlightMode !== 'none') m.material.opacity = 0.3;
    });

    edgesRef.current.forEach(l => {
      const isCon = l.userData.parentCallIndex === selectedNode.call_index || l.userData.childCallIndex === selectedNode.call_index;
      if (isCon && (highlightMode === 'connections' || highlightMode === 'both')) { l.material.color.setHex(0x4ecdc4); l.material.opacity = 1; }
      else if (highlightMode !== 'none') l.material.opacity = 0.2;
    });
  }, [selectedNode, highlightMode]);

  useEffect(() => {
    if (!cameraRef.current || !controlsRef.current || !nodesRef.current.length) return;
    const box = new THREE.Box3();
    nodesRef.current.forEach(m => box.expandByObject(m));
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());
    const maxDim = Math.max(size.x, size.y, size.z);
    cameraRef.current.position.set(center.x + maxDim, center.y + maxDim * 0.5, center.z + maxDim);
    controlsRef.current.target.copy(center);
    controlsRef.current.update();
  }, [fitTrigger, profile, layoutMode]);

  return <div ref={containerRef} style={{ width: '100%', height: '100%', cursor: 'grab', background: '#0d0d0d', outline: 'none' }} />;
});

function ThreeDVisualizer() {
  const [files, setFiles] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const [selectedKey, setSelectedKey] = useState(null);
  const [layoutMode, setLayoutMode] = useState('force');
  const [sizeBy, setSizeBy] = useState('duration');
  const [selectedNode, setSelectedNode] = useState(null);
  const [hoveredNode, setHoveredNode] = useState(null);
  const [fitTrigger, setFitTrigger] = useState(0);
  const [showEdges, setShowEdges] = useState(true);
  const [isMaximized, setIsMaximized] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [highlightMode, setHighlightMode] = useState('connections');
  const [navAction, setNavAction] = useState(null);
  const [hoverEnabled, setHoverEnabled] = useState(false);
  const [graphSettings, setGraphSettings] = useState({ minNodeSize: 2, maxNodeSize: 15, fontSize: 8, labelLength: 16, linkDistance: 60, repulsion: 150, collision: 2 });

  const updateSetting = (k, v) => setGraphSettings(p => ({ ...p, [k]: v }));
  const resetSettings = () => setGraphSettings({ minNodeSize: 2, maxNodeSize: 15, fontSize: 8, labelLength: 16, linkDistance: 60, repulsion: 150, collision: 2 });

  const profiles = useMemo(() => files.map(processCallTreeFile).filter(Boolean), [files]);
  const selectedProfile = useMemo(() => profiles.find(p => p.key === selectedKey) || profiles[0] || null, [profiles, selectedKey]);
  useEffect(() => { if (profiles.length && !selectedKey) setSelectedKey(profiles[0].key); }, [profiles, selectedKey]);

  const handleDragOver = useCallback((e) => { e.preventDefault(); setIsDragging(true); }, []);
  const handleDragLeave = useCallback((e) => { e.preventDefault(); setIsDragging(false); }, []);
  const handleDrop = useCallback((e) => {
    e.preventDefault(); setIsDragging(false);
    Array.from(e.dataTransfer.files).filter(f => f.name.endsWith('.json') && f.name.includes('full')).forEach(file => {
      const reader = new FileReader();
      reader.onload = (ev) => { try { const data = JSON.parse(ev.target.result); setFiles(p => p.some(f => f.name === file.name) ? p : [...p, { name: file.name, data }]); } catch {} };
      reader.readAsText(file);
    });
  }, []);

  const handleNodeClick = useCallback((node) => setSelectedNode(p => p?.call_index === node.call_index ? null : node), []);
  const displayNode = hoverEnabled ? (hoveredNode || selectedNode) : selectedNode;

  const buttonStyle = { padding: '6px 12px', fontSize: 11, background: '#1a1a1a', border: '1px solid #333', color: '#ccc', borderRadius: 4, cursor: 'pointer', fontFamily: 'inherit' };
  const toggleButtonStyle = (active) => ({ padding: '6px 12px', fontSize: 11, background: active ? '#4ecdc4' : '#1a1a1a', border: '1px solid', borderColor: active ? '#4ecdc4' : '#333', color: active ? '#000' : '#888', borderRadius: 4, cursor: 'pointer', fontFamily: 'inherit', fontWeight: active ? 600 : 400 });

  if (isMaximized) {
    return (
      <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: '#0d0d0d', zIndex: 9999, display: 'flex', flexDirection: 'column' }} onDragOver={handleDragOver} onDragLeave={handleDragLeave} onDrop={handleDrop}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '8px 16px', background: '#111', borderBottom: '1px solid #1a1a1a' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div style={{ width: 24, height: 24, background: 'linear-gradient(135deg, #4ecdc4, #44a08d)', borderRadius: 4, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 12 }}>🎲</div>
            <span style={{ fontWeight: 600, color: '#4ecdc4', fontSize: 14 }}>3D Visualizer</span>
          </div>
          <div style={{ flex: 1, padding: '8px 16px', background: isDragging ? 'rgba(78, 205, 196, 0.1)' : '#0d0d0d', border: `2px dashed ${isDragging ? '#4ecdc4' : '#2a2a2a'}`, borderRadius: 6, textAlign: 'center', color: isDragging ? '#4ecdc4' : '#555', fontSize: 12 }}>Drag & drop full_*.json files</div>
          <button onClick={() => setShowSettings(!showSettings)} style={{ ...buttonStyle, background: showSettings ? 'rgba(78, 205, 196, 0.15)' : '#1a1a1a', color: showSettings ? '#4ecdc4' : '#ccc', borderColor: showSettings ? '#4ecdc4' : '#333' }}>⚙ Settings {showSettings ? '▲' : '▼'}</button>
          <button onClick={() => setFitTrigger(t => t + 1)} style={buttonStyle}>Fit to View</button>
          {selectedProfile && <div style={{ fontSize: 11, color: '#888' }}>Nodes: <strong style={{ color: '#4ecdc4' }}>{selectedProfile.nodeCount}</strong></div>}
          <button onClick={() => setIsMaximized(false)} style={{ ...buttonStyle, fontSize: 16, padding: '4px 10px' }} title="Exit fullscreen">✕</button>
        </div>
        {showSettings && (
          <div style={{ background: '#151515', borderBottom: '1px solid #1a1a1a', padding: '12px 24px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 24 }}>
              <div><div style={{ fontSize: 10, color: '#666', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 12 }}>Node Size</div><div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}><Slider label="Min" value={graphSettings.minNodeSize} min={1} max={10} onChange={(v) => updateSetting('minNodeSize', v)} unit="px" /><Slider label="Max" value={graphSettings.maxNodeSize} min={5} max={30} onChange={(v) => updateSetting('maxNodeSize', v)} unit="px" /></div></div>
              <div><div style={{ fontSize: 10, color: '#666', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 12 }}>Force Layout</div><div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}><Slider label="Link Dist" value={graphSettings.linkDistance} min={20} max={150} onChange={(v) => updateSetting('linkDistance', v)} unit="px" /><Slider label="Repulsion" value={graphSettings.repulsion} min={50} max={500} onChange={(v) => updateSetting('repulsion', v)} unit="" /></div></div>
              <div><div style={{ fontSize: 10, color: '#666', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 12 }}>Highlight</div><div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>{['none', 'connections', 'sameName', 'both'].map(m => <button key={m} onClick={() => setHighlightMode(m)} style={toggleButtonStyle(highlightMode === m)}>{m === 'sameName' ? 'Same Name' : m.charAt(0).toUpperCase() + m.slice(1)}</button>)}</div></div>
            </div>
            <div style={{ marginTop: 12, display: 'flex', justifyContent: 'flex-end' }}><button onClick={resetSettings} style={buttonStyle}>Reset</button></div>
          </div>
        )}
        <div style={{ flex: 1, position: 'relative' }}>
          {selectedProfile && <ThreeJSVisualization profile={selectedProfile} layoutMode={layoutMode} sizeBy={sizeBy} selectedNode={selectedNode} onNodeClick={handleNodeClick} setHoveredNode={setHoveredNode} fitTrigger={fitTrigger} showEdges={showEdges} graphSettings={graphSettings} highlightMode={highlightMode} navAction={navAction} setNavAction={setNavAction} hoverEnabled={hoverEnabled} />}
          <div style={{ position: 'absolute', bottom: 70, right: 20, display: 'flex', flexDirection: 'column', gap: 4, background: 'rgba(17, 17, 17, 0.9)', padding: 12, borderRadius: 8, border: '1px solid #333' }}>
            <div style={{ fontSize: 9, color: '#666', textTransform: 'uppercase', marginBottom: 4, textAlign: 'center' }}>Navigate</div>
            <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 4 }}><NavButton onClick={() => setNavAction('up')} title="Move Up">↑</NavButton></div>
            <div style={{ display: 'flex', gap: 4 }}><NavButton onClick={() => setNavAction('left')} title="Move Left">←</NavButton><NavButton onClick={() => setNavAction('reset')} title="Reset View">⌂</NavButton><NavButton onClick={() => setNavAction('right')} title="Move Right">→</NavButton></div>
            <div style={{ display: 'flex', justifyContent: 'center' }}><NavButton onClick={() => setNavAction('down')} title="Move Down">↓</NavButton></div>
            <div style={{ borderTop: '1px solid #333', marginTop: 8, paddingTop: 8 }}><div style={{ fontSize: 9, color: '#666', textTransform: 'uppercase', marginBottom: 4, textAlign: 'center' }}>Zoom</div><div style={{ display: 'flex', gap: 4, justifyContent: 'center' }}><NavButton onClick={() => setNavAction('zoomIn')} title="Zoom In">+</NavButton><NavButton onClick={() => setNavAction('zoomOut')} title="Zoom Out">−</NavButton></div></div>
            <div style={{ borderTop: '1px solid #333', marginTop: 8, paddingTop: 8 }}><div style={{ fontSize: 9, color: '#666', textTransform: 'uppercase', marginBottom: 4, textAlign: 'center' }}>Rotate</div><div style={{ display: 'flex', gap: 4, justifyContent: 'center' }}><NavButton onClick={() => setNavAction('rotateLeft')} title="Rotate Left">↺</NavButton><NavButton onClick={() => setNavAction('rotateRight')} title="Rotate Right">↻</NavButton></div></div>
          </div>
          {displayNode && <div style={{ position: 'absolute', top: 20, left: 20, background: 'rgba(17, 17, 17, 0.95)', border: '1px solid #333', borderRadius: 8, padding: 16, minWidth: 220, fontFamily: "'JetBrains Mono', monospace" }}><div style={{ fontSize: 12, color: '#e0e0e0', fontWeight: 600, marginBottom: 8, wordBreak: 'break-all' }}>{displayNode.name}</div><div style={{ display: 'grid', gap: 4, fontSize: 11 }}><div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: '#666' }}>Duration:</span><span style={{ color: '#4ecdc4' }}>{formatDuration(displayNode.duration_ms)}</span></div><div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: '#666' }}>Self Time:</span><span style={{ color: getHotspotColorCSS(displayNode.self_ms, selectedProfile?.totalSelfMs) }}>{formatDuration(displayNode.self_ms)}</span></div><div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: '#666' }}>Depth:</span><span style={{ color: '#888' }}>{displayNode.depth}</span></div></div></div>}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14, padding: '10px 16px', background: '#111', borderTop: '1px solid #1a1a1a', fontSize: 10, color: '#888' }}>
          <span>Hotspot (self time %):</span>
          {[{ color: '#4ecdc4', label: '<1%' }, { color: '#6bcb77', label: '1-3%' }, { color: '#ffd93d', label: '3-8%' }, { color: '#ffa502', label: '8-15%' }, { color: '#ff6b6b', label: '>15%' }].map((item, i) => <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 4 }}><div style={{ width: 10, height: 10, borderRadius: 2, background: item.color }} /><span>{item.label}</span></div>)}
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '240px 1fr', gridTemplateRows: '1fr', height: '100vh', background: '#0d0d0d', color: '#e0e0e0', fontFamily: "'Space Grotesk', -apple-system, sans-serif", overflow: 'hidden' }} onDragOver={handleDragOver} onDragLeave={handleDragLeave} onDrop={handleDrop}>
      <aside style={{ background: '#111', borderRight: '1px solid #1a1a1a', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <div style={{ padding: '16px', borderBottom: '1px solid #1a1a1a', display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ width: 24, height: 24, background: 'linear-gradient(135deg, #4ecdc4, #44a08d)', borderRadius: 4, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 12 }}>🎲</div>
          <span style={{ fontWeight: 600, color: '#4ecdc4' }}>3D Visualizer</span>
        </div>
        <div style={{ flex: 1, overflowY: 'auto' }}>
          <div style={{ padding: '12px 16px', borderBottom: '1px solid #1a1a1a' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
              <span style={{ fontSize: 11, color: '#888', textTransform: 'uppercase', letterSpacing: 0.5 }}>Profiles ({profiles.length})</span>
              {profiles.length > 0 && <button onClick={() => { setFiles([]); setSelectedKey(null); setSelectedNode(null); }} style={{ ...buttonStyle, padding: '2px 8px', fontSize: 10 }}>Clear</button>}
            </div>
            {profiles.length === 0 ? <div style={{ color: '#555', fontSize: 12, fontStyle: 'italic' }}>Drop full_*.json files here</div> : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                {profiles.map(p => (
                  <button key={p.key} onClick={() => setSelectedKey(p.key)} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 10px', background: selectedKey === p.key ? 'rgba(78, 205, 196, 0.15)' : '#1a1a1a', border: '1px solid', borderColor: selectedKey === p.key ? '#4ecdc4' : '#2a2a2a', borderRadius: 6, cursor: 'pointer', textAlign: 'left', width: '100%' }}>
                    <div style={{ width: 14, height: 14, borderRadius: 3, background: selectedKey === p.key ? '#4ecdc4' : '#333', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 10, color: selectedKey === p.key ? '#000' : '#888' }}>{selectedKey === p.key ? '✓' : ''}</div>
                    <div style={{ flex: 1, overflow: 'hidden' }}><div style={{ fontSize: 12, color: selectedKey === p.key ? '#4ecdc4' : '#ccc', fontWeight: 500, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{p.key}</div><div style={{ fontSize: 10, color: '#666' }}>{p.nodeCount} calls</div></div>
                  </button>
                ))}
              </div>
            )}
          </div>
          <div style={{ padding: '12px 16px', borderBottom: '1px solid #1a1a1a' }}>
            <div style={{ fontSize: 11, color: '#888', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 8 }}>Layout</div>
            <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
              {[{ id: 'force', label: '🔮 Force' }, { id: 'tree', label: '🌳 Tree' }, { id: 'city', label: '🏙️ City' }].map(mode => <button key={mode.id} onClick={() => setLayoutMode(mode.id)} style={toggleButtonStyle(layoutMode === mode.id)}>{mode.label}</button>)}
            </div>
          </div>
          <div style={{ padding: '12px 16px', borderBottom: '1px solid #1a1a1a' }}>
            <div style={{ fontSize: 11, color: '#888', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 8 }}>Node Size</div>
            <div style={{ display: 'flex', gap: 4 }}>
              {['duration', 'self', 'uniform'].map(mode => <button key={mode} onClick={() => setSizeBy(mode)} style={toggleButtonStyle(sizeBy === mode)}>{mode.charAt(0).toUpperCase() + mode.slice(1)}</button>)}
            </div>
          </div>
          <div style={{ padding: '12px 16px', borderBottom: '1px solid #1a1a1a' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}><input type="checkbox" checked={showEdges} onChange={(e) => setShowEdges(e.target.checked)} style={{ accentColor: '#4ecdc4' }} /><span style={{ fontSize: 12, color: '#ccc' }}>Show Edges</span></label>
              <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}><input type="checkbox" checked={hoverEnabled} onChange={(e) => setHoverEnabled(e.target.checked)} style={{ accentColor: '#4ecdc4' }} /><span style={{ fontSize: 12, color: '#ccc' }}>Hover Selection</span></label>
            </div>
          </div>
          {displayNode && (
            <div style={{ padding: '12px 16px', borderBottom: '1px solid #1a1a1a' }}>
              <div style={{ fontSize: 11, color: '#888', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 8 }}>Node Details</div>
              <div style={{ background: '#1a1a1a', borderRadius: 6, padding: 10, fontFamily: "'JetBrains Mono', monospace" }}>
                <div style={{ fontSize: 12, color: '#e0e0e0', fontWeight: 600, marginBottom: 8, wordBreak: 'break-all' }}>{displayNode.name}</div>
                <div style={{ display: 'grid', gap: 4, fontSize: 11 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: '#666' }}>Duration:</span><span style={{ color: '#4ecdc4' }}>{formatDuration(displayNode.duration_ms)}</span></div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: '#666' }}>Self Time:</span><span style={{ color: getHotspotColorCSS(displayNode.self_ms, selectedProfile?.totalSelfMs) }}>{formatDuration(displayNode.self_ms)} ({selectedProfile ? ((displayNode.self_ms / selectedProfile.totalSelfMs) * 100).toFixed(1) : 0}%)</span></div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: '#666' }}>Depth:</span><span style={{ color: '#888' }}>{displayNode.depth}</span></div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: '#666' }}>Children:</span><span style={{ color: '#888' }}>{displayNode.children?.length || 0}</span></div>
                </div>
              </div>
            </div>
          )}
        </div>
        <div style={{ padding: '12px 16px', borderTop: '1px solid #1a1a1a' }}>
          <div style={{ fontSize: 10, color: '#555', lineHeight: 1.6 }}>
            <div>🖱️ Left drag: Rotate</div>
            <div>🖱️ Right drag: Pan</div>
            <div>🖱️ Scroll: Zoom</div>
            <div>⌨️ Arrows: Rotate</div>
            <div>⌨️ WASD: Pan</div>
            <div>⌨️ +/-: Zoom • R: Reset</div>
          </div>
        </div>
      </aside>
      <main style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '10px 16px', background: '#111', borderBottom: '1px solid #1a1a1a' }}>
          <div style={{ flex: 1, padding: '8px 16px', background: isDragging ? 'rgba(78, 205, 196, 0.1)' : '#0d0d0d', border: `2px dashed ${isDragging ? '#4ecdc4' : '#2a2a2a'}`, borderRadius: 6, textAlign: 'center', color: isDragging ? '#4ecdc4' : '#555', fontSize: 12, transition: 'all 0.2s' }}>Drag & drop full_*.json files</div>
          <button onClick={() => setShowSettings(!showSettings)} style={{ ...buttonStyle, display: 'flex', alignItems: 'center', gap: 6, background: showSettings ? 'rgba(78, 205, 196, 0.15)' : '#1a1a1a', color: showSettings ? '#4ecdc4' : '#ccc', borderColor: showSettings ? '#4ecdc4' : '#333' }}>⚙ Graph Settings {showSettings ? '▲' : '▼'}</button>
          <button onClick={() => setFitTrigger(t => t + 1)} style={buttonStyle}>Fit to View</button>
          {selectedProfile && <div style={{ display: 'flex', gap: 12, fontSize: 11, color: '#888', alignItems: 'center' }}><span>Nodes: <strong style={{ color: '#4ecdc4' }}>{selectedProfile.nodeCount}</strong></span><span>Duration: <strong style={{ color: '#4ecdc4' }}>{formatDuration(selectedProfile.totalDurationMs)}</strong></span><button onClick={() => setIsMaximized(true)} style={{ width: 28, height: 28, background: '#1a1a1a', border: '1px solid #333', color: '#888', borderRadius: 4, cursor: 'pointer', fontSize: 16, display: 'flex', alignItems: 'center', justifyContent: 'center' }} title="Maximize">⊕</button></div>}
        </div>
        {showSettings && (
          <div style={{ background: '#151515', borderBottom: '1px solid #1a1a1a', padding: '16px 24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}><span style={{ fontSize: 12, color: '#888', textTransform: 'uppercase', letterSpacing: 0.5 }}>Graph Settings</span><button onClick={resetSettings} style={buttonStyle}>Reset</button></div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 32 }}>
              <div><div style={{ fontSize: 10, color: '#666', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 12 }}>Node Size</div><div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}><Slider label="Min" value={graphSettings.minNodeSize} min={1} max={10} onChange={(v) => updateSetting('minNodeSize', v)} unit="px" /><Slider label="Max" value={graphSettings.maxNodeSize} min={5} max={30} onChange={(v) => updateSetting('maxNodeSize', v)} unit="px" /></div></div>
              <div><div style={{ fontSize: 10, color: '#666', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 12 }}>Force Layout</div><div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}><Slider label="Link Dist" value={graphSettings.linkDistance} min={20} max={150} onChange={(v) => updateSetting('linkDistance', v)} unit="px" /><Slider label="Repulsion" value={graphSettings.repulsion} min={50} max={500} onChange={(v) => updateSetting('repulsion', v)} unit="" /><Slider label="Collision" value={graphSettings.collision} min={0} max={10} onChange={(v) => updateSetting('collision', v)} unit="px" /></div></div>
              <div><div style={{ fontSize: 10, color: '#666', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 12 }}>Highlight</div><div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>{['none', 'connections', 'sameName', 'both'].map(m => <button key={m} onClick={() => setHighlightMode(m)} style={toggleButtonStyle(highlightMode === m)}>{m === 'sameName' ? 'Same Name' : m.charAt(0).toUpperCase() + m.slice(1)}</button>)}</div></div>
            </div>
          </div>
        )}
        <div style={{ flex: 1, position: 'relative' }}>
          {!selectedProfile ? <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', textAlign: 'center', color: '#444' }}><div style={{ fontSize: 48, marginBottom: 16 }}>🎲</div><div style={{ fontSize: 14, fontStyle: 'italic' }}>Drop a full_*.json file to visualize in 3D</div></div> : <ThreeJSVisualization profile={selectedProfile} layoutMode={layoutMode} sizeBy={sizeBy} selectedNode={selectedNode} onNodeClick={handleNodeClick} setHoveredNode={setHoveredNode} fitTrigger={fitTrigger} showEdges={showEdges} graphSettings={graphSettings} highlightMode={highlightMode} navAction={navAction} setNavAction={setNavAction} hoverEnabled={hoverEnabled} />}
          {selectedProfile && (
            <div style={{ position: 'absolute', bottom: 20, right: 20, display: 'flex', flexDirection: 'column', gap: 4, background: 'rgba(17, 17, 17, 0.9)', padding: 12, borderRadius: 8, border: '1px solid #333' }}>
              <div style={{ fontSize: 9, color: '#666', textTransform: 'uppercase', marginBottom: 4, textAlign: 'center' }}>Navigate</div>
              <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 4 }}><NavButton onClick={() => setNavAction('up')} title="Move Up">↑</NavButton></div>
              <div style={{ display: 'flex', gap: 4 }}><NavButton onClick={() => setNavAction('left')} title="Move Left">←</NavButton><NavButton onClick={() => setNavAction('reset')} title="Reset View">⌂</NavButton><NavButton onClick={() => setNavAction('right')} title="Move Right">→</NavButton></div>
              <div style={{ display: 'flex', justifyContent: 'center' }}><NavButton onClick={() => setNavAction('down')} title="Move Down">↓</NavButton></div>
              <div style={{ borderTop: '1px solid #333', marginTop: 8, paddingTop: 8 }}><div style={{ fontSize: 9, color: '#666', textTransform: 'uppercase', marginBottom: 4, textAlign: 'center' }}>Zoom</div><div style={{ display: 'flex', gap: 4, justifyContent: 'center' }}><NavButton onClick={() => setNavAction('zoomIn')} title="Zoom In">+</NavButton><NavButton onClick={() => setNavAction('zoomOut')} title="Zoom Out">−</NavButton></div></div>
              <div style={{ borderTop: '1px solid #333', marginTop: 8, paddingTop: 8 }}><div style={{ fontSize: 9, color: '#666', textTransform: 'uppercase', marginBottom: 4, textAlign: 'center' }}>Rotate</div><div style={{ display: 'flex', gap: 4, justifyContent: 'center' }}><NavButton onClick={() => setNavAction('rotateLeft')} title="Rotate Left">↺</NavButton><NavButton onClick={() => setNavAction('rotateRight')} title="Rotate Right">↻</NavButton></div></div>
            </div>
          )}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14, padding: '10px 16px', background: '#111', borderTop: '1px solid #1a1a1a', fontSize: 10, color: '#888' }}>
          <span>Hotspot (self time %):</span>
          {[{ color: '#4ecdc4', label: '<1%' }, { color: '#6bcb77', label: '1-3%' }, { color: '#ffd93d', label: '3-8%' }, { color: '#ffa502', label: '8-15%' }, { color: '#ff6b6b', label: '>15%' }].map((item, i) => <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 4 }}><div style={{ width: 10, height: 10, borderRadius: 2, background: item.color }} /><span>{item.label}</span></div>)}
          <span style={{ marginLeft: 'auto', color: '#555' }}>Layout: {layoutMode === 'tree' ? '3D Tree' : layoutMode === 'city' ? 'Code City' : '3D Force Graph'}</span>
        </div>
      </main>
    </div>
  );
}
