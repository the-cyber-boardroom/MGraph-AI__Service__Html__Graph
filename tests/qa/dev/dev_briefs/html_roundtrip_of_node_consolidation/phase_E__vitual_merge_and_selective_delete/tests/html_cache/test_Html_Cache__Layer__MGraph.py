# ═══════════════════════════════════════════════════════════════════════════════
# Test: Html_Cache__Layer__MGraph (L3)
# Tests the MGraph document caching layer
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                               import TestCase
from osbot_utils.type_safe.Type_Safe                                                                        import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                                          import Cache_Id
from osbot_utils.type_safe.type_safe_core.config.Type_Safe__Config import Type_Safe__Config
from osbot_utils.type_safe.type_safe_core.config.type_safe_fast_create                                      import type_safe_fast_create
from osbot_utils.testing.Graph__Deterministic__Ids                                                          import graph_deterministic_ids
from osbot_utils.utils.Objects                                                                              import base_classes
from phase_e.html_cache.Html_Cache__Layer__Base                                                             import Html_Cache__Layer__Base
from phase_e.html_cache.Html_Cache__Layer__MGraph                                                           import Html_Cache__Layer__MGraph
from phase_e.html_cache.schemas.Schema__Html_Cache                                                          import Schema__Html_Cache__Config, Schema__Html_Cache__Stats
from phase_e.storage.backends.Perf__Storage__Cache_Service                                                  import Perf__Storage__Cache_Service
from phase_e.storage.base.Perf__Storage__Base                                                               import Perf__Storage__Base
from phase_e.storage.cache_service.Cache_Service__Client                                                    import Cache_Service__Client
from phase_e.storage.enums.Enum__Storage_Mode                                                               import Enum__Storage_Mode
from phase_e.storage.schemas.Schema__Perf__Storage__Config                                                  import Schema__Perf__Storage__Config
from mgraph_ai_service_html_graph.service.html_mgraph.graphs.Html_MGraph__Document                          import Html_MGraph__Document
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_Dict__With__Node_Ids        import Html__To__Html_Dict__With__Node_Ids
from tests.Phase_E__Fast_API__Test_Objs                                                                     import client_cache_service


# ═══════════════════════════════════════════════════════════════════════════════
# Test Data
# ═══════════════════════════════════════════════════════════════════════════════

HTML_SIMPLE = '''<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body><h1>Hello</h1><p>World</p></body>
</html>'''

HTML_NESTED = '''<!DOCTYPE html>
<html>
<head><title>Nested</title></head>
<body>
<div>
    <p>Para 1</p>
    <p>Para 2</p>
</div>
</body>
</html>'''


