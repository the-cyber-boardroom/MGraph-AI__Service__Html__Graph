/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - QA Scenarios
   v0.2.0 - User Acceptance Test Scenarios for Playground
   
   These scenarios test complete user journeys through the application.
   Each scenario represents a user story that should work end-to-end.
   ═══════════════════════════════════════════════════════════════════════════════ */

// ═══════════════════════════════════════════════════════════════════════════════
// Scenario 1: Basic Graph Rendering
// User Story: As a user, I can enter HTML and see it rendered as a graph
// ═══════════════════════════════════════════════════════════════════════════════

const scenario01_BasicRender = new QAScenario({
    id: 's01-basic-render',
    name: 'Basic Graph Rendering',
    description: 'Test the core workflow of entering HTML and rendering a graph',
    tags: ['core', 'smoke-test']
});

scenario01_BasicRender.addSteps([
    {
        name: 'Verify page loads correctly',
        description: 'Check that all main components are present on the page',
        action: async () => {
            // Wait for components to be ready
            await new Promise(r => setTimeout(r, 500));
        },
        assertions: [
            QAAssert.elementExists('html-input', 'HTML input component should exist'),
            QAAssert.elementExists('config-panel', 'Config panel should exist'),
            QAAssert.elementExists('graph-canvas', 'Graph canvas should exist'),
            QAAssert.elementExists('stats-toolbar', 'Stats toolbar should exist')
        ]
    },
    {
        name: 'Enter simple HTML',
        description: 'Type a simple HTML structure into the input',
        action: async () => {
            const htmlInput = document.querySelector('html-input');
            const textarea = htmlInput.querySelector('#html-input');
            textarea.value = '<div><p>Hello World</p></div>';
            textarea.dispatchEvent(new Event('input', { bubbles: true }));
            await new Promise(r => setTimeout(r, 100));
        },
        assertions: [
            QAAssert.custom(async () => {
                const textarea = document.querySelector('html-input #html-input');
                return textarea.value.includes('<div>');
            }, 'HTML input should contain our text')
        ]
    },
    {
        name: 'Click Render button',
        description: 'Trigger graph rendering by clicking the render button',
        action: async () => {
            const renderBtn = document.querySelector('#render-btn');
            if (renderBtn) {
                renderBtn.click();
                // Wait for render to complete
                await new Promise(r => setTimeout(r, 2000));
            }
        },
        assertions: [
            QAAssert.custom(async () => {
                // Check that stats were updated (indicating successful API call)
                const nodesEl = document.querySelector('#stat-nodes');
                return nodesEl && nodesEl.textContent !== '-' && nodesEl.textContent !== '0';
            }, 'Stats should show node count after render')
        ]
    },
    {
        name: 'Verify graph is displayed',
        description: 'Check that an SVG or canvas element is present in the graph area',
        action: async () => {
            await new Promise(r => setTimeout(r, 500));
        },
        assertions: [
            QAAssert.custom(async () => {
                const canvasArea = document.querySelector('#canvas-area');
                const hasSvg = canvasArea?.querySelector('svg');
                const hasCanvas = canvasArea?.querySelector('canvas');
                const hasContent = canvasArea?.children.length > 0;
                return hasSvg || hasCanvas || hasContent;
            }, 'Graph canvas should contain rendered content')
        ]
    }
]);

// ═══════════════════════════════════════════════════════════════════════════════
// Scenario 2: Configuration Panel Workflow
// User Story: As a user, I can change config options and see the graph update
// ═══════════════════════════════════════════════════════════════════════════════

const scenario02_ConfigChanges = new QAScenario({
    id: 's02-config-changes',
    name: 'Configuration Panel Workflow',
    description: 'Test changing configuration options and verifying graph updates',
    tags: ['config', 'interaction']
});

