// ═══════════════════════════════════════════════════════════════════════════════
// MGraph HTML Graph - Keyboard Shortcuts Component
// v0.2.6 - Event-driven keyboard shortcuts system
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * KeyboardShortcuts - Event-driven keyboard shortcuts manager
 *
 * Features:
 * - Loads shortcuts from JSON configuration
 * - Dispatches custom events on key press
 * - Provides hideable UI panel showing available shortcuts
 * - Supports modifier keys (shift, ctrl, alt, meta)
 *
 * Events dispatched:
 * - shortcut:reload
 * - shortcut:maximize-toggle
 * - shortcut:transformation-next/prev
 * - shortcut:engine-next/prev
 * - shortcut:transformation-select (with index in detail)
 * - shortcut:help-toggle
 * - shortcut:escape
 * - shortcut:zoom-in/out/reset/fit
 */
function KeyboardShortcuts(options) {
    options = options || {};

    this.configUrl = options.configUrl || '/static/js/keyboard-shortcuts.json';
    this.shortcuts = [];
    this.categories = {};
    this.enabled = true;
    this.helpVisible = false;
    this.helpPanel = null;

    // Elements where shortcuts should be disabled (text inputs, etc.)
    this.disableInElements = ['INPUT', 'TEXTAREA'];

    this.init();
}

// ═══════════════════════════════════════════════════════════════════════════════
// Initialization
// ═══════════════════════════════════════════════════════════════════════════════

KeyboardShortcuts.prototype.init = function() {
    this.loadConfig();
    this.bindKeyListener();
    this.createHelpPanel();
};

KeyboardShortcuts.prototype.loadConfig = function() {
    var self = this;

    fetch(this.configUrl)
        .then(function(response) {
            if (!response.ok) throw new Error('Failed to load shortcuts config');
            return response.json();
        })
        .then(function(config) {
            self.shortcuts = config.shortcuts || [];
            self.categories = config.categories || {};
            self.updateHelpPanel();
            console.log('Keyboard shortcuts loaded:', self.shortcuts.length, 'shortcuts');

            // Dispatch event indicating shortcuts are ready
            document.dispatchEvent(new CustomEvent('shortcuts:loaded', {
                detail: { shortcuts: self.shortcuts, categories: self.categories }
            }));
        })
        .catch(function(error) {
            console.warn('Could not load keyboard shortcuts config:', error);
            // Use default shortcuts if config fails to load
            self.useDefaultShortcuts();
        });
};

KeyboardShortcuts.prototype.useDefaultShortcuts = function() {
    // Fallback defaults if JSON fails to load
    this.shortcuts = [
        { key: 'r', event: 'shortcut:reload', label: 'Reload', category: 'actions' },
        { key: 'm', event: 'shortcut:maximize-toggle', label: 'Maximize', category: 'view' },
        { key: 't', event: 'shortcut:transformation-next', label: 'Transform →', category: 'transformations' },
        { key: 'e', event: 'shortcut:engine-next', label: 'Engine →', category: 'engines' },
        { key: 'h', event: 'shortcut:help-toggle', label: 'Help', category: 'help' },
        { key: 'Escape', event: 'shortcut:escape', label: 'Close', category: 'navigation' }
    ];
    this.categories = {
        actions: { label: 'Actions', order: 1 },
        view: { label: 'View', order: 2 },
        engines: { label: 'Engines', order: 3 },
        transformations: { label: 'Transformations', order: 4 },
        navigation: { label: 'Navigation', order: 5 },
        help: { label: 'Help', order: 6 }
    };
    this.updateHelpPanel();
};

// ═══════════════════════════════════════════════════════════════════════════════
// Key Listener
// ═══════════════════════════════════════════════════════════════════════════════

KeyboardShortcuts.prototype.bindKeyListener = function() {
    var self = this;

    document.addEventListener('keydown', function(e) {
        self.handleKeydown(e);
    });
};

KeyboardShortcuts.prototype.handleKeydown = function(e) {
    // Skip if shortcuts disabled
    if (!this.enabled) return;

    // Skip if focused on text input elements
    if (this.disableInElements.includes(e.target.tagName)) return;

    // Skip if in contenteditable
    if (e.target.isContentEditable) return;

    // Find matching shortcut
    var shortcut = this.findMatchingShortcut(e);

    if (shortcut) {
        e.preventDefault();
        e.stopPropagation();
        this.dispatchShortcutEvent(shortcut);
    }
};

