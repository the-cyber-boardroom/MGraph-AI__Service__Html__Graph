from unittest                                                                   import TestCase
from osbot_utils.utils.Env                                                      import in_github_action
from osbot_utils.helpers.duration.decorators.capture_duration                   import capture_duration
from osbot_utils.testing.__                                                     import __
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.utils.Objects                                                  import base_classes
from mgraph_db.mgraph.MGraph                                                    import MGraph
from mgraph_ai_service_html_graph.service.html_graph.Html_Dict__To__Html_MGraph import Html_Dict__To__Html_MGraph
from mgraph_ai_service_html_graph.service.html_graph.Html_MGraph__Path          import Html_MGraph__Path
from mgraph_db.utils.testing.mgraph_test_ids                                    import mgraph_test_ids


class test_Html_Dict__To__Html_MGraph(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.converter = Html_Dict__To__Html_MGraph()

        cls.simple_html_dict = { 'tag'        : 'div'                                      ,   # Simple HTML dict for testing
                                 'attrs'      : {'class': 'main', 'id': 'content'}         ,
                                 'child_nodes': []                                         ,
                                 'text_nodes' : [{'data': 'Hello World', 'position': 0}]   }

        cls.nested_html_dict = { 'tag'        : 'div'                                      ,   # Nested HTML dict with children
                                 'attrs'      : {'class': 'container'}                     ,
                                 'child_nodes': [
                                     { 'tag'        : 'p'                                  ,
                                       'attrs'      : {}                                   ,
                                       'child_nodes': []                                   ,
                                       'text_nodes' : [{'data': 'First paragraph', 'position': 0}],
                                       'position'   : 0                                    },
                                     { 'tag'        : 'p'                                  ,
                                       'attrs'      : {}                                   ,
                                       'child_nodes': []                                   ,
                                       'text_nodes' : [{'data': 'Second paragraph', 'position': 0}],
                                       'position'   : 1                                    }
                                 ],
                                 'text_nodes' : []                                         }

        cls.mixed_content_dict = { 'tag'        : 'div'                                    ,   # Mixed content with text and elements
                                   'attrs'      : {}                                       ,
                                   'child_nodes': [
                                       { 'tag'        : 'span'                             ,
                                         'attrs'      : {}                                 ,
                                         'child_nodes': []                                 ,
                                         'text_nodes' : [{'data': 'middle', 'position': 0}],
                                         'position'   : 1                                  }
                                   ],
                                   'text_nodes' : [
                                       {'data': 'before', 'position': 0},
                                       {'data': 'after' , 'position': 2}
                                   ]}

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                     # Test auto-initialization
        with Html_Dict__To__Html_MGraph() as _:
            assert type(_)            is Html_Dict__To__Html_MGraph
            assert base_classes(_)    == [Type_Safe, object]
            assert _.mgraph           is None                                   # Not initialized until convert()
            assert type(_.path_utils) is Html_MGraph__Path
            assert type(_.tag_cache)  is dict
            assert _.tag_cache        == {}

    # ═══════════════════════════════════════════════════════════════════════════════
    # convert Tests - Basic
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_convert__returns_mgraph(self):                                     # Test convert returns MGraph
        with mgraph_test_ids():
            converter = Html_Dict__To__Html_MGraph()
            result    = converter.convert(self.simple_html_dict)
            assert type(result) is MGraph
            assert result.data().nodes_ids()       is not None
            assert result.data().edges_ids()       is not None
            assert result.graph_model_data().obj() ==__(graph_data=None,
                                                        graph_path=None,
                                                        graph_type=None,
                                                        schema_types=None,
                                                        edges=__(e0000001=__(edge_data=None,
                                                                             edge_type='mgraph_db.mgraph.schemas.Schema__MGraph__Edge.Schema__MGraph__Edge',
                                                                             edge_label=__(incoming  = None,
                                                                                           outgoing  = None,
                                                                                           predicate = 'tag'),
                                                                            edge_path=None,
                                                                            from_node_id='c0000001',
                                                                            to_node_id='c0000002',
                                                                            edge_id='e0000001'),
                                                                e0000002=__(edge_data=None,
                                                                            edge_type='mgraph_db.mgraph.schemas.Schema__MGraph__Edge.Schema__MGraph__Edge',
                                                                            edge_label=__(incoming=None,
                                                                                          outgoing=None,
                                                                                          predicate='attr'),
                                                                            edge_path='class',
                                                                            from_node_id='c0000001',
                                                                            to_node_id='c0000003',
                                                                            edge_id='e0000002'),
                                                                e0000003=__(edge_data=None,
                                                                            edge_type='mgraph_db.mgraph.schemas.Schema__MGraph__Edge.Schema__MGraph__Edge',
                                                                            edge_label=__(incoming=None,
                                                                                          outgoing=None,
                                                                                          predicate='attr'),
                                                                            edge_path    ='id',
                                                                            from_node_id ='c0000001',
                                                                            to_node_id   ='c0000004',
                                                                            edge_id      ='e0000003'),
                                                                e0000004=__(edge_data=None,
                                                                            edge_type='mgraph_db.mgraph.schemas.Schema__MGraph__Edge.Schema__MGraph__Edge',
                                                                            edge_label=__(incoming=None,
                                                                                          outgoing=None,
                                                                                          predicate='text'),
                                                                            edge_path='0',
                                                                            from_node_id ='c0000001',
                                                                            to_node_id   ='c0000005',
                                                                            edge_id      ='e0000004')),
                                                       graph_id='a0000001',
                                                       nodes=__(c0000001=__(node_data=None,
                                                                            node_path='div',
                                                                            node_type='mgraph_db.mgraph.schemas.Schema__MGraph__Node.Schema__MGraph__Node',
                                                                            node_id='c0000001'),
                                                                c0000002=__(node_data=__(value_type='builtins.str',
                                                                                         value='div',
                                                                                         key=''),
                                                                            node_id='c0000002',
                                                                            node_type='mgraph_db.mgraph.schemas.Schema__MGraph__Node__Value.Schema__MGraph__Node__Value',
                                                                            node_path='tag:div'),
                                                                c0000003=__(node_data=__(value_type='builtins.str',
                                                                                         value='main',
                                                                                         key=''),
                                                                            node_id='c0000003',
                                                                            node_type='mgraph_db.mgraph.schemas.Schema__MGraph__Node__Value.Schema__MGraph__Node__Value',
                                                                            node_path='attr:class'),
                                                                c0000004=__(node_data=__(value_type='builtins.str',
                                                                                         value='content',
                                                                                         key=''),
                                                                            node_id='c0000004',
                                                                            node_type='mgraph_db.mgraph.schemas.Schema__MGraph__Node__Value.Schema__MGraph__Node__Value',
                                                                            node_path='attr:id'),
                                                                c0000005=__(node_data=__(value_type='builtins.str',
                                                                                         value='Hello World',
                                                                                         key=''),
                                                                            node_id='c0000005',
                                                                            node_type='mgraph_db.mgraph.schemas.Schema__MGraph__Node__Value.Schema__MGraph__Node__Value',
                                                                            node_path='text')))

    def test_convert__simple_element(self):                                     # Test converting simple element
        converter = Html_Dict__To__Html_MGraph()
        mgraph    = converter.convert(self.simple_html_dict)

        stats = self._get_graph_stats(mgraph)
        assert stats['element_count'] == 1                                      # One div element
        assert stats['tag_count']     == 1                                      # One tag node (div)
        assert stats['text_count']    == 1                                      # One text node
        assert stats['attr_count']    == 2                                      # Two attributes (class, id)

    def test_convert__nested_elements(self):                                    # Test converting nested elements
        converter = Html_Dict__To__Html_MGraph()
        mgraph    = converter.convert(self.nested_html_dict)

        stats = self._get_graph_stats(mgraph)
        assert stats['element_count'] == 3                                      # div + 2 p elements
        assert stats['tag_count']     == 2                                      # Two unique tags (div, p)
        assert stats['text_count']    == 2                                      # Two text nodes

    def test_convert__mixed_content(self):                                      # Test converting mixed text and elements
        converter = Html_Dict__To__Html_MGraph()
        mgraph    = converter.convert(self.mixed_content_dict)

        stats = self._get_graph_stats(mgraph)
        assert stats['element_count'] == 2                                      # div + span
        assert stats['text_count']    == 3                                      # before, middle, after

    # ═══════════════════════════════════════════════════════════════════════════════
    # convert Tests - Node Paths
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_convert__element_node_paths(self):                                 # Test element nodes have correct paths
        converter = Html_Dict__To__Html_MGraph()
        mgraph    = converter.convert(self.nested_html_dict)

        element_paths = self._get_element_paths(mgraph)
        assert 'div'      in element_paths                                      # Root element
        assert 'div.p[0]' in element_paths                                      # First p (indexed because multiple p)
        assert 'div.p[1]' in element_paths                                      # Second p

    def test_convert__tag_value_node_paths(self):                               # Test tag value nodes have correct paths
        converter = Html_Dict__To__Html_MGraph()
        mgraph    = converter.convert(self.nested_html_dict)

        value_paths = self._get_value_node_paths(mgraph)
        assert 'tag:div' in value_paths
        assert 'tag:p'   in value_paths

    def test_convert__attr_value_node_paths(self):                              # Test attribute value nodes have correct paths
        converter = Html_Dict__To__Html_MGraph()
        mgraph    = converter.convert(self.simple_html_dict)

        value_paths = self._get_value_node_paths(mgraph)
        assert 'attr:class' in value_paths
        assert 'attr:id'    in value_paths

    def test_convert__text_value_node_paths(self):                              # Test text value nodes have correct paths
        converter = Html_Dict__To__Html_MGraph()
        mgraph    = converter.convert(self.simple_html_dict)

        value_paths = self._get_value_node_paths(mgraph)
        assert 'text' in value_paths

    # ═══════════════════════════════════════════════════════════════════════════════
    # convert Tests - Edge Predicates
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_convert__tag_edges(self):                                          # Test edges to tag nodes
        converter  = Html_Dict__To__Html_MGraph()
        mgraph     = converter.convert(self.simple_html_dict)
        predicates = self._get_edge_predicates(mgraph)

        assert 'tag' in predicates

    def test_convert__attr_edges(self):                                         # Test edges to attribute nodes
        converter  = Html_Dict__To__Html_MGraph()
        mgraph     = converter.convert(self.simple_html_dict)
        predicates = self._get_edge_predicates(mgraph)

        assert 'attr' in predicates

    def test_convert__child_edges(self):                                        # Test edges to child elements
        converter  = Html_Dict__To__Html_MGraph()
        mgraph     = converter.convert(self.nested_html_dict)
        predicates = self._get_edge_predicates(mgraph)

        assert 'child' in predicates

    def test_convert__text_edges(self):                                         # Test edges to text nodes
        converter  = Html_Dict__To__Html_MGraph()
        mgraph     = converter.convert(self.simple_html_dict)
        predicates = self._get_edge_predicates(mgraph)

        assert 'text' in predicates

    # ═══════════════════════════════════════════════════════════════════════════════
    # convert Tests - Edge Paths (Positions)
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_convert__child_edge_positions(self):                               # Test child edges have position in edge_path
        converter  = Html_Dict__To__Html_MGraph()
        mgraph     = converter.convert(self.nested_html_dict)
        edge_paths = self._get_child_edge_paths(mgraph)

        assert '0' in edge_paths                                                # First child at position 0
        assert '1' in edge_paths                                                # Second child at position 1

    def test_convert__text_edge_positions(self):                                # Test text edges have position in edge_path
        converter  = Html_Dict__To__Html_MGraph()
        mgraph     = converter.convert(self.mixed_content_dict)
        edge_paths = self._get_text_edge_paths(mgraph)

        assert '0' in edge_paths                                                # Text at position 0
        assert '2' in edge_paths                                                # Text at position 2

    def test_convert__attr_edge_names(self):                                    # Test attribute edges have attr name in edge_path
        converter  = Html_Dict__To__Html_MGraph()
        mgraph     = converter.convert(self.simple_html_dict)
        edge_paths = self._get_attr_edge_paths(mgraph)

        assert 'class' in edge_paths
        assert 'id'    in edge_paths

    # ═══════════════════════════════════════════════════════════════════════════════
    # Value Node Deduplication Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_convert__tag_deduplication(self):                                  # Test same tags share same value node
        converter = Html_Dict__To__Html_MGraph()
        mgraph    = converter.convert(self.nested_html_dict)

        tag_nodes = self._count_nodes_with_path_prefix(mgraph, 'tag:p')
        assert tag_nodes == 1                                                   # Only one 'p' tag node despite two <p> elements

    # ═══════════════════════════════════════════════════════════════════════════════
    # Performance tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__performance__mgraph_convert_performance(self):
        with mgraph_test_ids():
            converter = Html_Dict__To__Html_MGraph()
            max = 2
            with capture_duration(precision=3) as duration:
                for i in range(0,max):
                    converter.convert(self.simple_html_dict)
            if in_github_action():
                assert duration.seconds < 0.5
            else:
                assert duration.seconds < 0.2           # locally this is about 0.035
            # --------------------------------------
            # stats for ghost ids bug in Type_Safe
            # --------------------------------------
            #       before fix       | after fix
            # --------------------------------------
            #   1 - 0.006 seconds    | 0.003 seconds
            #  10 - 0.06 seconds     | 0.033 seconds
            #  50 - 0.300 seconds    | 0.163 seconds
            # 100 - 0.615 seconds    | 0.315 seconds
            # 200 - 1.235 seconds    | 0.649 seconds


    # ═══════════════════════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def _get_graph_stats(self, mgraph: MGraph) -> dict:                         # Get statistics about the graph
        element_count = 0
        tag_count     = 0
        text_count    = 0
        attr_count    = 0

        for node_id in mgraph.data().nodes_ids():
            node      = mgraph.data().node(node_id).node
            node_path = str(node.data.node_path) if node.data.node_path else ''

            if node_path.startswith('tag:'):
                tag_count += 1
            elif node_path.startswith('attr:'):
                attr_count += 1
            elif node_path == 'text':
                text_count += 1
            else:
                element_count += 1

        return { 'element_count': element_count ,
                 'tag_count'    : tag_count     ,
                 'text_count'   : text_count    ,
                 'attr_count'   : attr_count    }

    def _get_element_paths(self, mgraph: MGraph) -> list:                       # Get all element node paths
        paths = []
        for node_id in mgraph.data().nodes_ids():
            node      = mgraph.data().node(node_id).node
            node_path = str(node.data.node_path) if node.data.node_path else ''
            if node_path and not node_path.startswith(('tag:', 'attr:', 'text')):
                paths.append(node_path)
        return paths

    def _get_value_node_paths(self, mgraph: MGraph) -> list:                    # Get all value node paths
        paths = []
        for node_id in mgraph.data().nodes_ids():
            node      = mgraph.data().node(node_id).node
            node_path = str(node.data.node_path) if node.data.node_path else ''
            if node_path.startswith(('tag:', 'attr:', 'text')):
                paths.append(node_path)
        return paths

    def _get_edge_predicates(self, mgraph: MGraph) -> list:                     # Get all edge predicates
        predicates = []
        for edge_id in mgraph.data().edges_ids():
            edge = mgraph.data().edge(edge_id).edge
            if edge and edge.data.edge_label and edge.data.edge_label.predicate:
                predicates.append(str(edge.data.edge_label.predicate))
        return predicates

    def _get_child_edge_paths(self, mgraph: MGraph) -> list:                    # Get edge_path values for child edges
        paths = []
        for edge_id in mgraph.data().edges_ids():
            edge = mgraph.data().edge(edge_id).edge
            if edge and edge.data.edge_label and edge.data.edge_label.predicate:
                if str(edge.data.edge_label.predicate) == 'child':
                    if edge.data.edge_path:
                        paths.append(str(edge.data.edge_path))
        return paths

    def _get_text_edge_paths(self, mgraph: MGraph) -> list:                     # Get edge_path values for text edges
        paths = []
        for edge_id in mgraph.data().edges_ids():
            edge = mgraph.data().edge(edge_id).edge
            if edge and edge.data.edge_label and edge.data.edge_label.predicate:
                if str(edge.data.edge_label.predicate) == 'text':
                    if edge.data.edge_path:
                        paths.append(str(edge.data.edge_path))
        return paths

    def _get_attr_edge_paths(self, mgraph: MGraph) -> list:                     # Get edge_path values for attr edges
        paths = []
        for edge_id in mgraph.data().edges_ids():
            edge = mgraph.data().edge(edge_id).edge
            if edge and edge.data.edge_label and edge.data.edge_label.predicate:
                if str(edge.data.edge_label.predicate) == 'attr':
                    if edge.data.edge_path:
                        paths.append(str(edge.data.edge_path))
        return paths

    def _count_nodes_with_path_prefix(self, mgraph: MGraph, prefix: str) -> int:  # Count nodes with path starting with prefix
        count = 0
        for node_id in mgraph.data().nodes_ids():
            node      = mgraph.data().node(node_id).node
            node_path = str(node.data.node_path) if node.data.node_path else ''
            if node_path.startswith(prefix):
                count += 1
        return count