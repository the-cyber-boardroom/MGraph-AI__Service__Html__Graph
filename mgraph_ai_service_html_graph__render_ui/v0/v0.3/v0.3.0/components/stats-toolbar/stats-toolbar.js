/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - Stats Toolbar Component
   v0.3.0 - From v0.2.0 (unchanged)
   ═══════════════════════════════════════════════════════════════════════════════ */

class StatsToolbar extends HTMLElement {
    constructor() {
        super();
        this.isRendering = false;
    }

    connectedCallback() {
        this.render();
        this.setupEventListeners();
    }

    render() {
        this.innerHTML = `
            <div class="stats-toolbar">
                <div class="stats-toolbar-left">
                    <button class="render-btn" id="render-btn">
                        <span class="render-btn-text">▶ Render Graph</span>
                        <span class="render-btn-loading" style="display: none;">
                            <span class="spinner-small"></span>
                            Rendering...
                        </span>
                    </button>
                </div>
                <div class="stats-toolbar-center">
                    <div class="stats-display" id="stats-display">
                        <span class="stat-item" id="stat-nodes" title="Total nodes in graph">
                            <span class="stat-label">Nodes:</span>
                            <span class="stat-value">-</span>
                        </span>
                        <span class="stat-item" id="stat-edges" title="Total edges in graph">
                            <span class="stat-label">Edges:</span>
                            <span class="stat-value">-</span>
                        </span>
                        <span class="stat-item" id="stat-time" title="Total processing time">
                            <span class="stat-label">Time:</span>
                            <span class="stat-value">-</span>
                        </span>
                    </div>
                </div>
                <div class="stats-toolbar-right">
                    <span class="keyboard-hint" title="Keyboard shortcut">Ctrl+Enter</span>
                </div>
            </div>
            <div class="error-banner" id="error-banner" style="display: none;">
                <div class="error-content">
                    <span class="error-icon">⚠️</span>
                    <div class="error-text">
                        <strong id="error-title">Error</strong>
                        <p id="error-message"></p>
                        <p id="error-hint" class="error-hint"></p>
                    </div>
                    <button class="error-close" id="error-close">×</button>
                </div>
            </div>
        `;
    }

    setupEventListeners() {
        this.querySelector('#render-btn').addEventListener('click', () => {
            if (!this.isRendering) {
                this.dispatchEvent(new CustomEvent('render-requested', { bubbles: true }));
            }
        });

        this.querySelector('#error-close').addEventListener('click', () => {
            this.hideError();
        });
    }

    setRenderingState(isRendering) {
        this.isRendering = isRendering;
        const btn = this.querySelector('#render-btn');
        const textSpan = btn.querySelector('.render-btn-text');
        const loadingSpan = btn.querySelector('.render-btn-loading');

        btn.disabled = isRendering;

        if (isRendering) {
            textSpan.style.display = 'none';
            loadingSpan.style.display = 'inline-flex';
            btn.classList.add('rendering');
        } else {
            textSpan.style.display = 'inline';
            loadingSpan.style.display = 'none';
            btn.classList.remove('rendering');
        }
    }

    setStats(stats) {
        const nodesEl = this.querySelector('#stat-nodes .stat-value');
        const edgesEl = this.querySelector('#stat-edges .stat-value');

        nodesEl.textContent = stats.total_nodes ?? '-';
        edgesEl.textContent = stats.total_edges ?? '-';
    }

    setTiming(timing) {
        const timeEl = this.querySelector('#stat-time .stat-value');
        const totalMs = (timing.api_ms || 0) + (timing.render_ms || 0);
        timeEl.textContent = `${totalMs}ms`;
        timeEl.title = `API: ${timing.api_ms}ms, Server: ${timing.server_ms}ms, Render: ${timing.render_ms}ms`;
    }

    clearStats() {
        this.querySelector('#stat-nodes .stat-value').textContent = '-';
        this.querySelector('#stat-edges .stat-value').textContent = '-';
        this.querySelector('#stat-time .stat-value').textContent = '-';
    }

    showError(title, message, hint = '') {
        const banner = this.querySelector('#error-banner');
        const titleEl = this.querySelector('#error-title');
        const messageEl = this.querySelector('#error-message');
        const hintEl = this.querySelector('#error-hint');

        titleEl.textContent = title;
        messageEl.textContent = message;
        hintEl.textContent = hint;
        hintEl.style.display = hint ? 'block' : 'none';

        banner.style.display = 'block';
    }

    hideError() {
        this.querySelector('#error-banner').style.display = 'none';
    }
}

customElements.define('stats-toolbar', StatsToolbar);
