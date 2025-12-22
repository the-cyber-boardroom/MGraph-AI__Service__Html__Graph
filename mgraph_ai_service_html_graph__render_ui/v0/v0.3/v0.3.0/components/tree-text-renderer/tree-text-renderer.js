/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - Tree Text Renderer Component
   v0.3.0 - From v0.2.9 (unchanged)
   
   Renders tree_text format - a syntax-highlighted ASCII tree representation
   ═══════════════════════════════════════════════════════════════════════════════ */

class TreeTextRenderer extends HTMLElement {
    constructor() {
        super();
        this.targetCanvas = null;
    }

    connectedCallback() {
        this.style.display = 'none';
    }

    setTargetCanvas(canvasElement) {
        this.targetCanvas = canvasElement;
    }

    async render(response) {
        if (!this.targetCanvas) {
            throw new Error('No target canvas set for Tree Text renderer');
        }

        const { tree_text } = response;

        this.targetCanvas.innerHTML = '';
        this.targetCanvas.style.background = '#1e1e1e';
        this.targetCanvas.style.overflow = 'auto';
        this.targetCanvas.style.padding = '20px';

        const container = document.createElement('div');
        container.className = 'tree-text-container';

        const pre = document.createElement('pre');
        pre.className = 'tree-text-content';
        pre.style.cssText = `
            font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', monospace;
            font-size: 13px;
            line-height: 1.5;
            color: #d4d4d4;
            margin: 0;
            white-space: pre;
            tab-size: 4;
        `;

        // Apply syntax highlighting
        pre.innerHTML = this.highlightSyntax(tree_text);

        container.appendChild(pre);
        this.targetCanvas.appendChild(container);

        return { size: tree_text.length };
    }

    highlightSyntax(text) {
        if (!text) return '';

        // Escape HTML first
        let escaped = this.escapeHtml(text);

        // Highlight tree structure characters (├, │, └, ─)
        escaped = escaped.replace(/([├│└─┬┴┼]+)/g, '<span style="color: #555;">$1</span>');

        // Highlight HTML tags (anything in angle brackets)
        escaped = escaped.replace(/(&lt;[^&]*&gt;)/g, '<span style="color: #569cd6;">$1</span>');

        // Highlight quoted strings
        escaped = escaped.replace(/(&quot;[^&]*&quot;)/g, '<span style="color: #ce9178;">$1</span>');

        // Highlight attributes (word followed by =)
        escaped = escaped.replace(/(\w+)(=)/g, '<span style="color: #9cdcfe;">$1</span><span style="color: #d4d4d4;">$2</span>');

        // Highlight node IDs (hex patterns)
        escaped = escaped.replace(/\[([a-f0-9-]{8,})\]/gi, '[<span style="color: #808080;">$1</span>]');

        return escaped;
    }

    escapeHtml(text) {
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

customElements.define('tree-text-renderer', TreeTextRenderer);
