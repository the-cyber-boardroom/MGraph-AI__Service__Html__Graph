/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - HTML Input Component
   v0.1.1 - Core UI Framework
   ═══════════════════════════════════════════════════════════════════════════════ */

class HtmlInput extends HTMLElement {
    constructor() {
        super();
        this.samples = [
            { name: 'simple', label: 'Simple' },
            { name: 'nested', label: 'Nested Structure' },
            { name: 'attributes', label: 'With Attributes' },
            { name: 'mixed-content', label: 'Mixed Content' },
            { name: 'bootstrap', label: 'Bootstrap Layout' }
        ];
        this.textarea = null;
        this.sampleSelect = null;
    }

    connectedCallback() {
        this.render();
        this.setupEventListeners();
        this.loadSample('simple'); // Load default sample
    }

    render() {
        const sampleOptions = this.samples
            .map(s => `<option value="${s.name}">${s.label}</option>`)
            .join('');

        this.innerHTML = `
            <div class="card">
                <div class="panel-header">
                    <span class="panel-title">
                        <span class="panel-title-icon">📝</span>
                        HTML Input
                    </span>
                    <div class="sample-selector">
                        <label for="sample-select">Sample:</label>
                        <select id="sample-select">
                            <option value="">-- Custom --</option>
                            ${sampleOptions}
                        </select>
                    </div>
                </div>
                <textarea 
                    id="html-input" 
                    class="html-input-area" 
                    placeholder="Enter HTML here or select a sample..."
                    spellcheck="false"
                ></textarea>
            </div>
        `;

        this.textarea = this.querySelector('#html-input');
        this.sampleSelect = this.querySelector('#sample-select');
    }

    setupEventListeners() {
        // Sample selection change
        this.sampleSelect.addEventListener('change', (e) => {
            const sampleName = e.target.value;
            if (sampleName) {
                this.loadSample(sampleName);
            }
        });

        // HTML input change (debounced)
        let debounceTimer;
        this.textarea.addEventListener('input', () => {
            this.sampleSelect.value = ''; // Clear sample selection
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                this.emitChange();
            }, 300);
        });
    }

    async loadSample(sampleName) {
        try {
            const response = await fetch(`/console/v0/v0.1/v0.1.0/samples/${sampleName}.html`);
            if (!response.ok) throw new Error(`Failed to load sample: ${response.statusText}`);
            const html = await response.text();
            this.textarea.value = html;
            this.sampleSelect.value = sampleName;
            this.emitChange();
        } catch (error) {
            console.error('Failed to load sample:', error);
            this.textarea.value = `<!-- Error loading sample: ${error.message} -->`;
        }
    }

    emitChange() {
        this.dispatchEvent(new CustomEvent('html-changed', {
            detail: { html: this.textarea.value },
            bubbles: true
        }));
    }

    getHtml() {
        return this.textarea.value;
    }

    setHtml(html) {
        this.textarea.value = html;
        this.sampleSelect.value = '';
    }
}

customElements.define('html-input', HtmlInput);
