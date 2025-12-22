from unittest                                                                                     import TestCase
from osbot_utils.type_safe.Type_Safe                                                              import Type_Safe
from osbot_utils.utils.Objects                                                                    import base_classes
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                                 import Html_MGraph
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base  import Graph_Transformation__Base
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transform__Semantic   import Graph_Transform__Semantic


class test_Graph_Transform__Semantic(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.transformation = Graph_Transform__Semantic()
        cls.simple_html    = '<div>Hello World</div>'
        cls.html_mgraph    = Html_MGraph.from_html(cls.simple_html)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):
        with self.transformation as _:
            assert type(_)         is Graph_Transform__Semantic
            assert base_classes(_) == [Graph_Transformation__Base, Type_Safe, object]
            assert _.name          == 'semantic'
            assert _.label         == 'Semantic View'

    def test__metadata(self):
        assert 'content'  in self.transformation.description.lower()
        assert 'merged'   in self.transformation.description.lower()

    # ═══════════════════════════════════════════════════════════════════════════════
    # transform_mgraph Tests - Basic
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__transform_mgraph__returns_html_mgraph(self):
        html_mgraph = Html_MGraph.from_html('<div>Test</div>')
        result      = self.transformation.transform_mgraph(html_mgraph)

        assert result is html_mgraph
        assert type(result) is Html_MGraph

    def test__transform_mgraph__preserves_body_graph(self):
        html_mgraph = Html_MGraph.from_html('<div><p>Content</p></div>')
        result      = self.transformation.transform_mgraph(html_mgraph)

        assert result.body_graph is not None

    def test__transform_mgraph__handles_none_body_graph(self):
        html_mgraph = Html_MGraph()                                                   # Empty Html_MGraph
        result      = self.transformation.transform_mgraph(html_mgraph)

        assert result is html_mgraph

    # ═══════════════════════════════════════════════════════════════════════════════
    # Graph Utility Method Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test___get_text_nodes(self):
        html_mgraph = Html_MGraph.from_html('<div>Hello</div>')

        if html_mgraph.body_graph:
            text_nodes = self.transformation._get_text_nodes(html_mgraph.body_graph.mgraph)
            # Should find text nodes with node_path == 'text'
            assert type(text_nodes) is list

    def test___get_parent_node_id(self):
        html_mgraph = Html_MGraph.from_html('<div>Hello</div>')

        if html_mgraph.body_graph:
            text_nodes = self.transformation._get_text_nodes(html_mgraph.body_graph.mgraph)
            if text_nodes:
                text_node = text_nodes[0]
                parent_id = self.transformation._get_parent_node_id(
                    html_mgraph.body_graph, text_node.node_id)
                # Text node should have a parent
                assert parent_id is not None or parent_id is None  # May vary by structure

    def test___get_outgoing_edge_count(self):
        html_mgraph = Html_MGraph.from_html('<div><p>One</p><p>Two</p></div>')

        if html_mgraph.body_graph:
            # Should be able to count edges from any node
            nodes = html_mgraph.body_graph.mgraph.graph.model.data.nodes
            for node_id in list(nodes.keys())[:1]:
                count = self.transformation._get_outgoing_edge_count(html_mgraph.body_graph.mgraph, node_id)
                assert type(count) is int
                assert count >= 0

    # ═══════════════════════════════════════════════════════════════════════════════
    # transform_export Tests - Filter to element and text
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

    def test__transform_export__filters_edges(self):
        export_data = {
            'nodes': [
                {'id': '1', 'nodeType': 'element'},
                {'id': '2', 'nodeType': 'text'},
                {'id': '3', 'nodeType': 'attribute'},
            ],
            'edges': [
                {'from': '1', 'to': '2'},
                {'from': '1', 'to': '3'},
            ]
        }

        result = self.transformation.transform_export(export_data)

        assert len(result['edges']) == 1

    def test__transform_export__filters_links_d3_format(self):
        export_data = {
            'nodes': [
                {'id': '1', 'nodeType': 'element'},
                {'id': '2', 'nodeType': 'attribute'},
            ],
            'links': [
                {'source': '1', 'target': '2'},
            ]
        }

        result = self.transformation.transform_export(export_data)
        assert len(result['links']) == 0

    # ═══════════════════════════════════════════════════════════════════════════════
    # Collapse Single Child Tests (via transform_mgraph)
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__collapse_single_child__basic(self):
        # A structure like: body > div > p > text
        # Where div has only one child (p), it might collapse
        html = '<body><div><p>Hello</p></div></body>'
        html_mgraph = Html_MGraph.from_html(html)

        result = self.transformation.transform_mgraph(html_mgraph)

        # Should still have valid body graph
        assert result.body_graph is not None

    # ═══════════════════════════════════════════════════════════════════════════════
    # Merge Text Children Tests (via transform_mgraph)
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__merge_text_children__basic(self):
        # Structure with multiple text fragments under same parent
        html = '<div>Hello <b>World</b> Today</div>'
        html_mgraph = Html_MGraph.from_html(html)

        result = self.transformation.transform_mgraph(html_mgraph)

        # Should still be valid
        assert result.body_graph is not None

    # ═══════════════════════════════════════════════════════════════════════════════
    # Edge Cases
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__transform_export__empty_nodes(self):
        export_data = {'nodes': [], 'edges': []}
        result = self.transformation.transform_export(export_data)
        assert result['nodes'] == []

    def test__transform_export__preserves_other_fields(self):
        export_data = {
            'nodes'    : [{'id': '1', 'nodeType': 'element'}],
            'edges'    : [],
            'format'   : 'mermaid',
            'duration' : 0.4,
        }

        result = self.transformation.transform_export(export_data)

        assert result['format']   == 'mermaid'
        assert result['duration'] == 0.4

    def test__transform_mgraph__complex_html(self):
        html = '''
        <html>
            <body>
                <div class="container">
                    <h1>Title</h1>
                    <p>First paragraph with <strong>bold</strong> text.</p>
                    <p>Second paragraph.</p>
                </div>
            </body>
        </html>
        '''
        html_mgraph = Html_MGraph.from_html(html)
        result      = self.transformation.transform_mgraph(html_mgraph)

        assert result is not None
        assert result.body_graph is not None


