/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Cache Browser Component
   v0.2.11 - Entity-based browser with virtual folder tree
   
   Features:
   - Loads entities from /cache-entity/{namespace}/entities API
   - Builds virtual folder tree from cache_key paths
   - Click to drill down, double-click to open entity
   - Breadcrumb navigation
   - Stores cache_id for each entity node
   ═══════════════════════════════════════════════════════════════════════════════ */

class CacheBrowser extends BaseComponent {
    constructor() {
        super();
        this.namespace = 'html-cache';
        this.entities = [];           // Flat list from API
        this.virtualTree = {};        // Tree structure built from cache_keys
        this.currentPath = [];        // Current navigation path
        this.selectedItem = null;
        this.isLoading = false;
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Lifecycle
    // ═══════════════════════════════════════════════════════════════════════════

    bindElements() {
        this.backBtn = this.$('#browser-back-btn');
        this.refreshBtn = this.$('#browser-refresh-btn');
        this.homeBtn = this.$('#browser-home-btn');
        this.pathEl = this.$('#browser-path');
        this.listEl = this.$('#browser-list');
    }

    setupEventListeners() {
        this.addTrackedListener(this.backBtn, 'click', this.navigateUp);
        this.addTrackedListener(this.refreshBtn, 'click', this.refresh);
        this.addTrackedListener(this.homeBtn, 'click', () => this.navigateToPath([]));
        
        // List click delegation
        this.addTrackedListener(this.listEl, 'click', this.handleListClick);
        this.addTrackedListener(this.listEl, 'dblclick', this.handleListDoubleClick);
        
        // Path breadcrumb clicks
        this.addTrackedListener(this.pathEl, 'click', this.handlePathClick);
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Public API
    // ═══════════════════════════════════════════════════════════════════════════

    /**
     * Set namespace and optionally start browsing
     */
    setNamespace(namespace, autoBrowse = true) {
        this.namespace = namespace;
        if (autoBrowse) {
            this.navigateToPath([]);
        }
    }

    /**
     * Refresh current view
     */
    async refresh() {
        await this.loadEntities();
        this.renderCurrentFolder();
    }

    /**
     * Navigate to specific path
     */
    navigateToPath(pathArray) {
        this.currentPath = pathArray;
        this.selectedItem = null;
        if (this.entities.length === 0) {
            this.loadEntities().then(() => this.renderCurrentFolder());
        } else {
            this.renderCurrentFolder();
        }
    }

    /**
     * Navigate up one level
     */
    navigateUp() {
        if (this.currentPath.length > 0) {
            this.currentPath.pop();
            this.selectedItem = null;
            this.renderCurrentFolder();
        }
    }

    /**
     * Get current path as array
     */
    getCurrentPath() {
        return [...this.currentPath];
    }

    /**
     * Get current path as string
     */
    getCurrentPathString() {
        return this.currentPath.join('/');
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Data Loading
    // ═══════════════════════════════════════════════════════════════════════════

    async loadEntities() {
        if (this.isLoading) return;

        this.isLoading = true;
        this.showLoading();

        try {
            const response = await window.apiClient.listEntities(this.namespace, true);

            if (response.success) {
                this.entities = response.entities || [];
                this.buildVirtualTree();
                
                this.emit('entities-loaded', {
                    namespace: this.namespace,
                    count: this.entities.length
                });
            } else {
                this.showError('Failed to load entities');
            }
        } catch (error) {
            console.error('[CacheBrowser] Load error:', error);
            this.showError(error.message || 'Failed to load entities');
        } finally {
            this.isLoading = false;
        }
    }

    /**
     * Build virtual folder tree from flat entity list
     * 
     * Input: [{ cache_id: "abc", cache_key: "site/example.com/pages/home", ... }]
     * Output: {
     *   site: {
     *     _isFolder: true,
     *     example.com: {
     *       _isFolder: true,
     *       pages: {
     *         _isFolder: true,
     *         home: { _isFolder: false, _entity: {...} }
     *       }
     *     }
     *   }
     * }
     */
    buildVirtualTree() {
        this.virtualTree = {};

        for (const entity of this.entities) {
            const parts = (entity.cache_key || '').split('/').filter(p => p);
            let current = this.virtualTree;

            for (let i = 0; i < parts.length; i++) {
                const part = parts[i];
                const isLast = i === parts.length - 1;

                if (!current[part]) {
                    current[part] = isLast 
                        ? { _isFolder: false, _entity: entity }
                        : { _isFolder: true };
                } else if (isLast) {
                    // Entity at this path - mark as entity
                    current[part]._entity = entity;
                    current[part]._isFolder = false;
                }

                if (!isLast) {
                    // Ensure it's marked as a folder if we're traversing through it
                    if (!current[part]._isFolder && !current[part]._entity) {
                        current[part]._isFolder = true;
                    }
                    current = current[part];
                }
            }
        }
    }

    /**
     * Get items at current path
     */
    getItemsAtCurrentPath() {
        let node = this.virtualTree;
        
        for (const segment of this.currentPath) {
            if (node[segment]) {
                node = node[segment];
            } else {
                return [];
            }
        }

        // Extract children (excluding _ prefixed internal props)
        const items = [];
        for (const [name, value] of Object.entries(node)) {
            if (!name.startsWith('_')) {
                items.push({
                    name,
                    isFolder: value._isFolder !== false && !value._entity,
                    entity: value._entity || null
                });
            }
        }

        // Sort: folders first, then alphabetically
        items.sort((a, b) => {
            if (a.isFolder !== b.isFolder) return a.isFolder ? -1 : 1;
            return a.name.toLowerCase().localeCompare(b.name.toLowerCase());
        });

        return items;
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Event Handlers
    // ═══════════════════════════════════════════════════════════════════════════

    handleListClick(e) {
        const item = e.target.closest('.cache-browser-item');
        if (!item) return;

        // Deselect previous
        const prev = this.$('.cache-browser-item.selected');
        if (prev) prev.classList.remove('selected');

        // Select new
        item.classList.add('selected');
        this.selectedItem = item.dataset.name;

        const isFolder = item.classList.contains('folder');
        const cacheId = item.dataset.cacheId || null;
        const entity = cacheId ? this.entities.find(e => e.cache_id === cacheId) : null;

        this.emit('item-selected', {
            namespace: this.namespace,
            name: this.selectedItem,
            path: [...this.currentPath, this.selectedItem],
            pathString: [...this.currentPath, this.selectedItem].join('/'),
            isFolder,
            cacheId,
            entity
        });
    }

    handleListDoubleClick(e) {
        const item = e.target.closest('.cache-browser-item');
        if (!item) return;

        const name = item.dataset.name;
        const isFolder = item.classList.contains('folder');
        const cacheId = item.dataset.cacheId || null;

        if (isFolder) {
            // Drill down into folder
            this.currentPath.push(name);
            this.selectedItem = null;
            this.renderCurrentFolder();
            
            this.emit('path-changed', {
                namespace: this.namespace,
                path: this.currentPath,
                pathString: this.currentPath.join('/')
            });
        } else if (cacheId) {
            // Open entity
            const entity = this.entities.find(e => e.cache_id === cacheId);
            
            this.emit('entity-opened', {
                namespace: this.namespace,
                name,
                cacheId,
                cacheKey: entity?.cache_key || [...this.currentPath, name].join('/'),
                entity
            });
        }
    }

    handlePathClick(e) {
        const segment = e.target.closest('.path-segment');
        if (!segment) return;

        const pathStr = segment.dataset.path;
        const newPath = pathStr ? pathStr.split('/') : [];
        this.navigateToPath(newPath);

        this.emit('path-changed', {
            namespace: this.namespace,
            path: this.currentPath,
            pathString: this.currentPath.join('/')
        });
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Rendering
    // ═══════════════════════════════════════════════════════════════════════════

    renderCurrentFolder() {
        const items = this.getItemsAtCurrentPath();
        this.renderBreadcrumb();
        this.renderItemList(items);
    }

    renderBreadcrumb() {
        let segments = [`<span class="path-segment" data-path="">root</span>`];
        let accumulated = '';

        for (const part of this.currentPath) {
            accumulated = accumulated ? `${accumulated}/${part}` : part;
            segments.push(`
                <span class="path-separator">/</span>
                <span class="path-segment" data-path="${this.escapeHtml(accumulated)}">${this.escapeHtml(part)}</span>
            `);
        }

        this.pathEl.innerHTML = segments.join('');
    }

    renderItemList(items) {
        if (items.length === 0) {
            this.listEl.innerHTML = `
                <div class="cache-browser-empty">
                    <div class="cache-browser-empty-icon">📭</div>
                    <p>No items in this folder</p>
                    <p class="empty-path">Path: ${this.currentPath.join('/') || '(root)'}</p>
                </div>
            `;
            return;
        }

        this.listEl.innerHTML = items.map(item => {
            const cacheIdAttr = item.entity ? `data-cache-id="${item.entity.cache_id}"` : '';
            const typeClass = item.isFolder ? 'folder' : 'entity';
            const icon = item.isFolder ? '📁' : '📄';
            
            return `
                <div class="cache-browser-item ${typeClass}" 
                     data-name="${this.escapeHtml(item.name)}" 
                     ${cacheIdAttr}>
                    <span class="item-icon">${icon}</span>
                    <span class="item-name">${this.escapeHtml(item.name)}</span>
                    ${item.entity ? `<span class="item-meta">${this.formatBytes(item.entity.content_size || 0)}</span>` : ''}
                </div>
            `;
        }).join('');
    }

    showLoading() {
        this.listEl.innerHTML = `
            <div class="cache-browser-loading">
                <div class="spinner"></div>
                <span>Loading entities...</span>
            </div>
        `;
    }

    showError(message) {
        this.listEl.innerHTML = `
            <div class="cache-browser-empty">
                <div class="cache-browser-empty-icon">❌</div>
                <p class="error-message">${this.escapeHtml(message)}</p>
                <button class="btn btn-sm btn-secondary retry-btn">Retry</button>
            </div>
        `;
        
        const retryBtn = this.$('.retry-btn');
        if (retryBtn) {
            this.addTrackedListener(retryBtn, 'click', this.refresh);
        }
    }
}

customElements.define('cache-browser', CacheBrowser);
