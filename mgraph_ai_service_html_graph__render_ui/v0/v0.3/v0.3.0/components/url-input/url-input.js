/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - URL Input Component
   v0.3.0 - From v0.2.0 (unchanged)
   ═══════════════════════════════════════════════════════════════════════════════ */

class UrlInput extends HTMLElement {
    constructor() {
        super();
        this.urlInput = null;
        this.fetchBtn = null;
        this.isFetching = false;
    }

    connectedCallback() {
        this.render();
        this.setupEventListeners();
    }

    render() {
        this.innerHTML = `
            <div class="card url-input-card">
                <div class="panel-header">
                    <span class="panel-title">
                        <span class="panel-title-icon">🌐</span>
                        Fetch from URL
                    </span>
                </div>
                <div class="url-input-row">
                    <input 
                        type="url" 
                        id="url-input" 
                        class="url-input-field" 
                        placeholder="https://example.com"
                    >
                    <button id="fetch-btn" class="btn btn-primary fetch-btn">
                        <span class="fetch-btn-text">Fetch</span>
                        <span class="fetch-btn-loading" style="display: none;">
                            <span class="spinner-small"></span>
                        </span>
                    </button>
                </div>
                <div id="url-error" class="url-error" style="display: none;"></div>
            </div>
        `;

        this.urlInput = this.querySelector('#url-input');
        this.fetchBtn = this.querySelector('#fetch-btn');
        this.errorDiv = this.querySelector('#url-error');
    }

    setupEventListeners() {
        this.fetchBtn.addEventListener('click', () => this.fetchUrl());

        this.urlInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.fetchUrl();
            }
        });

        this.urlInput.addEventListener('input', () => {
            this.hideError();
        });
    }

    async fetchUrl() {
        const url = this.urlInput.value.trim();

        if (!url) {
            this.showError('Please enter a URL');
            return;
        }

        if (!this.isValidUrl(url)) {
            this.showError('Please enter a valid URL (including https://)');
            return;
        }

        if (this.isFetching) return;

        this.setFetchingState(true);
        this.hideError();

        try {
            const response = await fetch(`/proxy/fetch?url=${encodeURIComponent(url)}`);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            this.dispatchEvent(new CustomEvent('url-html-fetched', {
                detail: {
                    html: data.html,
                    url: data.url,
                    contentType: data.content_type
                },
                bubbles: true
            }));

        } catch (error) {
            console.error('Fetch error:', error);
            this.showError(error.message || 'Failed to fetch URL');
        } finally {
            this.setFetchingState(false);
        }
    }

    isValidUrl(string) {
        try {
            const url = new URL(string);
            return url.protocol === 'http:' || url.protocol === 'https:';
        } catch {
            return false;
        }
    }

    setFetchingState(isFetching) {
        this.isFetching = isFetching;
        this.fetchBtn.disabled = isFetching;
        this.urlInput.disabled = isFetching;

        const textSpan = this.fetchBtn.querySelector('.fetch-btn-text');
        const loadingSpan = this.fetchBtn.querySelector('.fetch-btn-loading');

        if (isFetching) {
            textSpan.style.display = 'none';
            loadingSpan.style.display = 'inline-flex';
        } else {
            textSpan.style.display = 'inline';
            loadingSpan.style.display = 'none';
        }
    }

    showError(message) {
        this.errorDiv.textContent = message;
        this.errorDiv.style.display = 'block';
    }

    hideError() {
        this.errorDiv.style.display = 'none';
    }

    setUrl(url) {
        this.urlInput.value = url;
    }

    getUrl() {
        return this.urlInput.value.trim();
    }
}

customElements.define('url-input', UrlInput);