scenario02_ConfigChanges.addSteps([
    {
        name: 'Setup: Enter HTML and render initial graph',
        description: 'First, we need a graph to modify',
        action: async () => {
            const htmlInput = document.querySelector('html-input');
            if (htmlInput) {
                htmlInput.setHtml('<article><header><h1>Title</h1></header><section><p>Content</p></section></article>');
                await new Promise(r => setTimeout(r, 100));
                
                const renderBtn = document.querySelector('#render-btn');
                if (renderBtn) {
                    renderBtn.click();
                    await new Promise(r => setTimeout(r, 2000));
                }
            }
        },
        assertions: [
            QAAssert.custom(async () => {
                const nodesEl = document.querySelector('#stat-nodes');
                return nodesEl && nodesEl.textContent !== '-';
            }, 'Initial render should complete')
        ]
    },
    {
        name: 'Change preset to Structure Only',
        description: 'Select the "Structure Only" preset from the dropdown',
        action: async () => {
            const presetSelect = document.querySelector('#config-preset');
            if (presetSelect) {
                presetSelect.value = 'structure_only';
                presetSelect.dispatchEvent(new Event('change', { bubbles: true }));
                await new Promise(r => setTimeout(r, 500));
            }
        },
        assertions: [
            QAAssert.custom(async () => {
                const presetSelect = document.querySelector('#config-preset');
                return presetSelect?.value === 'structure_only';
            }, 'Preset should be set to structure_only')
        ]
    },
    {
        name: 'Verify checkboxes updated',
        description: 'Structure Only preset should uncheck attribute and text nodes',
        action: async () => {
            await new Promise(r => setTimeout(r, 100));
        },
        assertions: [
            QAAssert.custom(async () => {
                const showTag = document.querySelector('#config-show-tag');
                const showAttr = document.querySelector('#config-show-attr');
                const showText = document.querySelector('#config-show-text');
                return showTag?.checked === true && 
                       showAttr?.checked === false && 
                       showText?.checked === false;
            }, 'Checkboxes should reflect structure_only preset')
        ]
    },
    {
        name: 'Change to Minimal preset',
        description: 'Select the "Minimal" preset',
        action: async () => {
            const presetSelect = document.querySelector('#config-preset');
            if (presetSelect) {
                presetSelect.value = 'minimal';
                presetSelect.dispatchEvent(new Event('change', { bubbles: true }));
                await new Promise(r => setTimeout(r, 500));
            }
        },
        assertions: [
            QAAssert.custom(async () => {
                const showTag = document.querySelector('#config-show-tag');
                const showAttr = document.querySelector('#config-show-attr');
                const showText = document.querySelector('#config-show-text');
                return showTag?.checked === false && 
                       showAttr?.checked === false && 
                       showText?.checked === false;
            }, 'All optional node checkboxes should be unchecked for minimal preset')
        ]
    },
    {
        name: 'Change color scheme',
        description: 'Select a different color scheme',
        action: async () => {
            const colorSelect = document.querySelector('#config-color-scheme');
            if (colorSelect) {
                colorSelect.value = 'monochrome';
                colorSelect.dispatchEvent(new Event('change', { bubbles: true }));
                await new Promise(r => setTimeout(r, 300));
            }
        },
        assertions: [
            QAAssert.custom(async () => {
                const colorSelect = document.querySelector('#config-color-scheme');
                return colorSelect?.value === 'monochrome';
            }, 'Color scheme should be set to monochrome')
        ]
    }
]);

// ═══════════════════════════════════════════════════════════════════════════════
// Scenario 3: Renderer Switching
// User Story: As a user, I can switch between different graph renderers
// ═══════════════════════════════════════════════════════════════════════════════

const scenario03_RendererSwitching = new QAScenario({
    id: 's03-renderer-switching',
    name: 'Renderer Switching',
    description: 'Test switching between DOT, vis.js, D3, Cytoscape, and Mermaid renderers',
    tags: ['renderer', 'interaction']
});

