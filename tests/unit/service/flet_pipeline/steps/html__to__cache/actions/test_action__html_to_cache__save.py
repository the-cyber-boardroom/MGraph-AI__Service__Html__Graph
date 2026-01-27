# ═══════════════════════════════════════════════════════════════════════════════
# test_action__html_to_cache__save - Tests for HTML to cache save action
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                                            import TestCase
from mgraph_ai_service_cache_client.client.cache_service.register_cache_service                                          import register_cache_service__in_memory
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Client                                               import Html_Cache__Client
from mgraph_ai_service_html_graph.service.cache_storage.schemas.Schema__Html_Cache__Entry                                import Schema__Html_Cache__Entry
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__to__cache.actions.action__html_to_cache__save   import action__html_to_cache__save
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__to__cache.schemas.Schema__Html_To_Cache__Input  import Schema__Html_To_Cache__Input
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__to__cache.schemas.Schema__Html_To_Cache__Output import Schema__Html_To_Cache__Output
from osbot_utils.testing.__                                                                                              import __, __SKIP__
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html                                                import Safe_Str__Html


class test_action__html_to_cache__save(TestCase):

    @classmethod
    def setUpClass(cls):                                                                  # Shared test objects
        cls.cache_service_client = register_cache_service__in_memory(return_client=True)
        cls.cache_client         = Html_Cache__Client()
        cls.sample_html          = '<html><body><p>Test content</p></body></html>'
        cls.namespace            = 'test-action-save'
        cls.cache_id             = cls.create_test_entity()

    @classmethod
    def create_test_entity(cls):                                                          # Create entity for tests
        entry    = Schema__Html_Cache__Entry()
        response = cls.cache_client.entry__store(namespace = cls.namespace     ,
                                                 cache_key = 'test/save-action',
                                                 file_id   = 'root'            ,
                                                 entry     = entry             )
        return response.cache_id if response else None

    # ═══════════════════════════════════════════════════════════════════════════
    # Without Dependencies Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_action__without_cache_client(self):                                          # Test with no cache_client
        input_data = Schema__Html_To_Cache__Input(html = Safe_Str__Html(self.sample_html))

        result = action__html_to_cache__save(input_data   = input_data,
                                             cache_client = None      ,
                                             cache_id     = None      ,
                                             namespace    = None      )

        assert type(result)      is Schema__Html_To_Cache__Output
        assert result.success    is False
        assert result.char_count == len(self.sample_html)
        assert result.data_key   == 'html'
        assert result.data_file_id == 'raw'

    def test_action__without_cache_id(self):                                              # Test with cache_client but no cache_id
        input_data = Schema__Html_To_Cache__Input(html = Safe_Str__Html(self.sample_html))

        result = action__html_to_cache__save(input_data   = input_data       ,
                                             cache_client = self.cache_client,
                                             cache_id     = None             ,
                                             namespace    = self.namespace   )

        assert result.success is False

    def test_action__without_namespace(self):                                             # Test without namespace
        input_data = Schema__Html_To_Cache__Input(html = Safe_Str__Html(self.sample_html))

        result = action__html_to_cache__save(input_data   = input_data       ,
                                             cache_client = self.cache_client,
                                             cache_id     = self.cache_id    ,
                                             namespace    = None             )

        assert result.success is False

    # ═══════════════════════════════════════════════════════════════════════════
    # With Dependencies Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_action__with_all_dependencies(self):                                         # Test with all dependencies
        input_data = Schema__Html_To_Cache__Input(html = Safe_Str__Html(self.sample_html))

        result = action__html_to_cache__save(input_data   = input_data       ,
                                             cache_client = self.cache_client,
                                             cache_id     = self.cache_id    ,
                                             namespace    = self.namespace   )

        assert type(result)           is Schema__Html_To_Cache__Output
        assert result.success         is True
        assert result.data_key        == 'html'
        assert result.data_file_id    == 'raw'
        assert result.char_count      == len(self.sample_html)
        assert result.store_response  is not None
        assert result.obj()           == __(success        = True                     ,
                                            data_key       = 'html'                   ,
                                            data_file_id   = 'raw'                    ,
                                            char_count     = 45                       ,
                                            store_response = __(cache_id           = self.cache_id                                                       ,
                                                                data_files_created = ['test-action-save/data/key-based/test/save-action/root/data/html/raw.txt'],
                                                                data_key           = 'html'                                                              ,
                                                                data_type          = 'string'                                                            ,
                                                                extension          = 'txt'                                                               ,
                                                                file_id            = 'raw'                                                               ,
                                                                file_size          = 45                                                                  ,
                                                                namespace          = 'test-action-save'                                                  ,
                                                                timestamp          = __SKIP__                                                            ))

    def test_action__with_custom_data_key(self):                                          # Test with custom data_key
        input_data = Schema__Html_To_Cache__Input(html         = Safe_Str__Html('<p>custom</p>'),
                                                  data_key     = 'custom/path'                 ,
                                                  data_file_id = 'custom-file'                 )

        result = action__html_to_cache__save(input_data   = input_data       ,
                                             cache_client = self.cache_client,
                                             cache_id     = self.cache_id    ,
                                             namespace    = self.namespace   )

        assert result.success      is True
        assert result.data_key     == 'custom/path'
        assert result.data_file_id == 'custom-file'
        assert result.char_count   == 13

    # ═══════════════════════════════════════════════════════════════════════════
    # Character Count Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_action__char_count(self):                                                    # Test character count calculation
        html       = '<p>Short</p>'
        input_data = Schema__Html_To_Cache__Input(html = Safe_Str__Html(html))

        result = action__html_to_cache__save(input_data   = input_data       ,
                                             cache_client = self.cache_client,
                                             cache_id     = self.cache_id    ,
                                             namespace    = self.namespace   )

        assert result.char_count == len(html)
        assert result.char_count == 12

    # ═══════════════════════════════════════════════════════════════════════════
    # Store Response Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_action__store_response_on_success(self):                                     # Test store_response populated on success
        input_data = Schema__Html_To_Cache__Input(html         = Safe_Str__Html('<p>response test</p>'),
                                                  data_key     = 'response-test'                      ,
                                                  data_file_id = 'file'                               )

        result = action__html_to_cache__save(input_data   = input_data       ,
                                             cache_client = self.cache_client,
                                             cache_id     = self.cache_id    ,
                                             namespace    = self.namespace   )

        assert result.success                            is True
        assert result.store_response                     is not None
        assert result.store_response.cache_id            == self.cache_id
        assert result.store_response.data_key            == 'response-test'
        assert result.store_response.file_id             == 'file'
        assert result.store_response.data_type           == 'string'
        assert result.store_response.file_size           == 20

    def test_action__store_response_none_on_failure(self):                                # Test store_response is None on failure
        input_data = Schema__Html_To_Cache__Input(html = Safe_Str__Html('<p>fail</p>'))

        result = action__html_to_cache__save(input_data   = input_data,
                                             cache_client = None      ,
                                             cache_id     = None      ,
                                             namespace    = None      )

        assert result.success        is False
        assert result.store_response is None