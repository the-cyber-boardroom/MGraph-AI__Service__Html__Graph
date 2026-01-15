# ═══════════════════════════════════════════════════════════════════════════════
# test_Html_LETS__Dict__To__MGraph - Tests for dictionary to MGraph LETS
# Tests building MGraph document from HTML dictionary
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                            import TestCase
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.base.Html_LETS__Base                        import Html_LETS__Base
from osbot_utils.type_safe.Type_Safe                                                                     import Type_Safe
from osbot_utils.utils.Objects                                                                           import base_types
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.implementations.Html_LETS__Dict__To__MGraph import Schema__Dict_To_MGraph__Load__Input, Schema__Dict_To_MGraph__Load__Output, Schema__Dict_To_MGraph__Transform__Input, Schema__Dict_To_MGraph__Transform__Output, Schema__MGraph_Document, Schema__Dict_To_MGraph__Save__Input, Html_LETS__Dict__To__MGraph
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.implementations.Html_LETS__Html__To__Dict   import Schema__Html_Dict


class test_Html_LETS__Dict__To__MGraph(TestCase):

    @classmethod
    def setUpClass(cls):                                                         # Shared setup
        cls.sample_html_dict = Schema__Html_Dict(html_dict={'tag'     : 'html'    ,
                                                            'children': []        ,
                                                            'node_id' : 'root-1'  })
        cls.nested_html_dict = Schema__Html_Dict(html_dict={'tag'     : 'html'    ,
                                                            'children': [
                                                                {'tag'     : 'body'    ,
                                                                 'children': [
                                                                     {'tag' : 'p'          ,
                                                                      'text': 'Hello'      ,
                                                                      'node_id': 'p-1'     }],
                                                                 'node_id': 'body-1'   }],
                                                            'node_id' : 'html-1'  })

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                      # Test auto-initialization
        with Html_LETS__Dict__To__MGraph() as _:
            assert type(_)       is Html_LETS__Dict__To__MGraph
            assert base_types(_) == [Html_LETS__Base, Type_Safe, object]

    def test__init____config_is_none(self):                                      # Test config starts None
        with Html_LETS__Dict__To__MGraph() as _:
            assert _.config is None

    # ═══════════════════════════════════════════════════════════════════════════
    # Setup Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_setup(self):                                                        # Test setup initializes config
        with Html_LETS__Dict__To__MGraph() as _:
            result = _.setup()

            assert result             is _
            assert _.config           is not None
            assert _.config.name      == 'dict-to-mgraph'
            assert 'MGraph'           in _.config.description

    def test_setup__returns_self(self):                                          # Test chaining
        lets = Html_LETS__Dict__To__MGraph().setup()
        assert type(lets)        is Html_LETS__Dict__To__MGraph
        assert lets.config.name  == 'dict-to-mgraph'

    # ═══════════════════════════════════════════════════════════════════════════
    # Load Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_load(self):                                                         # Test load returns dict
        with Html_LETS__Dict__To__MGraph().setup() as _:
            load_input  = Schema__Dict_To_MGraph__Load__Input(html_dict=self.sample_html_dict)
            load_output = _.load(load_input=load_input)

            assert type(load_output)          is Schema__Dict_To_MGraph__Load__Output
            assert type(load_output.html_dict) is Schema__Html_Dict
            assert load_output.html_dict      == self.sample_html_dict

    # ═══════════════════════════════════════════════════════════════════════════
    # Transform Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_transform(self):                                                    # Test transform creates MGraph
        with Html_LETS__Dict__To__MGraph().setup() as _:
            transform_input  = Schema__Dict_To_MGraph__Transform__Input(html_dict=self.sample_html_dict)
            transform_output = _.transform(transform_input=transform_input)

            assert type(transform_output)                 is Schema__Dict_To_MGraph__Transform__Output
            assert type(transform_output.mgraph_document) is Schema__MGraph_Document
            assert transform_output.mgraph_document.mgraph_data is not None

    def test_transform__output_has_graph_structure(self):                        # Test MGraph structure
        with Html_LETS__Dict__To__MGraph().setup() as _:
            transform_input  = Schema__Dict_To_MGraph__Transform__Input(html_dict=self.sample_html_dict)
            transform_output = _.transform(transform_input=transform_input)

            mgraph_data = transform_output.mgraph_document.mgraph_data
            assert 'graph'  in mgraph_data                                       # Has graph key
            assert 'source' in mgraph_data                                       # Has source key

    def test_transform__nested_dict(self):                                       # Test with nested input
        with Html_LETS__Dict__To__MGraph().setup() as _:
            transform_input  = Schema__Dict_To_MGraph__Transform__Input(html_dict=self.nested_html_dict)
            transform_output = _.transform(transform_input=transform_input)

            mgraph_data = transform_output.mgraph_document.mgraph_data
            assert mgraph_data['source']['tag'] == 'html'

    # ═══════════════════════════════════════════════════════════════════════════
    # Save Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_save(self):                                                         # Test save returns success
        with Html_LETS__Dict__To__MGraph().setup() as _:
            mgraph_doc  = Schema__MGraph_Document(mgraph_data={'graph': {}, 'source': {}})
            save_input  = Schema__Dict_To_MGraph__Save__Input(mgraph_document=mgraph_doc)
            save_output = _.save(save_input=save_input)

            assert save_output.success is True

    # ═══════════════════════════════════════════════════════════════════════════
    # build_mgraph Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_build_mgraph(self):                                                 # Test helper method
        with Html_LETS__Dict__To__MGraph().setup() as _:
            result = _.build_mgraph(self.sample_html_dict)

            assert type(result)     is dict
            assert 'graph'          in result
            assert 'source'         in result
            assert 'nodes'          in result['graph']
            assert 'edges'          in result['graph']

    def test_build_mgraph__preserves_source(self):                               # Test source preserved
        with Html_LETS__Dict__To__MGraph().setup() as _:
            result = _.build_mgraph(self.sample_html_dict)

            assert result['source'] == self.sample_html_dict.html_dict

    # ═══════════════════════════════════════════════════════════════════════════
    # Schema Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_Schema__MGraph_Document(self):                                      # Test MGraph schema
        data   = {'graph': {'nodes': [], 'edges': []}, 'metadata': {}}
        schema = Schema__MGraph_Document(mgraph_data=data)

        assert schema.mgraph_data            == data
        assert schema.mgraph_data['graph']   is not None

    def test_Schema__MGraph_Document__empty_graph(self):                         # Test empty graph
        data   = {'graph': {'nodes': [], 'edges': []}}
        schema = Schema__MGraph_Document(mgraph_data=data)

        assert len(schema.mgraph_data['graph']['nodes']) == 0
        assert len(schema.mgraph_data['graph']['edges']) == 0

    # ═══════════════════════════════════════════════════════════════════════════
    # Integration Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_integration__full_pipeline(self):                                   # Test L-E-T-S flow
        with Html_LETS__Dict__To__MGraph().setup() as _:
            # Load
            load_input  = Schema__Dict_To_MGraph__Load__Input(html_dict=self.nested_html_dict)
            load_output = _.load(load_input=load_input)

            # Transform
            transform_input  = Schema__Dict_To_MGraph__Transform__Input(html_dict=load_output.html_dict)
            transform_output = _.transform(transform_input=transform_input)

            # Save
            save_input  = Schema__Dict_To_MGraph__Save__Input(mgraph_document=transform_output.mgraph_document)
            save_output = _.save(save_input=save_input)

            assert save_output.success                               is True
            assert transform_output.mgraph_document.mgraph_data      is not None
            assert 'graph' in transform_output.mgraph_document.mgraph_data
