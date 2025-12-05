/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - Wallaby.js Configuration
   v0.2.0 - Consolidated from v0.1.x
   ═══════════════════════════════════════════════════════════════════════════════ */

module.exports = function(wallaby) {
    return {
        files: [
            // Test utilities first
            'tests/test-utils.js',
            'tests/test-paths.js',

            // Source files
            'components/**/*.js',
            'js/**/*.js',

            // Exclude test files from source
            '!components/**/*.test.js',
            '!tests/unit/**/*.test.js'
        ],

        tests: [
            // Co-located tests
            'components/**/*.test.js',

            // Central test location (legacy)
            'tests/unit/**/*.test.js'
        ],

        testFramework: 'qunit',

        env: {
            type: 'browser',
            kind: 'chrome'
        },

        setup: function(wallaby) {
            // QUnit configuration
            QUnit.config.autostart = false;
            QUnit.config.testTimeout = 5000;
        },

        debug: true
    };
};
