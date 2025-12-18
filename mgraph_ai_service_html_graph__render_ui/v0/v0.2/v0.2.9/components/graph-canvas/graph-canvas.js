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

        console.log('[v0.2.9] GraphCanvas patched: tree renderers added');
    };

    patchGraphCanvas();
})();