KeyboardShortcuts.prototype.findMatchingShortcut = function(e) {
    var key = e.key;

    for (var i = 0; i < this.shortcuts.length; i++) {
        var shortcut = this.shortcuts[i];

        // Check key match (case-sensitive for letters with shift)
        var keyMatch = (shortcut.key === key) ||
                       (shortcut.key.toLowerCase() === key.toLowerCase() && !shortcut.shift);

        if (!keyMatch) continue;

        // Check modifier keys
        var shiftMatch = !!shortcut.shift === e.shiftKey;
        var ctrlMatch = !!shortcut.ctrl === (e.ctrlKey || e.metaKey);
        var altMatch = !!shortcut.alt === e.altKey;

        // For uppercase letters, shift must be pressed
        if (shortcut.shift && shortcut.key === shortcut.key.toUpperCase() &&
            shortcut.key !== shortcut.key.toLowerCase()) {
            shiftMatch = e.shiftKey;
            keyMatch = key === shortcut.key || key.toUpperCase() === shortcut.key;
        }

        if (keyMatch && shiftMatch && ctrlMatch && altMatch) {
            return shortcut;
        }
    }

    return null;
};

KeyboardShortcuts.prototype.dispatchShortcutEvent = function(shortcut) {
    var eventName = shortcut.event;
    var detail = Object.assign({}, shortcut.data || {}, {
        shortcut: shortcut
    });

    console.log('Shortcut triggered:', eventName, detail);

    document.dispatchEvent(new CustomEvent(eventName, { detail: detail }));
};

// ═══════════════════════════════════════════════════════════════════════════════
// Help Panel UI
// ═══════════════════════════════════════════════════════════════════════════════

KeyboardShortcuts.prototype.createHelpPanel = function() {
    // Create panel element
    this.helpPanel = document.createElement('div');
    this.helpPanel.id = 'keyboard-shortcuts-help';
    this.helpPanel.className = 'keyboard-shortcuts-help hidden';
    this.helpPanel.innerHTML = this.generateHelpHTML();

    // Add styles
    this.addStyles();

    // Add to document
    document.body.appendChild(this.helpPanel);

    // Close button
    var self = this;
    this.helpPanel.querySelector('.shortcuts-close')?.addEventListener('click', function() {
        self.hideHelp();
    });
};

KeyboardShortcuts.prototype.generateHelpHTML = function() {
    var html = '<div class="shortcuts-dialog">';
    html += '<div class="shortcuts-header">';
    html += '<h2>⌨️ Keyboard Shortcuts</h2>';
    html += '<button class="shortcuts-close" aria-label="Close">×</button>';
    html += '</div>';
    html += '<div class="shortcuts-content">';

    // Group by category
    var grouped = this.groupByCategory();
    var categoryOrder = this.getSortedCategories();

    for (var i = 0; i < categoryOrder.length; i++) {
        var catKey = categoryOrder[i];
        var shortcuts = grouped[catKey];
        if (!shortcuts || shortcuts.length === 0) continue;

        var catLabel = this.categories[catKey]?.label || catKey;

        html += '<div class="shortcuts-category">';
        html += '<h3>' + catLabel + '</h3>';
        html += '<div class="shortcuts-list">';

        for (var j = 0; j < shortcuts.length; j++) {
            var s = shortcuts[j];
            html += '<div class="shortcut-item">';
            html += '<kbd class="shortcut-key">' + this.formatKey(s) + '</kbd>';
            html += '<span class="shortcut-label">' + s.label + '</span>';
            html += '</div>';
        }

        html += '</div></div>';
    }

    html += '</div></div>';
    return html;
};

KeyboardShortcuts.prototype.formatKey = function(shortcut) {
    var parts = [];
    if (shortcut.ctrl) parts.push('Ctrl');
    if (shortcut.alt) parts.push('Alt');
    if (shortcut.shift) parts.push('Shift');

    var key = shortcut.key;
    // Pretty-print special keys
    if (key === 'Escape') key = 'Esc';
    if (key === ' ') key = 'Space';

    parts.push(key);
    return parts.join(' + ');
};

KeyboardShortcuts.prototype.groupByCategory = function() {
    var grouped = {};
    for (var i = 0; i < this.shortcuts.length; i++) {
        var s = this.shortcuts[i];
        var cat = s.category || 'other';
        if (!grouped[cat]) grouped[cat] = [];
        grouped[cat].push(s);
    }
    return grouped;
};

