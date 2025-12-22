# ═══════════════════════════════════════════════════════════════════════════════
# Test: MGraph__Engine__Cytoscape
#
# Tests the Cytoscape.js rendering engine for MGraph export.
# Validates JSON structure with elements/style/layout format.
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                       import TestCase
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__Cytoscape import MGraph__Engine__Config__Cytoscape
from mgraph_db.utils.testing.mgraph_test_ids                                                        import mgraph_test_ids
from osbot_utils.type_safe.Type_Safe                                                                import Type_Safe
from osbot_utils.utils.Objects                                                                      import base_classes
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                                   import Html_MGraph
from mgraph_ai_service_html_graph.service.mgraph__engines.MGraph__Engine__Base                      import MGraph__Engine__Base
from mgraph_ai_service_html_graph.service.mgraph__engines.MGraph__Engine__Cytoscape                 import MGraph__Engine__Cytoscape


class test_MGraph__Engine__Cytoscape(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.simple_html = '<html><body><div><p>Hello</p><span>World</span></div></body></html>'
        cls.complex_html = '''
            <html>
                <body>
                    <div class="container">
                        <h1>Title</h1>
                        <p>First paragraph</p>
                        <p>Second paragraph</p>
                    </div>
                </body>
            </html>
        '''
        with mgraph_test_ids():
            cls.html_mgraph_simple  = Html_MGraph.from_html(cls.simple_html)
            cls.mgraph_simple       = cls.html_mgraph_simple.body_graph.mgraph

            cls.html_mgraph_complex = Html_MGraph.from_html(cls.complex_html)
            cls.mgraph_complex      = cls.html_mgraph_complex.body_graph.mgraph

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                      # Test engine initialization
        with MGraph__Engine__Cytoscape() as _:
            assert type(_) is MGraph__Engine__Cytoscape
            assert isinstance(_, MGraph__Engine__Base)

    def test__init__creates_default_config(self):                                # Test auto-creates config
        with MGraph__Engine__Cytoscape() as _:
            assert _.config is not None
            assert type(_.config) is MGraph__Engine__Config__Cytoscape

    def test__init__with_custom_config(self):                                    # Test custom config
        config = MGraph__Engine__Config__Cytoscape(layout_name='cose')
        with MGraph__Engine__Cytoscape(config=config) as _:
            assert _.config.layout_name == 'cose'

    def test__inheritance(self):                                                 # Test inheritance chain
        engine = MGraph__Engine__Cytoscape()
        assert base_classes(engine) == [MGraph__Engine__Base, Type_Safe, object]

    # ═══════════════════════════════════════════════════════════════════════════
    # export Tests - Basic Structure
    # ═══════════════════════════════════════════════════════════════════════════

    def test__export__returns_dict(self):                                        # Test export returns dict
        with MGraph__Engine__Cytoscape(mgraph=self.mgraph_simple) as _:
            result = _.export()
            assert type(result) is dict

    def test__export__has_elements(self):                                        # Test elements key present
        with MGraph__Engine__Cytoscape(mgraph=self.mgraph_simple) as _:
            result = _.export()
            assert 'elements' in result
            assert 'nodes'    in result['elements']
            assert 'edges'    in result['elements']

    def test__export__has_layout(self):                                          # Test layout key present
        with MGraph__Engine__Cytoscape(mgraph=self.mgraph_simple) as _:
            result = _.export()
            assert 'layout' in result

    def test__export__includes_style_by_default(self):                           # Test style included
        with MGraph__Engine__Cytoscape(mgraph=self.mgraph_simple) as _:
            result = _.export()
            assert 'style' in result

    def test__export__style_can_be_disabled(self):                               # Test style disabled
        config = MGraph__Engine__Config__Cytoscape(include_style=False)
        with MGraph__Engine__Cytoscape(mgraph=self.mgraph_simple, config=config) as _:
            result = _.export()
            assert 'style' not in result

    def test__export__includes_stats_by_default(self):                           # Test stats included
        with MGraph__Engine__Cytoscape(mgraph=self.mgraph_simple) as _:
            result = _.export()
            assert 'stats' in result

    def test__export__stats_can_be_disabled(self):                               # Test stats disabled
        config = MGraph__Engine__Config__Cytoscape(include_stats=False)
        with MGraph__Engine__Cytoscape(mgraph=self.mgraph_simple, config=config) as _:
            result = _.export()
            assert 'stats' not in result

    # ═══════════════════════════════════════════════════════════════════════════
    # export Tests - Nodes
    # ═══════════════════════════════════════════════════════════════════════════

    def test__export__nodes_is_list(self):                                       # Test nodes is list
        with MGraph__Engine__Cytoscape(mgraph=self.mgraph_simple) as _:
            result = _.export()
            assert type(result['elements']['nodes']) is list

    def test__export__nodes_not_empty(self):                                     # Test has nodes
        with MGraph__Engine__Cytoscape(mgraph=self.mgraph_simple) as _:
            result = _.export()
            assert len(result['elements']['nodes']) > 0

    def test__export__node_has_data_wrapper(self):                               # Test Cytoscape data wrapper
        with MGraph__Engine__Cytoscape(mgraph=self.mgraph_simple) as _:
            result = _.export()
            node   = result['elements']['nodes'][0]
            assert 'data' in node

    def test__export__node_data_has_required_fields(self):                       # Test node data fields
        with MGraph__Engine__Cytoscape(mgraph=self.mgraph_simple) as _:
            result = _.export()
            data   = result['elements']['nodes'][0]['data']

            assert 'id'    in data
            assert 'label' in data

    def test__export__node_includes_type(self):                                  # Test nodeType in node data
        with MGraph__Engine__Cytoscape(mgraph=self.mgraph_simple) as _:
            result = _.export()
            data   = result['elements']['nodes'][0]['data']
            assert 'nodeType' in data

    # ═══════════════════════════════════════════════════════════════════════════
    # export Tests - Edges
    # ═══════════════════════════════════════════════════════════════════════════

    def test__export__edges_is_list(self):                                       # Test edges is list
        with MGraph__Engine__Cytoscape(mgraph=self.mgraph_simple) as _:
            result = _.export()
            assert type(result['elements']['edges']) is list

    def test__export__edges_not_empty(self):                                     # Test has edges
        with MGraph__Engine__Cytoscape(mgraph=self.mgraph_simple) as _:
            result = _.export()
            assert len(result['elements']['edges']) > 0

    def test__export__edge_has_data_wrapper(self):                               # Test Cytoscape data wrapper
        with MGraph__Engine__Cytoscape(mgraph=self.mgraph_simple) as _:
            result = _.export()
            edge   = result['elements']['edges'][0]
            assert 'data' in edge

    def test__export__edge_data_has_required_fields(self):                       # Test edge data fields
        with MGraph__Engine__Cytoscape(mgraph=self.mgraph_simple) as _:
            result = _.export()
            data   = result['elements']['edges'][0]['data']

            assert 'id'     in data
            assert 'source' in data
            assert 'target' in data

    def test__export__edge_ids_sequential(self):                                 # Test edge IDs are sequential
        with MGraph__Engine__Cytoscape(mgraph=self.mgraph_simple) as _:
            result = _.export()
            ids    = [e['data']['id'] for e in result['elements']['edges']]
            assert ids[0] == 'e0'                                                # First edge ID

    def test__export__edges_reference_valid_nodes(self):                         # Test edges reference nodes
        with MGraph__Engine__Cytoscape(mgraph=self.mgraph_simple) as _:
            result   = _.export()
            node_ids = {n['data']['id'] for n in result['elements']['nodes']}

            for edge in result['elements']['edges']:
                assert edge['data']['source'] in node_ids
                assert edge['data']['target'] in node_ids

    # ═══════════════════════════════════════════════════════════════════════════
    # export Tests - Layout
    # ═══════════════════════════════════════════════════════════════════════════

    def test__export__layout_has_name(self):                                     # Test layout name
        with MGraph__Engine__Cytoscape(mgraph=self.mgraph_simple) as _:
            result = _.export()
            assert result['layout']['name'] == 'dagre'

    def test__export__dagre_layout_has_rankdir(self):                            # Test dagre rankDir
        with MGraph__Engine__Cytoscape(mgraph=self.mgraph_simple) as _:
            result = _.export()
            assert result['layout']['rankDir'] == 'TB'

    def test__export__layout_respects_config(self):                              # Test layout config
        config = MGraph__Engine__Config__Cytoscape(
            layout_name='cose',
            layout_direction='LR'
        )
        with MGraph__Engine__Cytoscape(mgraph=self.mgraph_simple, config=config) as _:
            result = _.export()
            assert result['layout']['name'] == 'cose'

    # ═══════════════════════════════════════════════════════════════════════════
    # export Tests - Style
    # ═══════════════════════════════════════════════════════════════════════════

    def test__export__style_is_list(self):                                       # Test style is list
        with MGraph__Engine__Cytoscape(mgraph=self.mgraph_simple) as _:
            result = _.export()
            assert type(result['style']) is list

    def test__export__style_has_node_selector(self):                             # Test node style selector
        with MGraph__Engine__Cytoscape(mgraph=self.mgraph_simple) as _:
            result    = _.export()
            selectors = [s['selector'] for s in result['style']]
            assert 'node' in selectors

    def test__export__style_has_edge_selector(self):                             # Test edge style selector
        with MGraph__Engine__Cytoscape(mgraph=self.mgraph_simple) as _:
            result    = _.export()
            selectors = [s['selector'] for s in result['style']]
            assert 'edge' in selectors

    def test__export__node_style_uses_config(self):                              # Test node style from config
        config = MGraph__Engine__Config__Cytoscape(
            node_bg_color='#ff0000',
            node_width=150
        )
        with MGraph__Engine__Cytoscape(mgraph=self.mgraph_simple, config=config) as _:
            result     = _.export()
            node_style = next(s for s in result['style'] if s['selector'] == 'node')

            assert node_style['style']['background-color'] == '#ff0000'
            assert node_style['style']['width'] == 150

    def test__export__edge_style_uses_config(self):                              # Test edge style from config
        config = MGraph__Engine__Config__Cytoscape(
            edge_color='#00ff00',
            edge_width=3
        )
        with MGraph__Engine__Cytoscape(mgraph=self.mgraph_simple, config=config) as _:
            result     = _.export()
            edge_style = next(s for s in result['style'] if s['selector'] == 'edge')

            assert edge_style['style']['line-color'] == '#00ff00'
            assert edge_style['style']['width'] == 3

    # ═══════════════════════════════════════════════════════════════════════════
    # export Tests - Stats
    # ═══════════════════════════════════════════════════════════════════════════

    def test__export__stats_correct_counts(self):                                # Test stats values
        with MGraph__Engine__Cytoscape(mgraph=self.mgraph_simple) as _:
            result = _.export()
            stats  = result['stats']

            assert stats['nodeCount'] == len(result['elements']['nodes'])
            assert stats['edgeCount'] == len(result['elements']['edges'])

    # ═══════════════════════════════════════════════════════════════════════════
    # export Tests - Complex Graph
    # ═══════════════════════════════════════════════════════════════════════════

    def test__export__complex_graph_structure(self):                             # Test complex HTML export
        with MGraph__Engine__Cytoscape(mgraph=self.mgraph_complex) as _:
            result = _.export()
            assert len(result['elements']['nodes']) > 5
            assert len(result['elements']['edges']) > 5

    # ═══════════════════════════════════════════════════════════════════════════
    # export Tests - Empty Graph
    # ═══════════════════════════════════════════════════════════════════════════

    def test__export__minimal_html(self):                                        # Test minimal HTML
        html = '<html><body><div></div></body></html>'
        with mgraph_test_ids():
            html_mgraph = Html_MGraph.from_html(html)
            mgraph      = html_mgraph.body_graph.mgraph

        with MGraph__Engine__Cytoscape(mgraph=mgraph) as _:
            result = _.export()
            assert 'elements' in result
            assert 'layout'   in result