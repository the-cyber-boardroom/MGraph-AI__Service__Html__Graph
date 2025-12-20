/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Playground Surgical Override
   v0.2.10 - Server reload detector integration

   Adds:
   - ServerReloadDetector initialization
   - Toggle button in toolbar
   ═══════════════════════════════════════════════════════════════════════════════ */

(function() {
    'use strict';

    const patchPlayground = () => {
        if (typeof Playground === 'undefined' || typeof ServerReloadDetector === 'undefined') {
            setTimeout(patchPlayground, 50);
            return;
        }

        // Store original init
        const originalInit = Playground.prototype.init;

        Playground.prototype.init = function() {
            // Call original init
            originalInit.call(this);

            // Initialize server reload detector
            this.initServerReloadDetector();
        };

        /**
         * NEW: Initialize server reload detector
         */
        Playground.prototype.initServerReloadDetector = function() {
            var self = this;

            this.serverReloadDetector = new ServerReloadDetector({
                endpoint: '/events/server',
                enabled: false,  // Default off, remembers preference in localStorage
                onReload: function() {
                    self.renderGraph();
                }
            });

            // Add toggle to UI
            this.addAutoReloadToggle();
        };

        /**
         * NEW: Add auto-reload toggle to toolbar
         */
        Playground.prototype.addAutoReloadToggle = function() {
            var self = this;

            // Find toolbar (try multiple locations)
            var toolbar = document.querySelector('.canvas-toolbar-right') ||
                          document.querySelector('.stats-toolbar-right') ||
                          document.querySelector('stats-toolbar');

            if (!toolbar) {
                console.warn('[v0.2.10] Could not find toolbar for auto-reload toggle');
                return;
            }

            // Create toggle button
            var toggle = document.createElement('button');
            toggle.id = 'auto-reload-toggle';
            toggle.className = 'auto-reload-toggle';
            toggle.title = 'Auto-reload on server restart';
            toggle.innerHTML = '🔄 <span>Auto</span>';

            // Set initial state
            if (this.serverReloadDetector.isEnabled()) {
                toggle.classList.add('active');
            }

            // Click handler
            toggle.addEventListener('click', function() {
                var enabled = self.serverReloadDetector.toggle();
                toggle.classList.toggle('active', enabled);
            });

            // Insert at beginning of toolbar
            toolbar.insertBefore(toggle, toolbar.firstChild);

            // Also add to maximize toolbar if it exists
            this.addAutoReloadToggleToMaximize();
        };

        /**
         * NEW: Add toggle to maximize toolbar
         */
        Playground.prototype.addAutoReloadToggleToMaximize = function() {
            var self = this;

            // Patch initMaximizeMode to add toggle there too
            var originalInitMaximizeMode = Playground.prototype.initMaximizeMode;

            Playground.prototype.initMaximizeMode = function() {
                originalInitMaximizeMode.call(this);

                var maxToolbarRight = document.querySelector('.maximize-toolbar-right');
                if (maxToolbarRight && !document.getElementById('max-auto-reload-toggle')) {
                    var toggle = document.createElement('button');
                    toggle.id = 'max-auto-reload-toggle';
                    toggle.className = 'max-toolbar-btn auto-reload-toggle';
                    toggle.title = 'Auto-reload on server restart';
                    toggle.innerHTML = '🔄';

                    if (self.serverReloadDetector && self.serverReloadDetector.isEnabled()) {
                        toggle.classList.add('active');
                    }

                    toggle.addEventListener('click', function() {
                        var enabled = self.serverReloadDetector.toggle();
                        toggle.classList.toggle('active', enabled);

                        // Sync with main toggle
                        var mainToggle = document.getElementById('auto-reload-toggle');
                        if (mainToggle) {
                            mainToggle.classList.toggle('active', enabled);
                        }
                    });

                    maxToolbarRight.insertBefore(toggle, maxToolbarRight.firstChild);
                }
            };
        };

        /**
         * Patch initMaximizeMode to add copy button
         */
        const originalInitMaximizeMode = Playground.prototype.initMaximizeMode;
        Playground.prototype.initMaximizeMode = function() {
            originalInitMaximizeMode.call(this);

            var maxToolbarRight = document.querySelector('.maximize-toolbar-right');
            if (maxToolbarRight && !document.getElementById('max-copy-screenshot')) {
                var copyBtn = document.createElement('button');
                copyBtn.id = 'max-copy-screenshot';
                copyBtn.className = 'max-toolbar-btn';
                copyBtn.title = 'Copy to Clipboard';
                copyBtn.textContent = '📋';
                copyBtn.addEventListener('click', function() {
                    var graphCanvas = document.querySelector('graph-canvas');
                    if (graphCanvas && graphCanvas.copyScreenshot) {
                        graphCanvas.copyScreenshot();
                    }
                });

                // Insert at beginning
                maxToolbarRight.insertBefore(copyBtn, maxToolbarRight.firstChild);
            }
        };
        console.log('[v0.2.10] Playground patched: server reload detector');
    };

    patchPlayground();
})();