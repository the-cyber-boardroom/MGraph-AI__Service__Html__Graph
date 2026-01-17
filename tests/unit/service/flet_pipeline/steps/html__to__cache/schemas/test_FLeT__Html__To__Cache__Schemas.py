from unittest                                                                                                                   import TestCase
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__to__cache.schemas.Schema__Html_To_Cache__Load__Input   import Schema__Html_To_Cache__Load__Input
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__to__cache.schemas.Schema__Html_To_Cache__Save__Output  import Schema__Html_To_Cache__Save__Output


class test_FLeT__Html__To__Cache__Schemas(TestCase):

    def test_Schema__Html_To_Cache__Load__Input(self):
        schema = Schema__Html_To_Cache__Load__Input(html      = '<p>test</p>'        ,
                                                    namespace = 'test-ns'            ,
                                                    cache_key = 'abc/123'          ,
                                                    url       = 'https://example.com')

        assert schema.html           == '<p>test</p>'
        assert schema.namespace      == 'test-ns'
        assert schema.cache_key      == 'abc/123'
        assert schema.url            == 'https://example.com'

    def test_Schema__Html_To_Cache__Save__Output(self):
        schema = Schema__Html_To_Cache__Save__Output(success   = True          ,
                                                     html_hash = 'c000000001'  ,
                                                     cache_key = 'an/cache/key',
                                                     from_cache= False         )

        assert schema.success    is True
        assert schema.from_cache is False