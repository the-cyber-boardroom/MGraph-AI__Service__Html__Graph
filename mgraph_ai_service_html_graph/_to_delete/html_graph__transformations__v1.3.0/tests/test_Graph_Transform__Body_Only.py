from unittest                                                                                     import TestCase
from osbot_utils.type_safe.Type_Safe                                                              import Type_Safe
from osbot_utils.utils.Objects                                                                    import base_classes
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                                 import Html_MGraph
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base  import Graph_Transformation__Base
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transform__Body_Only  import Graph_Transform__Body_Only


class test_Graph_Transform__Body_Only(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.transformation = Graph_Transform__Body_Only()
        cls.simple_html    = '<html><head><title>Test</title></head><body><div>Content</div></body></html>'
        cls.html_mgraph    = Html_MGraph.from_html(cls.simple_html)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):
        with self.transformation as _:
            assert type(_)         is Graph_Transform__Body_Only
            assert base_classes(_) == [Graph_Transformation__Base, Type_Safe, object]
            assert _.name          == 'body_only'
            assert _.label         == 'Body Only'

    def test__metadata(self):
        assert 'body'   in self.transformation.description.lower()
        assert 'head'   in self.transformation.description.lower()

    # ═══════════════════════════════════════════════════════════════════════════════
    # transform_export Tests - vis.js/D3 format
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__transform_export__filters_nodes_by_source(self):
        export_data = {
            'nodes': [
                {'id': '1', 'label': 'head',  'graph_source': 'head'},
                {'id': '2', 'label': 'body',  'graph_source': 'body'},
                {'id': '3', 'label': 'div',   'graph_source': 'body'},
                {'id': '4', 'label': 'class', 'graph_source': 'attrs'},
            ],
            'edges': []
        }

        result = self.transformation.transform_export(export_data)

        assert len(result['nodes']) == 2
        sources = [node['graph_source'] for node in result['nodes']]
        assert all(s == 'body' for s in sources)

    def test__transform_export__filters_edges_to_remaining_nodes(self):
        export_data = {
            'nodes': [
                {'id': '1', 'label': 'head', 'graph_source': 'head'},
                {'id': '2', 'label': 'body', 'graph_source': 'body'},
                {'id': '3', 'label': 'div',  'graph_source': 'body'},
            ],
            'edges': [
                {'from': '1', 'to': '2'},                                             # head to body - should be removed
                {'from': '2', 'to': '3'},                                             # body to div - should remain
            ]
        }

        result = self.transformation.transform_export(export_data)

        assert len(result['edges']) == 1
        assert result['edges'][0]['from'] == '2'
        assert result['edges'][0]['to']   == '3'

    def test__transform_export__filters_links_d3_format(self):
        export_data = {
            'nodes': [
                {'id': '1', 'label': 'head', 'graph_source': 'head'},
                {'id': '2', 'label': 'body', 'graph_source': 'body'},
            ],
            'links': [
                {'source': '1', 'target': '2'},
                {'source': '2', 'target': '3'},
            ]
        }

        result = self.transformation.transform_export(export_data)

        assert 'links' in result
        # Only body node remains, so no valid links
        assert len(result['links']) == 0

    # ═══════════════════════════════════════════════════════════════════════════════
    # transform_export Tests - Cytoscape format
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__transform_export__cytoscape_format(self):
        export_data = {
            'elements': {
                'nodes': [
                    {'data': {'id': '1', 'graph_source': 'head'}},
                    {'data': {'id': '2', 'graph_source': 'body'}},
                    {'data': {'id': '3', 'graph_source': 'body'}},
                ],
                'edges': [
                    {'data': {'source': '1', 'target': '2'}},
                    {'data': {'source': '2', 'target': '3'}},
                ]
            }
        }

        result = self.transformation.transform_export(export_data)

        assert len(result['elements']['nodes']) == 2
        assert len(result['elements']['edges']) == 1

    # ═══════════════════════════════════════════════════════════════════════════════
    # Empty/Edge Cases
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__transform_export__empty_nodes(self):
        export_data = {'nodes': [], 'edges': []}
        result = self.transformation.transform_export(export_data)
        assert result['nodes'] == []
        assert result['edges'] == []

    def test__transform_export__no_body_nodes(self):
        export_data = {
            'nodes': [
                {'id': '1', 'graph_source': 'head'},
                {'id': '2', 'graph_source': 'attrs'},
            ],
            'edges': []
        }

        result = self.transformation.transform_export(export_data)
        assert result['nodes'] == []

    def test__transform_export__preserves_other_fields(self):
        export_data = {
            'nodes'    : [{'id': '1', 'graph_source': 'body'}],
            'edges'    : [],
            'format'   : 'visjs',
            'duration' : 0.5,
            'stats'    : {'total': 10}
        }

        result = self.transformation.transform_export(export_data)

        assert result['format']   == 'visjs'
        assert result['duration'] == 0.5
        assert result['stats']    == {'total': 10}