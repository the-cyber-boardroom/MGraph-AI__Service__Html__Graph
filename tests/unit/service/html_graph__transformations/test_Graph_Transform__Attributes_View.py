from unittest                                                                                           import TestCase
from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe
from osbot_utils.utils.Objects                                                                          import base_classes
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                                       import Html_MGraph
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base        import Graph_Transformation__Base
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transform__Attributes_View  import Graph_Transform__Attributes_View


class test_Graph_Transform__Attributes_View(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.transformation = Graph_Transform__Attributes_View()
        cls.simple_html    = '<div class="main" id="content">Hello</div>'
        cls.html_mgraph    = Html_MGraph.from_html(cls.simple_html)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):
        with self.transformation as _:
            assert type(_)         is Graph_Transform__Attributes_View
            assert base_classes(_) == [Graph_Transformation__Base, Type_Safe, object]
            assert _.name          == 'attributes_view'
            assert _.label         == 'Attributes View'

    def test__metadata(self):
        assert 'attribute' in self.transformation.description.lower()

    # ═══════════════════════════════════════════════════════════════════════════════
    # transform_export Tests - Filter by source
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__transform_export__filters_by_attrs_source(self):
        export_data = {
            'nodes': [
                {'id': '1', 'label': 'div',   'graph_source': 'body'},
                {'id': '2', 'label': 'class', 'graph_source': 'attrs'},
                {'id': '3', 'label': 'id',    'graph_source': 'attrs'},
                {'id': '4', 'label': 'Hello', 'graph_source': 'body'},
            ],
            'edges': []
        }

        result = self.transformation.transform_export(export_data)

        assert len(result['nodes']) == 2
        sources = [node['graph_source'] for node in result['nodes']]
        assert all(s == 'attrs' for s in sources)

    def test__transform_export__includes_tag_nodeType(self):
        export_data = {
            'nodes': [
                {'id': '1', 'label': 'div',   'nodeType': 'element'},
                {'id': '2', 'label': '<div>', 'nodeType': 'tag'},
                {'id': '3', 'label': 'class', 'nodeType': 'attribute'},
                {'id': '4', 'label': 'Hello', 'nodeType': 'text'},
            ],
            'edges': []
        }

        result = self.transformation.transform_export(export_data)

        assert len(result['nodes']) == 2
        types = [node['nodeType'] for node in result['nodes']]
        assert 'tag'       in types
        assert 'attribute' in types

    def test__transform_export__filters_edges(self):
        export_data = {
            'nodes': [
                {'id': '1', 'graph_source': 'body'},
                {'id': '2', 'graph_source': 'attrs'},
                {'id': '3', 'graph_source': 'attrs'},
            ],
            'edges': [
                {'from': '1', 'to': '2'},                                             # body to attrs - removed
                {'from': '2', 'to': '3'},                                             # attrs to attrs - kept
            ]
        }

        result = self.transformation.transform_export(export_data)

        assert len(result['edges']) == 1
        assert result['edges'][0]['from'] == '2'
        assert result['edges'][0]['to']   == '3'

    def test__transform_export__filters_links_d3_format(self):
        export_data = {
            'nodes': [
                {'id': '1', 'graph_source': 'body'},
                {'id': '2', 'graph_source': 'attrs'},
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
                    {'data': {'id': '1', 'graph_source': 'body'}},
                    {'data': {'id': '2', 'graph_source': 'attrs'}},
                    {'data': {'id': '3', 'nodeType': 'tag'}},
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
    # Edge Cases
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__transform_export__empty_nodes(self):
        export_data = {'nodes': [], 'edges': []}
        result = self.transformation.transform_export(export_data)
        assert result['nodes'] == []

    def test__transform_export__no_attrs(self):
        export_data = {
            'nodes': [
                {'id': '1', 'graph_source': 'body'},
                {'id': '2', 'graph_source': 'head'},
            ],
            'edges': []
        }

        result = self.transformation.transform_export(export_data)
        assert result['nodes'] == []

    def test__transform_export__mixed_sources_and_types(self):
        export_data = {
            'nodes': [
                {'id': '1', 'graph_source': 'body',  'nodeType': 'element'},
                {'id': '2', 'graph_source': 'attrs', 'nodeType': 'tag'},
                {'id': '3', 'graph_source': 'body',  'nodeType': 'attribute'},        # Should match nodeType
                {'id': '4', 'graph_source': 'head',  'nodeType': 'text'},
            ],
            'edges': []
        }

        result = self.transformation.transform_export(export_data)

        assert len(result['nodes']) == 2
        ids = [node['id'] for node in result['nodes']]
        assert '2' in ids                                                             # attrs source
        assert '3' in ids                                                             # attribute nodeType

    def test__transform_export__preserves_other_fields(self):
        export_data = {
            'nodes'    : [{'id': '1', 'graph_source': 'attrs'}],
            'edges'    : [],
            'format'   : 'd3',
            'duration' : 0.3,
        }

        result = self.transformation.transform_export(export_data)

        assert result['format']   == 'd3'
        assert result['duration'] == 0.3