KeyboardShortcuts.prototype.getSortedCategories = function() {
    var self = this;
    var keys = Object.keys(this.categories);
    keys.sort(function(a, b) {
        var orderA = self.categories[a]?.order || 999;
        var orderB = self.categories[b]?.order || 999;
        return orderA - orderB;
    });
    return keys;
};

KeyboardShortcuts.prototype.updateHelpPanel = function() {
    if (this.helpPanel) {
        var content = this.helpPanel.querySelector('.shortcuts-dialog');
        if (content) {
            this.helpPanel.innerHTML = this.generateHelpHTML();
            // Re-bind close button
            var self = this;
            this.helpPanel.querySelector('.shortcuts-close')?.addEventListener('click', function() {
                self.hideHelp();
            });
        }
    }
};

KeyboardShortcuts.prototype.showHelp = function() {
    if (this.helpPanel) {
        this.helpPanel.classList.remove('hidden');
        this.helpVisible = true;
    }
};

KeyboardShortcuts.prototype.hideHelp = function() {
    if (this.helpPanel) {
        this.helpPanel.classList.add('hidden');
        this.helpVisible = false;
    }
};

KeyboardShortcuts.prototype.toggleHelp = function() {
    if (this.helpVisible) {
        this.hideHelp();
    } else {
        this.showHelp();
    }
};

// ═══════════════════════════════════════════════════════════════════════════════
// Styles
// ═══════════════════════════════════════════════════════════════════════════════

KeyboardShortcuts.prototype.addStyles = function() {
    if (document.getElementById('keyboard-shortcuts-styles')) return;

    var style = document.createElement('style');
    style.id = 'keyboard-shortcuts-styles';
    style.textContent = `
        .keyboard-shortcuts-help {
            position: fixed;
            top: 70px;
            right: 20px;
            z-index: 10000;
            pointer-events: auto;
        }
        
        .keyboard-shortcuts-help.hidden {
            display: none;
        }
        
        .shortcuts-dialog {
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            width: 480px;
            max-height: calc(100vh - 100px);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            border: 1px solid #e0e0e0;
        }
        
        .shortcuts-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 16px;
            border-bottom: 1px solid #e0e0e0;
            background: #f8f9fa;
        }
        
        .shortcuts-header h2 {
            margin: 0;
            font-size: 16px;
            font-weight: 600;
            color: #333;
        }
        
        .shortcuts-close {
            background: none;
            border: none;
            font-size: 20px;
            cursor: pointer;
            color: #666;
            padding: 0;
            width: 28px;
            height: 28px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 6px;
        }
        
        .shortcuts-close:hover {
            background: #e0e0e0;
            color: #333;
        }
        
        .shortcuts-content {
            padding: 16px;
            overflow-y: auto;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
        }
        
        .shortcuts-category h3 {
            margin: 0 0 8px 0;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            color: #888;
            letter-spacing: 0.5px;
        }
        
        .shortcuts-list {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }
        
        .shortcut-item {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .shortcut-key {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 24px;
            height: 24px;
            padding: 0 6px;
            background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
            border: 1px solid #ced4da;
            border-radius: 4px;
            font-family: 'SF Mono', 'Monaco', 'Menlo', monospace;
            font-size: 11px;
            font-weight: 500;
            color: #333;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        }
        
        .shortcut-label {
            font-size: 13px;
            color: #333;
        }
    `;
    document.head.appendChild(style);
};

// ═══════════════════════════════════════════════════════════════════════════════
// Public API
// ═══════════════════════════════════════════════════════════════════════════════

KeyboardShortcuts.prototype.enable = function() {
    this.enabled = true;
};

KeyboardShortcuts.prototype.disable = function() {
    this.enabled = false;
};

KeyboardShortcuts.prototype.isEnabled = function() {
    return this.enabled;
};

KeyboardShortcuts.prototype.getShortcuts = function() {
    return this.shortcuts;
};

KeyboardShortcuts.prototype.getShortcutForEvent = function(eventName) {
    for (var i = 0; i < this.shortcuts.length; i++) {
        if (this.shortcuts[i].event === eventName) {
            return this.shortcuts[i];
        }
    }
    return null;
};

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = KeyboardShortcuts;
}