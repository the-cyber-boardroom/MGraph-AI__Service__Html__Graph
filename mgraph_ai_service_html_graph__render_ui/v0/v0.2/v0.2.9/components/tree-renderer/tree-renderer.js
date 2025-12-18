/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Tree Renderer Component
   v0.2.9 - Collapsible hierarchical tree view for JSON tree structure
   
   Displays the tree format output from /graph/from/html/to/tree endpoint
   Features:
   - Collapsible nodes with expand/collapse all
   - Color-coded by predicate type (tag, attr, text, child)
   - Click to select, hover to highlight
   - Copy node path to clipboard
   ═══════════════════════════════════════════════════════════════════════════════ */

class TreeRenderer extends HTMLElement {
    constructor() {
        super();
        this.targetCanvas = null;
        this.treeData = null;
        this.expandedNodes = new Set();
        this.selectedNode = null;
        
        // Color scheme matching other renderers
        this.colors = {
            tag:   { bg: '#4A90D9', text: '#FFFFFF', label: 'Tag' },
            attr:  { bg: '#B39DDB', text: '#333333', label: 'Attribute' },
            text:  { bg: '#FFFACD', text: '#333333', label: 'Text' },
            child: { bg: '#E8E8E8', text: '#333333', label: 'Element' },
            root:  { bg: '#6366f1', text: '#FFFFFF', label: 'Root' }
        };
    }

    connectedCallback() {
        // Styles loaded from ../v0.2.9/css/tree-renderers.css
    }

    /**
     * Set the target canvas element
     */
    setTargetCanvas(canvasElement) {
        this.targetCanvas = canvasElement;
    }

    /**
     * Render tree data from API response
     * @param {object} graphData - { tree, rootId, stats, duration }
     */
    async render(graphData) {
        if (!this.targetCanvas) {
            throw new Error('No target canvas set for Tree renderer');
        }

        this.treeData = graphData.tree;
        this.rootId = graphData.rootId;

        if (!this.treeData || Object.keys(this.treeData).length === 0) {
            this.showEmpty();
            return { nodes: 0 };
        }

        // Clear and render
        this.targetCanvas.innerHTML = '';

        // Create container
        const container = document.createElement('div');
        container.className = 'tree-renderer-container';

        // Toolbar
        const toolbar = this.createToolbar();
        container.appendChild(toolbar);

        // Tree content
        const treeContent = document.createElement('div');
        treeContent.className = 'tree-content';
        treeContent.appendChild(this.renderNode(this.treeData, 0, 'root'));
        container.appendChild(treeContent);

        this.targetCanvas.appendChild(container);

        // // Expand root by default
        // this.expandedNodes.add(this.treeData.id);
        // this.updateExpandedState();
        // Expand all by default
        this.expandAll();

        // Count nodes
        const nodeCount = this.countNodes(this.treeData);
        return { nodes: nodeCount };
    }

    /**
     * Create toolbar with expand/collapse controls
     */
    createToolbar() {
        const toolbar = document.createElement('div');
        toolbar.className = 'tree-toolbar';
        toolbar.innerHTML = `
            <div class="tree-toolbar-left">
                <button class="tree-btn" data-action="expand-all" title="Expand All">
                    <span>▼</span> Expand All
                </button>
                <button class="tree-btn" data-action="collapse-all" title="Collapse All">
                    <span>▶</span> Collapse All
                </button>
            </div>
            <div class="tree-toolbar-right">
                <div class="tree-legend">
                    <span class="legend-item tag">Tag</span>
                    <span class="legend-item attr">Attr</span>
                    <span class="legend-item text">Text</span>
                    <span class="legend-item child">Element</span>
                </div>
            </div>
        `;

        // Bind toolbar events
        toolbar.querySelector('[data-action="expand-all"]').addEventListener('click', () => this.expandAll());
        toolbar.querySelector('[data-action="collapse-all"]').addEventListener('click', () => this.collapseAll());

        return toolbar;
    }

