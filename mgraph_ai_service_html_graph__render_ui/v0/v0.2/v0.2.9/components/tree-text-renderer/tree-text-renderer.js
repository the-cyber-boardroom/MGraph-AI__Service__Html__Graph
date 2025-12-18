/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Tree Text Renderer Component
   v0.2.9 - Formatted text display with syntax highlighting
   
   Displays the tree_text format output from /graph/from/html/to/tree_text endpoint
   Features:
   - Syntax highlighting for predicate labels
   - Line numbers
   - Copy to clipboard
   - Search/filter
   ═══════════════════════════════════════════════════════════════════════════════ */

class TreeTextRenderer extends HTMLElement {
    constructor() {
        super();
        this.targetCanvas = null;
        this.treeText = '';
        this.showLineNumbers = true;
        
        // Syntax highlighting colors
        this.syntaxColors = {
            predicate: '#6366f1',    // tag:, attr:, text:, child:
            nodeId: '#888888',       // c0000001
            indent: '#e0e0e0',       // visual indent guides
            value: '#333333'         // actual values
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
     * Render tree text from API response
     * @param {object} graphData - { tree_text, tree_text_size, rootId, stats, duration }
     */
    async render(graphData) {
        if (!this.targetCanvas) {
            throw new Error('No target canvas set for Tree Text renderer');
        }

        this.treeText = graphData.tree_text || '';
        this.rootId = graphData.rootId;

        if (!this.treeText) {
            this.showEmpty();
            return { size: 0, lines: 0 };
        }

        // Clear and render
        this.targetCanvas.innerHTML = '';

        // Create container
        const container = document.createElement('div');
        container.className = 'tree-text-renderer-container';

        // Toolbar
        const toolbar = this.createToolbar();
        container.appendChild(toolbar);

        // Content area
        const content = document.createElement('div');
        content.className = 'tree-text-content';

        // Render highlighted text
        content.innerHTML = this.highlightSyntax(this.treeText);
        container.appendChild(content);

        this.targetCanvas.appendChild(container);

        const lines = this.treeText.split('\n').length;
        return { size: this.treeText.length, lines };
    }

    /**
     * Create toolbar with controls
     */
    createToolbar() {
        const toolbar = document.createElement('div');
        toolbar.className = 'tree-text-toolbar';
        toolbar.innerHTML = `
            <div class="tree-text-toolbar-left">
                <button class="tree-text-btn" data-action="copy" title="Copy to Clipboard">
                    📋 Copy
                </button>
                <button class="tree-text-btn" data-action="toggle-lines" title="Toggle Line Numbers">
                    # Lines
                </button>
                <button class="tree-text-btn" data-action="wrap" title="Toggle Word Wrap">
                    ↩ Wrap
                </button>
            </div>
            <div class="tree-text-toolbar-right">
                <div class="tree-text-search">
                    <input type="text" placeholder="Search..." class="tree-text-search-input" />
                    <span class="tree-text-search-count"></span>
                </div>
            </div>
        `;

        // Bind events
        toolbar.querySelector('[data-action="copy"]').addEventListener('click', () => this.copyToClipboard());
        toolbar.querySelector('[data-action="toggle-lines"]').addEventListener('click', (e) => this.toggleLineNumbers(e.target));
        toolbar.querySelector('[data-action="wrap"]').addEventListener('click', (e) => this.toggleWrap(e.target));
        toolbar.querySelector('.tree-text-search-input').addEventListener('input', (e) => this.search(e.target.value));

        return toolbar;
    }

    /**
     * Apply syntax highlighting to tree text
     */
    highlightSyntax(text) {
        const lines = text.split('\n');
        let html = '<div class="tree-text-lines">';

        lines.forEach((line, index) => {
            const lineNum = index + 1;
            const highlightedLine = this.highlightLine(line);

            html += `
                <div class="tree-text-line" data-line="${lineNum}">
                    <span class="line-number">${lineNum}</span>
                    <span class="line-content">${highlightedLine}</span>
                </div>
            `;
        });

        html += '</div>';
        return html;
    }

    /**
     * Highlight a single line
     */
    highlightLine(line) {
        if (!line) return '&nbsp;';

        // Escape HTML first
        let escaped = this.escapeHtml(line);

        // Highlight predicate labels (tag:, attr:, text:, child:)
        escaped = escaped.replace(
            /^(\s*)(tag|attr|text|child)(:)$/,
            '$1<span class="syntax-predicate">$2$3</span>'
        );

        // Highlight node IDs (c0000001 pattern at start of line or after indent)
        escaped = escaped.replace(
            /^(\s*)(c[0-9a-f]{7})$/i,
            '$1<span class="syntax-node-id">$2</span>'
        );

        // Preserve indentation with visible guides
        const indentMatch = escaped.match(/^(\s+)/);
        if (indentMatch) {
            const indent = indentMatch[1];
            const indentGuides = this.createIndentGuides(indent.length);
            escaped = indentGuides + escaped.substring(indent.length);
        }

        return escaped;
    }

    /**
     * Create visual indent guides
     */
    createIndentGuides(spaces) {
        const levels = Math.floor(spaces / 4);
        let guides = '';

        for (let i = 0; i < levels; i++) {
            guides += '<span class="indent-guide">│   </span>';
        }

        // Remaining spaces
        const remainder = spaces % 4;
        if (remainder > 0) {
            guides += '&nbsp;'.repeat(remainder);
        }

        return guides;
    }

    /**
     * Copy text to clipboard
     */
    async copyToClipboard() {
        try {
            await navigator.clipboard.writeText(this.treeText);
            this.showToast('Copied to clipboard!');
        } catch (err) {
            // Fallback for older browsers
            const textarea = document.createElement('textarea');
            textarea.value = this.treeText;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            this.showToast('Copied to clipboard!');
        }
    }

    /**
     * Toggle line numbers visibility
     */
    toggleLineNumbers(button) {
        this.showLineNumbers = !this.showLineNumbers;
        const container = this.targetCanvas.querySelector('.tree-text-renderer-container');
        container.classList.toggle('hide-line-numbers', !this.showLineNumbers);
        button.classList.toggle('active', this.showLineNumbers);
    }

    /**
     * Toggle word wrap
     */
    toggleWrap(button) {
        const container = this.targetCanvas.querySelector('.tree-text-renderer-container');
        container.classList.toggle('word-wrap');
        button.classList.toggle('active');
    }

    /**
     * Search within text
     */
    search(query) {
        const content = this.targetCanvas.querySelector('.tree-text-content');
        const countEl = this.targetCanvas.querySelector('.tree-text-search-count');

        // Remove previous highlights
        content.querySelectorAll('.search-highlight').forEach(el => {
            el.outerHTML = el.textContent;
        });

        if (!query || query.length < 2) {
            countEl.textContent = '';
            return;
        }

        // Find and highlight matches
        let matchCount = 0;
        const regex = new RegExp(`(${this.escapeRegex(query)})`, 'gi');

        content.querySelectorAll('.line-content').forEach(line => {
            const html = line.innerHTML;
            const newHtml = html.replace(regex, (match) => {
                matchCount++;
                return `<span class="search-highlight">${match}</span>`;
            });
            line.innerHTML = newHtml;
        });

        countEl.textContent = matchCount > 0 ? `${matchCount} found` : 'No matches';
    }

    /**
     * Show toast notification
     */
    showToast(message) {
        const existing = document.querySelector('.tree-text-toast');
        if (existing) existing.remove();

        const toast = document.createElement('div');
        toast.className = 'tree-text-toast';
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => toast.classList.add('visible'), 10);
        setTimeout(() => {
            toast.classList.remove('visible');
            setTimeout(() => toast.remove(), 300);
        }, 2000);
    }

    /**
     * Show empty state
     */
    showEmpty() {
        this.targetCanvas.innerHTML = `
            <div class="tree-text-empty">
                <div class="tree-text-empty-icon">📄</div>
                <p>No tree text data available</p>
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
     * Export raw text
     */
    exportText() {
        return this.treeText;
    }

    /**
     * Escape HTML entities
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Escape regex special characters
     */
    escapeRegex(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
}

customElements.define('tree-text-renderer', TreeTextRenderer);

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TreeTextRenderer;
}