/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Test Suite - Top Nav Tests
   v0.2.0 - New tests to improve coverage
   ═══════════════════════════════════════════════════════════════════════════════ */

QUnit.module('Top Nav', function(hooks) {

    hooks.before(async function(assert) {
        await TestUtils.loadCss(TestPaths.commonCss);
        await TestUtils.loadScript(TestPaths.topNav);
        //await TestUtils.loadScript(TestPaths.statsToolbar);
        assert.ok(customElements.get('top-nav'), 'top-nav should be registered');
    });

    hooks.afterEach(function() {
        TestUtils.cleanup();
    });

    QUnit.test('component renders correctly', async function(assert) {
        const toolbar = await TestUtils.createComponent('stats-toolbar');
        const nav = await TestUtils.createComponent('top-nav');
        assert.ok(nav.querySelector('.top-nav'), 'should have top-nav container');
        assert.ok(nav.querySelector('.top-nav-brand'), 'should have brand element');
        assert.ok(nav.querySelector('.top-nav-links'), 'should have links container');
    });

    QUnit.test('brand link points to index', async function(assert) {
        const nav = await TestUtils.createComponent('top-nav');

        const brandLink = nav.querySelector('.top-nav-brand');
        assert.ok(brandLink, 'brand link should exist');
        assert.ok(brandLink.getAttribute('href').includes('index.html'), 'brand should link to index.html');
    });

    QUnit.test('brand has icon', async function(assert) {
        const nav = await TestUtils.createComponent('top-nav');

        const icon = nav.querySelector('.top-nav-brand-icon');
        assert.ok(icon, 'brand icon should exist');
        assert.ok(icon.textContent.includes('🔗'), 'should have link emoji icon');
    });

    QUnit.test('brand has text', async function(assert) {
        const nav = await TestUtils.createComponent('top-nav');

        const brand = nav.querySelector('.top-nav-brand');
        assert.ok(brand.textContent.includes('HTML Graph'), 'brand should contain "HTML Graph" text');
    });

    QUnit.test('has Dashboard link', async function(assert) {
        const nav = await TestUtils.createComponent('top-nav');

        const links = nav.querySelectorAll('.top-nav-link');
        const dashboardLink = Array.from(links).find(link => link.textContent.includes('Dashboard'));

        assert.ok(dashboardLink, 'should have Dashboard link');
        assert.ok(dashboardLink.getAttribute('href').includes('index.html'), 'Dashboard should link to index.html');
    });

    QUnit.test('has Playground link', async function(assert) {
        const nav = await TestUtils.createComponent('top-nav');

        const links = nav.querySelectorAll('.top-nav-link');
        const playgroundLink = Array.from(links).find(link => link.textContent.includes('Playground'));

        assert.ok(playgroundLink, 'should have Playground link');
        assert.ok(playgroundLink.getAttribute('href').includes('playground.html'), 'Playground should link to playground.html');
    });

    QUnit.test('has API Docs link', async function(assert) {
        const nav = await TestUtils.createComponent('top-nav');

        const links = nav.querySelectorAll('.top-nav-link');
        const docsLink = Array.from(links).find(link => link.textContent.includes('API Docs'));

        assert.ok(docsLink, 'should have API Docs link');
        assert.ok(docsLink.getAttribute('href').includes('/docs'), 'API Docs should link to /docs');
    });

    QUnit.test('API Docs link opens in new tab', async function(assert) {
        const nav = await TestUtils.createComponent('top-nav');

        const links = nav.querySelectorAll('.top-nav-link');
        const docsLink = Array.from(links).find(link => link.textContent.includes('API Docs'));

        assert.strictEqual(docsLink.getAttribute('target'), '_blank', 'API Docs should open in new tab');
    });

    QUnit.test('Playground link has active class', async function(assert) {
        const nav = await TestUtils.createComponent('top-nav');

        const links = nav.querySelectorAll('.top-nav-link');
        const playgroundLink = Array.from(links).find(link => link.textContent.includes('Playground'));

        assert.ok(playgroundLink.classList.contains('active'), 'Playground should have active class');
    });

    QUnit.test('has correct number of nav links', async function(assert) {
        const nav = await TestUtils.createComponent('top-nav');

        const links = nav.querySelectorAll('.top-nav-link');
        assert.strictEqual(links.length, 3, 'should have 3 nav links');
    });

    QUnit.test('nav element is present', async function(assert) {
        const nav = await TestUtils.createComponent('top-nav');

        const navElement = nav.querySelector('nav');
        assert.ok(navElement, 'should contain a nav element');
    });

    QUnit.test('component has inline styles', async function(assert) {
        const nav = await TestUtils.createComponent('top-nav');

        const style = nav.querySelector('style');
        assert.ok(style, 'should have inline style element');
    });

    QUnit.test('style contains top-nav class definitions', async function(assert) {
        const nav = await TestUtils.createComponent('top-nav');

        const style = nav.querySelector('style');
        assert.ok(style.textContent.includes('.top-nav'), 'style should define .top-nav class');
        assert.ok(style.textContent.includes('.top-nav-brand'), 'style should define .top-nav-brand class');
        assert.ok(style.textContent.includes('.top-nav-link'), 'style should define .top-nav-link class');
    });

    QUnit.test('brand link is an anchor element', async function(assert) {
        const nav = await TestUtils.createComponent('top-nav');

        const brand = nav.querySelector('.top-nav-brand');
        assert.strictEqual(brand.tagName.toLowerCase(), 'a', 'brand should be an anchor element');
    });

    QUnit.test('all nav links are anchor elements', async function(assert) {
        const nav = await TestUtils.createComponent('top-nav');

        const links = nav.querySelectorAll('.top-nav-link');
        links.forEach(link => {
            assert.strictEqual(link.tagName.toLowerCase(), 'a', 'nav link should be an anchor element');
        });
    });
});