/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Stats Toolbar Component
   v0.2.1 - Refactored to use Shadow DOM + BaseComponent
   
   Combines render button, stats display, and timing info in a compact toolbar.
   
   Original v0.2.0: ~200 lines (inline CSS + HTML)
   This version: ~120 lines (slim, template-based)
   ═══════════════════════════════════════════════════════════════════════════════ */

class StatsToolbar extends BaseComponent {
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
        this.isRendering = false;
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Lifecycle Hooks
    // ═══════════════════════════════════════════════════════════════════════════
    
    bindElements() {
        this.renderButton = this.$('#render-btn');
        this.errorBanner = this.$('#error-banner');
    }

    setupEventListeners() {
        this.addTrackedListener(this.renderButton, 'click', this.onRenderClick);
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Event Handlers
    // ═══════════════════════════════════════════════════════════════════════════
    
    onRenderClick() {
        this.emit('render-requested');
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Public API
    // ═══════════════════════════════════════════════════════════════════════════
    
    setStats(stats) {
        this.stats = { ...this.stats, ...stats };
        this.$('#stat-nodes').textContent = this.formatNumber(this.stats.total_nodes);
        this.$('#stat-edges').textContent = this.formatNumber(this.stats.total_edges);
        this.$('#stat-elements').textContent = this.formatNumber(this.stats.element_nodes);
        this.$('#stat-attrs').textContent = this.formatNumber(this.stats.attr_nodes);
        this.$('#stat-text').textContent = this.formatNumber(this.stats.text_nodes);
    }

    setTiming(timing) {
        this.timing = { ...this.timing, ...timing };
        this.$('#timing-api').textContent = this.timing.api_ms ? `${this.timing.api_ms}ms` : '-';
        this.$('#timing-server').textContent = this.timing.server_ms ? `${this.timing.server_ms}ms` : '-';
        this.$('#timing-render').textContent = this.timing.render_ms ? `${this.timing.render_ms}ms` : '-';
        this.$('#timing-dot-size').textContent = this.timing.dot_size ? this.formatBytes(this.timing.dot_size) : '-';
    }

    setRenderingState(rendering) {
        this.isRendering = rendering;
        this.renderButton.disabled = rendering;
        this.renderButton.innerHTML = rendering
            ? '<span class="spinner"></span> Rendering...'
            : '🔄 Render Graph';
    }

    showError(title, detail, hint = '') {
        this.$('#error-title').textContent = title;
        this.$('#error-detail').textContent = detail;
        
        const hintEl = this.$('#error-hint');
        if (hint.startsWith('Error:')) {
            hintEl.innerHTML = `<code>${this.escapeHtml(hint)}</code>`;
        } else {
            hintEl.textContent = hint;
        }
        
        this.errorBanner.classList.add('show');
    }

    hideError() {
        this.errorBanner.classList.remove('show');
    }

    clearStats() {
        this.stats = {
            total_nodes: 0, total_edges: 0, element_nodes: 0,
            value_nodes: 0, tag_nodes: 0, text_nodes: 0, attr_nodes: 0
        };
        this.timing = { api_ms: 0, server_ms: 0, render_ms: 0, dot_size: 0 };

        this.$('#stat-nodes').textContent = '-';
        this.$('#stat-edges').textContent = '-';
        this.$('#stat-elements').textContent = '-';
        this.$('#stat-attrs').textContent = '-';
        this.$('#stat-text').textContent = '-';
        this.$('#timing-api').textContent = '-';
        this.$('#timing-server').textContent = '-';
        this.$('#timing-render').textContent = '-';
        this.$('#timing-dot-size').textContent = '-';

        this.hideError();
    }
}

customElements.define('stats-toolbar', StatsToolbar);
