// ═══════════════════════════════════════════════════════════════════════════════
// MGraph HTML Graph - Playground v0.2.6 (Surgical Override)
// Adds: Keyboard shortcuts support
// Base: v0.2.0 → v0.2.3 → v0.2.4 → v0.2.5 → v0.2.6
// ═══════════════════════════════════════════════════════════════════════════════

(function() {
    var _originalInit = Playground.prototype.init;

    /**
     * OVERRIDE: Add keyboard shortcuts initialization
     */
    Playground.prototype.init = function() {
        _originalInit.call(this);
        this.initKeyboardShortcuts();
    };

    /**
     * NEW: Initialize keyboard shortcuts system
     */
    Playground.prototype.initKeyboardShortcuts = function() {
        // Ensure transformations array exists
        if (!this.transformations) {
            this.transformations = ['default'];
            this.loadTransformationsForShortcuts();
        }

        // Ensure currentTransformation exists
        if (!this.currentTransformation) {
            this.currentTransformation = 'default';
        }

        this.keyboardShortcuts = new KeyboardShortcuts({
            configUrl: this.getShortcutsConfigUrl()
        });
        this.bindShortcutEvents();
        this.addShortcutsLinks();
        console.log('Keyboard shortcuts initialized');
    };

    /**
     * NEW: Load transformations if not already loaded
     */
    Playground.prototype.loadTransformationsForShortcuts = function() {
        var self = this;

        // First try to get from existing dropdown
        var select = document.querySelector('#main-transformation-select, #max-transformation-select, .transformation-select');
        if (select && select.options.length > 0) {
            this.transformations = Array.from(select.options).map(function(opt) {
                return opt.value;
            });
            console.log('Transformations loaded from dropdown:', this.transformations);
            return;
        }

        // Otherwise fetch from API
        if (this.apiClient && typeof this.apiClient.getTransformations === 'function') {
            this.apiClient.getTransformations()
                .then(function(transformations) {
                    self.transformations = transformations;
                    console.log('Transformations loaded from API:', transformations);
                })
                .catch(function(error) {
                    console.warn('Could not load transformations:', error);
                });
        }
    };

    /**
     * NEW: Format transformation name for display
     */
    Playground.prototype.formatTransformationName = function(name) {
        if (!name) return 'Unknown';
        return name.split('_').map(function(word) {
            return word.charAt(0).toUpperCase() + word.slice(1);
        }).join(' ');
    };

    /**
     * NEW: Add shortcuts links to UI
     */
    Playground.prototype.addShortcutsLinks = function() {
        var self = this;

        // Add to main canvas toolbar (right side)
        var toolbarRight = document.querySelector('.canvas-toolbar-right');
        if (toolbarRight) {
            var link = document.createElement('button');
            link.className = 'shortcuts-link';
            link.innerHTML = '⌨️ <span>Shortcuts</span>';
            link.title = 'Keyboard Shortcuts (H)';
            link.addEventListener('click', function() {
                self.toggleShortcutsHelp();
            });
            toolbarRight.insertBefore(link, toolbarRight.firstChild);
        }

        // Add styles for the link
        this.addShortcutsLinkStyles();
    };

    /**
     * NEW: Styles for shortcuts link
     */
    Playground.prototype.addShortcutsLinkStyles = function() {
        if (document.getElementById('shortcuts-link-styles')) return;

        var style = document.createElement('style');
        style.id = 'shortcuts-link-styles';
        style.textContent = `
            .shortcuts-link {
                display: inline-flex;
                align-items: center;
                gap: 4px;
                background: transparent;
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 13px;
                color: #666;
                cursor: pointer;
                transition: all 0.2s;
            }
            .shortcuts-link:hover {
                background: #f5f5f5;
                border-color: #ccc;
                color: #333;
            }
            .shortcuts-link span {
                font-size: 12px;
            }
        `;
        document.head.appendChild(style);
    };

    /**
     * NEW: Get shortcuts config URL based on script location
     */
    Playground.prototype.getShortcutsConfigUrl = function() {
        var scripts = document.querySelectorAll('script[src*="keyboard-shortcuts"]');
        if (scripts.length > 0) {
            var src = scripts[0].src;
            return src.replace('.js', '.json');
        }
        return '/static/v0.2.6/js/keyboard-shortcuts.json';
    };

    /**
     * NEW: Bind all shortcut event listeners
     */
    Playground.prototype.bindShortcutEvents = function() {
        var self = this;

        // Actions
        document.addEventListener('shortcut:reload', function() {
            self.renderGraph();
        });

        // View
        document.addEventListener('shortcut:maximize-toggle', function() {
            self.toggleMaximizeMode();
        });

        document.addEventListener('shortcut:zoom-in', function() {
            self.zoomIn();
        });

        document.addEventListener('shortcut:zoom-out', function() {
            self.zoomOut();
        });

        document.addEventListener('shortcut:zoom-reset', function() {
            self.zoomReset();
        });

        document.addEventListener('shortcut:zoom-fit', function() {
            self.zoomFit();
        });

        // Transformations
        document.addEventListener('shortcut:transformation-next', function() {
            self.cycleTransformation(1);
        });

        document.addEventListener('shortcut:transformation-prev', function() {
            self.cycleTransformation(-1);
        });

        document.addEventListener('shortcut:transformation-select', function(e) {
            var index = e.detail?.index;
            if (typeof index === 'number') {
                self.selectTransformationByIndex(index);
            }
        });

        // Engines
        document.addEventListener('shortcut:engine-next', function() {
            self.cycleEngine(1);
        });

        document.addEventListener('shortcut:engine-prev', function() {
            self.cycleEngine(-1);
        });

        // Help & Navigation
        document.addEventListener('shortcut:help-toggle', function() {
            self.toggleShortcutsHelp();
        });

        document.addEventListener('shortcut:escape', function() {
            self.handleEscape();
        });
    };

    /**
     * NEW: Toggle maximize mode
     */
    Playground.prototype.toggleMaximizeMode = function() {
        var playground = document.querySelector('.playground');
        if (playground && playground.classList.contains('maximized')) {
            this.exitMaximizeMode();
        } else {
            this.enterMaximizeMode();
        }
    };

    /**
     * NEW: Cycle through transformations
     */
    Playground.prototype.cycleTransformation = function(direction) {
        // Try to load from dropdown if not available
        if (!this.transformations || this.transformations.length <= 1) {
            var select = document.querySelector('#main-transformation-select, #max-transformation-select');
            if (select && select.options.length > 1) {
                this.transformations = Array.from(select.options).map(function(opt) {
                    return opt.value;
                });
                // Also sync current transformation from dropdown
                this.currentTransformation = select.value;
            }
        }

        if (!this.transformations || this.transformations.length === 0) {
            this.showToast('Transformations not loaded');
            return;
        }

        // Get current from dropdown if not set
        if (!this.currentTransformation) {
            var sel = document.querySelector('#main-transformation-select, #max-transformation-select');
            this.currentTransformation = sel ? sel.value : 'default';
        }

        var currentIndex = this.transformations.indexOf(this.currentTransformation);
        if (currentIndex === -1) currentIndex = 0;

        var newIndex = (currentIndex + direction + this.transformations.length) % this.transformations.length;
        var newTransformation = this.transformations[newIndex];

        this.setTransformation(newTransformation);
        this.renderGraph();
        this.showToast('Transform: ' + this.formatTransformationName(newTransformation));
    };

    /**
     * NEW: Select transformation by index (for number keys 1-0)
     */
    Playground.prototype.selectTransformationByIndex = function(index) {
        // Try to load from dropdown if not available
        if (!this.transformations || this.transformations.length <= 1) {
            var select = document.querySelector('#main-transformation-select, #max-transformation-select');
            if (select && select.options.length > 1) {
                this.transformations = Array.from(select.options).map(function(opt) {
                    return opt.value;
                });
            }
        }

        if (!this.transformations || this.transformations.length === 0) {
            this.showToast('Transformations not loaded');
            return;
        }

        if (index >= 0 && index < this.transformations.length) {
            var newTransformation = this.transformations[index];
            this.setTransformation(newTransformation);
            this.renderGraph();
            this.showToast('Transform: ' + this.formatTransformationName(newTransformation));
        }
    };

    /**
     * NEW: Set transformation and sync selects
     */
    Playground.prototype.setTransformation = function(transformation) {
        this.currentTransformation = transformation;

        // Sync all transformation selects
        var selects = document.querySelectorAll('#main-transformation-select, #max-transformation-select, .transformation-select');
        selects.forEach(function(select) {
            select.value = transformation;
        });
    };

    /**
     * NEW: Cycle through engines
     */
    Playground.prototype.cycleEngine = function(direction) {
        var engines = ['dot', 'visjs', 'd3', 'cytoscape', 'mermaid'];
        var currentEngine = this.getCurrentEngine();
        var currentIndex = engines.indexOf(currentEngine);
        if (currentIndex === -1) currentIndex = 0;

        var newIndex = (currentIndex + direction + engines.length) % engines.length;
        var newEngine = engines[newIndex];

        this.setEngine(newEngine);
        this.renderGraph();
        this.showToast('Engine: ' + this.formatEngineName(newEngine));
    };

    /**
     * NEW: Get current engine from select
     */
    Playground.prototype.getCurrentEngine = function() {
        var select = document.querySelector('#renderer-select');
        return select ? select.value : 'dot';
    };

    /**
     * NEW: Set engine and sync selects
     */
    Playground.prototype.setEngine = function(engine) {
        var mainSelect = document.querySelector('#renderer-select');
        if (mainSelect) {
            mainSelect.value = engine;
            mainSelect.dispatchEvent(new Event('change', { bubbles: true }));
        }

        var maxSelect = document.getElementById('max-renderer-select');
        if (maxSelect) {
            maxSelect.value = engine;
        }
    };

    /**
     * NEW: Format engine name for display
     */
    Playground.prototype.formatEngineName = function(engine) {
        var names = {
            'dot': 'DOT (Graphviz)',
            'visjs': 'VisJS',
            'd3': 'D3 Force',
            'cytoscape': 'Cytoscape',
            'mermaid': 'Mermaid'
        };
        return names[engine] || engine;
    };

    /**
     * NEW: Zoom in
     */
    Playground.prototype.zoomIn = function() {
        var graphCanvas = document.querySelector('graph-canvas');
        if (graphCanvas && typeof graphCanvas.zoomIn === 'function') {
            graphCanvas.zoomIn();
        } else {
            // Fallback: dispatch event for renderers to handle
            document.dispatchEvent(new CustomEvent('graph:zoom', { detail: { direction: 'in' } }));
        }
        this.showToast('Zoom In');
    };

    /**
     * NEW: Zoom out
     */
    Playground.prototype.zoomOut = function() {
        var graphCanvas = document.querySelector('graph-canvas');
        if (graphCanvas && typeof graphCanvas.zoomOut === 'function') {
            graphCanvas.zoomOut();
        } else {
            document.dispatchEvent(new CustomEvent('graph:zoom', { detail: { direction: 'out' } }));
        }
        this.showToast('Zoom Out');
    };

    /**
     * NEW: Reset zoom
     */
    Playground.prototype.zoomReset = function() {
        var graphCanvas = document.querySelector('graph-canvas');
        if (graphCanvas && typeof graphCanvas.zoomReset === 'function') {
            graphCanvas.zoomReset();
        } else {
            document.dispatchEvent(new CustomEvent('graph:zoom', { detail: { direction: 'reset' } }));
        }
        this.showToast('Zoom Reset');
    };

    /**
     * NEW: Fit to view
     */
    Playground.prototype.zoomFit = function() {
        var graphCanvas = document.querySelector('graph-canvas');
        if (graphCanvas && typeof graphCanvas.zoomFit === 'function') {
            graphCanvas.zoomFit();
        } else {
            document.dispatchEvent(new CustomEvent('graph:zoom', { detail: { direction: 'fit' } }));
        }
        this.showToast('Fit to View');
    };

    /**
     * NEW: Toggle shortcuts help panel
     */
    Playground.prototype.toggleShortcutsHelp = function() {
        if (this.keyboardShortcuts) {
            this.keyboardShortcuts.toggleHelp();
        }
    };

    /**
     * NEW: Handle escape key
     */
    Playground.prototype.handleEscape = function() {
        // First close help if open
        if (this.keyboardShortcuts && this.keyboardShortcuts.helpVisible) {
            this.keyboardShortcuts.hideHelp();
            return;
        }

        // Then exit maximize mode if active
        var playground = document.querySelector('.playground');
        if (playground && playground.classList.contains('maximized')) {
            this.exitMaximizeMode();
        }
    };

    /**
     * NEW: Show toast notification
     */
    Playground.prototype.showToast = function(message, duration) {
        duration = duration || 1500;

        var existing = document.getElementById('playground-toast');
        if (existing) existing.remove();

        var toast = document.createElement('div');
        toast.id = 'playground-toast';
        toast.className = 'playground-toast';
        toast.textContent = message;

        this.addToastStyles();
        document.body.appendChild(toast);

        requestAnimationFrame(function() {
            toast.classList.add('visible');
        });

        setTimeout(function() {
            toast.classList.remove('visible');
            setTimeout(function() { toast.remove(); }, 300);
        }, duration);
    };

    /**
     * NEW: Add toast styles
     */
    Playground.prototype.addToastStyles = function() {
        if (document.getElementById('playground-toast-styles')) return;

        var style = document.createElement('style');
        style.id = 'playground-toast-styles';
        style.textContent = `
            .playground-toast {
                position: fixed;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%) translateY(20px);
                background: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                z-index: 10001;
                opacity: 0;
                transition: opacity 0.3s, transform 0.3s;
                pointer-events: none;
            }
            .playground-toast.visible {
                opacity: 1;
                transform: translateX(-50%) translateY(0);
            }
        `;
        document.head.appendChild(style);
    };
})();