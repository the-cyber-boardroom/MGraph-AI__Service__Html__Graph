/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - Karma Configuration
   v0.2.0 - Consolidated from v0.1.x
   ═══════════════════════════════════════════════════════════════════════════════ */

module.exports = function(config) {
    config.set({
        // Base path for resolving patterns
        basePath: '',

        // Frameworks to use
        frameworks: ['qunit'],

        // List of files/patterns to load
        files: [
            // Test utilities
            'tests/test-utils.js',
            'tests/test-paths.js',

            // Source files (components)
            'components/**/*.js',

            // Source files (services)
            'js/services/*.js',

            // Test files - co-located with components
            'components/**/*.test.js',

            // Test files - central location (legacy)
            'tests/unit/**/*.test.js'
        ],

        // Files to exclude
        exclude: [],

        // Preprocess files before serving
        preprocessors: {},

        // Test results reporters
        reporters: ['progress'],

        // Web server port
        port: 9876,

        // Enable colors in output
        colors: true,

        // Level of logging
        logLevel: config.LOG_INFO,

        // Watch files and re-run on changes
        autoWatch: true,

        // Browsers to launch
        browsers: ['ChromeHeadless'],

        // Continuous Integration mode
        singleRun: false,

        // Concurrency level
        concurrency: Infinity,

        // Client configuration
        client: {
            clearContext: false,
            qunit: {
                showUI: true,
                testTimeout: 5000
            }
        }
    });
};