    /**
     * Render a single node and its children
     */
    renderNode(node, depth, predicateType) {
        const nodeEl = document.createElement('div');
        nodeEl.className = 'tree-node';
        nodeEl.dataset.nodeId = node.id;
        nodeEl.dataset.depth = depth;

        const hasChildren = node.children && Object.keys(node.children).length > 0;
        const isExpanded = this.expandedNodes.has(node.id);

        // Node header (clickable row)
        const header = document.createElement('div');
        header.className = `tree-node-header ${predicateType}`;
        header.style.paddingLeft = `${depth * 20 + 8}px`;

        // Expand/collapse toggle
        const toggle = document.createElement('span');
        toggle.className = `tree-toggle ${hasChildren ? '' : 'hidden'}`;
        toggle.innerHTML = isExpanded ? '▼' : '▶';
        toggle.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleNode(node.id);
        });

        // Node badge (predicate type)
        const badge = document.createElement('span');
        badge.className = `tree-badge ${predicateType}`;
        badge.textContent = this.colors[predicateType]?.label || predicateType;
        badge.style.backgroundColor = this.colors[predicateType]?.bg || '#888';
        badge.style.color = this.colors[predicateType]?.text || '#fff';

        // Node value
        const value = document.createElement('span');
        value.className = 'tree-value';
        value.textContent = this.truncateValue(node.value, 60);
        value.title = node.value;

        // Node ID (subtle)
        const nodeId = document.createElement('span');
        nodeId.className = 'tree-node-id';
        nodeId.textContent = node.id;

        header.appendChild(toggle);
        header.appendChild(badge);
        header.appendChild(value);
        header.appendChild(nodeId);

        // Click to select
        header.addEventListener('click', () => this.selectNode(node.id, header));

        nodeEl.appendChild(header);

        // Children container
        if (hasChildren) {
            const childrenContainer = document.createElement('div');
            childrenContainer.className = `tree-children ${isExpanded ? '' : 'collapsed'}`;
            childrenContainer.dataset.parentId = node.id;

            // Render children grouped by predicate
            const predicateOrder = ['tag', 'attr', 'text', 'child'];

            for (const predicate of predicateOrder) {
                const children = node.children[predicate];
                if (children && children.length > 0) {
                    for (const child of children) {
                        childrenContainer.appendChild(this.renderNode(child, depth + 1, predicate));
                    }
                }
            }

            // Handle any other predicates not in our standard order
            for (const predicate of Object.keys(node.children)) {
                if (!predicateOrder.includes(predicate)) {
                    const children = node.children[predicate];
                    for (const child of children) {
                        childrenContainer.appendChild(this.renderNode(child, depth + 1, predicate));
                    }
                }
            }

            nodeEl.appendChild(childrenContainer);
        }

        return nodeEl;
    }

    /**
     * Toggle node expansion
     */
    toggleNode(nodeId) {
        if (this.expandedNodes.has(nodeId)) {
            this.expandedNodes.delete(nodeId);
        } else {
            this.expandedNodes.add(nodeId);
        }
        this.updateExpandedState();
    }

    /**
     * Update DOM to reflect expanded/collapsed state
     */
    updateExpandedState() {
        const container = this.targetCanvas.querySelector('.tree-content');
        if (!container) return;

        container.querySelectorAll('.tree-node').forEach(nodeEl => {
            const nodeId = nodeEl.dataset.nodeId;
            const isExpanded = this.expandedNodes.has(nodeId);

            const toggle = nodeEl.querySelector(':scope > .tree-node-header .tree-toggle');
            if (toggle && !toggle.classList.contains('hidden')) {
                toggle.innerHTML = isExpanded ? '▼' : '▶';
            }

            const children = nodeEl.querySelector(':scope > .tree-children');
            if (children) {
                children.classList.toggle('collapsed', !isExpanded);
            }
        });
    }

    /**
     * Expand all nodes
     */
    expandAll() {
        this.collectAllNodeIds(this.treeData, this.expandedNodes);
        this.updateExpandedState();
    }

    /**
     * Collapse all nodes
     */
    collapseAll() {
        this.expandedNodes.clear();
        this.expandedNodes.add(this.treeData.id); // Keep root expanded
        this.updateExpandedState();
    }

    /**
     * Collect all node IDs recursively
     */
    collectAllNodeIds(node, set) {
        set.add(node.id);
        if (node.children) {
            for (const children of Object.values(node.children)) {
                for (const child of children) {
                    this.collectAllNodeIds(child, set);
                }
            }
        }
    }

    /**
     * Select a node
     */
    selectNode(nodeId, headerEl) {
        // Deselect previous
        const prev = this.targetCanvas.querySelector('.tree-node-header.selected');
        if (prev) prev.classList.remove('selected');

        // Select new
        headerEl.classList.add('selected');
        this.selectedNode = nodeId;

        // Dispatch event for external listeners
        this.dispatchEvent(new CustomEvent('node-selected', {
            detail: { nodeId },
            bubbles: true
        }));
    }

    /**
     * Count total nodes in tree
     */
    countNodes(node) {
        let count = 1;
        if (node.children) {
            for (const children of Object.values(node.children)) {
                for (const child of children) {
                    count += this.countNodes(child);
                }
            }
        }
        return count;
    }

    /**
     * Truncate long values
     */
    truncateValue(value, maxLength) {
        if (!value) return '';
        if (value.length <= maxLength) return value;
        return value.substring(0, maxLength - 3) + '...';
    }

    /**
     * Show empty state
     */
    showEmpty() {
        this.targetCanvas.innerHTML = `
            <div class="tree-empty">
                <div class="tree-empty-icon">🌳</div>
                <p>No tree data available</p>
            </div>
        `;
    }

    /**
     * Fit to view (scroll to top)
     */
    fitToView() {
        if (this.targetCanvas) {
            this.targetCanvas.scrollTop = 0;
        }
    }

    /**
     * Export as JSON
     */
    exportJson() {
        return JSON.stringify(this.treeData, null, 2);
    }
}

customElements.define('tree-renderer', TreeRenderer);

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TreeRenderer;
}