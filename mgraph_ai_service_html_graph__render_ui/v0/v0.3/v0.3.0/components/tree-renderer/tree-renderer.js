/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - Tree Renderer Component
   v0.3.0 - From v0.2.9 (unchanged)
   
   Renders hierarchical tree data as an interactive, collapsible JSON tree view
   ═══════════════════════════════════════════════════════════════════════════════ */

class TreeRenderer extends HTMLElement {
    constructor() {
        super();
        this.targetCanvas = null;
        this.expandedNodes = new Set();
    }

    connectedCallback() {
        this.style.display = 'none';
    }

    setTargetCanvas(canvasElement) {
        this.targetCanvas = canvasElement;
    }

    async render(response) {
        if (!this.targetCanvas) {
            throw new Error('No target canvas set for Tree renderer');
        }

        const { tree, rootId } = response;

        this.targetCanvas.innerHTML = '';
        this.targetCanvas.style.background = '#1e1e1e';
        this.targetCanvas.style.overflow = 'auto';
        this.targetCanvas.style.padding = '20px';

        const container = document.createElement('div');
        container.className = 'tree-view-container';
        container.style.cssText = `
            font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', monospace;
            font-size: 13px;
            line-height: 1.6;
            color: #d4d4d4;
        `;

        const treeHtml = this.renderNode(tree, rootId, 0);
        container.innerHTML = treeHtml;

        this.targetCanvas.appendChild(container);
        this.setupEventListeners(container);

        return { nodes: this.countNodes(tree) };
    }

    renderNode(tree, nodeId, depth) {
        const node = tree[nodeId];
        if (!node) return '';

        const hasChildren = node.children && node.children.length > 0;
        const isExpanded = this.expandedNodes.has(nodeId) || depth < 2;
        const indent = depth * 20;

        const typeColors = {
            'tag': '#569cd6',
            'element': '#4ec9b0',
            'attribute': '#9cdcfe',
            'text': '#ce9178',
            'default': '#d4d4d4'
        };

        const nodeType = node.type || 'default';
        const color = typeColors[nodeType] || typeColors.default;

        let html = `
            <div class="tree-node" data-node-id="${nodeId}" style="margin-left: ${indent}px;">
                <span class="tree-toggle" style="cursor: ${hasChildren ? 'pointer' : 'default'}; width: 16px; display: inline-block; color: #808080;">
                    ${hasChildren ? (isExpanded ? '▼' : '▶') : ' '}
                </span>
                <span class="tree-label" style="color: ${color};">${this.escapeHtml(node.label || nodeId)}</span>
                ${node.value ? `<span class="tree-value" style="color: #ce9178; margin-left: 8px;">${this.escapeHtml(this.truncate(node.value, 50))}</span>` : ''}
            </div>
        `;

        if (hasChildren && isExpanded) {
            html += `<div class="tree-children" data-parent-id="${nodeId}">`;
            for (const childId of node.children) {
                html += this.renderNode(tree, childId, depth + 1);
            }
            html += '</div>';
        }

        return html;
    }

    setupEventListeners(container) {
        container.addEventListener('click', (e) => {
            const toggle = e.target.closest('.tree-toggle');
            if (!toggle) return;

            const nodeEl = toggle.closest('.tree-node');
            const nodeId = nodeEl.dataset.nodeId;

            if (this.expandedNodes.has(nodeId)) {
                this.expandedNodes.delete(nodeId);
            } else {
                this.expandedNodes.add(nodeId);
            }

            // Re-render - for simplicity, we toggle visibility
            const childrenEl = container.querySelector(`.tree-children[data-parent-id="${nodeId}"]`);
            if (childrenEl) {
                childrenEl.style.display = this.expandedNodes.has(nodeId) ? 'block' : 'none';
                toggle.textContent = this.expandedNodes.has(nodeId) ? '▼' : '▶';
            }
        });
    }

    countNodes(tree) {
        return Object.keys(tree).length;
    }

    truncate(str, maxLength) {
        if (!str) return '';
        if (str.length <= maxLength) return str;
        return str.substring(0, maxLength) + '...';
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    fitToView() {
        if (this.targetCanvas) {
            this.targetCanvas.scrollTop = 0;
            this.targetCanvas.scrollLeft = 0;
        }
    }
}

customElements.define('tree-renderer', TreeRenderer);
