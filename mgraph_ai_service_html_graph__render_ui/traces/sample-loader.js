/**
 * Sample Loader Module
 *
 * Handles loading sample trace data from the API and distributing it to visualizer iframes.
 *
 * Usage in parent HTML:
 *   <script src="./sample-loader.js"></script>
 *   <div id="sample-loader-container"></div>
 *   <script>
 *     SampleLoader.init('sample-loader-container', {
 *       // optional config overrides
 *     });
 *   </script>
 *
 * Child iframes should listen for messages:
 *   window.addEventListener('message', (event) => {
 *     if (event.data.type === 'LOAD_TRACE_DATA') {
 *       // event.data.payload contains { name, data }
 *     }
 *   });
 */

const SampleLoader = (function() {

  // Default configuration
  const DEFAULT_CONFIG = {
    // Available sample sizes
    sampleSizes: [1, 5, 10, 20, 30, 40, 50, 100],

    // Available named samples (from Enum__Sample__Html__File__Name)
    namedSamples: [
      'simple-html',
      'html-with-some-tags',
      'html-with-one-paragraph',
      'html-bootstrap-example'
    ],

    // API endpoints
    endpoints: {
      htmlBySize: (size) => `/samples/html/with/size/${size}`,
      htmlByName: (name) => `/samples/html/with/name/${name}`,
      // Transform endpoint - outputFormat will be appended (full, speedscope, summary)
      transform: (engine = 'dot', transformation = 'default', outputFormat = 'full') =>
        `/timestamps/graph/from/html/to/${engine}/${transformation}/${outputFormat}`
    },

    // Available output formats
    outputFormats: [
      { value: 'full', label: 'Full Trace', description: 'Call Tree, Network, 3D' },
      { value: 'speedscope', label: 'Speedscope', description: 'Flame Graph' },
      { value: 'summary', label: 'Summary', description: 'Summary View' }
    ],

    // Default output format
    defaultOutputFormat: 'full',

    // Default transformation parameters
    defaultEngine: 'dot',
    defaultTransformation: 'default',

    // Transform request payload template
    transformPayload: (html) => ({
      graph_request: {
        html: html,
        preset: "full_detail",
        show_tag_nodes: true,
        show_attr_nodes: true,
        show_text_nodes: true,
        color_scheme: "default"
      },
      trace_config: {
        output: 'traces_only'
      }
    }),

    // If true, endpoints return trace data directly (no transform step needed)
    directTraceEndpoint: false,

    // Optional: direct trace file URL function
    directTraceUrl: null,

    // Iframe selectors to send data to (will try all)
    iframeSelectors: [
      '#frame-call_tree',
      '#frame-network_graph',
      '#frame-three_d',
      '#frame-speedscope',
      '#frame-summary_full'
    ],

    // Message type for postMessage
    messageType: 'LOAD_TRACE_DATA',

    // Callback when data is loaded (optional)
    onDataLoaded: null,

    // Callback for errors (optional)
    onError: null
  };

  let config = { ...DEFAULT_CONFIG };
  let currentData = null;
  let lastRequest = null;  // Store { type, value } for reload
  let isLoading = false;
  let containerEl = null;

  // ============================================================================
  // API Functions
  // ============================================================================

  async function fetchSample({ type, value, outputFormat }) {
    const { endpoints, defaultEngine, defaultTransformation, transformPayload,
            directTraceEndpoint, directTraceUrl, defaultOutputFormat } = config;

    const format = outputFormat || defaultOutputFormat;
    let traceData;
    let fileName;

    if (type === 'size') {
      fileName = `with_size_${value}`;

      // Option 1: Direct trace file URL
      if (directTraceUrl) {
        const url = directTraceUrl(value);
        const response = await fetch(url);
        if (!response.ok) throw new Error(`Failed to fetch trace: ${response.status}`);
        traceData = await response.json();
      }
      // Option 2: Direct trace endpoint
      else if (directTraceEndpoint) {
        const url = endpoints.htmlBySize(value);
        const response = await fetch(url);
        if (!response.ok) throw new Error(`Failed to fetch: ${response.status}`);
        traceData = await response.json();
      }
      // Option 3: Chain calls - get HTML, then transform
      else {
        // Step 1: Get HTML
        const htmlUrl = endpoints.htmlBySize(value);
        const htmlResponse = await fetch(htmlUrl);
        if (!htmlResponse.ok) throw new Error(`Failed to fetch HTML: ${htmlResponse.status}`);
        const htmlData = await htmlResponse.json();

        // Step 2: Transform HTML to trace data (with selected output format)
        const transformUrl = endpoints.transform(defaultEngine, defaultTransformation, format);
        const payload = transformPayload(htmlData.html);

        const transformResponse = await fetch(transformUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (!transformResponse.ok) throw new Error(`Failed to transform: ${transformResponse.status}`);
        traceData = await transformResponse.json();
      }
    } else {
      // Load by name
      fileName = value.replace(/-/g, '_');

      if (directTraceEndpoint) {
        const url = endpoints.htmlByName(value);
        const response = await fetch(url);
        if (!response.ok) throw new Error(`Failed to fetch: ${response.status}`);
        traceData = await response.json();
      } else {
        // Chain calls
        const htmlUrl = endpoints.htmlByName(value);
        const htmlResponse = await fetch(htmlUrl);
        if (!htmlResponse.ok) throw new Error(`Failed to fetch HTML: ${htmlResponse.status}`);
        const htmlData = await htmlResponse.json();

        // Transform with selected output format
        const transformUrl = endpoints.transform(defaultEngine, defaultTransformation, format);
        const payload = transformPayload(htmlData.html);

        const transformResponse = await fetch(transformUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (!transformResponse.ok) throw new Error(`Failed to transform: ${transformResponse.status}`);
        traceData = await transformResponse.json();
      }
    }

    return { name: fileName, data: traceData, format };
  }

  // ============================================================================
  // Iframe Communication
  // ============================================================================

  function broadcastToIframes(data) {
    const message = {
      type: config.messageType,
      payload: data
    };

    config.iframeSelectors.forEach(selector => {
      const iframe = document.querySelector(selector);
      if (iframe && iframe.contentWindow) {
        try {
          iframe.contentWindow.postMessage(message, '*');
          console.log(`[SampleLoader] Sent data to ${selector}`);
        } catch (e) {
          console.warn(`[SampleLoader] Failed to send to ${selector}:`, e);
        }
      }
    });
  }

  // Re-fetch from server and broadcast
  async function reloadFromServer() {
    if (!lastRequest) {
      console.warn('[SampleLoader] No previous request to reload');
      return null;
    }

    console.log('[SampleLoader] Reloading from server:', lastRequest);

    try {
      currentData = await fetchSample(lastRequest);
      broadcastToIframes(currentData);
      return currentData;
    } catch (err) {
      console.error('[SampleLoader] Reload failed:', err);
      throw err;
    }
  }

  function reloadCurrentData() {
    if (currentData) {
      broadcastToIframes(currentData);
    }
  }

  // ============================================================================
  // UI Rendering
  // ============================================================================

  function render() {
    if (!containerEl) return;

    const { sampleSizes, namedSamples, outputFormats, defaultOutputFormat } = config;

    containerEl.innerHTML = `
      <div class="sample-loader" style="
        display: flex;
        align-items: center;
        gap: 8px;
        font-family: 'Space Grotesk', -apple-system, sans-serif;
      ">
        <button class="sl-toggle-btn" style="
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 8px 14px;
          background: #1a1a1a;
          border: 1px solid #333;
          color: #888;
          font-family: inherit;
          font-size: 12px;
          cursor: pointer;
          border-radius: 6px;
          transition: all 0.2s;
        ">
          <span>📥</span>
          <span class="sl-btn-text">Load Sample</span>
          <span class="sl-arrow" style="font-size: 10px;">▼</span>
        </button>
        
        <button class="sl-reload-btn" style="
          display: flex;
          align-items: center;
          justify-content: center;
          width: 32px;
          height: 32px;
          padding: 0;
          background: #1a1a1a;
          border: 1px solid #333;
          color: #888;
          font-family: inherit;
          font-size: 14px;
          cursor: pointer;
          border-radius: 6px;
          transition: all 0.2s;
          opacity: ${currentData ? 1 : 0.4};
          pointer-events: ${currentData ? 'auto' : 'none'};
        " title="Reload from server (re-fetch &amp; broadcast)">
          🔄
        </button>
        
        <div class="sl-dropdown" style="
          display: none;
          position: absolute;
          top: 100%;
          left: 0;
          margin-top: 4px;
          background: #1a1a1a;
          border: 1px solid #333;
          border-radius: 8px;
          padding: 12px;
          z-index: 1000;
          min-width: 280px;
          box-shadow: 0 8px 24px rgba(0,0,0,0.5);
        ">
          <div style="margin-bottom: 12px;">
            <div style="font-size: 10px; color: #666; text-transform: uppercase; margin-bottom: 6px;">
              Load By
            </div>
            <div class="sl-tab-group" style="display: flex; gap: 2px; background: #0d0d0d; padding: 2px; border-radius: 4px;">
              <button class="sl-tab active" data-tab="size" style="
                flex: 1;
                padding: 6px 12px;
                font-size: 11px;
                border: none;
                border-radius: 3px;
                cursor: pointer;
                font-family: inherit;
                background: #4ecdc4;
                color: #000;
              ">Size</button>
              <button class="sl-tab" data-tab="name" style="
                flex: 1;
                padding: 6px 12px;
                font-size: 11px;
                border: none;
                border-radius: 3px;
                cursor: pointer;
                font-family: inherit;
                background: transparent;
                color: #888;
              ">Name</button>
            </div>
          </div>
          
          <div class="sl-size-panel" style="margin-bottom: 12px;">
            <div style="font-size: 10px; color: #666; text-transform: uppercase; margin-bottom: 6px;">
              Element Count
            </div>
            <select class="sl-size-select" style="
              width: 100%;
              padding: 8px;
              background: #0d0d0d;
              border: 1px solid #333;
              border-radius: 4px;
              color: #e0e0e0;
              font-size: 12px;
              font-family: inherit;
              cursor: pointer;
            ">
              ${sampleSizes.map(size => `<option value="${size}">${size} elements</option>`).join('')}
            </select>
          </div>
          
          <div class="sl-name-panel" style="display: none; margin-bottom: 12px;">
            <div style="font-size: 10px; color: #666; text-transform: uppercase; margin-bottom: 6px;">
              Sample Name
            </div>
            <select class="sl-name-select" style="
              width: 100%;
              padding: 8px;
              background: #0d0d0d;
              border: 1px solid #333;
              border-radius: 4px;
              color: #e0e0e0;
              font-size: 12px;
              font-family: inherit;
              cursor: pointer;
            ">
              ${namedSamples.map(name => `<option value="${name}">${name}</option>`).join('')}
            </select>
          </div>
          
          <div class="sl-format-panel" style="margin-bottom: 12px;">
            <div style="font-size: 10px; color: #666; text-transform: uppercase; margin-bottom: 6px;">
              Output Format
            </div>
            <select class="sl-format-select" style="
              width: 100%;
              padding: 8px;
              background: #0d0d0d;
              border: 1px solid #333;
              border-radius: 4px;
              color: #e0e0e0;
              font-size: 12px;
              font-family: inherit;
              cursor: pointer;
            ">
              ${outputFormats.map(fmt => `<option value="${fmt.value}" ${fmt.value === defaultOutputFormat ? 'selected' : ''}>${fmt.label} - ${fmt.description}</option>`).join('')}
            </select>
          </div>
          
          <button class="sl-load-btn" style="
            width: 100%;
            padding: 10px;
            background: #4ecdc4;
            border: none;
            border-radius: 4px;
            color: #000;
            font-size: 12px;
            font-weight: 500;
            font-family: inherit;
            cursor: pointer;
            transition: all 0.2s;
          ">
            Load & Broadcast
          </button>
          
          <div class="sl-status" style="
            margin-top: 8px;
            font-size: 10px;
            color: #555;
            text-align: center;
          "></div>
        </div>
        
        <div class="sl-current" style="
          font-size: 11px;
          color: #666;
          display: ${currentData ? 'block' : 'none'};
        ">
          Loaded: <span style="color: #4ecdc4;">${currentData?.name || ''}</span>
          <span style="color: #888; margin-left: 4px;">(${currentData?.format || 'full'})</span>
        </div>
      </div>
    `;

    // Position the container relatively for dropdown
    containerEl.style.position = 'relative';

    attachEventListeners();
  }

  function attachEventListeners() {
    const toggleBtn = containerEl.querySelector('.sl-toggle-btn');
    const reloadBtn = containerEl.querySelector('.sl-reload-btn');
    const dropdown = containerEl.querySelector('.sl-dropdown');
    const tabs = containerEl.querySelectorAll('.sl-tab');
    const sizePanel = containerEl.querySelector('.sl-size-panel');
    const namePanel = containerEl.querySelector('.sl-name-panel');
    const sizeSelect = containerEl.querySelector('.sl-size-select');
    const nameSelect = containerEl.querySelector('.sl-name-select');
    const formatSelect = containerEl.querySelector('.sl-format-select');
    const loadBtn = containerEl.querySelector('.sl-load-btn');
    const status = containerEl.querySelector('.sl-status');
    const arrow = containerEl.querySelector('.sl-arrow');
    const btnText = containerEl.querySelector('.sl-btn-text');

    let isOpen = false;
    let currentTab = 'size';

    // Toggle dropdown
    toggleBtn.addEventListener('click', () => {
      isOpen = !isOpen;
      dropdown.style.display = isOpen ? 'block' : 'none';
      arrow.textContent = isOpen ? '▲' : '▼';
      toggleBtn.style.background = isOpen ? 'rgba(78, 205, 196, 0.1)' : '#1a1a1a';
      toggleBtn.style.borderColor = isOpen ? '#4ecdc4' : '#333';
      toggleBtn.style.color = isOpen ? '#4ecdc4' : '#888';
    });

    // Close on outside click
    document.addEventListener('click', (e) => {
      if (!containerEl.contains(e.target) && isOpen) {
        isOpen = false;
        dropdown.style.display = 'none';
        arrow.textContent = '▼';
        toggleBtn.style.background = '#1a1a1a';
        toggleBtn.style.borderColor = '#333';
        toggleBtn.style.color = '#888';
      }
    });

    // Tab switching
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        currentTab = tab.dataset.tab;
        tabs.forEach(t => {
          t.style.background = t.dataset.tab === currentTab ? '#4ecdc4' : 'transparent';
          t.style.color = t.dataset.tab === currentTab ? '#000' : '#888';
        });
        sizePanel.style.display = currentTab === 'size' ? 'block' : 'none';
        namePanel.style.display = currentTab === 'name' ? 'block' : 'none';
      });
    });

    // Reload button - re-fetches from server
    reloadBtn.addEventListener('click', async () => {
      if (!lastRequest || isLoading) return;

      isLoading = true;
      reloadBtn.style.opacity = '0.5';
      status.textContent = 'Reloading from server...';
      status.style.color = '#888';

      try {
        await reloadFromServer();
        status.textContent = `Reloaded "${currentData.name}" (${currentData.format}) from server`;
        status.style.color = '#4ecdc4';

        // Callback
        if (config.onDataLoaded) {
          config.onDataLoaded(currentData);
        }
      } catch (err) {
        status.textContent = `Reload failed: ${err.message}`;
        status.style.color = '#ff6b6b';

        if (config.onError) {
          config.onError(err);
        }
      } finally {
        isLoading = false;
        reloadBtn.style.opacity = '1';
        setTimeout(() => { status.textContent = ''; }, 3000);
      }
    });

    // Load button
    loadBtn.addEventListener('click', async () => {
      if (isLoading) return;

      isLoading = true;
      loadBtn.disabled = true;
      loadBtn.textContent = 'Loading...';
      btnText.textContent = 'Loading...';
      status.textContent = 'Fetching data...';
      status.style.color = '#888';

      try {
        const outputFormat = formatSelect.value;
        const request = currentTab === 'size'
          ? { type: 'size', value: parseInt(sizeSelect.value), outputFormat }
          : { type: 'name', value: nameSelect.value, outputFormat };

        // Store for reload
        lastRequest = request;

        currentData = await fetchSample(request);

        // Broadcast to all iframes
        broadcastToIframes(currentData);

        // Update UI
        status.textContent = `Loaded "${currentData.name}" (${outputFormat}) - broadcasted`;
        status.style.color = '#4ecdc4';

        // Update current indicator
        const currentEl = containerEl.querySelector('.sl-current');
        currentEl.style.display = 'block';
        currentEl.querySelector('span').textContent = currentData.name;
        // Update format indicator
        const formatSpan = currentEl.querySelectorAll('span')[1];
        if (formatSpan) formatSpan.textContent = `(${outputFormat})`;

        // Enable reload button
        reloadBtn.style.opacity = '1';
        reloadBtn.style.pointerEvents = 'auto';

        // Callback
        if (config.onDataLoaded) {
          config.onDataLoaded(currentData);
        }

      } catch (err) {
        console.error('[SampleLoader] Error:', err);
        status.textContent = `Error: ${err.message}`;
        status.style.color = '#ff6b6b';

        if (config.onError) {
          config.onError(err);
        }
      } finally {
        isLoading = false;
        loadBtn.disabled = false;
        loadBtn.textContent = 'Load & Broadcast';
        btnText.textContent = 'Load Sample';
      }
    });

    // Hover effects
    [toggleBtn, reloadBtn].forEach(btn => {
      btn.addEventListener('mouseenter', () => {
        if (!isOpen || btn !== toggleBtn) {
          btn.style.borderColor = '#4ecdc4';
          btn.style.color = '#4ecdc4';
        }
      });
      btn.addEventListener('mouseleave', () => {
        if (!isOpen || btn !== toggleBtn) {
          btn.style.borderColor = '#333';
          btn.style.color = '#888';
        }
        if (isOpen && btn === toggleBtn) {
          btn.style.borderColor = '#4ecdc4';
          btn.style.color = '#4ecdc4';
        }
      });
    });
  }

  // ============================================================================
  // Public API
  // ============================================================================

  return {
    /**
     * Initialize the sample loader
     * @param {string} containerId - ID of the container element
     * @param {object} customConfig - Optional config overrides
     */
    init(containerId, customConfig = {}) {
      containerEl = document.getElementById(containerId);
      if (!containerEl) {
        console.error(`[SampleLoader] Container #${containerId} not found`);
        return;
      }

      config = { ...DEFAULT_CONFIG, ...customConfig };
      render();

      console.log('[SampleLoader] Initialized');
    },

    /**
     * Programmatically load a sample
     * @param {object} request - { type: 'size'|'name', value: number|string }
     */
    async load(request) {
      try {
        lastRequest = request;  // Store for reload
        currentData = await fetchSample(request);
        broadcastToIframes(currentData);
        render();
        return currentData;
      } catch (err) {
        console.error('[SampleLoader] Error:', err);
        throw err;
      }
    },

    /**
     * Reload from server (re-fetches data) and broadcast to all iframes
     */
    async reload() {
      return reloadFromServer();
    },

    /**
     * Re-broadcast current cached data to all iframes (no server call)
     */
    rebroadcast() {
      reloadCurrentData();
    },

    /**
     * Get current loaded data
     */
    getData() {
      return currentData;
    },

    /**
     * Update configuration
     */
    configure(customConfig) {
      config = { ...config, ...customConfig };
      render();
    },

    /**
     * Broadcast arbitrary data to iframes
     */
    broadcast(data) {
      broadcastToIframes(data);
    }
  };
})();

// Export for module systems if available
if (typeof module !== 'undefined' && module.exports) {
  module.exports = SampleLoader;
}