# ═══════════════════════════════════════════════════════════════════════════════
# test_action__html_from_cache__load - Tests for HTML from cache load action
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                                                  import TestCase
from mgraph_ai_service_cache_client.client.cache_service.register_cache_service                                                import register_cache_service__in_memory
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Client                                                     import Html_Cache__Client
from mgraph_ai_service_html_graph.service.cache_storage.schemas.Schema__Html_Cache__Entry                                      import Schema__Html_Cache__Entry
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__from__cache.actions.action__html_from_cache__load     import action__html_from_cache__load
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__from__cache.schemas.Schema__Html_From_Cache__Input    import Schema__Html_From_Cache__Input
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__from__cache.schemas.Schema__Html_From_Cache__Output   import Schema__Html_From_Cache__Output
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__to__cache.actions.action__html_to_cache__save         import action__html_to_cache__save
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__to__cache.schemas.Schema__Html_To_Cache__Input        import Schema__Html_To_Cache__Input
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html                                                      import Safe_Str__Html


class test_action__html_from_cache__load(TestCase):

    @classmethod
    def setUpClass(cls):                                                                  # Shared test objects
        cls.cache_service_client = register_cache_service__in_memory(return_client=True)
        cls.html_cache_client    = Html_Cache__Client()

        cls.sample_html = '<html><body><p>Stored content</p></body></html>'
        cls.namespace   = 'test-action-load'
        cls.cache_id    = cls.create_and_populate_entity()

    @classmethod
    def create_and_populate_entity(cls):                                                  # Create and populate entity
        entry    = Schema__Html_Cache__Entry()
        response = cls.html_cache_client.entry__store(namespace       = cls.namespace   ,
                                                      cache_key       = 'test/load-action',
                                                      file_id         = 'root'           ,
                                                      entry           = entry            )
        cache_id = response.cache_id if response else None

        # Store HTML for retrieval tests
        save_input = Schema__Html_To_Cache__Input(html = Safe_Str__Html(cls.sample_html))
        action__html_to_cache__save(input_data   = save_input            ,
                                    cache_client = cls.html_cache_client ,
                                    cache_id     = cache_id              ,
                                    namespace    = cls.namespace         )
        return cache_id

    # ═══════════════════════════════════════════════════════════════════════════
    # Without Dependencies Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_action__without_cache_client(self):                                          # Test with no cache_client
        input_data = Schema__Html_From_Cache__Input()

        result = action__html_from_cache__load(input_data   = input_data,
                                               cache_client = None      ,
                                               cache_id     = None      ,
                                               namespace    = None      )

        assert type(result)   is Schema__Html_From_Cache__Output
        assert result.success is False
        assert result.found   is False

    def test_action__without_cache_id(self):                                              # Test without cache_id
        input_data = Schema__Html_From_Cache__Input()

        result = action__html_from_cache__load(input_data   = input_data            ,
                                               cache_client = self.html_cache_client,
                                               cache_id     = None                  ,
                                               namespace    = self.namespace        )

        assert result.success is False
        assert result.found   is False

    # ═══════════════════════════════════════════════════════════════════════════
    # With Dependencies Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_action__load_existing(self):                                                 # Test loading existing HTML
        input_data = Schema__Html_From_Cache__Input()

        result = action__html_from_cache__load(input_data   = input_data            ,
                                               cache_client = self.html_cache_client,
                                               cache_id     = self.cache_id         ,
                                               namespace    = self.namespace        )

        assert type(result)     is Schema__Html_From_Cache__Output
        assert result.success   is True
        assert result.found     is True
        assert str(result.html) == self.sample_html

    def test_action__load_nonexistent(self):                                              # Test loading nonexistent data
        input_data = Schema__Html_From_Cache__Input(data_key = 'nonexistent')

        result = action__html_from_cache__load(input_data   = input_data            ,
                                               cache_client = self.html_cache_client,
                                               cache_id     = self.cache_id         ,
                                               namespace    = self.namespace        )

        assert result.success   is True                                                   # Operation succeeded
        assert result.found     is False                                                  # But data not found
        assert str(result.html) == ''

    def test_action__load_with_custom_data_key(self):                                     # Test with custom data_key
        # First store with custom key
        save_input = Schema__Html_To_Cache__Input(html         = Safe_Str__Html('<p>custom</p>'),
                                                  data_key     = 'custom/path'                 ,
                                                  data_file_id = 'custom-file'                 )
        action__html_to_cache__save(input_data   = save_input            ,
                                    cache_client = self.html_cache_client,
                                    cache_id     = self.cache_id         ,
                                    namespace    = self.namespace        )

        # Then load from custom key
        load_input = Schema__Html_From_Cache__Input(data_key     = 'custom/path' ,
                                                    data_file_id = 'custom-file' )

        result = action__html_from_cache__load(input_data   = load_input            ,
                                               cache_client = self.html_cache_client,
                                               cache_id     = self.cache_id         ,
                                               namespace    = self.namespace        )

        assert result.success   is True
        assert result.found     is True
        assert str(result.html) == '<p>custom</p>'
