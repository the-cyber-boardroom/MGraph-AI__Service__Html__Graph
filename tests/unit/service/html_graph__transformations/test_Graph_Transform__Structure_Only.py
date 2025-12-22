from unittest                                                                                         import TestCase
from osbot_utils.type_safe.Type_Safe                                                                  import Type_Safe
from osbot_utils.utils.Objects                                                                        import base_classes
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                                     import Html_MGraph
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base      import Graph_Transformation__Base
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transform__Structure_Only import Graph_Transform__Structure_Only


class test_Graph_Transform__Structure_Only(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.transformation = Graph_Transform__Structure_Only()
        cls.simple_html    = '<div><p>Hello</p><span>World</span></div>'
        cls.html_mgraph    = Html_MGraph.from_html(cls.simple_html)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):
        with self.transformation as _:
            assert type(_)         is Graph_Transform__Structure_Only
            assert base_classes(_) == [Graph_Transformation__Base, Type_Safe, object]
            assert _.name          == 'structure_only'
            assert _.label         == 'Structure Only'

    def test__metadata(self):
        assert 'structure' in self.transformation.description.lower()
        assert 'd3'        in self.transformation.description.lower()

    # ═══════════════════════════════════════════════════════════════════════════════
    # transform_export Tests - Filter to elements only
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__transform_export__filters_to_element_nodes(self):
        export_data = {
            'nodes': [
                {'id': '1', 'label': 'div',   'nodeType': 'element', 'tag': 'div'},
                {'id': '2', 'label': 'Hello', 'nodeType': 'text'},
                {'id': '3', 'label': 'p',     'nodeType': 'element', 'tag': 'p'},
                {'id': '4', 'label': 'class', 'nodeType': 'attribute'},
            ],
            'edges': []
        }

        result = self.transformation.transform_export(export_data)

        assert len(result['nodes']) == 2
        types = [node['nodeType'] for node in result['nodes']]
        assert all(t == 'element' for t in types)

    def test__transform_export__simplifies_node_structure(self):
        export_data = {
            'nodes': [
                {'id': '1', 'label': 'my-div', 'nodeType': 'element', 'tag': 'div',
                 'extra_field': 'value', 'graph_source': 'body', 'depth': 2}
            ],
            'edges': []
        }

        result = self.transformation.transform_export(export_data)
        node   = result['nodes'][0]

        assert node['id']    == '1'
        assert node['label'] == 'div'                                                 # Uses tag as label
        assert node['tag']   == 'div'

    def test__transform_export__filters_edges(self):
        export_data = {
            'nodes': [
                {'id': '1', 'nodeType': 'element'},
                {'id': '2', 'nodeType': 'text'},
                {'id': '3', 'nodeType': 'element'},
            ],
            'edges': [
                {'from': '1', 'to': '2'},                                             # Element to text - removed
                {'from': '1', 'to': '3'},                                             # Element to element - kept
            ]
        }

        result = self.transformation.transform_export(export_data)

        assert len(result['edges']) == 1
        assert result['edges'][0]['from'] == '1'
        assert result['edges'][0]['to']   == '3'

    def test__transform_export__filters_links_d3_format(self):
        export_data = {
            'nodes': [
                {'id': '1', 'nodeType': 'element'},
                {'id': '2', 'nodeType': 'text'},
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
                    {'data': {'id': '1', 'nodeType': 'element', 'tag': 'div'}},
                    {'data': {'id': '2', 'nodeType': 'text'}},
                ],
                'edges': [
                    {'data': {'source': '1', 'target': '2'}},
                ]
            }
        }

        result = self.transformation.transform_export(export_data)

        assert len(result['elements']['nodes']) == 1
        assert len(result['elements']['edges']) == 0

    # ═══════════════════════════════════════════════════════════════════════════════
    # transform_export Tests - Tree format
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__transform_export__tree_format(self):
        export_data = {
            'tree': {
                'id': '1', 'value': 'div', 'type': 'element', 'tag': 'div',
                'children': [
                    {'id': '2', 'value': 'Hello', 'type': 'text', 'children': []},
                    {'id': '3', 'value': 'p', 'type': 'element', 'children': []},
                ]
            }
        }

        result = self.transformation.transform_export(export_data)
        tree   = result['tree']

        assert tree['id'] == '1'
        assert len(tree['children']) == 1                                             # Only element child
        assert tree['children'][0]['id'] == '3'

    def test__transform_export__tree_nested(self):
        export_data = {
            'tree': {
                'id': '1', 'type': 'element', 'nodeType': 'element',
                'children': [
                    {'id': '2', 'type': 'element', 'nodeType': 'element',
                     'children': [
                         {'id': '3', 'type': 'text', 'children': []},
                     ]},
                ]
            }
        }

        result = self.transformation.transform_export(export_data)
        tree   = result['tree']

        assert len(tree['children']) == 1
        assert len(tree['children'][0]['children']) == 0                              # Text child removed

    # ═══════════════════════════════════════════════════════════════════════════════
    # Edge Cases
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__transform_export__empty_nodes(self):
        export_data = {'nodes': [], 'edges': []}
        result = self.transformation.transform_export(export_data)
        assert result['nodes'] == []

    def test__transform_export__all_text_nodes(self):
        export_data = {
            'nodes': [
                {'id': '1', 'nodeType': 'text'},
                {'id': '2', 'nodeType': 'text'},
            ],
            'edges': []
        }

        result = self.transformation.transform_export(export_data)
        assert result['nodes'] == []