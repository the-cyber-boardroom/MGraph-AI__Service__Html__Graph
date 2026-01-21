# ═══════════════════════════════════════════════════════════════════════════════
# test_Html_LETS__Dict__To__MGraph - Tests for dictionary to MGraph LETS
# Tests building MGraph document from HTML dictionary
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                  import TestCase
from osbot_utils.testing.__                                                                    import __
from osbot_utils.type_safe.Type_Safe                                                           import Type_Safe
from osbot_utils.utils.Objects                                                                 import base_types
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.base.Html_LETS__Base              import Html_LETS__Base
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.steps.Html_LETS__Dict__To__MGraph import Html_LETS__Dict__To__MGraph
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.steps.Html_LETS__Dict__To__MGraph import Schema__Dict_To_MGraph__Load__Input
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.steps.Html_LETS__Dict__To__MGraph import Schema__MGraph_Document
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.steps.Html_LETS__Dict__To__MGraph import build_mgraph
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.steps.Html_LETS__Html__To__Dict   import Schema__Html_Dict


class test_Html_LETS__Dict__To__MGraph(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.sample_html_dict = Schema__Html_Dict(html_dict={'tag'     : 'html'   ,
                                                            'children': []       ,
                                                            'node_id' : 'root-1' })
        cls.nested_html_dict = Schema__Html_Dict(html_dict={'tag'     : 'html'   ,
                                                            'children': [
                                                                {'tag'     : 'body'    ,
                                                                 'children': [
                                                                     {'tag'    : 'p'     ,
                                                                      'text'   : 'Hello' ,
                                                                      'node_id': 'p-1'   }],
                                                                 'node_id': 'body-1'   }],
                                                            'node_id' : 'html-1' })

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):
        with Html_LETS__Dict__To__MGraph() as _:
            assert type(_)       is Html_LETS__Dict__To__MGraph
            assert base_types(_) == [Html_LETS__Base, Type_Safe, object]

    def test__init____config_is_none(self):
        with Html_LETS__Dict__To__MGraph() as _:
            assert _.config is None

    def test__init____actions_wired(self):
        with Html_LETS__Dict__To__MGraph() as _:
            assert _.load      is not None
            assert _.extract   is not None
            assert _.transform is not None
            assert _.save      is not None

    # ═══════════════════════════════════════════════════════════════════════════
    # Setup Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_setup(self):
        with Html_LETS__Dict__To__MGraph() as _:
            result = _.setup()

            assert result        is _
            assert _.config      is not None
            assert _.config.name == 'dict-to-mgraph'
            assert 'MGraph'      in _.config.description

    def test_setup__returns_self(self):
        lets = Html_LETS__Dict__To__MGraph().setup()
        assert type(lets)       is Html_LETS__Dict__To__MGraph
        assert lets.config.name == 'dict-to-mgraph'

    # ═══════════════════════════════════════════════════════════════════════════
    # build_mgraph Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_build_mgraph(self):
        result = build_mgraph(self.sample_html_dict)

        assert type(result) is dict
        assert 'graph'      in result
        assert 'source'     in result
        assert 'nodes'      in result['graph']
        assert 'edges'      in result['graph']

    def test_build_mgraph__preserves_source(self):
        result = build_mgraph(self.sample_html_dict)
        assert result['source'] == self.sample_html_dict.html_dict

    def test_build_mgraph__none_input(self):
        result = build_mgraph(None)
        assert result['graph']['nodes'] == []
        assert result['graph']['edges'] == []
        assert result['source']         == {}

    # ═══════════════════════════════════════════════════════════════════════════
    # Schema Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_Schema__MGraph_Document(self):
        data   = {'graph': {'nodes': [], 'edges': []}, 'metadata': {}}
        schema = Schema__MGraph_Document(mgraph_data=data)

        assert schema.mgraph_data          == data
        assert schema.mgraph_data['graph'] is not None

    def test_Schema__MGraph_Document__empty_graph(self):
        data   = {'graph': {'nodes': [], 'edges': []}}
        schema = Schema__MGraph_Document(mgraph_data=data)

        assert len(schema.mgraph_data['graph']['nodes']) == 0
        assert len(schema.mgraph_data['graph']['edges']) == 0

    # ═══════════════════════════════════════════════════════════════════════════
    # Execute Tests (Full Pipeline)
    # ═══════════════════════════════════════════════════════════════════════════

    def test_execute__simple(self):
        step       = Html_LETS__Dict__To__MGraph().setup()
        input_data = Schema__Dict_To_MGraph__Load__Input(html_dict=self.sample_html_dict)

        assert step.obj() == __(config=__(schema__input=None,
                                          schema__output=None,
                                          save_layer=None,
                                          save_file_id=None,
                                          save_type='string',
                                          load_layer=None,
                                          load_file_id=None,
                                          compute_stats=True,
                                          name='dict-to-mgraph',
                                          description='Build MGraph document from HTML dictionary'),
                                document=None,
                                flow=None,
                                output=None)


        result = step.execute(input_data)

        assert result.success is True

    def test_execute__nested(self):
        step       = Html_LETS__Dict__To__MGraph().setup()
        input_data = Schema__Dict_To_MGraph__Load__Input(html_dict=self.nested_html_dict)

        result = step.execute(input_data)

        assert result.success is True

    def test_execute__sets_flow(self):
        step       = Html_LETS__Dict__To__MGraph().setup()
        input_data = Schema__Dict_To_MGraph__Load__Input(html_dict=self.sample_html_dict)

        step.execute(input_data)

        assert step.flow   is not None
        assert step.output is not None

    # ═══════════════════════════════════════════════════════════════════════════
    # Observability Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_durations__after_execute(self):
        step       = Html_LETS__Dict__To__MGraph().setup()
        input_data = Schema__Dict_To_MGraph__Load__Input(html_dict=self.sample_html_dict)

        step.execute(input_data)
        durations = step.durations()

        assert type(durations) is dict

    def test_durations__before_execute(self):
        step = Html_LETS__Dict__To__MGraph().setup()
        assert step.durations() == {}