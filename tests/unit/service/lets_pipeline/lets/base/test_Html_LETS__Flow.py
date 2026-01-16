# ═══════════════════════════════════════════════════════════════════════════════
# test_Html_LETS__Flow - Tests for extended Flow with LETS dependencies
# ═══════════════════════════════════════════════════════════════════════════════
from types import NoneType
from unittest                                                                               import TestCase
from osbot_utils.helpers.flows.Flow                                                         import Flow
from osbot_utils.type_safe.Type_Safe                                                        import Type_Safe
from osbot_utils.utils.Objects                                                              import base_types
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Document                import Html_Cache__Document
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.base.Html_LETS__Flow           import Html_LETS__Flow
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.Schema__LETS__Config   import Schema__LETS__Config
from tests.unit.Html_Graph__Service__Fast_API__Test_Objs                                    import create_html_cache_client


class test_Html_LETS__Flow(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.html_cache_client, cls.cache_service = create_html_cache_client()
        cls.namespace = 'test-flow'

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):
        with Html_LETS__Flow() as _:
            assert type(_)             is Html_LETS__Flow
            assert base_types(_)       == [Flow, Type_Safe, object]
            assert type(_.document)    is NoneType
            assert type(_.config)      is NoneType

    def test__init____with_document(self):
        document = Html_Cache__Document(client    = self.html_cache_client ,
                                        namespace = self.namespace          ,
                                        cache_key = 'test/flow/init'        )
        with Html_LETS__Flow(document=document) as _:
            assert _.document is document
            assert _.config   is None

    def test__init____with_config(self):
        config = Schema__LETS__Config(name='test-config')
        with Html_LETS__Flow(config=config) as _:
            assert _.document       is None
            assert _.config         is config
            assert _.config.name    == 'test-config'

    def test__init____with_both(self):
        document = Html_Cache__Document(client    = self.html_cache_client ,
                                        namespace = self.namespace          ,
                                        cache_key = 'test/flow/both'        )
        config   = Schema__LETS__Config(name='test-both')

        with Html_LETS__Flow(document=document, config=config) as _:
            assert _.document is document
            assert _.config   is config

    # ═══════════════════════════════════════════════════════════════════════════
    # task_dependencies Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_task_dependencies(self):
        with Html_LETS__Flow() as _:
            deps = _.task_dependencies()
            assert type(deps)        is dict
            assert 'document'        in deps
            assert 'config'          in deps
            assert deps['document']  is None
            assert deps['config']    is None

    def test_task_dependencies__with_values(self):
        document = Html_Cache__Document(client    = self.html_cache_client ,
                                        namespace = self.namespace          ,
                                        cache_key = 'test/flow/deps'        )
        config   = Schema__LETS__Config(name='test-deps')

        with Html_LETS__Flow(document=document, config=config) as _:
            deps = _.task_dependencies()
            assert deps['document'] is document
            assert deps['config']   is config

    def test_task_dependencies__returns_current_values(self):
        with Html_LETS__Flow() as _:
            deps_before = _.task_dependencies()
            assert type(deps_before['config']) is NoneType

            _.config = Schema__LETS__Config(name='updated')
            deps_after = _.task_dependencies()
            assert deps_after['config']      is _.config
            assert deps_after['config'].name == 'updated'

    # ═══════════════════════════════════════════════════════════════════════════
    # Flow Integration Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_flow__setup_and_execute(self):
        with Html_LETS__Flow() as _:
            _.setup(lambda: 'test-result')
            _.execute()
            assert _.flow_return_value == 'test-result'

    def test_flow__with_document_access(self):
        document = Html_Cache__Document(client    = self.html_cache_client ,
                                        namespace = self.namespace          ,
                                        cache_key = 'test/flow/access'      )

        def target_fn():
            return 'accessed'

        with Html_LETS__Flow(document=document) as _:
            _.setup(target_fn)
            _.execute()
            assert _.flow_return_value == 'accessed'
            assert _.document          is document

    def test_flow__durations(self):
        with Html_LETS__Flow() as _:
            _.setup(lambda: 'timed')
            _.execute()
            durations = _.durations()
            assert type(durations) is dict

    def test_flow__captured_logs(self):
        with Html_LETS__Flow() as _:
            _.setup(lambda: print('test log message') or 'done')
            _.execute()
            logs = _.captured_logs()
            assert type(logs) is list


class test_Html_LETS__Flow__Type_Safety(TestCase):

    def test_document__type_safe(self):
        with Html_LETS__Flow() as _:
            _.document = Html_Cache__Document()
            assert _.document is not None

    def test_config__type_safe(self):
        with Html_LETS__Flow() as _:
            _.config = Schema__LETS__Config()
            assert _.config is not None