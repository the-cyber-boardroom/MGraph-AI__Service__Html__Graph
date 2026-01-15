from unittest                                                                                import TestCase
from osbot_utils.type_safe.Type_Safe                                                         import Type_Safe
from osbot_utils.utils.Objects                                                               import base_classes
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                            import Html_MGraph
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base import Graph_Transformation__Base


class test_Graph_Transformation__Base(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.transformation = Graph_Transformation__Base()
        cls.simple_html    = '<div class="main">Hello World</div>'
        cls.html_mgraph    = Html_MGraph.from_html(cls.simple_html)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):
        with self.transformation as _:
            assert type(_)         is Graph_Transformation__Base
            assert base_classes(_) == [Type_Safe, object]
            assert _.name          == 'default'
            assert _.label         == 'Default'
            assert _.description   == 'Standard HTML to MGraph conversion with full detail'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Phase 1: transform_html Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__transform_html__passthrough(self):
        html   = '<div>Test</div>'
        result = self.transformation.transform_html(html)
        assert result == html                                                         # Default passes through unchanged

    def test__transform_html__preserves_content(self):
        html   = '<!DOCTYPE html><html><body><p>Content</p></body></html>'
        result = self.transformation.transform_html(html)
        assert result == html

    # ═══════════════════════════════════════════════════════════════════════════════
    # Phase 2: transform_mgraph Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__transform_mgraph__passthrough(self):
        result = self.transformation.transform_mgraph(self.html_mgraph)
        assert result is self.html_mgraph                                             # Default passes through unchanged

    def test__transform_mgraph__preserves_graphs(self):
        result = self.transformation.transform_mgraph(self.html_mgraph)
        assert result.body_graph  is not None
        assert result.attrs_graph is not None

    # ═══════════════════════════════════════════════════════════════════════════════
    # Phase 3: transform_export Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__transform_export__passthrough(self):
        export_data = {'nodes': [], 'edges': [], 'format': 'test'}
        result      = self.transformation.transform_export(export_data)
        assert result is export_data                                                  # Default passes through unchanged

    def test__transform_export__preserves_structure(self):
        export_data = {'nodes'   : [{'id': '1', 'label': 'test'}],
                       'edges'   : [{'from': '1', 'to': '2'}]    ,
                       'format'  : 'visjs'                       ,
                       'duration': 0.1                           }
        result = self.transformation.transform_export(export_data)
        assert result['nodes']    == export_data['nodes']
        assert result['edges']    == export_data['edges']
        assert result['format']   == 'visjs'
        assert result['duration'] == 0.1

    # ═══════════════════════════════════════════════════════════════════════════════
    # Metadata Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__to_dict(self):
        result = self.transformation.to_dict()
        assert type(result)        is dict
        assert result['name']      == 'default'
        assert result['label']     == 'Default'
        assert 'description'       in result

    def test__to_dict__keys(self):
        result = self.transformation.to_dict()
        assert set(result.keys()) == {'name', 'label', 'description'}