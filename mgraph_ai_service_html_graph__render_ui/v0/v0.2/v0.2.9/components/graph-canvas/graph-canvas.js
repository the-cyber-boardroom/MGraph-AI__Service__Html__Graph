/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - GraphCanvas Surgical Override
   v0.2.9 - Add tree and tree_text renderers to available renderers
   ═══════════════════════════════════════════════════════════════════════════════ */

(function() {
    'use strict';

    const patchGraphCanvas = () => {
        // if (typeof GraphCanvas === 'undefined') {
        //     setTimeout(patchGraphCanvas, 50);
        //     return;
        // }

        // Patch any existing instances in the DOM

        const instance = document.querySelector('graph-canvas');

        instance.renderers.tree = { name: 'Tree (JSON)',
                                    available: true,
                                    description: 'Collapsible hierarchical tree view' };

        instance.renderers.tree_text = { name: 'Tree (Text)',
                                         available: true,
                                         description: 'Formatted text representation'};

        instance.connectedCallback();                               // retrigger rendering

        // Fix DOT SVG rendering to fit canvas
        GraphCanvas.prototype.renderSvg = function(svgContent) {
            this.canvasArea.innerHTML = svgContent;
            this.currentScale = 1;
            this.canvasArea.style.background = 'white';

            const svg = this.canvasArea.querySelector('svg');
            if (svg) {
                // Remove pt-based dimensions that cause overflow
                svg.removeAttribute('width');
                svg.removeAttribute('height');

                // Fit to container while preserving aspect ratio
                svg.style.width = '100%';
                svg.style.height = '100%';
                svg.style.maxWidth = '100%';
                svg.style.maxHeight = '100%';
                svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
            }
        };

        console.log('[v0.2.9] GraphCanvas patched: tree renderers added');
    };

    patchGraphCanvas();
})();