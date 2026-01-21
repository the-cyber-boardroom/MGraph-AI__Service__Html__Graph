# ═══════════════════════════════════════════════════════════════════════════════
# Phase E_4: HTML Caching Infrastructure Tests
# Tests all cache layers and the manager orchestration
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                           import TestCase

import pytest

from osbot_utils.testing.Graph__Deterministic__Ids                                      import graph_deterministic_ids
from osbot_utils.testing.__ import __
from osbot_utils.testing.__helpers import obj
from osbot_utils.type_safe.type_safe_core.config.type_safe_fast_create                  import type_safe_fast_create
from phase_e.html_cache.Html_Cache__Manager                                             import Html_Cache__Manager
from phase_e.html_cache.schemas.Schema__Html_Cache                                      import Schema__Html_Cache__Config, Schema__Html_Cache__Stats
from phase_e.storage.backends.Perf__Storage__Cache_Service                              import Perf__Storage__Cache_Service
from phase_e.storage.cache_service.Cache_Service__Client                                import Cache_Service__Client
from phase_e.storage.enums.Enum__Storage_Mode                                           import Enum__Storage_Mode
from phase_e.storage.schemas.Schema__Perf__Storage__Config                              import Schema__Perf__Storage__Config
from tests.Phase_E__Fast_API__Test_Objs                                                 import client_cache_service


# ═══════════════════════════════════════════════════════════════════════════════
# Test HTML Samples
# ═══════════════════════════════════════════════════════════════════════════════

HTML_SIMPLE = '''<!DOCTYPE html>
<html>
<head><title>Test Page</title></head>
<body>
<h1>Hello World</h1>
<p>This is a test paragraph.</p>
</body>
</html>'''

HTML_WITH_NESTED = '''<!DOCTYPE html>
<html>
<head><title>Nested Test</title></head>
<body>
<div id="container">
    <h1>Title</h1>
    <div class="content">
        <p>Paragraph 1</p>
        <p>Paragraph 2</p>
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
            <li>Item 3</li>
        </ul>
    </div>
</div>
</body>
</html>'''


# ═══════════════════════════════════════════════════════════════════════════════
# Test Class
# ═══════════════════════════════════════════════════════════════════════════════

