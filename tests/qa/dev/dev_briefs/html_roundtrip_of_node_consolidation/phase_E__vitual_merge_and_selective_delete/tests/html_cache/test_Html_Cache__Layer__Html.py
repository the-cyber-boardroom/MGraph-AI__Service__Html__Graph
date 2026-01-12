# ═══════════════════════════════════════════════════════════════════════════════
# Test: Html_Cache__Layer__Html (L1)
# Tests the raw HTML caching layer
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                           import TestCase
from osbot_utils.type_safe.Type_Safe                                                    import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                      import Cache_Id
from osbot_utils.utils.Objects                                                          import base_classes
from phase_e.html_cache.Html_Cache__Layer__Base                                         import Html_Cache__Layer__Base
from phase_e.html_cache.Html_Cache__Layer__Html                                         import Html_Cache__Layer__Html
from phase_e.html_cache.schemas.Schema__Html_Cache                                      import Schema__Html_Cache__Config, Schema__Html_Cache__Stats
from phase_e.storage.backends.Perf__Storage__Cache_Service                              import Perf__Storage__Cache_Service
from phase_e.storage.base.Perf__Storage__Base                                           import Perf__Storage__Base
from phase_e.storage.cache_service.Cache_Service__Client                                import Cache_Service__Client
from phase_e.storage.enums.Enum__Storage_Mode                                           import Enum__Storage_Mode
from phase_e.storage.schemas.Schema__Perf__Storage__Config                              import Schema__Perf__Storage__Config
from tests.Phase_E__Fast_API__Test_Objs                                                 import client_cache_service


# ═══════════════════════════════════════════════════════════════════════════════
# Test Data
# ═══════════════════════════════════════════════════════════════════════════════

HTML_SIMPLE = '''<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body><h1>Hello</h1></body>
</html>'''

HTML_WITH_UNICODE = '''<!DOCTYPE html>
<html>
<head><title>日本語</title></head>
<body><p>こんにちは世界</p></body>
</html>'''

HTML_LARGE = '<html><body>' + '<p>Paragraph</p>' * 1000 + '</body></html>'


