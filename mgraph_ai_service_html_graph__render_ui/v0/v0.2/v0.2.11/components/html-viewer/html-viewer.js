/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - HTML Viewer Component
   v0.2.11 - View, edit, and preview cached HTML content
   
   Features:
   - View mode: syntax-highlighted HTML code
   - Edit mode: editable textarea
   - Preview mode: rendered HTML in iframe
   - Save changes back to cache
   - Character count and stats
   - Loads by cache_id via /flet-html-domain/html/load/{namespace}/id
   ═══════════════════════════════════════════════════════════════════════════════ */

class HtmlViewer extends BaseComponent {
    constructor() {
        super();
        this.namespace = '';
        this.cacheKey = '';
        this.cacheId = '';
        this.html = '';
        this.originalHtml = '';
        this.mode = 'view'; // 'view', 'edit', 'preview'
        this.isModified = false;
        this.isLoading = false;
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Lifecycle
    // ═══════════════════════════════════════════════════════════════════════════

    bindElements() {
        this.toolbar = this.$('#viewer-toolbar');
        this.contentEl = this.$('#viewer-content');
        this.infoEl = this.$('#viewer-info');
        this.modeButtons = this.$$('.mode-btn');
        this.copyBtn = this.$('#copy-btn');
        this.saveBtn = this.$('#save-btn');
        this.maximizeBtn = this.$('#maximize-btn');
    }

    setupEventListeners() {
        // Mode toggle buttons
        this.modeButtons.forEach(btn => {
            this.addTrackedListener(btn, 'click', () => this.setMode(btn.dataset.mode));
        });

        this.addTrackedListener(this.copyBtn, 'click', this.copyToClipboard);
        this.addTrackedListener(this.saveBtn, 'click', this.saveChanges);
        this.addTrackedListener(this.maximizeBtn, 'click', () => {
            this.emit('maximize-requested');
        });

        // Keyboard shortcut for save
        this.addTrackedListener(this.shadowRoot, 'keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                this.saveChanges();
            }
        });
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Public API
    // ═══════════════════════════════════════════════════════════════════════════

    /**
     * Load HTML by cache_id
     * @param {string} namespace - Cache namespace
     * @param {string} cacheId - Entity cache_id
     * @param {string} cacheKey - Optional cache_key (for saving later)
     */
    async loadById(namespace, cacheId, cacheKey = '') {
        if (this.isLoading) return;

        this.isLoading = true;
        this.namespace = namespace;
        this.cacheId = cacheId;
        this.cacheKey = cacheKey;  // Store the key for saving
        this.showLoading();

        try {
            const response = await window.apiClient.loadHtmlById(namespace, cacheId);

            if (response.success && response.found) {
                this.html = response.html || '';
                this.originalHtml = this.html;
                this.cacheKey = response.cache_key || this.cacheKey;  // API response takes precedence
                this.isModified = false;

                this.updateInfo();
                this.renderContent();

                this.emit('html-loaded', {
                    namespace: this.namespace,
                    cacheKey: this.cacheKey,
                    cacheId: this.cacheId,
                    charCount: this.html.length,
                    response
                });
            } else {
                this.showNotFound();
            }
        } catch (error) {
            console.error('[HtmlViewer] Load error:', error);
            this.showError(error.message || 'Failed to load HTML');
        } finally {
            this.isLoading = false;
        }
    }

    /**
     * Load HTML by cache_key (legacy support)
     */
    async loadByKey(namespace, cacheKey) {
        if (this.isLoading) return;

        this.isLoading = true;
        this.namespace = namespace;
        this.cacheKey = cacheKey;
        this.showLoading();

        try {
            const response = await window.apiClient.loadHtmlByKey(namespace, cacheKey);

            if (response.success && response.found) {
                this.html = response.html || '';
                this.originalHtml = this.html;
                this.cacheId = response.cache_id || '';
                this.isModified = false;

                this.updateInfo();
                this.renderContent();

                this.emit('html-loaded', {
                    namespace: this.namespace,
                    cacheKey: this.cacheKey,
                    cacheId: this.cacheId,
                    charCount: this.html.length,
                    response
                });
            } else {
                this.showNotFound();
            }
        } catch (error) {
            console.error('[HtmlViewer] Load error:', error);
            this.showError(error.message || 'Failed to load HTML');
        } finally {
            this.isLoading = false;
        }
    }

