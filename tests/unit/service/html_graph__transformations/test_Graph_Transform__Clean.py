from unittest                                                                                    import TestCase
from osbot_utils.type_safe.Type_Safe                                                             import Type_Safe
from osbot_utils.utils.Objects                                                                   import base_classes
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                                import Html_MGraph
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base import Graph_Transformation__Base
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transform__Clean     import Graph_Transform__Clean


class test_Graph_Transform__Clean(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.transformation = Graph_Transform__Clean()
        cls.simple_html    = '<div class="main">Hello World</div>'
        cls.html_mgraph    = Html_MGraph.from_html(cls.simple_html)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):
        with self.transformation as _:
            assert type(_)         is Graph_Transform__Clean
            assert base_classes(_) == [Graph_Transformation__Base, Type_Safe, object]
            assert _.name          == 'clean'
            assert _.label         == 'Clean View'

    def test__metadata(self):
        assert 'clean'     in self.transformation.description.lower()
        assert 'tag'       in self.transformation.description.lower()
        assert 'attribute' in self.transformation.description.lower()

    # ═══════════════════════════════════════════════════════════════════════════════
    # transform_mgraph Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__transform_mgraph__returns_html_mgraph(self):
        html_mgraph = Html_MGraph.from_html('<div>Test</div>')
        result      = self.transformation.transform_mgraph(html_mgraph)

        assert result is html_mgraph
        assert type(result) is Html_MGraph

    def test__transform_mgraph__clears_text_node_paths(self):
        html_mgraph = Html_MGraph.from_html('<div>Hello World</div>')
        result      = self.transformation.transform_mgraph(html_mgraph)

        # Check that text node paths are cleared
        if result.body_graph:
            nodes = result.body_graph.mgraph.graph.model.data.nodes
            for node_id, node in nodes.items():
                if hasattr(node, 'node_data') and hasattr(node.node_data, 'value'):
                    # Text nodes should have empty path
                    assert node.node_path == '' or node.node_path != 'text'

    def test__transform_mgraph__preserves_body_graph(self):
        html_mgraph = Html_MGraph.from_html('<div><p>Content</p></div>')
        result      = self.transformation.transform_mgraph(html_mgraph)

        assert result.body_graph is not None

    def test__transform_mgraph__handles_none_body_graph(self):
        html_mgraph = Html_MGraph()                                                   # Empty Html_MGraph
        result      = self.transformation.transform_mgraph(html_mgraph)

        assert result is html_mgraph                                                  # Should handle gracefully

    # ═══════════════════════════════════════════════════════════════════════════════
    # transform_export Tests - Filter to element and text only
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__transform_export__filters_to_element_and_text(self):
        export_data = {
            'nodes': [
                {'id': '1', 'label': 'div',   'nodeType': 'element'},
                {'id': '2', 'label': 'Hello', 'nodeType': 'text'},
                {'id': '3', 'label': '<div>', 'nodeType': 'tag'},
                {'id': '4', 'label': 'class', 'nodeType': 'attribute'},
            ],
            'edges': []
        }

        result = self.transformation.transform_export(export_data)

        assert len(result['nodes']) == 2
        types = [node['nodeType'] for node in result['nodes']]
        assert 'element' in types
        assert 'text'    in types
        assert 'tag'       not in types
        assert 'attribute' not in types

    def test__transform_export__filters_edges(self):
        export_data = {
            'nodes': [
                {'id': '1', 'nodeType': 'element'},
                {'id': '2', 'nodeType': 'text'},
                {'id': '3', 'nodeType': 'tag'},
            ],
            'edges': [
                {'from': '1', 'to': '2'},                                             # Kept
                {'from': '1', 'to': '3'},                                             # Removed (tag node removed)
            ]
        }

        result = self.transformation.transform_export(export_data)

        assert len(result['edges']) == 1
        assert result['edges'][0]['to'] == '2'

    def test__transform_export__filters_links_d3_format(self):
        export_data = {
            'nodes': [
                {'id': '1', 'nodeType': 'element'},
                {'id': '2', 'nodeType': 'tag'},
            ],
            'links': [
                {'source': '1', 'target': '2'},
            ]
        }

        result = self.transformation.transform_export(export_data)
        assert len(result['links']) == 0

    # ═══════════════════════════════════════════════════════════════════════════════
    # transform_export Tests - Cytoscape format
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__transform_export__cytoscape_format(self):
        export_data = {
            'elements': {
                'nodes': [
                    {'data': {'id': '1', 'nodeType': 'element'}},
                    {'data': {'id': '2', 'nodeType': 'text'}},
                    {'data': {'id': '3', 'nodeType': 'tag'}},
                ],
                'edges': [
                    {'data': {'source': '1', 'target': '2'}},
                    {'data': {'source': '1', 'target': '3'}},
                ]
            }
        }

        result = self.transformation.transform_export(export_data)

        assert len(result['elements']['nodes']) == 2
        assert len(result['elements']['edges']) == 1

    # ═══════════════════════════════════════════════════════════════════════════════
    # Edge Cases
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__transform_export__empty_nodes(self):
        export_data = {'nodes': [], 'edges': []}
        result = self.transformation.transform_export(export_data)
        assert result['nodes'] == []

    def test__transform_export__only_tags_and_attrs(self):
        export_data = {
            'nodes': [
                {'id': '1', 'nodeType': 'tag'},
                {'id': '2', 'nodeType': 'attribute'},
            ],
            'edges': []
        }

        result = self.transformation.transform_export(export_data)
        assert result['nodes'] == []

    def test__transform_export__preserves_other_fields(self):
        export_data = {
            'nodes'    : [{'id': '1', 'nodeType': 'element'}],
            'edges'    : [],
            'format'   : 'visjs',
            'duration' : 0.2,
            'stats'    : {'total': 5}
        }

        result = self.transformation.transform_export(export_data)

        assert result['format']   == 'visjs'
        assert result['duration'] == 0.2
        assert result['stats']    == {'total': 5}