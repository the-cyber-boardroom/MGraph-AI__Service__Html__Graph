module.exports = function(config) {
  config.set({
    // Base path for resolving patterns
    basePath: '.',

    frameworks: ['qunit'],

    files: [
      // Test utilities - loaded as regular scripts (not modules) so they set globals
      { pattern: 'tests/test-paths.js', type: 'js' },
      { pattern: 'tests/test-utils.js', type: 'js' },

      // Unit tests
      { pattern: 'tests/unit/**/*.test.js', type: 'js' },


      // Source files (served but not included - loaded by tests)
      { pattern: 'v0.1.0/**/*.js', included: false, served: true, type: 'module' },
      { pattern: 'v0.1.1/**/*.js', included: false, served: true, type: 'module' },
      { pattern: 'v0.1.2/**/*.js', included: false, served: true, type: 'module' },
      { pattern: 'v0.1.3/**/*.js', included: false, served: true, type: 'module' },
      { pattern: 'v0.1.4/**/*.js', included: false, served: true, type: 'module' },

      // Source files - CSS
      { pattern: 'v0.1.0/**/*.css', included: false, served: true },
      { pattern: 'v0.1.1/**/*.css', included: false, served: true },
      { pattern: 'v0.1.2/**/*.css', included: false, served: true },
      { pattern: 'v0.1.3/**/*.css', included: false, served: true },
      { pattern: 'v0.1.4/**/*.css', included: false, served: true },

      // Sample HTML files
      { pattern: 'v0.1.0/samples/*.html', included: false, served: true },
    ],

        proxies: {
          '/console/v0/v0.1/': '/base/',
        },
    exclude: [],

    preprocessors: {},

    reporters: ['progress'],

    port: 9876,

    colors: true,

    logLevel: config.LOG_INFO,

    autoWatch: false,

    browsers: ['ChromeHeadless'],

    singleRun: true,

    concurrency: Infinity,

    // Increase timeouts for CI
    browserNoActivityTimeout: 60000,
    browserDisconnectTimeout: 10000,
    browserDisconnectTolerance: 1,
  });
};