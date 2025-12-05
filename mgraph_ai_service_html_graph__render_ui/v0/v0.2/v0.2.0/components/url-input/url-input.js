/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - URL Input Component
   v0.2.0 - Consolidated from v0.1.x
   ═══════════════════════════════════════════════════════════════════════════════ */

class UrlInput extends HTMLElement {
    constructor() {
        super();
        this.urlInput = null;
        this.fetchButton = null;
        this.statusText = null;
        this.isFetching = false;
    }

    connectedCallback() {
        this.render();
        this.setupEventListeners();
    }

    render() {
        this.innerHTML = `
            <style>
                .url-input-container {
                    display: flex;
                    flex-direction: column;
                    gap: var(--spacing-sm);
                }
                .url-input-row {
                    display: flex;
                    gap: var(--spacing-sm);
                }
                .url-input-field {
                    flex: 1;
                    padding: var(--spacing-sm);
                    border: 1px solid var(--color-border);
                    border-radius: var(--radius-sm);
                    font-family: var(--font-code);
                    font-size: 0.9em;
                }
                .url-input-field:focus {
                    outline: none;
                    border-color: var(--color-primary);
                }
                .url-fetch-btn {
                    padding: var(--spacing-sm) var(--spacing-md);
                    background: var(--color-info);
                    color: white;
                    border: none;
                    border-radius: var(--radius-sm);
                    font-weight: 500;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    white-space: nowrap;
                }
                .url-fetch-btn:hover:not(:disabled) {
                    opacity: 0.9;
                    transform: translateY(-1px);
                }
                .url-fetch-btn:disabled {
                    opacity: 0.6;
                    cursor: not-allowed;
                }
                .url-status {
                    font-size: 0.85em;
                    color: var(--color-text-secondary);
                    min-height: 1.2em;
                }
                .url-status.error {
                    color: var(--color-error);
                }
                .url-status.success {
                    color: var(--color-success);
                }
                .url-examples {
                    display: flex;
                    flex-wrap: wrap;
                    gap: var(--spacing-xs);
                    margin-top: var(--spacing-xs);
                }
                .url-example-btn {
                    padding: 2px 8px;
                    background: var(--color-bg-muted);
                    border: 1px solid var(--color-border);
                    border-radius: 12px;
                    font-size: 0.75em;
                    cursor: pointer;
                    transition: all 0.2s ease;
                }
                .url-example-btn:hover {
                    background: var(--color-border);
                }
            </style>
            <div class="card">
                <div class="panel-header">
                    <span class="panel-title">
                        <span class="panel-title-icon">🌐</span>
                        Fetch from URL
                    </span>
                </div>
                <div class="url-input-container">
                    <div class="url-input-row">
                        <input 
                            type="url" 
                            id="url-input" 
                            class="url-input-field" 
                            placeholder="https://example.com"
                            autocomplete="url"
                            value = "https://example.com"
                        >
                        <button id="url-fetch-btn" class="url-fetch-btn">
                            🔗 Fetch
                        </button>
                    </div>
                    <div id="url-status" class="url-status"></div>
                    <div class="url-examples">
                        <span style="font-size: 0.8em; color: var(--color-text-muted);">Try:</span>
                        <button class="url-example-btn" data-url="https://example.com">example.com</button>
                        <button class="url-example-btn" data-url="https://www.akeia.ai">akeia.ai</button>
                        <button class="url-example-btn" data-url="https://docs.diniscruz.ai/about.html">docs.diniscruz.ai</button>
                    </div>
                </div>
            </div>
        `;

        this.urlInput = this.querySelector('#url-input');
        this.fetchButton = this.querySelector('#url-fetch-btn');
        this.statusText = this.querySelector('#url-status');
    }

    setupEventListeners() {
        // Fetch button click
        this.fetchButton.addEventListener('click', () => this.fetchUrl());

        // Enter key in input
        this.urlInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.fetchUrl();
            }
        });

        // Example buttons
        this.querySelectorAll('.url-example-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.urlInput.value = btn.dataset.url;
                this.fetchUrl();
            });
        });
    }

    async fetchUrl() {
        const url = this.urlInput.value.trim();

        if (!url) {
            this.setStatus('Please enter a URL', 'error');
            return;
        }

        if (!this.isValidUrl(url)) {
            this.setStatus('Please enter a valid URL (including https://)', 'error');
            return;
        }

        if (this.isFetching) return;

        this.isFetching = true;
        this.setFetchingState(true);
        this.setStatus('Fetching HTML...', '');

        try {
            const response = await apiClient.post('/html/from/url', { url: url, timeout: 30 });

            this.setStatus(`✓ Fetched ${this.formatBytes(response.html.length)} from ${response.url}`, 'success');

            // Emit event with fetched HTML
            this.dispatchEvent(new CustomEvent('url-html-fetched', {
                detail: {
                    html: response.html,
                    url: response.url,
                    contentType: response.content_type
                },
                bubbles: true
            }));

        } catch (error) {
            console.error('URL fetch error:', error);
            this.setStatus(`✗ ${error.message || 'Failed to fetch URL'}`, 'error');
        } finally {
            this.isFetching = false;
            this.setFetchingState(false);
        }
    }

    setFetchingState(fetching) {
        this.fetchButton.disabled = fetching;
        this.fetchButton.innerHTML = fetching
            ? '<span class="spinner" style="width:14px;height:14px;"></span> Fetching...'
            : '🔗 Fetch';
    }

    setStatus(message, type = '') {
        this.statusText.textContent = message;
        this.statusText.className = 'url-status ' + type;
    }

    isValidUrl(string) {
        try {
            const url = new URL(string);
            return url.protocol === 'http:' || url.protocol === 'https:';
        } catch {
            return false;
        }
    }

    formatBytes(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }

    getUrl() {
        return this.urlInput.value.trim();
    }

    setUrl(url) {
        this.urlInput.value = url;
    }
}

customElements.define('url-input', UrlInput);
