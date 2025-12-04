module.exports = function(config) {
  config.set({
    // Base path for resolving patterns
    basePath: '..',

    frameworks: ['qunit'],

    files: [
      // QUnit CSS (for reporter)
      { pattern: 'https://code.jquery.com/qunit/qunit-2.20.0.css', included: true, type: 'css' },

      // Test utilities
      { pattern: 'tests/test-paths.js', type: 'module' },
      { pattern: 'tests/test-utils.js', type: 'module' },

      // Unit tests
      { pattern: 'tests/unit/*.test.js', type: 'module' },

      // Integration tests
      { pattern: 'tests/integration/*.test.js', type: 'module' },

      // Source files (served but not included - loaded by tests)
      { pattern: 'v0.1.0/**/*.js', included: false, served: true, type: 'module' },
      { pattern: 'v0.1.1/**/*.js', included: false, served: true, type: 'module' },
      { pattern: 'v0.1.2/**/*.js', included: false, served: true, type: 'module' },
      { pattern: 'v0.1.3/**/*.js', included: false, served: true, type: 'module' },
      { pattern: 'v0.1.4/**/*.js', included: false, served: true, type: 'module' },

      // Sample HTML files
      { pattern: 'v0.1.0/samples/*.html', included: false, served: true },
    ],

    // Proxy paths to match how tests expect to load files
    proxies: {
      '/v0.1.0/': '/base/v0.1.0/',
      '/v0.1.1/': '/base/v0.1.1/',
      '/v0.1.2/': '/base/v0.1.2/',
      '/v0.1.3/': '/base/v0.1.3/',
      '/v0.1.4/': '/base/v0.1.4/',
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