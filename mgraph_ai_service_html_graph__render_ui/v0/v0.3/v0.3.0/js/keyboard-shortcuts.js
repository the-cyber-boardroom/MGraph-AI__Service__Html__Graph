/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - Keyboard Shortcuts System
   v0.3.0 - From v0.2.6 (unchanged)
   
   Event-driven keyboard shortcut handler with customizable bindings
   ═══════════════════════════════════════════════════════════════════════════════ */

class KeyboardShortcuts {
    constructor(options = {}) {
        this.configUrl = options.configUrl || './js/keyboard-shortcuts.json';
        this.shortcuts = [];
        this.enabled = true;
        this.helpVisible = false;
        this.helpPanel = null;

        this.init();
    }

    async init() {
        await this.loadConfig();
        this.bindKeyboardEvents();
        this.createHelpPanel();
    }

    async loadConfig() {
        try {
            const response = await fetch(this.configUrl);
            if (response.ok) {
                const config = await response.json();
                this.shortcuts = config.shortcuts || [];
            } else {
                this.loadDefaultConfig();
            }
        } catch (error) {
            console.warn('Failed to load keyboard shortcuts config, using defaults:', error);
            this.loadDefaultConfig();
        }
    }

    loadDefaultConfig() {
        this.shortcuts = [
            { key: 'r', description: 'Reload/Render graph', event: 'shortcut:reload' },
            { key: 'm', description: 'Toggle maximize mode', event: 'shortcut:maximize-toggle' },
            { key: 't', description: 'Next transformation', event: 'shortcut:transformation-next' },
            { key: 'T', shift: true, description: 'Previous transformation', event: 'shortcut:transformation-prev' },
            { key: 'e', description: 'Next engine/renderer', event: 'shortcut:engine-next' },
            { key: 'E', shift: true, description: 'Previous engine/renderer', event: 'shortcut:engine-prev' },
            { key: '+', description: 'Zoom in', event: 'shortcut:zoom-in' },
            { key: '=', description: 'Zoom in', event: 'shortcut:zoom-in' },
            { key: '-', description: 'Zoom out', event: 'shortcut:zoom-out' },
            { key: '0', description: 'Reset zoom', event: 'shortcut:zoom-reset' },
            { key: 'f', description: 'Fit to view', event: 'shortcut:zoom-fit' },
            { key: 'h', description: 'Toggle help', event: 'shortcut:help-toggle' },
            { key: '?', shift: true, description: 'Toggle help', event: 'shortcut:help-toggle' },
            { key: 'Escape', description: 'Close/Exit', event: 'shortcut:escape' },
            { key: '1', description: 'Transformation 1', event: 'shortcut:transformation-select', data: { index: 0 } },
            { key: '2', description: 'Transformation 2', event: 'shortcut:transformation-select', data: { index: 1 } },
            { key: '3', description: 'Transformation 3', event: 'shortcut:transformation-select', data: { index: 2 } },
            { key: '4', description: 'Transformation 4', event: 'shortcut:transformation-select', data: { index: 3 } },
            { key: '5', description: 'Transformation 5', event: 'shortcut:transformation-select', data: { index: 4 } }
        ];
    }

    bindKeyboardEvents() {
        document.addEventListener('keydown', (e) => {
            if (!this.enabled) return;

            // Ignore if user is typing in an input
            if (this.isTyping(e)) return;

            const shortcut = this.findMatchingShortcut(e);
            if (shortcut) {
                e.preventDefault();
                this.dispatchShortcutEvent(shortcut);
            }
        });
    }

    isTyping(e) {
        const target = e.target;
        const tagName = target.tagName.toLowerCase();
        
        if (tagName === 'input' || tagName === 'textarea' || tagName === 'select') {
            return true;
        }
        
        if (target.isContentEditable) {
            return true;
        }
        
        return false;
    }

    findMatchingShortcut(e) {
        for (const shortcut of this.shortcuts) {
            if (this.matchesShortcut(e, shortcut)) {
                return shortcut;
            }
        }
        return null;
    }

