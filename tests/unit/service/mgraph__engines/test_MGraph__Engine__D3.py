# ═══════════════════════════════════════════════════════════════════════════════
# Test: MGraph__Engine__D3
#
# Tests the D3.js force-directed graph rendering engine for MGraph export.
# Validates JSON structure, node/link formatting, and physics config.
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                        import TestCase

from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__D3 import MGraph__Engine__Config__D3
from mgraph_db.utils.testing.mgraph_test_ids import mgraph_test_ids
from osbot_utils.type_safe.Type_Safe                                                 import Type_Safe
from osbot_utils.utils.Objects                                                       import base_classes

from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                    import Html_MGraph
from mgraph_ai_service_html_graph.service.mgraph__engines.MGraph__Engine__Base       import MGraph__Engine__Base
from mgraph_ai_service_html_graph.service.mgraph__engines.MGraph__Engine__D3         import MGraph__Engine__D3



class test_MGraph__Engine__Config__D3(TestCase):

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                      # Test config initialization
        with MGraph__Engine__Config__D3() as _:
            assert type(_) is MGraph__Engine__Config__D3
            assert isinstance(_, Type_Safe)

    def test__default_values(self):                                              # Test default config values
        with MGraph__Engine__Config__D3() as _:
            assert _.charge_strength  == -300.0
            assert _.link_distance    == 100
            assert _.collision_radius == 30
            assert _.center_strength  == 0.1
            assert _.node_radius      == 20
            assert _.include_stats    == True
            assert _.include_types    == True
            assert _.max_label_len    == 50

    def test__custom_values(self):                                               # Test custom config values
        config = MGraph__Engine__Config__D3(
            charge_strength  = -500.0,
            link_distance    = 150   ,
            collision_radius = 50    ,
            node_radius      = 30    ,
        )
        assert config.charge_strength  == -500.0
        assert config.link_distance    == 150
        assert config.collision_radius == 50
        assert config.node_radius      == 30