scenario03_RendererSwitching.addSteps([
    {
        name: 'Setup: Render initial graph with DOT',
        description: 'Create a graph using the default DOT renderer',
        action: async () => {
            const htmlInput = document.querySelector('html-input');
            if (htmlInput) {
                htmlInput.setHtml('<nav><ul><li>Item 1</li><li>Item 2</li></ul></nav>');
                await new Promise(r => setTimeout(r, 100));
                
                const renderBtn = document.querySelector('#render-btn');
                if (renderBtn) {
                    renderBtn.click();
                    await new Promise(r => setTimeout(r, 2000));
                }
            }
        },
        assertions: [
            QAAssert.elementExists('#renderer-select', 'Renderer selector should exist')
        ]
    },
    {
        name: 'Switch to vis.js renderer',
        description: 'Select vis.js from the renderer dropdown',
        action: async () => {
            const select = document.querySelector('#renderer-select');
            if (select) {
                select.value = 'visjs';
                select.dispatchEvent(new Event('change', { bubbles: true }));
                await new Promise(r => setTimeout(r, 1500));
            }
        },
        assertions: [
            QAAssert.custom(async () => {
                const select = document.querySelector('#renderer-select');
                return select?.value === 'visjs';
            }, 'Renderer should be set to visjs')
        ]
    },
    {
        name: 'Switch to D3 renderer',
        description: 'Select D3 from the renderer dropdown',
        action: async () => {
            const select = document.querySelector('#renderer-select');
            if (select) {
                select.value = 'd3';
                select.dispatchEvent(new Event('change', { bubbles: true }));
                await new Promise(r => setTimeout(r, 1500));
            }
        },
        assertions: [
            QAAssert.custom(async () => {
                const select = document.querySelector('#renderer-select');
                return select?.value === 'd3';
            }, 'Renderer should be set to d3')
        ]
    },
    {
        name: 'Switch to Cytoscape renderer',
        description: 'Select Cytoscape from the renderer dropdown',
        action: async () => {
            const select = document.querySelector('#renderer-select');
            if (select) {
                select.value = 'cytoscape';
                select.dispatchEvent(new Event('change', { bubbles: true }));
                await new Promise(r => setTimeout(r, 1500));
            }
        },
        assertions: [
            QAAssert.custom(async () => {
                const select = document.querySelector('#renderer-select');
                return select?.value === 'cytoscape';
            }, 'Renderer should be set to cytoscape')
        ]
    },
    {
        name: 'Switch to Mermaid renderer',
        description: 'Select Mermaid from the renderer dropdown',
        action: async () => {
            const select = document.querySelector('#renderer-select');
            if (select) {
                select.value = 'mermaid';
                select.dispatchEvent(new Event('change', { bubbles: true }));
                await new Promise(r => setTimeout(r, 1500));
            }
        },
        assertions: [
            QAAssert.custom(async () => {
                const select = document.querySelector('#renderer-select');
                return select?.value === 'mermaid';
            }, 'Renderer should be set to mermaid')
        ]
    },
    {
        name: 'Return to DOT renderer',
        description: 'Switch back to the default DOT renderer',
        action: async () => {
            const select = document.querySelector('#renderer-select');
            if (select) {
                select.value = 'dot';
                select.dispatchEvent(new Event('change', { bubbles: true }));
                await new Promise(r => setTimeout(r, 1000));
            }
        },
        assertions: [
            QAAssert.custom(async () => {
                const select = document.querySelector('#renderer-select');
                return select?.value === 'dot';
            }, 'Renderer should be set back to dot')
        ]
    }
]);

// ═══════════════════════════════════════════════════════════════════════════════
// Scenario 4: Sample HTML Loading
// User Story: As a user, I can load predefined HTML samples
// ═══════════════════════════════════════════════════════════════════════════════

const scenario04_SampleLoading = new QAScenario({
    id: 's04-sample-loading',
    name: 'Sample HTML Loading',
    description: 'Test loading different HTML samples from the dropdown',
    tags: ['samples', 'input']
});

scenario04_SampleLoading.addSteps([
    {
        name: 'Verify sample selector exists',
        description: 'Check that the sample dropdown is present',
        action: async () => {
            await new Promise(r => setTimeout(r, 300));
        },
        assertions: [
            QAAssert.elementExists('#sample-select', 'Sample selector should exist')
        ]
    },
    {
        name: 'Load nested sample',
        description: 'Select the "Nested Structure" sample',
        action: async () => {
            const select = document.querySelector('#sample-select');
            if (select) {
                select.value = 'nested';
                select.dispatchEvent(new Event('change', { bubbles: true }));
                await new Promise(r => setTimeout(r, 500));
            }
        },
        assertions: [
            QAAssert.custom(async () => {
                const textarea = document.querySelector('#html-input');
                return textarea && textarea.value.length > 10;
            }, 'HTML input should have sample content loaded')
        ]
    },
    {
        name: 'Load bootstrap sample',
        description: 'Select the "Bootstrap Layout" sample',
        action: async () => {
            const select = document.querySelector('#sample-select');
            if (select) {
                select.value = 'bootstrap';
                select.dispatchEvent(new Event('change', { bubbles: true }));
                await new Promise(r => setTimeout(r, 500));
            }
        },
        assertions: [
            QAAssert.custom(async () => {
                const textarea = document.querySelector('#html-input');
                return textarea && textarea.value.length > 50;
            }, 'Bootstrap sample should be loaded')
        ]
    }
]);

// ═══════════════════════════════════════════════════════════════════════════════
// Scenario 5: Stats and Timing Display
// User Story: As a user, I can see statistics about the rendered graph
// ═══════════════════════════════════════════════════════════════════════════════

const scenario05_StatsDisplay = new QAScenario({
    id: 's05-stats-display',
    name: 'Stats and Timing Display',
    description: 'Test that graph statistics are displayed correctly after rendering',
    tags: ['stats', 'ui']
});