    /**
     * Set the current view mode
     */
    setMode(mode) {
        if (mode === this.mode) return;

        // Capture content if leaving edit mode
        if (this.mode === 'edit') {
            this.captureEditContent();
        }

        this.mode = mode;

        // Update toggle buttons
        this.modeButtons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.mode === mode);
        });

        this.renderContent();
    }

    /**
     * Get current HTML content
     */
    getHtml() {
        if (this.mode === 'edit') {
            this.captureEditContent();
        }
        return this.html;
    }

    /**
     * Set HTML content directly
     */
    setHtml(html, cacheKey = '', cacheId = '', namespace = '') {
        this.html = html;
        this.originalHtml = html;
        this.cacheKey = cacheKey;
        this.cacheId = cacheId;
        this.namespace = namespace || this.namespace;
        this.isModified = false;

        this.updateInfo();
        this.updateSaveButton();
        this.renderContent();
    }

    /**
     * Clear content
     */
    clear() {
        this.html = '';
        this.originalHtml = '';
        this.cacheKey = '';
        this.cacheId = '';
        this.isModified = false;
        this.renderEmptyState();
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Internal Methods
    // ═══════════════════════════════════════════════════════════════════════════

    captureEditContent() {
        const textarea = this.$('.html-editor-textarea');
        if (textarea) {
            this.html = textarea.value;
            this.isModified = this.html !== this.originalHtml;
            this.updateSaveButton();
        }
    }

    async copyToClipboard() {
        try {
            await navigator.clipboard.writeText(this.html);
            this.showToast('Copied to clipboard!');
        } catch (error) {
            // Fallback
            const textarea = document.createElement('textarea');
            textarea.value = this.html;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            this.showToast('Copied to clipboard!');
        }
    }

    async saveChanges() {
        if (!this.isModified) {
            this.showToast('No changes to save');
            return;
        }
        
        if (!this.cacheKey && !this.cacheId) {
            this.showToast('Cannot save: no cache key or ID', 'error');
            return;
        }

        if (this.mode === 'edit') {
            this.captureEditContent();
        }

        this.showToast('Saving...');

        try {
            let response;
            
            if (this.cacheKey) {
                // Save by key (preferred - maintains the key)
                response = await window.apiClient.storeHtmlByKey(
                    this.namespace,
                    this.cacheKey,
                    this.html
                );
            } else {
                // Fallback: save as raw with cache_id reference
                response = await window.apiClient.storeHtmlRaw(
                    this.namespace,
                    this.html
                );
            }

            if (response.success) {
                this.originalHtml = this.html;
                this.cacheId = response.cache_id || this.cacheId;
                this.cacheKey = response.cache_key || this.cacheKey;
                this.isModified = false;
                this.updateSaveButton();
                this.updateInfo();
                this.showToast('Saved successfully!');

                this.emit('html-saved', {
                    namespace: this.namespace,
                    cacheKey: this.cacheKey,
                    cacheId: this.cacheId,
                    charCount: this.html.length,
                    response
                });
            } else {
                this.showToast('Save failed: ' + (response.error || 'Unknown error'), 'error');
            }
        } catch (error) {
            console.error('[HtmlViewer] Save error:', error);
            this.showToast('Save failed: ' + error.message, 'error');
        }
    }

    updateInfo() {
        const charCount = this.html.length;
        const lineCount = this.html.split('\n').length;
        const modified = this.isModified ? ' (modified)' : '';
        this.infoEl.textContent = `${this.formatNumber(charCount)} chars · ${this.formatNumber(lineCount)} lines${modified}`;
    }

    updateSaveButton() {
        this.saveBtn.disabled = !this.isModified;
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Rendering
    // ═══════════════════════════════════════════════════════════════════════════

    renderContent() {
        if (!this.html && !this.cacheKey) {
            this.renderEmptyState();
            return;
        }

        switch (this.mode) {
            case 'view':
                this.renderViewMode();
                break;
            case 'edit':
                this.renderEditMode();
                break;
            case 'preview':
                this.renderPreviewMode();
                break;
        }
    }

    renderViewMode() {
        this.contentEl.innerHTML = `
            <pre class="html-viewer-code">${this.escapeHtml(this.html)}</pre>
        `;
    }

    renderEditMode() {
        this.contentEl.innerHTML = `
            <textarea class="html-editor-textarea" spellcheck="false">${this.escapeHtml(this.html)}</textarea>
        `;

        const textarea = this.$('.html-editor-textarea');
        
        this.addTrackedListener(textarea, 'input', () => {
            this.html = textarea.value;
            this.isModified = this.html !== this.originalHtml;
            this.updateSaveButton();
            this.updateInfo();
        });

        textarea.focus();
    }

    renderPreviewMode() {
        this.contentEl.innerHTML = `
            <iframe class="html-viewer-preview" sandbox="allow-same-origin"></iframe>
        `;

        const iframe = this.$('iframe');
        
        iframe.onload = () => {
            try {
                const doc = iframe.contentDocument || iframe.contentWindow.document;
                doc.open();
                doc.write(this.html);
                doc.close();
            } catch (e) {
                console.error('[HtmlViewer] Preview error:', e);
            }
        };

        iframe.src = 'about:blank';
    }

    renderEmptyState() {
        this.contentEl.innerHTML = `
            <div class="html-viewer-empty">
                <div class="html-viewer-empty-icon">📄</div>
                <p>Select a cached page to view its HTML</p>
                <p class="empty-hint">Double-click an entity in the browser to load its content.</p>
            </div>
        `;
    }

    showLoading() {
        this.contentEl.innerHTML = `
            <div class="html-viewer-empty">
                <div class="spinner"></div>
                <p>Loading HTML...</p>
            </div>
        `;
    }

    showNotFound() {
        this.contentEl.innerHTML = `
            <div class="html-viewer-empty">
                <div class="html-viewer-empty-icon">🔍</div>
                <p>No HTML found</p>
                <p class="empty-hint">Cache ID: ${this.escapeHtml(this.cacheId || this.cacheKey)}</p>
            </div>
        `;
    }

    showError(message) {
        this.contentEl.innerHTML = `
            <div class="html-viewer-empty">
                <div class="html-viewer-empty-icon">❌</div>
                <p class="error-message">${this.escapeHtml(message)}</p>
            </div>
        `;
    }

    showToast(message, type = 'info') {
        // Emit toast event for page-level handling
        this.emit('toast', { message, type });
    }
}

customElements.define('html-viewer', HtmlViewer);
