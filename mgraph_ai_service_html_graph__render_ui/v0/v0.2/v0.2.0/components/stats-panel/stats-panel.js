/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - Stats Panel Component
   v0.2.0 - Consolidated from v0.1.x
   ═══════════════════════════════════════════════════════════════════════════════ */

class StatsPanel extends HTMLElement {
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
    }

    connectedCallback() {
        this.render();
    }

    render() {
        this.innerHTML = `
            <div class="card">
                <div class="panel-header">
                    <span class="panel-title">
                        <span class="panel-title-icon">📊</span>
                        Graph Statistics
                    </span>
                </div>
                <div class="stats-grid">
                    <div class="stat-item">
                        <span class="stat-label">Total Nodes</span>
                        <span class="stat-value" id="stat-total-nodes">${this.stats.total_nodes}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Total Edges</span>
                        <span class="stat-value" id="stat-total-edges">${this.stats.total_edges}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Elements</span>
                        <span class="stat-value" id="stat-element-nodes">${this.stats.element_nodes}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Values</span>
                        <span class="stat-value" id="stat-value-nodes">${this.stats.value_nodes}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Tags</span>
                        <span class="stat-value" id="stat-tag-nodes">${this.stats.tag_nodes}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Text</span>
                        <span class="stat-value" id="stat-text-nodes">${this.stats.text_nodes}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Attributes</span>
                        <span class="stat-value" id="stat-attr-nodes">${this.stats.attr_nodes}</span>
                    </div>
                </div>
            </div>
        `;
    }

    setStats(stats) {
        this.stats = { ...this.stats, ...stats };
        this.updateUI();
    }

    updateUI() {
        this.querySelector('#stat-total-nodes').textContent = this.stats.total_nodes;
        this.querySelector('#stat-total-edges').textContent = this.stats.total_edges;
        this.querySelector('#stat-element-nodes').textContent = this.stats.element_nodes;
        this.querySelector('#stat-value-nodes').textContent = this.stats.value_nodes;
        this.querySelector('#stat-tag-nodes').textContent = this.stats.tag_nodes;
        this.querySelector('#stat-text-nodes').textContent = this.stats.text_nodes;
        this.querySelector('#stat-attr-nodes').textContent = this.stats.attr_nodes;
    }

    clearStats() {
        this.stats = {
            total_nodes: 0,
            total_edges: 0,
            element_nodes: 0,
            value_nodes: 0,
            tag_nodes: 0,
            text_nodes: 0,
            attr_nodes: 0
        };
        this.updateUI();
    }
}

customElements.define('stats-panel', StatsPanel);