scenario05_StatsDisplay.addSteps([
    {
        name: 'Render a graph with known structure',
        description: 'Enter HTML and render to generate stats',
        action: async () => {
            const htmlInput = document.querySelector('html-input');
            if (htmlInput) {
                htmlInput.setHtml('<div id="main" class="container"><span>Text</span></div>');
                await new Promise(r => setTimeout(r, 100));
                
                const renderBtn = document.querySelector('#render-btn');
                if (renderBtn) {
                    renderBtn.click();
                    await new Promise(r => setTimeout(r, 2000));
                }
            }
        },
        assertions: [
            QAAssert.elementExists('#stat-nodes', 'Nodes stat should exist'),
            QAAssert.elementExists('#stat-edges', 'Edges stat should exist')
        ]
    },
    {
        name: 'Verify node count is displayed',
        description: 'Check that the total nodes statistic shows a value',
        action: async () => {
            await new Promise(r => setTimeout(r, 100));
        },
        assertions: [
            QAAssert.custom(async () => {
                const nodesEl = document.querySelector('#stat-nodes');
                const value = nodesEl?.textContent;
                return value && value !== '-' && value !== '0';
            }, 'Node count should be a positive number')
        ]
    },
    {
        name: 'Verify timing information',
        description: 'Check that API timing is displayed',
        action: async () => {
            await new Promise(r => setTimeout(r, 100));
        },
        assertions: [
            QAAssert.custom(async () => {
                const apiTiming = document.querySelector('#timing-api');
                return apiTiming && apiTiming.textContent.includes('ms');
            }, 'API timing should show milliseconds')
        ]
    }
]);

// ═══════════════════════════════════════════════════════════════════════════════
// Scenario 6: Error Handling
// User Story: As a user, I see clear error messages when something goes wrong
// ═══════════════════════════════════════════════════════════════════════════════

const scenario06_ErrorHandling = new QAScenario({
    id: 's06-error-handling',
    name: 'Error Handling',
    description: 'Test that errors are displayed appropriately to the user',
    tags: ['error', 'edge-case']
});

scenario06_ErrorHandling.addSteps([
    {
        name: 'Attempt render with empty HTML',
        description: 'Try to render without any HTML content',
        action: async () => {
            const htmlInput = document.querySelector('html-input');
            if (htmlInput) {
                htmlInput.setHtml('');
                await new Promise(r => setTimeout(r, 100));
                
                const renderBtn = document.querySelector('#render-btn');
                if (renderBtn) {
                    renderBtn.click();
                    await new Promise(r => setTimeout(r, 1000));
                }
            }
        },
        assertions: [
            QAAssert.custom(async () => {
                const errorBanner = document.querySelector('#error-banner');
                return errorBanner && errorBanner.classList.contains('show');
            }, 'Error banner should be displayed for empty HTML')
        ]
    },
    {
        name: 'Error banner shows helpful message',
        description: 'Verify error message is user-friendly',
        action: async () => {
            await new Promise(r => setTimeout(r, 100));
        },
        assertions: [
            QAAssert.custom(async () => {
                const errorTitle = document.querySelector('#error-title');
                return errorTitle && errorTitle.textContent.length > 0;
            }, 'Error should have a title')
        ]
    },
    {
        name: 'Render valid HTML clears error',
        description: 'After rendering valid HTML, error should disappear',
        action: async () => {
            const htmlInput = document.querySelector('html-input');
            if (htmlInput) {
                htmlInput.setHtml('<div>Valid HTML</div>');
                await new Promise(r => setTimeout(r, 100));
                
                const renderBtn = document.querySelector('#render-btn');
                if (renderBtn) {
                    renderBtn.click();
                    await new Promise(r => setTimeout(r, 2000));
                }
            }
        },
        assertions: [
            QAAssert.custom(async () => {
                const errorBanner = document.querySelector('#error-banner');
                return !errorBanner?.classList.contains('show');
            }, 'Error banner should be hidden after successful render')
        ]
    }
]);

// ═══════════════════════════════════════════════════════════════════════════════
// Register all scenarios with the engine
// ═══════════════════════════════════════════════════════════════════════════════

function registerAllScenarios(engine) {
    engine.registerScenario(scenario01_BasicRender);
    engine.registerScenario(scenario02_ConfigChanges);
    engine.registerScenario(scenario03_RendererSwitching);
    engine.registerScenario(scenario04_SampleLoading);
    engine.registerScenario(scenario05_StatsDisplay);
    engine.registerScenario(scenario06_ErrorHandling);
    
    console.log('[QA Scenarios] Registered 6 scenarios');
}

// Export for use
window.registerAllScenarios = registerAllScenarios;
window.QAScenarios = {
    scenario01_BasicRender,
    scenario02_ConfigChanges,
    scenario03_RendererSwitching,
    scenario04_SampleLoading,
    scenario05_StatsDisplay,
    scenario06_ErrorHandling
};
