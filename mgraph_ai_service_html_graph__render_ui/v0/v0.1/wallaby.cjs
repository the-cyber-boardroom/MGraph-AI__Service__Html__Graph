module.exports = function (wallaby) {
  return {
    files: [
        // Test utilities (loaded first)
        { pattern: 'tests/test-paths.js', instrument: false },
        { pattern: 'tests/test-utils.js', instrument: false },

        // Source files - all version folders
        { pattern: 'v0.1.0/**/*.js', load: false },
        { pattern: 'v0.1.1/**/*.js', load: false },
        { pattern: 'v0.1.2/**/*.js', load: false },
        { pattern: 'v0.1.3/**/*.js', load: false },
        { pattern: 'v0.1.4/**/*.js', load: false },

        { pattern: '!v0.1.0/js/dashboard.js'            },
        { pattern: '!v0.1.1/components/graph-canvas/**' },      // overridden by v0.1.4
        { pattern: '!v0.1.1/js/playground.js'           },      // overridden by v0.1.4
        { pattern: '!v0.1.1/components/stats-panel/**'  },      // if not tested
        { pattern: '!v0.1.1/components/top-nav/**'      },      // if not tested
        { pattern: '!v0.1.2/js/playground.js'           },
        { pattern: '!v0.1.3/js/playground.js'           },

        // CSS files
        { pattern: 'v0.1.0/**/*.css', load: false },
        { pattern: 'v0.1.1/**/*.css', load: false },
        { pattern: 'v0.1.2/**/*.css', load: false },
        { pattern: 'v0.1.3/**/*.css', load: false },
        { pattern: 'v0.1.4/**/*.css', load: false },

        // HTML samples
        { pattern: 'v0.1.0/samples/*.html', load: false },
    ],

    tests: [
      'tests/**/*.test.js',
    ],

    testFramework: 'qunit',

    env: {
      kind: 'chrome',
    },

    // Proxy /console/v0/v0.1/* to local files
    proxies: {
      '/console/v0/v0.1/': wallaby.projectCacheDir + '/',
    },

    // Alternative: use middleware if proxies doesn't work
    middleware: function (app, express) {
      app.use('/console/v0/v0.1', express.static(wallaby.projectCacheDir));
    },

    setup: function () {
      // Ensure QUnit fixture exists
      if (!document.getElementById('qunit-fixture')) {
        const fixture = document.createElement('div');
        fixture.id = 'qunit-fixture';
        document.body.appendChild(fixture);
      }
    },
  };
};