    matchesShortcut(e, shortcut) {
        // Check modifiers
        if (shortcut.ctrl && !e.ctrlKey) return false;
        if (shortcut.alt && !e.altKey) return false;
        if (shortcut.meta && !e.metaKey) return false;
        if (shortcut.shift && !e.shiftKey) return false;

        // If shift is not specified but is pressed (for non-shift shortcuts)
        if (!shortcut.shift && e.shiftKey && shortcut.key.length === 1 && shortcut.key === shortcut.key.toLowerCase()) {
            return false;
        }

        // Check key
        const pressedKey = e.key.toLowerCase();
        const shortcutKey = shortcut.key.toLowerCase();

        return pressedKey === shortcutKey;
    }

    dispatchShortcutEvent(shortcut) {
        const eventName = shortcut.event;
        const detail = shortcut.data || {};

        document.dispatchEvent(new CustomEvent(eventName, { 
            detail: detail,
            bubbles: true 
        }));
    }

    createHelpPanel() {
        this.helpPanel = document.createElement('div');
        this.helpPanel.className = 'keyboard-shortcuts-help';
        this.helpPanel.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            border-radius: 12px;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
            padding: 24px;
            z-index: 10002;
            display: none;
            max-width: 500px;
            max-height: 80vh;
            overflow: auto;
        `;

        this.helpPanel.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <h3 style="margin: 0; font-size: 18px;">Keyboard Shortcuts</h3>
                <button class="help-close" style="background: none; border: none; font-size: 24px; cursor: pointer; color: #666;">×</button>
            </div>
            <div class="shortcuts-list">
                ${this.renderShortcutsList()}
            </div>
        `;

        const overlay = document.createElement('div');
        overlay.className = 'keyboard-shortcuts-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            z-index: 10001;
            display: none;
        `;

        document.body.appendChild(overlay);
        document.body.appendChild(this.helpPanel);

        this.helpPanel.querySelector('.help-close').addEventListener('click', () => this.hideHelp());
        overlay.addEventListener('click', () => this.hideHelp());

        this.overlay = overlay;
    }

    renderShortcutsList() {
        const grouped = this.groupShortcuts();
        let html = '';

        for (const [group, shortcuts] of Object.entries(grouped)) {
            html += `<div style="margin-bottom: 16px;">
                <div style="font-weight: 600; color: #666; font-size: 12px; text-transform: uppercase; margin-bottom: 8px;">${group}</div>
                <div style="display: grid; gap: 8px;">
            `;

            for (const shortcut of shortcuts) {
                const keyDisplay = this.formatKeyDisplay(shortcut);
                html += `
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #333;">${shortcut.description}</span>
                        <kbd style="background: #f0f0f0; padding: 4px 8px; border-radius: 4px; font-family: monospace; font-size: 12px;">${keyDisplay}</kbd>
                    </div>
                `;
            }

            html += `</div></div>`;
        }

        return html;
    }

    groupShortcuts() {
        return {
            'Navigation': this.shortcuts.filter(s => ['reload', 'maximize', 'escape'].some(k => s.event.includes(k))),
            'Zoom': this.shortcuts.filter(s => s.event.includes('zoom')),
            'Transformation': this.shortcuts.filter(s => s.event.includes('transformation')),
            'Engine': this.shortcuts.filter(s => s.event.includes('engine')),
            'Help': this.shortcuts.filter(s => s.event.includes('help'))
        };
    }

    formatKeyDisplay(shortcut) {
        let parts = [];
        if (shortcut.ctrl) parts.push('Ctrl');
        if (shortcut.alt) parts.push('Alt');
        if (shortcut.meta) parts.push('⌘');
        if (shortcut.shift) parts.push('Shift');
        parts.push(shortcut.key.toUpperCase());
        return parts.join(' + ');
    }

    showHelp() {
        this.helpPanel.style.display = 'block';
        this.overlay.style.display = 'block';
        this.helpVisible = true;
    }

    hideHelp() {
        this.helpPanel.style.display = 'none';
        this.overlay.style.display = 'none';
        this.helpVisible = false;
    }

    toggleHelp() {
        if (this.helpVisible) {
            this.hideHelp();
        } else {
            this.showHelp();
        }
    }

    enable() {
        this.enabled = true;
    }

    disable() {
        this.enabled = false;
    }
}

// Make available globally
window.KeyboardShortcuts = KeyboardShortcuts;