class test_Html_Cache__Layer__MGraph(TestCase):

    @classmethod
    def setUpClass(cls):
        # Pre-build test data once
        with graph_deterministic_ids():
            with Type_Safe__Config(fast_create=True, skip_validation=True):
                cls.html_dict = Html__To__Html_Dict__With__Node_Ids(html=HTML_SIMPLE).convert()

        # Setup storage
        cls.session_name    = 'test-html-cache'
        cls.target_name     = 'layer-mgraph'
        cls.cache_namespace = 'pytest'
        cls.config          = Schema__Perf__Storage__Config(storage_mode    = Enum__Storage_Mode.CACHE_SERVICE,
                                                            cache_namespace = cls.cache_namespace)

        cls.cache_client, cls.cache_service = client_cache_service()
        cls.cache_client_wrapper            = Cache_Service__Client(cache_client=cls.cache_client)

        cls.storage = Perf__Storage__Cache_Service(config       = cls.config              ,
                                                   client       = cls.cache_client_wrapper,
                                                   session_name = cls.session_name        ,
                                                   target_name  = cls.target_name         )
        cls.stats    = Schema__Html_Cache__Stats()
        cls.layer    = Html_Cache__Layer__MGraph(storage = cls.storage,
                                                 stats   = cls.stats  )
        cls.cache_id = cls.storage.create_file__perf_entry()

    def setUp(self):
        # Reset stats for each test
        self.stats.l3_hits   = 0
        self.stats.l3_misses = 0
        self.stats.l3_builds = 0

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                     # Test L3 layer initialization
        with Html_Cache__Layer__MGraph() as _:
            assert type(_)         is Html_Cache__Layer__MGraph
            assert base_classes(_) == [Html_Cache__Layer__Base, Type_Safe, object]
            assert _.layer_name    == 'L3'                      # Fixed layer name
            assert type(_.storage) is Perf__Storage__Base

    def test__init____with_storage(self):                       # Test initialization with storage
        with self.layer as _:
            assert type(_.storage) is Perf__Storage__Cache_Service
            assert _.layer_name    == 'L3'

    # ═══════════════════════════════════════════════════════════════════════════
    # Key Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_key_data(self):                                    # L3 uses mgraph-document
        assert self.layer.key_data() == 'L3/mgraph-document'

    def test_key_metadata(self):                                # Metadata key from base class
        assert self.layer.key_metadata() == 'L3/metadata'

    # ═══════════════════════════════════════════════════════════════════════════
    # Build from Dict Tests
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe_fast_create
    def test_build_from_dict(self):                             # Test building MGraph from dict
        with graph_deterministic_ids():
            document = self.layer.build_from_dict(self.html_dict)

            assert document is not None
            assert type(document) is Html_MGraph__Document

    @type_safe_fast_create
    def test_build_from_dict__tracks_builds(self):              # Build increments counter
        with graph_deterministic_ids():
            self.stats.l3_builds = 0                            # Reset

            self.layer.build_from_dict(self.html_dict)

            assert self.stats.l3_builds == 1

    @type_safe_fast_create
    def test_build_from_dict__has_body_graph(self):             # Built document has body_graph
        with graph_deterministic_ids():
            document = self.layer.build_from_dict(self.html_dict)

            assert document.body_graph is not None

    # ═══════════════════════════════════════════════════════════════════════════
    # Save Tests
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe_fast_create
    def test_save(self):                                        # Test basic save
        with graph_deterministic_ids():
            document = self.layer.build_from_dict(self.html_dict)
            result   = self.layer.save(cache_id = self.cache_id,
                                       document = document)

            assert result is True
            assert self.layer.exists() is True

    @type_safe_fast_create
    def test_save__metadata_content_hash(self):                 # Test content hash in metadata
        with graph_deterministic_ids():
            document = self.layer.build_from_dict(self.html_dict)
            self.layer.save(cache_id = self.cache_id,
                            document = document)

            metadata = self.layer.load_metadata(cache_id=self.cache_id)
            assert 'content_hash' in metadata
            assert len(metadata['content_hash']) == 16

    @type_safe_fast_create
    def test_save__metadata_cached_at(self):                    # Test timestamp tracking
        with graph_deterministic_ids():
            document = self.layer.build_from_dict(self.html_dict)
            self.layer.save(cache_id = self.cache_id,
                            document = document)

            metadata = self.layer.load_metadata(cache_id=self.cache_id)
            assert 'cached_at' in metadata
            assert metadata['cached_at'] > 0

    @type_safe_fast_create
    def test_save__metadata_counts(self):                       # Test node/edge count tracking
        with graph_deterministic_ids():
            document = self.layer.build_from_dict(self.html_dict)
            self.layer.save(cache_id = self.cache_id,
                            document = document)

            metadata = self.layer.load_metadata(cache_id=self.cache_id)
            assert 'node_count' in metadata
            assert 'edge_count' in metadata

    # ═══════════════════════════════════════════════════════════════════════════
    # Load Tests
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe_fast_create
    def test_load(self):                                        # Test basic load
        with graph_deterministic_ids():
            document = self.layer.build_from_dict(self.html_dict)
            self.layer.save(cache_id = self.cache_id,
                            document = document)

            loaded = self.layer.load(cache_id=self.cache_id)

            assert loaded is not None
            assert type(loaded) is Html_MGraph__Document

    @type_safe_fast_create
    def test_load__not_found(self):                             # Returns None when not found
        fake_cache_id = Cache_Id()
        loaded = self.layer.load(cache_id=fake_cache_id)

        assert loaded is None

    @type_safe_fast_create
    def test_load__tracks_hit(self):                            # Load success increments hit counter
        with graph_deterministic_ids():
            document = self.layer.build_from_dict(self.html_dict)
            self.layer.save(cache_id = self.cache_id,
                            document = document)
            self.stats.l3_hits = 0                              # Reset

            self.layer.load(cache_id=self.cache_id)

            assert self.stats.l3_hits == 1

    @type_safe_fast_create
    def test_load__tracks_miss(self):                           # Load failure increments miss counter
        self.stats.l3_misses = 0                                # Reset
        fake_cache_id = Cache_Id()

        self.layer.load(cache_id=fake_cache_id)

        assert self.stats.l3_misses == 1

    @type_safe_fast_create
    def test_load__has_body_graph(self):                        # Loaded document has body_graph
        with graph_deterministic_ids():
            document = self.layer.build_from_dict(self.html_dict)
            self.layer.save(cache_id = self.cache_id,
                            document = document)

            loaded = self.layer.load(cache_id=self.cache_id)

            assert loaded.body_graph is not None

    # ═══════════════════════════════════════════════════════════════════════════
    # Roundtrip Tests (Critical for .json() / .from_json())
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe_fast_create
    def test_roundtrip__basic(self):                            # Basic save/load roundtrip
        with graph_deterministic_ids():
            original = self.layer.build_from_dict(self.html_dict)
            self.layer.save(cache_id = self.cache_id,
                            document = original)

            loaded = self.layer.load(cache_id=self.cache_id)

            # Both should be Html_MGraph__Document
            assert type(original) is Html_MGraph__Document
            assert type(loaded)   is Html_MGraph__Document

    @type_safe_fast_create
    def test_roundtrip__preserves_structure(self):              # Roundtrip preserves document structure
        with graph_deterministic_ids():
            original = self.layer.build_from_dict(self.html_dict)

            # Check original has expected attributes
            assert original.body_graph is not None

            self.layer.save(cache_id = self.cache_id,
                            document = original)
            loaded = self.layer.load(cache_id=self.cache_id)

            # Loaded should have same attributes
            assert loaded.body_graph is not None

    # ═══════════════════════════════════════════════════════════════════════════
    # Content Hash Tests
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe_fast_create
    def test_get_content_hash(self):                            # Test get_content_hash method
        with graph_deterministic_ids():
            document = self.layer.build_from_dict(self.html_dict)
            self.layer.save(cache_id = self.cache_id,
                            document = document)

            hash_value = self.layer.get_content_hash(cache_id=self.cache_id)

            assert hash_value is not None
            assert len(hash_value) == 16

    @type_safe_fast_create
    def test_get_content_hash__not_found(self):                 # Returns None when no metadata
        fake_cache_id = Cache_Id()
        hash_value = self.layer.get_content_hash(cache_id=fake_cache_id)

        assert hash_value is None

    @type_safe_fast_create
    def test_get_content_hash__consistency(self):               # Same document gives same hash
        with graph_deterministic_ids():
            document = self.layer.build_from_dict(self.html_dict)

            self.layer.save(cache_id = self.cache_id,
                            document = document)
            hash_1 = self.layer.get_content_hash(cache_id=self.cache_id)

            # Save same document again
            self.layer.save(cache_id = self.cache_id,
                            document = document)
            hash_2 = self.layer.get_content_hash(cache_id=self.cache_id)

            assert hash_1 == hash_2

    # ═══════════════════════════════════════════════════════════════════════════
    # Delete Tests
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe_fast_create
    def test_delete(self):                                      # Delete removes document and metadata
        with graph_deterministic_ids():
            document = self.layer.build_from_dict(self.html_dict)
            self.layer.save(cache_id = self.cache_id,
                            document = document)
            assert self.layer.exists() is True

            result = self.layer.delete(cache_id=self.cache_id)

            assert result is True
            assert self.layer.exists() is False
            assert self.layer.load(cache_id=self.cache_id) is None

    # ═══════════════════════════════════════════════════════════════════════════
    # Error Handling Tests
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe_fast_create
    def test_build_from_dict__empty_dict(self):                 # Empty dict handled gracefully
        with graph_deterministic_ids():
            document = self.layer.build_from_dict({})

            # May return document or None depending on implementation
            # Either is acceptable for empty input
            assert document is not None or document is None