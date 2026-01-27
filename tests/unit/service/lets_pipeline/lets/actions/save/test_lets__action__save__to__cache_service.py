# ═══════════════════════════════════════════════════════════════════════════════
# test_lets__action__save__to__cache_service - Tests for cache save action
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                                       import TestCase
from mgraph_ai_service_cache_client.client.cache_service.register_cache_service                                     import register_cache_service__in_memory
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Client import Html_Cache__Client
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.actions.save.lets__action__save__to__cache_service     import lets__action__save__to__cache_service
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.base.Html_LETS__Flow                                   import Html_LETS__Flow
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.Schema__LETS__Config                           import Schema__LETS__Config
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_save.Schema__LETS__Save__Output           import Schema__LETS__Save__Output
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_transform.Schema__LETS__Transform__Output import Schema__LETS__Transform__Output
from mgraph_ai_service_html_graph.utils.testing.Html_Generator__For_Tests                                           import Html_Generator__For_Tests
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html                                           import Safe_Str__Html
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Document                                        import Html_Cache__Document


class test_lets__action__save__to__cache_service(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cache_service_client = register_cache_service__in_memory(return_client=True)
        cls.html_cache_client    = Html_Cache__Client()
        cls.html_gen  = Html_Generator__For_Tests()
        cls.namespace = 'test-save-action'

    # ═══════════════════════════════════════════════════════════════════════════
    # No Document Tests (Stateless)
    # ═══════════════════════════════════════════════════════════════════════════

    def test_save__no_document(self):
        html       = self.html_gen.minimal_html()
        input_data = Schema__LETS__Transform__Output(html=html)

        with Html_LETS__Flow() as flow:
            flow.setup(lambda: lets__action__save__to__cache_service(input_data, this_flow=flow))
            flow.execute()
            result = flow.flow_return_value

        assert type(result)   is Schema__LETS__Save__Output
        assert result.success is True                                       # flow executed ok
        assert result.cached  is False                                      # but there was nothing to cache

    def test_save__no_config(self):
        document = Html_Cache__Document(client    = self.html_cache_client ,
                                        namespace = self.namespace          ,
                                        cache_key = 'test/save/no-config'   )
        document.ensure_cache_id()

        html       = self.html_gen.minimal_html()
        input_data = Schema__LETS__Transform__Output(html=html)

        with Html_LETS__Flow(document=document) as flow:
            flow.setup(lambda: lets__action__save__to__cache_service(input_data, this_flow=flow))
            flow.execute()
            result = flow.flow_return_value

        assert result.success is False
        assert result.cached  is False

    # ═══════════════════════════════════════════════════════════════════════════
    # Successful Save Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_save__with_document_and_config(self):
        document = Html_Cache__Document(client    = self.html_cache_client ,
                                        namespace = self.namespace          ,
                                        cache_key = 'test/save/success'     )
        document.ensure_cache_id()

        config = Schema__LETS__Config(save_layer   = 'test-layer' ,
                                      save_file_id = 'test-file'  ,
                                      save_type    = 'string'     )

        html       = self.html_gen.minimal_html()
        input_data = Schema__LETS__Transform__Output(html=html)

        with Html_LETS__Flow(document=document, config=config) as flow:
            flow.setup(lambda: lets__action__save__to__cache_service(input_data, this_flow=flow))
            flow.execute()
            result = flow.flow_return_value

        assert result.success is True
        assert result.cached  is True
        assert result.layer   == 'test-layer'
        assert result.file_id == 'test-file'

    def test_save__verifies_storage(self):
        document = Html_Cache__Document(client    = self.html_cache_client ,
                                        namespace = self.namespace          ,
                                        cache_key = 'test/save/verify'      )
        document.ensure_cache_id()

        config = Schema__LETS__Config(save_layer   = 'verify-layer' ,
                                      save_file_id = 'verify-file'  ,
                                      save_type    = 'string'       )

        html       = self.html_gen.minimal_html()
        input_data = Schema__LETS__Transform__Output(html=html)

        with Html_LETS__Flow(document=document, config=config) as flow:
            flow.setup(lambda: lets__action__save__to__cache_service(input_data, this_flow=flow))
            flow.execute()

        layer   = document.layer(layer_name='verify-layer')
        content = layer.load_string(file_id='verify-file')

        assert content    is not None
        assert '<html>'   in content
        assert content    == html                                                   # confirm html was saved on the cache service

    # ═══════════════════════════════════════════════════════════════════════════
    # Save Type Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_save__string_type(self):
        document = Html_Cache__Document(client    = self.html_cache_client ,
                                        namespace = self.namespace          ,
                                        cache_key = 'test/save/string'      )
        document.ensure_cache_id()

        config = Schema__LETS__Config(save_layer   = 'string-layer' ,
                                      save_file_id = 'string-file'  ,
                                      save_type    = 'string'       )

        html       = self.html_gen.simple_html()
        input_data = Schema__LETS__Transform__Output(html=html)

        with Html_LETS__Flow(document=document, config=config) as flow:
            flow.setup(lambda: lets__action__save__to__cache_service(input_data, this_flow=flow))
            flow.execute()

        layer   = document.layer(layer_name='string-layer')
        content = layer.load_string(file_id='string-file')

        assert type(content)                  is str
        assert '<title>Test Page</title>'     in content

    # ═══════════════════════════════════════════════════════════════════════════
    # Edge Case Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_save__empty_html(self):
        document = Html_Cache__Document(client    = self.html_cache_client ,
                                        namespace = self.namespace          ,
                                        cache_key = 'test/save/empty'       )
        document.ensure_cache_id()

        config = Schema__LETS__Config(save_layer   = 'empty-layer' ,
                                      save_file_id = 'empty-file'  )

        html       = Safe_Str__Html('')
        input_data = Schema__LETS__Transform__Output(html=html)

        with Html_LETS__Flow(document=document, config=config) as flow:
            flow.setup(lambda: lets__action__save__to__cache_service(input_data, this_flow=flow))
            flow.execute()
            result = flow.flow_return_value

        assert result.success is True
        assert result.cached  is True

    def test_save__none_html(self):
        document = Html_Cache__Document(client    = self.html_cache_client ,
                                        namespace = self.namespace          ,
                                        cache_key = 'test/save/none'        )
        document.ensure_cache_id()

        config = Schema__LETS__Config(save_layer   = 'none-layer' ,
                                      save_file_id = 'none-file'  )

        input_data = Schema__LETS__Transform__Output(html=None)

        with Html_LETS__Flow(document=document, config=config) as flow:
            flow.setup(lambda: lets__action__save__to__cache_service(input_data, this_flow=flow))
            flow.execute()
            result = flow.flow_return_value

        assert result.success is True

    # ═══════════════════════════════════════════════════════════════════════════
    # Type Safety Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_save__output_type(self):
        document = Html_Cache__Document(client    = self.html_cache_client ,
                                        namespace = self.namespace          ,
                                        cache_key = 'test/save/type'        )
        document.ensure_cache_id()

        config     = Schema__LETS__Config(save_layer='type-layer', save_file_id='type-file')
        input_data = Schema__LETS__Transform__Output(html=self.html_gen.minimal_html())

        with Html_LETS__Flow(document=document, config=config) as flow:
            flow.setup(lambda: lets__action__save__to__cache_service(input_data, this_flow=flow))
            flow.execute()
            result = flow.flow_return_value

        assert type(result)         is Schema__LETS__Save__Output
        assert type(result.success) is bool
        assert type(result.cached)  is bool