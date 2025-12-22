/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - Config Panel Component
   v0.3.0 - From v0.2.0 (unchanged)
   ═══════════════════════════════════════════════════════════════════════════════ */

class ConfigPanel extends HTMLElement {
    constructor() {
        super();
        this.config = {
            preset: 'full_detail',
            show_tag_nodes: true,
            show_attr_nodes: true,
            show_text_nodes: true,
            color_scheme: 'default'
        };
    }

    connectedCallback() {
        this.render();
        this.setupEventListeners();
    }

    render() {
        this.innerHTML = `
            <div class="card">
                <div class="panel-header">
                    <span class="panel-title">
                        <span class="panel-title-icon">⚙️</span>
                        Configuration
                    </span>
                </div>
                
                <div class="config-section">
                    <div class="config-section-title">Preset</div>
                    <div class="config-row">
                        <select id="config-preset" class="form-control">
                            <option value="full_detail">Full Detail</option>
                            <option value="structure_only">Structure Only</option>
                            <option value="minimal">Minimal</option>
                        </select>
                    </div>
                </div>

                <div class="config-section">
                    <div class="config-section-title">Node Visibility</div>
                    <div class="form-check">
                        <input type="checkbox" id="config-show-tag" checked>
                        <label for="config-show-tag">Show Tag Nodes</label>
                    </div>
                    <div class="form-check">
                        <input type="checkbox" id="config-show-attr" checked>
                        <label for="config-show-attr">Show Attribute Nodes</label>
                    </div>
                    <div class="form-check">
                        <input type="checkbox" id="config-show-text" checked>
                        <label for="config-show-text">Show Text Nodes</label>
                    </div>
                </div>

                <div class="config-section">
                    <div class="config-section-title">Color Scheme</div>
                    <div class="config-row">
                        <select id="config-color-scheme" class="form-control">
                            <option value="default">Default</option>
                            <option value="monochrome">Monochrome</option>
                            <option value="high_contrast">High Contrast</option>
                        </select>
                    </div>
                </div>
            </div>
        `;
    }

    setupEventListeners() {
        this.querySelector('#config-preset').addEventListener('change', (e) => {
            this.config.preset = e.target.value;
            this.applyPreset(e.target.value);
            this.emitChange();
        });

        this.querySelector('#config-show-tag').addEventListener('change', (e) => {
            this.config.show_tag_nodes = e.target.checked;
            this.emitChange();
        });

        this.querySelector('#config-show-attr').addEventListener('change', (e) => {
            this.config.show_attr_nodes = e.target.checked;
            this.emitChange();
        });

        this.querySelector('#config-show-text').addEventListener('change', (e) => {
            this.config.show_text_nodes = e.target.checked;
            this.emitChange();
        });

        this.querySelector('#config-color-scheme').addEventListener('change', (e) => {
            this.config.color_scheme = e.target.value;
            this.emitChange();
        });
    }

    applyPreset(preset) {
        const showTagCheckbox = this.querySelector('#config-show-tag');
        const showAttrCheckbox = this.querySelector('#config-show-attr');
        const showTextCheckbox = this.querySelector('#config-show-text');

        switch (preset) {
            case 'full_detail':
                showTagCheckbox.checked = true;
                showAttrCheckbox.checked = true;
                showTextCheckbox.checked = true;
                break;
            case 'structure_only':
                showTagCheckbox.checked = true;
                showAttrCheckbox.checked = false;
                showTextCheckbox.checked = false;
                break;
            case 'minimal':
                showTagCheckbox.checked = false;
                showAttrCheckbox.checked = false;
                showTextCheckbox.checked = false;
                break;
        }

        this.config.show_tag_nodes = showTagCheckbox.checked;
        this.config.show_attr_nodes = showAttrCheckbox.checked;
        this.config.show_text_nodes = showTextCheckbox.checked;
    }

    emitChange() {
        this.dispatchEvent(new CustomEvent('config-changed', {
            detail: { config: this.getConfig() },
            bubbles: true
        }));
    }

    getConfig() {
        return { ...this.config };
    }

    setConfig(config) {
        this.config = { ...this.config, ...config };
        this.updateUI();
    }

    updateUI() {
        this.querySelector('#config-preset').value = this.config.preset;
        this.querySelector('#config-show-tag').checked = this.config.show_tag_nodes;
        this.querySelector('#config-show-attr').checked = this.config.show_attr_nodes;
        this.querySelector('#config-show-text').checked = this.config.show_text_nodes;
        this.querySelector('#config-color-scheme').value = this.config.color_scheme;
    }
}

customElements.define('config-panel', ConfigPanel);
