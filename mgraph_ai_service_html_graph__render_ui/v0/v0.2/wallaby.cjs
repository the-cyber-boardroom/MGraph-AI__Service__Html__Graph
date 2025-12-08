module.exports = function (wallaby) {
  return {
    files: [
      // Test utilities (not instrumented)
      { pattern: 'tests/test-paths.js', instrument: false },
      { pattern: 'tests/test-utils.js', instrument: false },
      //
      // Source files - all versions
      { pattern: 'v0.2.*/**/*.js', load: false },
      { pattern: 'v0.2.*/**/*.css', load: false },

      // Exclude test files from source (they're in tests array)
      { pattern: '!v0.2.*/**/*.test.js' },
    ],

    tests: [
      'v0.2.*/**/*.test.js',
    ],

    testFramework: 'qunit',

    env: {
      kind: 'chrome',
    },

    // use middleware to proxy requests to the correct folder
    middleware: function (app, express) {
        app.use('/console/v0/v0.2', express.static(wallaby.projectCacheDir));
    },


    setup: function () {
      if (!document.getElementById('qunit-fixture')) {
        const fixture = document.createElement('div');
        fixture.id = 'qunit-fixture';
        document.body.appendChild(fixture);
      }
    },
  };
};