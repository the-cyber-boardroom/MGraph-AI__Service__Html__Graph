# ═══════════════════════════════════════════════════════════════════════════════
# test_FLeT__Html__To__Cache - Tests for HTML to cache FLeT
# Tests storing HTML in cache with hash-based deduplication
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                                                   import TestCase
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__to__cache.FLeT__Html__To__Cache                        import FLeT__Html__To__Cache
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__to__cache.schemas.Schema__Html_To_Cache__Load__Input   import Schema__Html_To_Cache__Load__Input
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__to__cache.schemas.Schema__Html_To_Cache__Save__Output  import Schema__Html_To_Cache__Save__Output
from osbot_utils.type_safe.Type_Safe                                                                                            import Type_Safe
from osbot_utils.utils.Objects                                                                                                  import base_types
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html                                                       import Safe_Str__Html
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Namespace                                          import Safe_Str__Namespace
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.base.Html_FLeT__Base                                               import Html_FLeT__Base
from tests.unit.Html_Graph__Service__Fast_API__Test_Objs                                                                        import create_html_cache_client


class test_FLeT__Html__To__Cache(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cache_client, cls.cache_service = create_html_cache_client()
        cls.sample_html = '<html><body><p>Test content</p></body></html>'
        cls.namespace   = 'test-html-to-cache'

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):
        with FLeT__Html__To__Cache() as _:
            assert type(_)        is FLeT__Html__To__Cache
            assert base_types(_)  == [Html_FLeT__Base, Type_Safe, object]
            assert _.cache_client is None
            assert _.config       is None

    def test__init____with_cache_client(self):
        with FLeT__Html__To__Cache(cache_client=self.cache_client) as _:
            assert _.cache_client is self.cache_client

    def test__init____actions_wired(self):
        with FLeT__Html__To__Cache() as _:
            assert _.load      is not None
            assert _.extract   is not None
            assert _.transform is not None
            assert _.save      is not None

    # ═══════════════════════════════════════════════════════════════════════════
    # Setup Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_setup(self):
        with FLeT__Html__To__Cache() as _:
            result = _.setup()

            assert result        is _
            assert _.config      is not None
            assert _.config.name == 'html-to-cache'
            assert 'cache'       in _.config.description.lower()

    def test_setup__returns_self(self):
        flet = FLeT__Html__To__Cache().setup()
        assert type(flet)       is FLeT__Html__To__Cache
        assert flet.config.name == 'html-to-cache'

    # ═══════════════════════════════════════════════════════════════════════════
    # Execute Tests (without cache client)
    # ═══════════════════════════════════════════════════════════════════════════

    def test_execute__without_cache_client(self):
        flet       = FLeT__Html__To__Cache().setup()
        input_data = Schema__Html_To_Cache__Load__Input(html      = Safe_Str__Html(self.sample_html)  ,
                                                        namespace = Safe_Str__Namespace(self.namespace))

        result = flet.execute(input_data)

        assert type(result)     is Schema__Html_To_Cache__Save__Output
        assert result.success   is True
        assert result.cache_id  == ''                                                 # No cache client = no ID
        assert result.html_hash == ''                                                 # No hash without client

    # ═══════════════════════════════════════════════════════════════════════════
    # Execute Tests (with cache client)
    # ═══════════════════════════════════════════════════════════════════════════

    def test_execute__with_cache_client(self):
        flet       = FLeT__Html__To__Cache(cache_client=self.cache_client).setup()
        input_data = Schema__Html_To_Cache__Load__Input(html      = Safe_Str__Html(self.sample_html)  ,
                                                        namespace = Safe_Str__Namespace(self.namespace))

        result = flet.execute(input_data)

        assert type(result)        is Schema__Html_To_Cache__Save__Output
        assert result.success      is True
        assert result.html_hash    != ''
        assert result.from_cache   is False                                          # First time = not from cache

    def test__bug__execute__deduplication(self):
        flet       = FLeT__Html__To__Cache(cache_client=self.cache_client).setup()
        input_data = Schema__Html_To_Cache__Load__Input(html      = Safe_Str__Html(self.sample_html)  ,
                                                        namespace = Safe_Str__Namespace(self.namespace))

        result1 = flet.execute(input_data)
        result2 = flet.execute(input_data)                                           # Same HTML again

        assert result1.html_hash  == result2.html_hash                               # Same hash
        assert result2.from_cache is not True               # BUG                               # Second time = from cache

        assert result1.from_cache is False                  # BUG

    def test_execute__with_explicit_cache_key(self):
        flet       = FLeT__Html__To__Cache(cache_client=self.cache_client).setup()
        input_data = Schema__Html_To_Cache__Load__Input(html      = Safe_Str__Html('<p>unique</p>')    ,
                                                        namespace = Safe_Str__Namespace(self.namespace),
                                                        cache_key = 'my-explicit-key'                  )

        result = flet.execute(input_data)

        assert result.success   is True
        assert result.cache_key == 'my-explicit-key'

    def test__bug__execute__with_url_as_key(self):
        flet       = FLeT__Html__To__Cache(cache_client=self.cache_client).setup()
        input_data = Schema__Html_To_Cache__Load__Input(html      = Safe_Str__Html('<p>from url</p>')  ,
                                                        namespace = Safe_Str__Namespace(self.namespace),
                                                        url       = 'https://example.com/page'         )

        result = flet.execute(input_data)

        assert result.success   is True
        assert result.cache_key == 'html-cache'                # BUG
        assert result.cache_key != 'https://example.com/page'  # BUG

    # ═══════════════════════════════════════════════════════════════════════════
    # Convenience Method Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_from_html__classmethod(self):
        result = FLeT__Html__To__Cache.from_html(html        = '<div>class method test</div>',
                                                 cache_client= self.cache_client             ,
                                                 namespace   = self.namespace                )

        assert result.success   is True
        assert result.html_hash != ''

    # ═══════════════════════════════════════════════════════════════════════════
    # Observability Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_observability__after_execute(self):
        flet       = FLeT__Html__To__Cache(cache_client=self.cache_client).setup()
        input_data = Schema__Html_To_Cache__Load__Input(html      = Safe_Str__Html('<p>observe</p>')   ,
                                                        namespace = Safe_Str__Namespace(self.namespace))

        flet.execute(input_data)

        assert flet.flow   is not None
        assert flet.output is not None
        assert type(flet.durations()) is dict



