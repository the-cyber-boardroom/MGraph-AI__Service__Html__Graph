# ═══════════════════════════════════════════════════════════════════════════════
# test_Html_FLeT__Flow - Tests for FLeT Flow with typed dependencies
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                             import TestCase
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.base.Html_FLeT__Flow         import Html_FLeT__Flow
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.schemas.Schema__FLeT__Config import Schema__FLeT__Config
from osbot_utils.helpers.flows.Flow                                                       import Flow
from osbot_utils.testing.__ import __
from osbot_utils.testing.__helpers import obj
from osbot_utils.type_safe.Type_Safe                                                      import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Namespace import Safe_Str__Namespace
from osbot_utils.utils.Objects                                                            import base_types


class test_Html_FLeT__Flow(TestCase):

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                               # Test auto-initialization
        with Html_FLeT__Flow() as _:
            assert type(_)        is Html_FLeT__Flow
            assert base_types(_)  == [Flow, Type_Safe, object]
            assert _.cache_client is None
            assert _.cache_id     is None
            assert _.namespace    is None
            assert _.config       is None

    def test__init____with_config(self):                                                  # Test with config provided
        config = Schema__FLeT__Config(name='test-flow', description='Test')
        with Html_FLeT__Flow(config=config) as _:
            assert _.config      is config
            assert _.config.name == 'test-flow'

    # ═══════════════════════════════════════════════════════════════════════════
    # Task Dependencies Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_task_dependencies(self):                                                     # Test dependency dict
        with Html_FLeT__Flow() as _:
            deps = _.task_dependencies()

            assert type(deps)             is dict
            assert 'cache_client'         in deps
            assert 'cache_id'             in deps
            assert 'namespace'            in deps
            assert 'config'               in deps
            assert deps['cache_client']   is None
            assert deps['cache_id']       is None

    def test_task_dependencies__with_values(self):                                        # Test dependencies with values
        config = Schema__FLeT__Config(name='test', description='Test flow')
        with Html_FLeT__Flow(config    = config     ,
                             namespace = 'test-ns'  ) as _:
            deps = _.task_dependencies()

            assert deps['config'   ] is config
            assert deps['namespace'] == 'test-ns'
            assert obj(deps)         == __(cache_client = None          ,
                                           cache_id     = None          ,
                                           namespace    = 'test-ns'     ,
                                           config       = config        )                   # todo: review the fact that this is not an .obj() value but it is the actual instance (this could be a bug in the obj(deps) )
