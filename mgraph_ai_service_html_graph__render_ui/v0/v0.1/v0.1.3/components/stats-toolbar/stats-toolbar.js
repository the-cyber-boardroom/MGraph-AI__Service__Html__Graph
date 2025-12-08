/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - Stats Toolbar Component
   v0.1.4 - Improved Layout & Error Handling

   Combines render button, stats display, and timing info in a compact toolbar
   ═══════════════════════════════════════════════════════════════════════════════ */

class StatsToolbar extends HTMLElement {
    constructor() {
        super();
        this.stats = {
            total_nodes: 0,
            total_edges: 0,
            element_nodes: 0,
            value_nodes: 0,
            tag_nodes: 0,
            text_nodes: 0,
            attr_nodes: 0
        };
        this.timing = {
            api_ms: 0,
            server_ms: 0,
            render_ms: 0,
            dot_size: 0
        };
        this.renderButton = null;
        this.isRendering = false;
    }

    connectedCallback() {
        this.render();
        this.setupEventListeners();
    }

    render() {
        this.innerHTML = `
            <style>
                .stats-toolbar {
                    display: flex;
                    flex-direction: column;
                    gap: var(--spacing-sm);
                    padding: var(--spacing-md);
                    background: white;
                    border-radius: var(--radius-md);
                    box-shadow: var(--shadow-sm);
                    margin-bottom: var(--spacing-md);
                }
                .stats-toolbar-row {
                    display: flex;
                    align-items: center;
                    gap: var(--spacing-md);
                    flex-wrap: wrap;
                }
                .render-btn {
                    padding: var(--spacing-sm) var(--spacing-lg);
                    background: var(--gradient-bg);
                    color: white;
                    border: none;
                    border-radius: var(--radius-sm);
                    font-size: 1em;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    display: flex;
                    align-items: center;
                    gap: var(--spacing-xs);
                }
                .render-btn:hover:not(:disabled) {
                    opacity: 0.9;
                    transform: translateY(-1px);
                    box-shadow: var(--shadow-md);
                }
                .render-btn:disabled {
                    opacity: 0.6;
                    cursor: not-allowed;
                }
                .stats-group {
                    display: flex;
                    align-items: center;
                    gap: var(--spacing-md);
                    flex: 1;
                    flex-wrap: wrap;
                }
                .stat-badge {
                    display: flex;
                    align-items: center;
                    gap: 4px;
                    padding: 4px 10px;
                    background: var(--color-bg-muted);
                    border-radius: 15px;
                    font-size: 0.85em;
                }
                .stat-badge-label {
                    color: var(--color-text-muted);
                }
                .stat-badge-value {
                    font-weight: 600;
                    color: var(--color-text-primary);
                }
                .stat-badge.highlight {
                    background: rgba(102, 126, 234, 0.1);
                }
                .stat-badge.highlight .stat-badge-value {
                    color: var(--color-primary);
                }
                .timing-group {
                    display: flex;
                    align-items: center;
                    gap: var(--spacing-sm);
                    font-size: 0.8em;
                    color: var(--color-text-muted);
                }
                .timing-item {
                    display: flex;
                    align-items: center;
                    gap: 3px;
                }
                .timing-value {
                    font-weight: 500;
                    color: var(--color-text-secondary);
                }
                .error-banner {
                    display: none;
                    padding: var(--spacing-sm) var(--spacing-md);
                    background: rgba(239, 68, 68, 0.1);
                    border: 1px solid rgba(239, 68, 68, 0.3);
                    border-radius: var(--radius-sm);
                    color: var(--color-error);
                    font-size: 0.9em;
                }
                .error-banner.show {
                    display: flex;
                    align-items: flex-start;
                    gap: var(--spacing-sm);
                }
                .error-banner-icon {
                    font-size: 1.2em;
                }
                .error-banner-content {
                    flex: 1;
                }
                .error-banner-title {
                    font-weight: 600;
                    margin-bottom: 2px;
                }
                .error-banner-detail {
                    font-size: 0.9em;
                    opacity: 0.8;
                }
                .error-banner-hint {
                    margin-top: var(--spacing-xs);
                    font-size: 0.85em;
                    color: var(--color-text-secondary);
                }
            </style>
            <div class="stats-toolbar">
                <div class="stats-toolbar-row">
                    <button id="render-btn" class="render-btn">
                        🔄 Render Graph
                    </button>
                    <div class="stats-group">
                        <div class="stat-badge highlight">
                            <span class="stat-badge-label">Nodes:</span>
                            <span class="stat-badge-value" id="stat-nodes">0</span>
                        </div>
                        <div class="stat-badge highlight">
                            <span class="stat-badge-label">Edges:</span>
                            <span class="stat-badge-value" id="stat-edges">0</span>
                        </div>
                        <div class="stat-badge">
                            <span class="stat-badge-label">Elements:</span>
                            <span class="stat-badge-value" id="stat-elements">0</span>
                        </div>
                        <div class="stat-badge">
                            <span class="stat-badge-label">Attrs:</span>
                            <span class="stat-badge-value" id="stat-attrs">0</span>
                        </div>
                        <div class="stat-badge">
                            <span class="stat-badge-label">Text:</span>
                            <span class="stat-badge-value" id="stat-text">0</span>
                        </div>
                    </div>
                </div>
                <div class="stats-toolbar-row">
                    <div class="timing-group">
                        <div class="timing-item">
                            <span>📡 API:</span>
                            <span class="timing-value" id="timing-api">-</span>
                        </div>
                        <div class="timing-item">
                            <span>⚙️ Server:</span>
                            <span class="timing-value" id="timing-server">-</span>
                        </div>
                        <div class="timing-item">
                            <span>🎨 Render:</span>
                            <span class="timing-value" id="timing-render">-</span>
                        </div>
                        <div class="timing-item">
                            <span>📦 DOT:</span>
                            <span class="timing-value" id="timing-dot-size">-</span>
                        </div>
                    </div>
                </div>
                <div id="error-banner" class="error-banner">
                    <span class="error-banner-icon">⚠️</span>
                    <div class="error-banner-content">
                        <div class="error-banner-title" id="error-title">Error</div>
                        <div class="error-banner-detail" id="error-detail"></div>
                        <div class="error-banner-hint" id="error-hint"></div>
                    </div>
                </div>
            </div>
        `;

        this.renderButton = this.querySelector('#render-btn');
    }