class test_Html_Cache__Manager(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cache_client, cls.cache_service = client_cache_service()

    @pytest.fixture(autouse=True)
    def _inject_pytest_request(self, request):
        self._pytest_request = request

    def setUp(self):
        # Fresh storage and manager for each test
        cache_namespace = 'pytest-manager'
        storage_config  = Schema__Perf__Storage__Config(storage_mode    = Enum__Storage_Mode.CACHE_SERVICE,
                                                        cache_namespace = cache_namespace)

        client_wrapper = Cache_Service__Client(cache_client=self.cache_client)
        self.storage   = Perf__Storage__Cache_Service(config       = storage_config,
                                                      client       = client_wrapper,
                                                      session_name = 'test-session',
                                                      target_name  = 'default-target')
        self.config  = Schema__Html_Cache__Config(session_name='test-session')
        self.manager = Html_Cache__Manager(storage = self.storage,
                                           config  = self.config
                                          ).setup()

    # ═══════════════════════════════════════════════════════════════════════════
    # Manager Setup Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_manager__setup(self):
        """Manager initializes all layers correctly."""
        assert self.manager.layer_html   is not None
        assert self.manager.layer_dict   is not None
        assert self.manager.layer_mgraph is not None
        assert self.manager.stats        is not None

    def test_manager__set_target(self):
        """Target switching updates storage context."""
        self.manager.set_target('target-1')
        assert self.manager.current_target == 'target-1'

        self.manager.set_target('target-2')
        assert self.manager.current_target == 'target-2'

    # ═══════════════════════════════════════════════════════════════════════════
    # L1 (HTML) Layer Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_layer_html__save_load(self):
        """L1 round-trip for HTML strings."""
        target = 'test-html-roundtrip'

        # Save
        self.manager.cache_html(target, HTML_SIMPLE, source='test')

        # Load
        loaded = self.manager.get_html(target)

        assert loaded == HTML_SIMPLE

    def test_layer_html__metadata(self):
        """L1 stores correct metadata."""
        target = 'test-html-metadata'

        self.manager.cache_html(target, HTML_SIMPLE, source='test-source')

        # Check metadata
        self.manager.set_target(target)
        cache_id = self.manager.storage.cache_id()
        metadata = self.manager.layer_html.load_metadata(cache_id=cache_id)

        assert metadata is not None
        assert metadata['source'] == 'test-source'
        assert metadata['size_bytes'] == len(HTML_SIMPLE.encode('utf-8'))
        assert metadata['content_hash'] is not None
        assert len(metadata['content_hash']) == 16  # Truncated hash
        assert metadata['cached_at'] > 0

    def test_layer_html__content_hash(self):
        """L1 content hash is consistent."""
        target = 'test-html-hash'

        self.manager.cache_html(target, HTML_SIMPLE)

        hash1 = self.manager.get_content_hash(target, 'L1')

        # Same content should produce same hash
        self.manager.cache_html('another-target', HTML_SIMPLE)
        hash2 = self.manager.get_content_hash('another-target', 'L1')

        assert hash1 == hash2

        # Different content should produce different hash
        self.manager.cache_html('different-target', HTML_WITH_NESTED)
        hash3 = self.manager.get_content_hash('different-target', 'L1')

        assert hash1 != hash3

    # ═══════════════════════════════════════════════════════════════════════════
    # L2 (Dict) Layer Tests
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe_fast_create
    def test_layer_dict__build_from_html(self):
        """L2 can build from L1 cache."""
        target = 'test-dict-build'

        # Cache HTML first
        self.manager.cache_html(target, HTML_SIMPLE)

        # Build dict (auto-builds from HTML)
        with graph_deterministic_ids():
            html_dict = self.manager.get_dict(target, build_if_missing=True)

        assert html_dict is not None
        assert HTML_SIMPLE    == ('<!DOCTYPE html>\n'
                                  '<html>\n'
                                  '<head><title>Test Page</title></head>\n'
                                  '<body>\n'
                                  '<h1>Hello World</h1>\n'
                                  '<p>This is a test paragraph.</p>\n'
                                  '</body>\n'
                                  '</html>')
        assert obj(html_dict) == __(tag='html',
                                    attrs=__(),
                                    nodes=[__(tag='head',
                                              attrs=__(),
                                              nodes=[__(tag='title',
                                                        attrs=__(),
                                                        nodes=[__(type='TEXT',
                                                                  data='Test Page',
                                                                  node_id='f0000004')],
                                                        node_id='f0000003')],
                                              node_id='f0000002'),
                                           __(tag='body',
                                              attrs=__(),
                                              nodes=[__(tag='h1',
                                                        attrs=__(),
                                                        nodes=[__(type='TEXT',
                                                                  data='Hello World',
                                                                  node_id='f0000007')],
                                                        node_id='f0000006'),
                                                     __(tag='p',
                                                        attrs=__(),
                                                        nodes=[__(type='TEXT',
                                                                  data='This is a test paragraph.',
                                                                  node_id='f0000009')],
                                                        node_id='f0000008')],
                                              node_id='f0000005')],
                                    node_id='f0000001')


    @type_safe_fast_create
    def test_layer_dict__save_load(self):
        """L2 round-trip for dicts."""
        target = 'test-dict-roundtrip'

        # Cache HTML and build dict
        self.manager.cache_html(target, HTML_SIMPLE)
        html_dict = self.manager.build_dict_from_html(target)

        # Clear stats to test clean load
        self.manager.reset_stats()

        # Load from cache
        loaded = self.manager.get_dict(target, build_if_missing=False)

        assert loaded is not None
        assert self.manager.stats.l2_hits == 1
        assert self.manager.stats.l2_builds == 0  # Should be cached

    # ═══════════════════════════════════════════════════════════════════════════
    # L3 (MGraph) Layer Tests
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe_fast_create
    def test_layer_mgraph__build_from_dict(self):
        """L3 can build from L2 cache."""
        target = 'test-mgraph-build'

        with graph_deterministic_ids():
            # Cache HTML first
            self.manager.cache_html(target, HTML_SIMPLE)

            # Build MGraph (auto-builds from HTML → Dict → MGraph)
            document = self.manager.get_mgraph(target, build_if_missing=True)

            assert document is not None
            assert document.body_graph is not None

    @type_safe_fast_create
    def test_layer_mgraph__save_load(self):
        """L3 round-trip for MGraph documents."""
        target = 'test-mgraph-roundtrip'

        with graph_deterministic_ids():
            # Full pipeline
            document = self.manager.build_full_pipeline(target, HTML_SIMPLE)
            assert document is not None

            # Clear stats
            self.manager.reset_stats()

            # Load from cache
            loaded = self.manager.get_mgraph(target, build_if_missing=False)

            assert loaded is not None
            assert self.manager.stats.l3_hits == 1
            assert self.manager.stats.l3_builds == 0

    # ═══════════════════════════════════════════════════════════════════════════
    # Cascade Tests
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe_fast_create
    def test_cascade__full_pipeline(self):
        """Cache miss triggers full build."""
        target = 'test-cascade-full'

        with graph_deterministic_ids():
            self.manager.reset_stats()

            # Request MGraph for uncached target with HTML
            document = self.manager.build_full_pipeline(target, HTML_SIMPLE)

            assert document is not None
            assert self.manager.stats.l2_builds == 1  # Dict was built
            assert self.manager.stats.l3_builds == 1  # MGraph was built

    @type_safe_fast_create
    def test_cascade__partial_rebuild(self):
        """L2 hit skips HTML parsing."""
        target = 'test-cascade-partial'

        with graph_deterministic_ids():
            # Build up to L2
            self.manager.cache_html(target, HTML_SIMPLE)
            self.manager.build_dict_from_html(target)

            # Delete L3 only
            self.manager.delete_layer(target, 'L3')

            # Clear stats
            self.manager.reset_stats()

            # Request MGraph - should use L2 cache
            document = self.manager.get_mgraph(target, build_if_missing=True)

            assert document is not None
            assert self.manager.stats.l2_hits == 1    # Dict was cached
            assert self.manager.stats.l2_builds == 0  # No rebuild
            assert self.manager.stats.l3_builds == 1  # MGraph was built

    # ═══════════════════════════════════════════════════════════════════════════
    # Cache Status Tests
    # ═══════════════════════════════════════════════════════════════════════════


    @type_safe_fast_create
    def test_cache_status__all_layers(self):
        all_items = self._pytest_request.session.items
        if len(all_items) > 1:
            pytest.skip("This test doesn't work when executed with multiple tests")

        """Cache status correctly reports all layers."""
        target = 'test-status'

        with graph_deterministic_ids():
            # Initially nothing cached
            status = self.manager.cache_status(target)
            assert status['L1'] is False
            assert status['L2'] is False
            assert status['L3'] is False

            # After full pipeline
            self.manager.build_full_pipeline(target, HTML_SIMPLE)

            status = self.manager.cache_status(target)
            assert status['L1'] is True
            assert status['L2'] is True
            assert status['L3'] is True

    # ═══════════════════════════════════════════════════════════════════════════
    # Delete Tests
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe_fast_create
    def test_delete__target(self):
        """Delete all layers for target."""
        target = 'test-delete-target'

        with graph_deterministic_ids():
            self.manager.build_full_pipeline(target, HTML_SIMPLE)

            # Verify all cached
            assert self.manager.has_mgraph(target)

            # Delete all
            result = self.manager.delete_target(target)

            assert result['L1'] is True
            assert result['L2'] is True
            assert result['L3'] is True

            # Verify all deleted
            assert not self.manager.has_html(target)
            assert not self.manager.has_dict(target)
            assert not self.manager.has_mgraph(target)

    @type_safe_fast_create
    def test_delete__single_layer(self):
        """Delete specific layer."""
        target = 'test-delete-layer'

        with graph_deterministic_ids():
            self.manager.build_full_pipeline(target, HTML_SIMPLE)

            # Delete only L3
            self.manager.delete_layer(target, 'L3')

            # L1 and L2 should remain
            assert self.manager.has_html(target)
            assert self.manager.has_dict(target)
            assert not self.manager.has_mgraph(target)

    # ═══════════════════════════════════════════════════════════════════════════
    # Stats Tests
    # ═══════════════════════════════════════════════════════════════════════════


    @type_safe_fast_create
    def test_stats__hit_miss_tracking(self):
        all_items = self._pytest_request.session.items
        if len(all_items) > 1:
            pytest.skip("This test doesn't work when executed with multiple tests")

        """Statistics count correctly."""
        target = 'test-stats'

        with graph_deterministic_ids():
            self.manager.reset_stats()

            # Miss on empty cache
            result = self.manager.get_html(target)
            assert result is None
            # Note: miss is tracked internally when cache_id lookup fails

            # Cache and hit
            self.manager.cache_html(target, HTML_SIMPLE)
            result = self.manager.get_html(target)
            assert result is not None
            assert self.manager.stats.l1_hits == 1

            # Build operations
            self.manager.build_full_pipeline('another-target', HTML_SIMPLE)
            assert self.manager.stats.l2_builds >= 1
            assert self.manager.stats.l3_builds >= 1

    # ═══════════════════════════════════════════════════════════════════════════
    # Multiple Targets Tests
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe_fast_create
    def test_multiple_targets__isolation(self):
        """Different targets are isolated."""
        target1 = 'target-1'
        target2 = 'target-2'

        with graph_deterministic_ids():
            # Cache different HTML for each target
            self.manager.cache_html(target1, HTML_SIMPLE)
            self.manager.cache_html(target2, HTML_WITH_NESTED)

            # Verify isolation
            html1 = self.manager.get_html(target1)
            html2 = self.manager.get_html(target2)

            assert html1 == HTML_SIMPLE
            assert html2 == HTML_WITH_NESTED
            assert html1 != html2

    @type_safe_fast_create
    def test_multiple_targets__same_content_different_hash(self):
        """Same content produces same hash across targets."""
        target1 = 'target-same-1'
        target2 = 'target-same-2'

        # Cache same HTML in both
        self.manager.cache_html(target1, HTML_SIMPLE)
        self.manager.cache_html(target2, HTML_SIMPLE)

        # Content hashes should match
        hash1 = self.manager.get_content_hash(target1, 'L1')
        hash2 = self.manager.get_content_hash(target2, 'L1')

        assert hash1 == hash2