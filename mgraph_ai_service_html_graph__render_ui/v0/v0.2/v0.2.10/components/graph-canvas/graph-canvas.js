/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - GraphCanvas Surgical Override
   v0.2.10 - Add screenshot to clipboard functionality (high resolution)
   ═══════════════════════════════════════════════════════════════════════════════ */

(function() {
    'use strict';

    const patchGraphCanvas = () => {
        const instance = document.querySelector('graph-canvas');
        if (!instance) {
            setTimeout(patchGraphCanvas, 50);
            return;
        }

        // Add copy screenshot button to toolbar
        const toolbarRight = instance.querySelector('.canvas-toolbar-right');
        if (toolbarRight) {
            const copyBtn = document.createElement('button');
            copyBtn.id = 'btn-copy-screenshot';
            copyBtn.className = 'btn btn-sm btn-secondary';
            copyBtn.title = 'Copy to Clipboard';
            copyBtn.textContent = '📋';
            copyBtn.addEventListener('click', () => instance.copyScreenshot());

            // Insert before download button
            const downloadBtn = toolbarRight.querySelector('#btn-download');
            toolbarRight.insertBefore(copyBtn, downloadBtn);
        }

        /**
         * Copy current graph as image to clipboard
         */
        GraphCanvas.prototype.copyScreenshot = async function() {
            try {
                const canvas = await this.getGraphAsCanvas();
                if (!canvas) {
                    this.showToast('No graph to copy');
                    return;
                }

                const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'));
                await navigator.clipboard.write([
                    new ClipboardItem({ 'image/png': blob })
                ]);

                this.showToast('Copied to clipboard!');
            } catch (error) {
                console.error('[v0.2.10] Copy failed:', error);
                this.showToast('Copy failed: ' + error.message);
            }
        };

        /**
         * Get current graph as canvas element
         */
        GraphCanvas.prototype.getGraphAsCanvas = async function() {
            // Try canvas first (vis.js, Cytoscape)
            const existingCanvas = this.canvasArea.querySelector('canvas');
            if (existingCanvas) {
                // For canvas renderers, create a copy at higher resolution
                return this.copyCanvasHighRes(existingCanvas);
            }

            // Try SVG (DOT, D3, Mermaid)
            const svg = this.canvasArea.querySelector('svg');
            if (svg) {
                return this.svgToCanvas(svg);
            }

            return null;
        };

        /**
         * Copy canvas at higher resolution
         */
        GraphCanvas.prototype.copyCanvasHighRes = function(sourceCanvas) {
            const scale = 2;  // 2x resolution
            const canvas = document.createElement('canvas');
            canvas.width = sourceCanvas.width * scale;
            canvas.height = sourceCanvas.height * scale;

            const ctx = canvas.getContext('2d');
            ctx.scale(scale, scale);
            ctx.drawImage(sourceCanvas, 0, 0);

            return canvas;
        };

        /**
         * Convert SVG element to Canvas (high resolution)
         */
        GraphCanvas.prototype.svgToCanvas = function(svg) {
            return new Promise((resolve, reject) => {
                // Get actual dimensions from viewBox or attributes
                const viewBox = svg.getAttribute('viewBox');
                let width, height;

                if (viewBox) {
                    const parts = viewBox.split(/\s+|,/).map(Number);
                    width = parts[2];
                    height = parts[3];
                } else {
                    // Fallback to width/height attributes (strip 'pt' or 'px')
                    width = parseFloat(svg.getAttribute('width')) || svg.clientWidth || 800;
                    height = parseFloat(svg.getAttribute('height')) || svg.clientHeight || 600;
                }

                // Scale factor for high resolution
                const scale = 2;
                const scaledWidth = width * scale;
                const scaledHeight = height * scale;

                // Clone SVG and set explicit dimensions
                const svgClone = svg.cloneNode(true);
                svgClone.setAttribute('width', width);
                svgClone.setAttribute('height', height);

                // Ensure white background in SVG
                const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
                rect.setAttribute('width', '100%');
                rect.setAttribute('height', '100%');
                rect.setAttribute('fill', 'white');
                svgClone.insertBefore(rect, svgClone.firstChild);

                const svgData = new XMLSerializer().serializeToString(svgClone);
                const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
                const url = URL.createObjectURL(svgBlob);

                const img = new Image();
                img.onload = function() {
                    const canvas = document.createElement('canvas');
                    canvas.width = scaledWidth;
                    canvas.height = scaledHeight;

                    const ctx = canvas.getContext('2d');
                    ctx.fillStyle = 'white';
                    ctx.fillRect(0, 0, scaledWidth, scaledHeight);
                    ctx.scale(scale, scale);
                    ctx.drawImage(img, 0, 0, width, height);

                    URL.revokeObjectURL(url);
                    resolve(canvas);
                };
                img.onerror = function() {
                    URL.revokeObjectURL(url);
                    reject(new Error('Failed to load SVG'));
                };
                img.src = url;
            });
        };

        /**
         * Show toast notification
         */
        GraphCanvas.prototype.showToast = function(message) {
            const existing = document.getElementById('graph-canvas-toast');
            if (existing) existing.remove();

            const toast = document.createElement('div');
            toast.id = 'graph-canvas-toast';
            toast.className = 'graph-canvas-toast';
            toast.textContent = message;
            document.body.appendChild(toast);

            requestAnimationFrame(() => toast.classList.add('visible'));

            setTimeout(() => {
                toast.classList.remove('visible');
                setTimeout(() => toast.remove(), 300);
            }, 2000);
        };

        console.log('[v0.2.10] GraphCanvas patched: copy screenshot');
    };

    patchGraphCanvas();
})();