    setupEventListeners() {
        this.renderButton.addEventListener('click', () => {
            this.dispatchEvent(new CustomEvent('render-requested', { bubbles: true }));
        });
    }

    setStats(stats) {
        this.stats = { ...this.stats, ...stats };
        this.querySelector('#stat-nodes').textContent = this.formatNumber(this.stats.total_nodes);
        this.querySelector('#stat-edges').textContent = this.formatNumber(this.stats.total_edges);
        this.querySelector('#stat-elements').textContent = this.formatNumber(this.stats.element_nodes);
        this.querySelector('#stat-attrs').textContent = this.formatNumber(this.stats.attr_nodes);
        this.querySelector('#stat-text').textContent = this.formatNumber(this.stats.text_nodes);
    }

    setTiming(timing) {
        this.timing = { ...this.timing, ...timing };
        this.querySelector('#timing-api').textContent = this.timing.api_ms ? `${this.timing.api_ms}ms` : '-';
        this.querySelector('#timing-server').textContent = this.timing.server_ms ? `${this.timing.server_ms}ms` : '-';
        this.querySelector('#timing-render').textContent = this.timing.render_ms ? `${this.timing.render_ms}ms` : '-';
        this.querySelector('#timing-dot-size').textContent = this.timing.dot_size ? this.formatBytes(this.timing.dot_size) : '-';
    }

    setRenderingState(rendering) {
        this.isRendering = rendering;
        this.renderButton.disabled = rendering;
        this.renderButton.innerHTML = rendering
            ? '<span class="spinner" style="width:16px;height:16px;"></span> Rendering...'
            : '🔄 Render Graph';
    }

    showError(title, detail, hint = '') {
        const banner = this.querySelector('#error-banner');
        this.querySelector('#error-title').textContent = title;
        this.querySelector('#error-detail').textContent = detail;
        // Hint may contain error details - show as code if it looks like an error
        const hintEl = this.querySelector('#error-hint');
        if (hint.startsWith('Error:')) {
            hintEl.innerHTML = `<code style="font-size: 0.85em; background: rgba(0,0,0,0.05); padding: 2px 6px; border-radius: 3px; word-break: break-all;">${this.escapeHtml(hint)}</code>`;
        } else {
            hintEl.textContent = hint;
        }
        banner.classList.add('show');
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    hideError() {
        this.querySelector('#error-banner').classList.remove('show');
    }

    clearStats() {
        // Reset to zero/null values
        this.stats = {
            total_nodes: 0, total_edges: 0, element_nodes: 0,
            value_nodes: 0, tag_nodes: 0, text_nodes: 0, attr_nodes: 0
        };
        this.timing = { api_ms: 0, server_ms: 0, render_ms: 0, dot_size: 0 };

        // Display dashes to indicate "loading"
        this.querySelector('#stat-nodes').textContent = '-';
        this.querySelector('#stat-edges').textContent = '-';
        this.querySelector('#stat-elements').textContent = '-';
        this.querySelector('#stat-attrs').textContent = '-';
        this.querySelector('#stat-text').textContent = '-';
        this.querySelector('#timing-api').textContent = '-';
        this.querySelector('#timing-server').textContent = '-';
        this.querySelector('#timing-render').textContent = '-';
        this.querySelector('#timing-dot-size').textContent = '-';

        this.hideError();
    }

    formatNumber(num) {
        if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
        if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
        return num.toString();
    }

    formatBytes(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }
}

customElements.define('stats-toolbar', StatsToolbar);