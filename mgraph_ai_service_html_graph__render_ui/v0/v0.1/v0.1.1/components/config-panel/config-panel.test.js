/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Test Suite - Config Panel Tests
   v0.1.4 - Test Infrastructure
   ═══════════════════════════════════════════════════════════════════════════════ */

QUnit.module('Config Panel', function(hooks) {
    
    hooks.before(async function(assert) {
        // Load required CSS first
        await TestUtils.loadCss(TestPaths.commonCss);
        // Load the component
        await TestUtils.loadScript(TestPaths.configPanel);
        assert.ok(customElements.get('config-panel'), 'config-panel should be registered');
    });
    
    hooks.afterEach(function() {
        TestUtils.cleanup();
    });

    QUnit.test('component renders correctly', async function(assert) {
        const panel = await TestUtils.createComponent('config-panel');
        
        assert.ok(panel.querySelector('.card'), 'should have card container');
        assert.ok(panel.querySelector('#config-preset'), 'should have preset select');
        assert.ok(panel.querySelector('#config-show-tag'), 'should have show tag checkbox');
        assert.ok(panel.querySelector('#config-show-attr'), 'should have show attr checkbox');
        assert.ok(panel.querySelector('#config-show-text'), 'should have show text checkbox');
        assert.ok(panel.querySelector('#config-color-scheme'), 'should have color scheme select');
    });
    
    QUnit.test('default config values are correct', async function(assert) {
        const panel = await TestUtils.createComponent('config-panel');
        const config = panel.getConfig();
        
        assert.strictEqual(config.preset, 'full_detail', 'default preset should be full_detail');
        assert.strictEqual(config.show_tag_nodes, true, 'show_tag_nodes should default to true');
        assert.strictEqual(config.show_attr_nodes, true, 'show_attr_nodes should default to true');
        assert.strictEqual(config.show_text_nodes, true, 'show_text_nodes should default to true');
        assert.strictEqual(config.color_scheme, 'default', 'color_scheme should default to default');
    });
    
    QUnit.test('preset change updates checkboxes', async function(assert) {
        const panel = await TestUtils.createComponent('config-panel');
        const presetSelect = panel.querySelector('#config-preset');
        
        // Change to structure_only
        presetSelect.value = 'structure_only';
        TestUtils.triggerEvent(presetSelect, 'change');
        
        await TestUtils.nextFrame();
        
        const config = panel.getConfig();
        assert.strictEqual(config.show_tag_nodes, true, 'tags should still be shown');
        assert.strictEqual(config.show_attr_nodes, false, 'attrs should be hidden');
        assert.strictEqual(config.show_text_nodes, false, 'text should be hidden');
    });
    
    QUnit.test('minimal preset hides all optional nodes', async function(assert) {
        const panel = await TestUtils.createComponent('config-panel');
        const presetSelect = panel.querySelector('#config-preset');
        
        presetSelect.value = 'minimal';
        TestUtils.triggerEvent(presetSelect, 'change');
        
        await TestUtils.nextFrame();
        
        const config = panel.getConfig();
        assert.strictEqual(config.show_tag_nodes, false, 'tags should be hidden');
        assert.strictEqual(config.show_attr_nodes, false, 'attrs should be hidden');
        assert.strictEqual(config.show_text_nodes, false, 'text should be hidden');
    });
    
    QUnit.test('emits config-changed event on preset change', async function(assert) {
        const panel = await TestUtils.createComponent('config-panel');
        const presetSelect = panel.querySelector('#config-preset');
        
        const eventPromise = TestUtils.waitForEvent(panel, 'config-changed');
        
        presetSelect.value = 'structure_only';
        TestUtils.triggerEvent(presetSelect, 'change');
        
        const event = await eventPromise;
        assert.ok(event.detail.config, 'event should have config in detail');
        assert.strictEqual(event.detail.config.preset, 'structure_only', 'config should have new preset');
    });
    
    QUnit.test('emits config-changed event on checkbox change', async function(assert) {
        const panel = await TestUtils.createComponent('config-panel');
        const checkbox = panel.querySelector('#config-show-attr');
        
        const eventPromise = TestUtils.waitForEvent(panel, 'config-changed');
        
        checkbox.checked = false;
        TestUtils.triggerEvent(checkbox, 'change');
        
        const event = await eventPromise;
        assert.strictEqual(event.detail.config.show_attr_nodes, false, 'config should reflect unchecked state');
    });
    
    QUnit.test('emits config-changed event on color scheme change', async function(assert) {
        const panel = await TestUtils.createComponent('config-panel');
        const colorSelect = panel.querySelector('#config-color-scheme');
        
        const eventPromise = TestUtils.waitForEvent(panel, 'config-changed');
        
        colorSelect.value = 'monochrome';
        TestUtils.triggerEvent(colorSelect, 'change');
        
        const event = await eventPromise;
        assert.strictEqual(event.detail.config.color_scheme, 'monochrome', 'config should have new color scheme');
    });
    
    QUnit.test('setConfig updates UI correctly', async function(assert) {
        const panel = await TestUtils.createComponent('config-panel');
        
        panel.setConfig({
            preset: 'minimal',
            show_tag_nodes: false,
            show_attr_nodes: false,
            show_text_nodes: true,
            color_scheme: 'high_contrast'
        });
        
        assert.strictEqual(panel.querySelector('#config-preset').value, 'minimal', 'preset should be updated');
        assert.strictEqual(panel.querySelector('#config-show-tag').checked, false, 'tag checkbox should be unchecked');
        assert.strictEqual(panel.querySelector('#config-show-text').checked, true, 'text checkbox should be checked');
        assert.strictEqual(panel.querySelector('#config-color-scheme').value, 'high_contrast', 'color scheme should be updated');
    });
    
    QUnit.test('getConfig returns a copy, not reference', async function(assert) {
        const panel = await TestUtils.createComponent('config-panel');
        
        const config1 = panel.getConfig();
        const config2 = panel.getConfig();
        
        assert.notStrictEqual(config1, config2, 'should return different objects');
        assert.deepEqual(config1, config2, 'but with same values');
        
        config1.preset = 'modified';
        assert.notStrictEqual(panel.getConfig().preset, 'modified', 'modifying returned config should not affect internal state');
    });

});
