/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Cache Store Page Orchestrator
   v0.2.11 - Coordinates components for HTML cache browsing and editing
   
   Responsibilities:
   - Initialize all components
   - Wire up event communication
   - Handle keyboard shortcuts
   - Manage maximize mode
   - Coordinate state between components
   ═══════════════════════════════════════════════════════════════════════════════ */

class CacheStore {
    constructor() {
        // Component references
        this.cacheBrowser = null;
        this.htmlViewer = null;
        this.miniBrowser = null;
        this.cacheMetadata = null;
        this.flowTimeline = null;

        // State
        this.namespace = 'html-cache';
        this.currentCacheKey = '';
        this.currentCacheId = '';
        this.currentEntity = null;
        this.isMaximized = false;
    }

    /**
     * Initialize the page
     */
    async init() {
        // Wait for components to be ready
        await this.waitForComponents();

        // Get component references
        this.cacheBrowser = document.querySelector('cache-browser');
        this.htmlViewer = document.querySelector('html-viewer');
        this.miniBrowser = document.querySelector('mini-browser');
        this.cacheMetadata = document.querySelector('cache-metadata');
        this.flowTimeline = document.querySelector('flow-timeline');

        // Setup event listeners
        this.setupEventListeners();
        
        // Setup keyboard shortcuts
        this.setupKeyboardShortcuts();

        // Setup tab switching
        this.setupTabs();

        // Setup view mode tabs (raw vs browser)
        this.setupViewModeTabs();

        console.log('CacheStore v0.2.11 initialized');
    }

    /**
     * Wait for all components to be defined
     */
    async waitForComponents() {
        const components = [
            'cache-browser',
            'html-viewer',
            'mini-browser',
            'cache-metadata',
            'flow-timeline'
        ];

        await Promise.all(
            components.map(name => customElements.whenDefined(name))
        );
    }