class test_Html_Cache__Layer__Html(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.session_name    = 'test-html-cache'
        cls.target_name     = 'layer-html'
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
        cls.layer    = Html_Cache__Layer__Html(storage = cls.storage,
                                               stats   = cls.stats  )
        cls.cache_id = cls.storage.create_file__perf_entry()

    def setUp(self):
        # Reset stats for each test
        self.stats.l1_hits   = 0
        self.stats.l1_misses = 0

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                     # Test L1 layer initialization
        with Html_Cache__Layer__Html() as _:
            assert type(_)         is Html_Cache__Layer__Html
            assert base_classes(_) == [Html_Cache__Layer__Base, Type_Safe, object]
            assert _.layer_name    == 'L1'                      # Fixed layer name
            assert type(_.storage) is Perf__Storage__Base

    def test__init____with_storage(self):                       # Test initialization with storage
        with self.layer as _:
            assert type(_.storage) is Perf__Storage__Cache_Service
            assert _.layer_name    == 'L1'

    # ═══════════════════════════════════════════════════════════════════════════
    # Key Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_key_data(self):                                    # L1 uses raw-html
        assert self.layer.key_data() == 'L1/raw-html'

    def test_key_metadata(self):                                # Metadata key from base class
        assert self.layer.key_metadata() == 'L1/metadata'

    # ═══════════════════════════════════════════════════════════════════════════
    # Save Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_save(self):                                        # Test basic save
        with self.layer as _:
            data_folder = _.data_folder()
            data_file   = _.data_file()
            assert data_folder == 'pytest/data/key-based/sessions/test-html-cache/targets/layer-html/perf-entry/data'
            assert data_file   == f'{data_folder}/L1/raw-html.txt'
            result = _.save(cache_id = self.cache_id,
                            html     = HTML_SIMPLE)

            assert result         is True
            assert data_file      in _.storage.namespace__all_files()
            assert _.exists()     is True

    def test_save__with_source(self):                           # Test save with source identifier
        result = self.layer.save(cache_id = self.cache_id,
                                 html     = HTML_SIMPLE,
                                 source   = 'https://example.com')

        assert result is True

        metadata = self.layer.load_metadata(cache_id=self.cache_id)
        assert metadata['source'] == 'https://example.com'

    def test_save__default_source(self):                        # Test default source is 'unknown'
        self.layer.save(cache_id = self.cache_id,
                        html     = HTML_SIMPLE)

        metadata = self.layer.load_metadata(cache_id=self.cache_id)
        assert metadata['source'] == 'unknown'

    def test_save__metadata_content_hash(self):                 # Test content hash in metadata
        self.layer.save(cache_id = self.cache_id,
                        html     = HTML_SIMPLE)

        metadata = self.layer.load_metadata(cache_id=self.cache_id)
        assert 'content_hash' in metadata
        assert len(metadata['content_hash']) == 16

    def test_save__metadata_size_bytes(self):                   # Test size tracking
        self.layer.save(cache_id = self.cache_id,
                        html     = HTML_SIMPLE)

        metadata   = self.layer.load_metadata(cache_id=self.cache_id)
        expected   = len(HTML_SIMPLE.encode('utf-8'))

        assert metadata['size_bytes'] == expected

    def test_save__metadata_cached_at(self):                    # Test timestamp tracking
        self.layer.save(cache_id = self.cache_id,
                        html     = HTML_SIMPLE)

        metadata = self.layer.load_metadata(cache_id=self.cache_id)
        assert 'cached_at' in metadata
        assert metadata['cached_at'] > 0

    def test_save__unicode(self):                               # Test Unicode HTML saves correctly
        result = self.layer.save(cache_id = self.cache_id,
                                 html     = HTML_WITH_UNICODE)

        assert result is True

        loaded = self.layer.load(cache_id=self.cache_id)
        assert loaded == HTML_WITH_UNICODE

    def test_save__large_content(self):                         # Test large HTML saves correctly
        result = self.layer.save(cache_id = self.cache_id,
                                 html     = HTML_LARGE)

        assert result is True

        metadata = self.layer.load_metadata(cache_id=self.cache_id)
        assert metadata['size_bytes'] == len(HTML_LARGE.encode('utf-8'))

    def test_save__empty_string(self):                          # Test empty HTML saves
        self.layer.delete(cache_id = self.cache_id)
        result = self.layer.save(cache_id = self.cache_id,
                                 html     = '')                 # this has no effect (i.e. empty data is not acted on)

        assert result is True

        loaded = self.layer.load(cache_id=self.cache_id)
        assert loaded == ''

    # ═══════════════════════════════════════════════════════════════════════════
    # Load Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_load(self):                                        # Test basic load
        self.layer.save(cache_id = self.cache_id,
                        html     = HTML_SIMPLE)

        loaded = self.layer.load(cache_id=self.cache_id)

        assert loaded == HTML_SIMPLE

    def test_load__not_found(self):                             # Returns None when not found
        fake_cache_id = Cache_Id()
        loaded = self.layer.load(cache_id=fake_cache_id)

        assert loaded is None

    def test_load__tracks_hit(self):                            # Load success increments hit counter
        self.layer.save(cache_id = self.cache_id,
                        html     = HTML_SIMPLE)
        self.stats.l1_hits = 0                                  # Reset

        self.layer.load(cache_id=self.cache_id)

        assert self.stats.l1_hits == 1

    def test_load__tracks_miss(self):                           # Load failure increments miss counter
        self.stats.l1_misses = 0                                # Reset
        fake_cache_id = Cache_Id()

        self.layer.load(cache_id=fake_cache_id)

        assert self.stats.l1_misses == 1

    def test_load__roundtrip(self):                             # Save then load preserves content
        self.layer.save(cache_id = self.cache_id,
                        html     = HTML_SIMPLE)
        loaded = self.layer.load(cache_id=self.cache_id)

        assert loaded == HTML_SIMPLE

    def test_load__roundtrip_unicode(self):                     # Unicode roundtrip works
        self.layer.save(cache_id = self.cache_id,
                        html     = HTML_WITH_UNICODE)
        loaded = self.layer.load(cache_id=self.cache_id)

        assert loaded == HTML_WITH_UNICODE

    # ═══════════════════════════════════════════════════════════════════════════
    # Content Hash Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_content_hash(self):                            # Test get_content_hash method
        self.layer.save(cache_id = self.cache_id,
                        html     = HTML_SIMPLE)

        hash_value = self.layer.get_content_hash(cache_id=self.cache_id)

        assert hash_value is not None
        assert len(hash_value) == 16

    def test_get_content_hash__not_found(self):                 # Returns None when no metadata
        fake_cache_id = Cache_Id()
        hash_value = self.layer.get_content_hash(cache_id=fake_cache_id)

        assert hash_value is None

    def test_get_content_hash__consistency(self):               # Same content gives same hash
        self.layer.save(cache_id = self.cache_id,
                        html     = HTML_SIMPLE)
        hash_1 = self.layer.get_content_hash(cache_id=self.cache_id)

        # Save same content again
        self.layer.save(cache_id = self.cache_id,
                        html     = HTML_SIMPLE)
        hash_2 = self.layer.get_content_hash(cache_id=self.cache_id)

        assert hash_1 == hash_2

    def test_get_content_hash__different_content(self):         # Different content gives different hash
        self.layer.save(cache_id = self.cache_id,
                        html     = HTML_SIMPLE)
        hash_1 = self.layer.get_content_hash(cache_id=self.cache_id)

        self.layer.save(cache_id = self.cache_id,
                        html     = HTML_WITH_UNICODE)
        hash_2 = self.layer.get_content_hash(cache_id=self.cache_id)

        assert hash_1 != hash_2

    # ═══════════════════════════════════════════════════════════════════════════
    # Overwrite Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_save__overwrite(self):                             # Overwriting content works
        self.layer.save(cache_id = self.cache_id,
                        html     = HTML_SIMPLE,
                        source   = 'source-1')
        self.layer.save(cache_id = self.cache_id,
                        html     = HTML_WITH_UNICODE,
                        source   = 'source-2')

        loaded   = self.layer.load(cache_id=self.cache_id)
        metadata = self.layer.load_metadata(cache_id=self.cache_id)

        assert loaded == HTML_WITH_UNICODE
        assert metadata['source'] == 'source-2'

    # ═══════════════════════════════════════════════════════════════════════════
    # Delete Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_delete(self):                                      # Delete removes HTML and metadata
        self.layer.save(cache_id = self.cache_id,
                        html     = HTML_SIMPLE)
        assert self.layer.exists() is True

        assert self.layer.delete(cache_id=self.cache_id) is True
        assert self.layer.delete(cache_id=self.cache_id) is False
        assert self.layer.exists()                       is False
        assert self.layer.load(cache_id=self.cache_id) == ''