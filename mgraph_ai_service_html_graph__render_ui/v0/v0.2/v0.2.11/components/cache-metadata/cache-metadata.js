/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Cache Metadata Component
   v0.2.11 - Display entity metadata and data files
   
   Features:
   - Display cache_id, cache_key, cache_hash, strategy
   - Show timestamps (formatted)
   - Show content_size (formatted bytes)
   - List data_files with click to view
   ═══════════════════════════════════════════════════════════════════════════════ */

class CacheMetadata extends BaseComponent {
    constructor() {
        super();
        this.entity = null;
        this.namespace = '';
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Lifecycle
    // ═══════════════════════════════════════════════════════════════════════════

    bindElements() {
        this.contentEl = this.$('#metadata-content');
    }

    setupEventListeners() {
        // Data file clicks handled via delegation
        this.addTrackedListener(this.contentEl, 'click', this.handleContentClick);
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Public API
    // ═══════════════════════════════════════════════════════════════════════════

    /**
     * Set entity data from API response
     */
    setEntity(entity, namespace = '') {
        this.entity = entity;
        this.namespace = namespace || this.namespace;
        this.renderMetadata();
    }

    /**
     * Set from load response (includes html, found, etc.)
     */
    setFromLoadResponse(response, namespace = '') {
        this.entity = {
            cache_id: response.cache_id,
            cache_key: response.cache_key,
            cache_hash: response.cache_hash,
            namespace: namespace,
            found: response.found,
            success: response.success,
            content_size: response.html ? response.html.length : 0,
            stored_at: response.stored_at,
            data_files: response.data_files || null
        };
        this.namespace = namespace;
        this.renderMetadata();
    }

    /**
     * Set preview info for selected path (before loading)
     */
    setPathPreview(namespace, pathString) {
        this.entity = {
            cache_key: pathString,
            namespace: namespace
        };
        this.namespace = namespace;
        this.renderMetadata();
    }

    /**
     * Clear metadata
     */
    clear() {
        this.entity = null;
        this.renderMetadata();
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Event Handlers
    // ═══════════════════════════════════════════════════════════════════════════

    handleContentClick(e) {
        const dataFileItem = e.target.closest('.data-file-item');
        if (dataFileItem) {
            const dataKey = dataFileItem.dataset.dataKey;
            const fileId = dataFileItem.dataset.fileId;
            const dataType = dataFileItem.dataset.dataType;

            this.emit('data-file-selected', {
                namespace: this.namespace,
                cacheId: this.entity?.cache_id,
                dataKey,
                fileId,
                dataType
            });
        }
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Rendering
    // ═══════════════════════════════════════════════════════════════════════════

    renderMetadata() {
        if (!this.entity) {
            this.contentEl.innerHTML = `
                <div class="metadata-empty">
                    Select an entity to view its metadata
                </div>
            `;
            return;
        }

        const e = this.entity;

        this.contentEl.innerHTML = `
            <div class="metadata-section">
                <div class="metadata-section-title">Entity Info</div>
                ${this.renderRow('Cache ID', e.cache_id, true)}
                ${this.renderRow('Cache Key', e.cache_key, true)}
                ${this.renderRow('Cache Hash', e.cache_hash, true)}
                ${this.renderRow('Namespace', e.namespace || this.namespace)}
                ${e.strategy ? this.renderRow('Strategy', e.strategy) : ''}
            </div>
            
            <div class="metadata-section">
                <div class="metadata-section-title">Content</div>
                ${this.renderRow('Size', e.content_size != null ? this.formatBytes(e.content_size) : '-')}
                ${e.stored_at ? this.renderRow('Stored', this.formatTimestamp(e.stored_at)) : ''}
                ${e.found !== undefined ? this.renderRow('Found', e.found ? '✓ Yes' : '✗ No', false, e.found ? 'success' : 'error') : ''}
            </div>
            
            ${e.data_files && e.data_files.length > 0 ? this.renderDataFiles(e.data_files) : ''}
            
            ${e.success !== undefined ? `
            <div class="metadata-section">
                <div class="metadata-section-title">Status</div>
                ${this.renderRow('Success', e.success ? '✓ Yes' : '✗ No', false, e.success ? 'success' : 'error')}
            </div>
            ` : ''}
        `;
    }

    renderRow(label, value, mono = false, status = '') {
        const valueClass = `metadata-value ${mono ? 'mono' : ''} ${status}`;
        const displayValue = value || '-';
        
        return `
            <div class="metadata-row">
                <span class="metadata-label">${label}</span>
                <span class="${valueClass}" title="${this.escapeHtml(String(displayValue))}">${this.escapeHtml(String(displayValue))}</span>
            </div>
        `;
    }

    renderDataFiles(files) {
        return `
            <div class="metadata-section">
                <div class="metadata-section-title">Data Files (${files.length})</div>
                <div class="data-files-list">
                    ${files.map(f => `
                        <div class="data-file-item" 
                             data-data-key="${this.escapeHtml(f.data_key)}"
                             data-file-id="${this.escapeHtml(f.data_file_id)}"
                             data-data-type="${this.escapeHtml(f.data_type)}">
                            <span class="data-file-icon">${f.data_type === 'json' ? '📋' : '📄'}</span>
                            <span class="data-file-name">${this.escapeHtml(f.data_key)}/${this.escapeHtml(f.data_file_id)}</span>
                            <span class="data-file-size">${this.formatBytes(f.file_size || 0)}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    formatTimestamp(ts) {
        if (!ts) return '-';
        try {
            // Handle Unix timestamps (seconds or milliseconds)
            const ms = ts > 1e12 ? ts : ts * 1000;
            return new Date(ms).toLocaleString();
        } catch {
            return String(ts);
        }
    }
}

customElements.define('cache-metadata', CacheMetadata);