    /**
     * Setup event listeners for component communication
     */
    setupEventListeners() {
        // Browse button
        document.getElementById('browse-btn')?.addEventListener('click', () => {
            this.browse();
        });

        // Namespace input - enter key
        document.getElementById('namespace-input')?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                this.browse();
            }
        });

        // Cache browser events
        document.addEventListener('entities-loaded', (e) => {
            this.handleEntitiesLoaded(e.detail);
        });

        document.addEventListener('path-changed', (e) => {
            this.handlePathChanged(e.detail);
        });

        document.addEventListener('item-selected', (e) => {
            this.handleItemSelected(e.detail);
        });

        document.addEventListener('entity-opened', (e) => {
            this.handleEntityOpened(e.detail);
        });

        // HTML viewer events
        document.addEventListener('html-loaded', (e) => {
            this.handleHtmlLoaded(e.detail);
        });

        document.addEventListener('html-saved', (e) => {
            this.handleHtmlSaved(e.detail);
        });

        document.addEventListener('maximize-requested', () => {
            this.toggleMaximize();
        });

        // Toast events
        document.addEventListener('toast', (e) => {
            this.showToast(e.detail.message, e.detail.type);
        });

        // Data file selected (from metadata panel)
        document.addEventListener('data-file-selected', (e) => {
            this.handleDataFileSelected(e.detail);
        });

        // Maximize toolbar buttons
        document.getElementById('minimize-btn')?.addEventListener('click', () => {
            this.exitMaximize();
        });

        document.getElementById('max-refresh-btn')?.addEventListener('click', () => {
            this.refresh();
        });
    }

    /**
     * Setup keyboard shortcuts
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Skip if in input/textarea (including inside Shadow DOM)
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                return;
            }
            
            // Skip if html-viewer is in edit mode (textarea is in Shadow DOM)
            if (this.htmlViewer && this.htmlViewer.mode === 'edit') {
                return;
            }

            switch (e.key.toLowerCase()) {
                case 'r':
                    if (!e.ctrlKey && !e.metaKey) {
                        e.preventDefault();
                        this.refresh();
                    }
                    break;
                case 'm':
                    if (!e.ctrlKey && !e.metaKey) {
                        e.preventDefault();
                        this.toggleMaximize();
                    }
                    break;
                case 'escape':
                    if (this.isMaximized) {
                        this.exitMaximize();
                    }
                    break;
                case 'backspace':
                    if (!e.ctrlKey && !e.metaKey) {
                        e.preventDefault();
                        this.cacheBrowser?.navigateUp();
                    }
                    break;
                case 'h':
                    if (!e.ctrlKey && !e.metaKey) {
                        e.preventDefault();
                        this.showShortcutsHelp();
                    }
                    break;
            }
        });
    }

    /**
     * Setup right panel tab switching (Metadata vs Flows)
     */
    setupTabs() {
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const tab = btn.dataset.tab;
                this.switchTab(tab);
            });
        });
    }

    /**
     * Setup center panel view mode tabs (Raw vs Browser)
     */
    setupViewModeTabs() {
        document.querySelectorAll('.view-tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const view = btn.dataset.view;
                this.switchViewMode(view);
            });
        });
    }

    /**
     * Switch between metadata and flows tabs
     */
    switchTab(tabName) {
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });

        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.toggle('hidden', content.id !== `tab-${tabName}`);
        });
    }

    /**
     * Switch between raw view and browser view
     */
    switchViewMode(viewName) {
        document.querySelectorAll('.view-tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.view === viewName);
        });

        document.querySelectorAll('.view-content').forEach(content => {
            content.classList.toggle('hidden', content.id !== `view-${viewName}`);
        });
    }

    /**
     * Browse the cache with current namespace
     */
    browse() {
        const namespaceInput = document.getElementById('namespace-input');
        this.namespace = namespaceInput?.value.trim() || 'html-cache';
        
        this.cacheBrowser?.setNamespace(this.namespace, true);
        this.updateStatus('Browsing...');
    }

    /**
     * Refresh current view
     */
    refresh() {
        if (this.currentCacheId) {
            this.htmlViewer?.loadById(this.namespace, this.currentCacheId);
        } else {
            this.cacheBrowser?.refresh();
        }
        this.showToast('Refreshed');
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Event Handlers
    // ═══════════════════════════════════════════════════════════════════════════

    handleEntitiesLoaded(detail) {
        this.updateStatus(`Loaded ${detail.count} entities`);
    }

    handlePathChanged(detail) {
        this.updateStatus('Ready');
        this.updateStatusPath(detail.pathString || '(root)');
    }

    handleItemSelected(detail) {
        if (detail.entity) {
            this.cacheMetadata?.setEntity(detail.entity, detail.namespace);
        } else {
            this.cacheMetadata?.setPathPreview(detail.namespace, detail.pathString);
        }
        this.updateStatusPath(detail.pathString);
    }

    handleEntityOpened(detail) {
        this.currentCacheKey = detail.cacheKey;
        this.currentCacheId = detail.cacheId;
        this.currentEntity = detail.entity;
        
        this.updateStatus('Loading HTML...');
        this.updateStatusPath(detail.cacheKey);

        // Load HTML by cache_id, passing cacheKey for save operations
        this.htmlViewer?.loadById(detail.namespace, detail.cacheId, detail.cacheKey);
    }

    handleHtmlLoaded(detail) {
        this.currentCacheId = detail.cacheId;
        this.updateStatus('Loaded');

        // Update metadata panel
        this.cacheMetadata?.setFromLoadResponse(detail.response, detail.namespace);

        // Update mini browser with the HTML
        this.miniBrowser?.setHtml(
            detail.response.html,
            detail.cacheKey,
            detail.response.final_url || detail.cacheKey
        );

        // Load flows for this entity
        if (detail.cacheId) {
            this.flowTimeline?.loadFlows(detail.namespace, detail.cacheId);
        }

        // Update maximize toolbar
        const maxTitle = document.getElementById('max-title');
        if (maxTitle) {
            maxTitle.textContent = detail.cacheKey;
        }

        const maxStats = document.getElementById('max-stats');
        if (maxStats) {
            maxStats.textContent = `${detail.charCount.toLocaleString()} chars`;
        }
    }

    handleHtmlSaved(detail) {
        this.updateStatus('Saved');
        this.cacheMetadata?.setFromLoadResponse(detail.response, detail.namespace);
        this.showToast('Saved successfully!');
    }

    handleDataFileSelected(detail) {
        console.log('[CacheStore] Data file selected:', detail);

        // Load the data file into the viewer
        this.htmlViewer?.loadDataFile(
            detail.namespace,
            detail.cacheId,
            detail.dataKey,
            detail.fileId,
            detail.dataType
        );

        // Update status
        this.updateStatus(`Loading ${detail.dataKey}/${detail.fileId}...`);
        this.updateStatusPath(`${detail.dataKey}/${detail.fileId}`);

        // Switch to Raw view (data files don't preview well in browser)
        this.switchViewMode('raw');

        if (detail.dataType !== 'string' || !detail.dataKey.includes('html')) {
            this.miniBrowser?.clear();
            // Or show a message that preview isn't available for this file type
        }
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Maximize Mode
    // ═══════════════════════════════════════════════════════════════════════════

    toggleMaximize() {
        if (this.isMaximized) {
            this.exitMaximize();
        } else {
            this.enterMaximize();
        }
    }

    enterMaximize() {
        document.querySelector('.cache-store-app')?.classList.add('maximized');
        this.isMaximized = true;
    }

    exitMaximize() {
        document.querySelector('.cache-store-app')?.classList.remove('maximized');
        this.isMaximized = false;
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // UI Updates
    // ═══════════════════════════════════════════════════════════════════════════

    updateStatus(message) {
        const statusEl = document.getElementById('status-message');
        if (statusEl) {
            statusEl.textContent = message;
        }
    }

    updateStatusPath(path) {
        const pathEl = document.getElementById('status-path');
        if (pathEl) {
            pathEl.textContent = path;
        }
    }

    showShortcutsHelp() {
        const shortcuts = `
Keyboard Shortcuts:

R         - Refresh
M         - Maximize/Minimize
H         - Show this help
Backspace - Go up one folder
Esc       - Exit maximize
Ctrl+S    - Save (in edit mode)
        `.trim();

        alert(shortcuts);
    }

    showToast(message, type = 'info') {
        const existing = document.querySelector('.cache-store-toast');
        if (existing) existing.remove();

        const toast = document.createElement('div');
        toast.className = `cache-store-toast ${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);

        requestAnimationFrame(() => toast.classList.add('visible'));

        setTimeout(() => {
            toast.classList.remove('visible');
            setTimeout(() => toast.remove(), 300);
        }, 2000);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const cacheStore = new CacheStore();
    cacheStore.init();

    // Make available globally for debugging
    window.cacheStore = cacheStore;
});