class test_MGraph__Engine__D3(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.simple_html = '<html><body><div><p>Hello</p><span>World</span></div></body></html>'
        cls.complex_html = '''
            <html>
                <body>
                    <div class="container">
                        <h1>Title</h1>
                        <p>First paragraph</p>
                        <ul><li>Item 1</li><li>Item 2</li></ul>
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
        with MGraph__Engine__D3() as _:
            assert type(_) is MGraph__Engine__D3
            assert isinstance(_, MGraph__Engine__Base)
            assert isinstance(_, Type_Safe)

    def test__init__creates_default_config(self):                                # Test auto-creates config
        with MGraph__Engine__D3() as _:
            assert _.config is not None
            assert type(_.config) is MGraph__Engine__Config__D3

    def test__init__with_mgraph(self):                                           # Test initialization with MGraph
        with MGraph__Engine__D3(mgraph=self.mgraph_simple) as _:
            assert _.mgraph is self.mgraph_simple

    def test__init__with_custom_config(self):                                    # Test initialization with config
        config = MGraph__Engine__Config__D3(node_radius=40)
        with MGraph__Engine__D3(config=config) as _:
            assert _.config is config
            assert _.config.node_radius == 40

    def test__inheritance(self):                                                 # Test inheritance chain
        engine = MGraph__Engine__D3()
        assert base_classes(engine) == [MGraph__Engine__Base, Type_Safe, object]

    # ═══════════════════════════════════════════════════════════════════════════
    # export Tests - Basic Structure
    # ═══════════════════════════════════════════════════════════════════════════

    def test__export__returns_dict(self):                                        # Test export returns dict
        with MGraph__Engine__D3(mgraph=self.mgraph_simple) as _:
            result = _.export()
            assert type(result) is dict

    def test__export__has_required_keys(self):                                   # Test required keys present
        with MGraph__Engine__D3(mgraph=self.mgraph_simple) as _:
            result = _.export()
            assert 'nodes'  in result
            assert 'links'  in result
            assert 'config' in result

    def test__export__includes_stats_by_default(self):                           # Test stats included
        with MGraph__Engine__D3(mgraph=self.mgraph_simple) as _:
            result = _.export()
            assert 'stats' in result

    def test__export__stats_can_be_disabled(self):                               # Test stats disabled
        config = MGraph__Engine__Config__D3(include_stats=False)
        with MGraph__Engine__D3(mgraph=self.mgraph_simple, config=config) as _:
            result = _.export()
            assert 'stats' not in result

    # ═══════════════════════════════════════════════════════════════════════════
    # export Tests - Nodes
    # ═══════════════════════════════════════════════════════════════════════════

    def test__export__nodes_is_list(self):                                       # Test nodes is list
        with MGraph__Engine__D3(mgraph=self.mgraph_simple) as _:
            result = _.export()
            assert type(result['nodes']) is list

    def test__export__nodes_not_empty(self):                                     # Test has nodes
        with MGraph__Engine__D3(mgraph=self.mgraph_simple) as _:
            result = _.export()
            assert len(result['nodes']) > 0

    def test__export__node_has_required_fields(self):                            # Test node required fields
        with MGraph__Engine__D3(mgraph=self.mgraph_simple) as _:
            result = _.export()
            node   = result['nodes'][0]

            assert 'id'     in node
            assert 'label'  in node
            assert 'radius' in node

    def test__export__node_radius_from_config(self):                             # Test radius uses config
        config = MGraph__Engine__Config__D3(node_radius=35)
        with MGraph__Engine__D3(mgraph=self.mgraph_simple, config=config) as _:
            result = _.export()
            for node in result['nodes']:
                assert node['radius'] == 35

    def test__export__node_includes_type(self):                                  # Test node type included
        with MGraph__Engine__D3(mgraph=self.mgraph_simple) as _:
            result = _.export()
            node   = result['nodes'][0]
            assert 'nodeType' in node

    def test__export__node_type_can_be_disabled(self):                           # Test node type disabled
        config = MGraph__Engine__Config__D3(include_types=False)
        with MGraph__Engine__D3(mgraph=self.mgraph_simple, config=config) as _:
            result = _.export()
            node   = result['nodes'][0]
            assert 'nodeType' not in node

    def test__export__node_has_text_content(self):                               # Test text in labels
        with MGraph__Engine__D3(mgraph=self.mgraph_simple) as _:
            result = _.export()
            labels = [n['label'] for n in result['nodes']]
            assert 'Hello' in labels or 'World' in labels

    # ═══════════════════════════════════════════════════════════════════════════
    # export Tests - Links
    # ═══════════════════════════════════════════════════════════════════════════

    def test__export__links_is_list(self):                                       # Test links is list
        with MGraph__Engine__D3(mgraph=self.mgraph_simple) as _:
            result = _.export()
            assert type(result['links']) is list

    def test__export__links_not_empty(self):                                     # Test has links
        with MGraph__Engine__D3(mgraph=self.mgraph_simple) as _:
            result = _.export()
            assert len(result['links']) > 0

    def test__export__link_has_required_fields(self):                            # Test link required fields
        with MGraph__Engine__D3(mgraph=self.mgraph_simple) as _:
            result = _.export()
            link   = result['links'][0]

            assert 'source'   in link
            assert 'target'   in link
            assert 'distance' in link

    def test__export__link_distance_from_config(self):                           # Test distance uses config
        config = MGraph__Engine__Config__D3(link_distance=200)
        with MGraph__Engine__D3(mgraph=self.mgraph_simple, config=config) as _:
            result = _.export()
            for link in result['links']:
                assert link['distance'] == 200

    def test__export__link_source_target_match_nodes(self):                      # Test links reference nodes
        with MGraph__Engine__D3(mgraph=self.mgraph_simple) as _:
            result   = _.export()
            node_ids = {n['id'] for n in result['nodes']}

            for link in result['links']:
                assert link['source'] in node_ids
                assert link['target'] in node_ids

    # ═══════════════════════════════════════════════════════════════════════════
    # export Tests - Config Output
    # ═══════════════════════════════════════════════════════════════════════════

    def test__export__config_has_physics_params(self):                           # Test physics in config
        with MGraph__Engine__D3(mgraph=self.mgraph_simple) as _:
            result = _.export()
            config = result['config']

            assert 'chargeStrength'  in config
            assert 'linkDistance'    in config
            assert 'collisionRadius' in config
            assert 'centerStrength'  in config

    def test__export__config_uses_engine_config(self):                           # Test config values match
        engine_config = MGraph__Engine__Config__D3(
            charge_strength  = -500.0,
            link_distance    = 150   ,
            collision_radius = 40    ,
            center_strength  = 0.2   ,
        )
        with MGraph__Engine__D3(mgraph=self.mgraph_simple, config=engine_config) as _:
            result = _.export()
            config = result['config']

            assert config['chargeStrength']  == -500.0
            assert config['linkDistance']    == 150
            assert config['collisionRadius'] == 40
            assert config['centerStrength']  == 0.2

    # ═══════════════════════════════════════════════════════════════════════════
    # export Tests - Stats
    # ═══════════════════════════════════════════════════════════════════════════

    def test__export__stats_has_counts(self):                                    # Test stats structure
        with MGraph__Engine__D3(mgraph=self.mgraph_simple) as _:
            result = _.export()
            stats  = result['stats']

            assert 'nodeCount' in stats
            assert 'linkCount' in stats

    def test__export__stats_correct_counts(self):                                # Test stats values match
        with MGraph__Engine__D3(mgraph=self.mgraph_simple) as _:
            result = _.export()
            stats  = result['stats']

            assert stats['nodeCount'] == len(result['nodes'])
            assert stats['linkCount'] == len(result['links'])

    # ═══════════════════════════════════════════════════════════════════════════
    # export Tests - Complex Graph
    # ═══════════════════════════════════════════════════════════════════════════

    def test__export__complex_graph_structure(self):                             # Test complex HTML export
        with MGraph__Engine__D3(mgraph=self.mgraph_complex) as _:
            result = _.export()
            assert len(result['nodes']) > 5                                      # Many nodes
            assert len(result['links']) > 5                                      # Many links

    def test__export__complex_graph_text_content(self):                          # Test text content visible
        with MGraph__Engine__D3(mgraph=self.mgraph_complex) as _:
            result = _.export()
            labels = [n['label'] for n in result['nodes']]
            assert any('Title' in str(l) or 'Item' in str(l) for l in labels)

    # ═══════════════════════════════════════════════════════════════════════════
    # export Tests - Empty Graph
    # ═══════════════════════════════════════════════════════════════════════════

    def test__export__minimal_html(self):                                        # Test minimal HTML
        html = '<div></div>'
        with mgraph_test_ids():
            html_mgraph = Html_MGraph.from_html(html)
            mgraph      = html_mgraph.body_graph.mgraph

        with MGraph__Engine__D3(mgraph=mgraph) as _:
            result = _.export()
            assert 'nodes'  in result
            assert 'links'  in result
            assert 'config' in result

    # ═══════════════════════════════════════════════════════════════════════════
    # export Tests - Label Truncation
    # ═══════════════════════════════════════════════════════════════════════════

    def test__export__truncates_long_labels(self):                               # Test label truncation
        long_text = 'A' * 100
        html = f'<html><body><div>{long_text}</div></body></html>'
        with mgraph_test_ids():
            html_mgraph = Html_MGraph.from_html(html)
            mgraph      = html_mgraph.body_graph.mgraph

        config = MGraph__Engine__Config__D3(max_label_len=20)
        with MGraph__Engine__D3(mgraph=mgraph, config=config) as _:
            result = _.export()
            for node in result['nodes']:
                assert len(node['label']) <= 20

    # ═══════════════════════════════════════════════════════════════════════════
    # export Tests - Predictable IDs
    # ═══════════════════════════════════════════════════════════════════════════

    def test__export__consistent_with_mgraph_test_ids(self):                     # Test predictable IDs
        html = '<html><body><div><p>Test</p></div></body></html>'
        with mgraph_test_ids():
            html_mgraph = Html_MGraph.from_html(html)
            mgraph      = html_mgraph.body_graph.mgraph

        with MGraph__Engine__D3(mgraph=mgraph) as _:
            result = _.export()
            # All node IDs should be strings
            for node in result['nodes']:
                assert type(node['id']) is str
                assert len(node['id']) > 0