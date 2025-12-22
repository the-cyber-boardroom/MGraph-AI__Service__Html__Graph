# ═══════════════════════════════════════════════════════════════════════════════
# Test: MGraph__Engine__Base
#
# Tests the base class for MGraph rendering engines, including helper methods
# for node/edge access, styling, and utility functions.
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                    import TestCase

from mgraph_db.mgraph.domain.Domain__MGraph__Edge import Domain__MGraph__Edge
from mgraph_db.mgraph.domain.Domain__MGraph__Node import Domain__MGraph__Node
from mgraph_db.utils.testing.mgraph_test_ids                                     import mgraph_test_ids
from osbot_utils.testing.__ import __
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                import Html_MGraph
from mgraph_ai_service_html_graph.service.mgraph__engines.MGraph__Engine__Base   import MGraph__Engine__Base
from mgraph_ai_service_html_graph.service.mgraph__engines.MGraph__Engine__Base   import MGraph__Engine__Config__Base


class test_MGraph__Engine__Base(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.simple_html = '<html><body><div><p>Hello</p><span>World</span></div></body></html>'
        with mgraph_test_ids():
            cls.html_mgraph = Html_MGraph.from_html(cls.simple_html)
            cls.mgraph      = cls.html_mgraph.body_graph.mgraph                  # Extract MGraph from body_graph

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                      # Test base engine initialization
        with MGraph__Engine__Base() as _:
            assert type(_) is MGraph__Engine__Base
            assert _.mgraph is None
            assert _.config is None

    def test__init__with_mgraph(self):                                           # Test initialization with MGraph
        with MGraph__Engine__Base(mgraph=self.mgraph) as _:
            assert _.mgraph is self.mgraph

    def test__init__with_config(self):                                           # Test initialization with config
        config = MGraph__Engine__Config__Base()
        with MGraph__Engine__Base(config=config) as _:
            assert _.config is config

    def test__inheritance(self):                                                 # Test engine inherits Type_Safe
        engine = MGraph__Engine__Base()
        assert isinstance(engine, Type_Safe)

    # ═══════════════════════════════════════════════════════════════════════════
    # export Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__export__raises_not_implemented(self):                              # Test export must be overridden
        with MGraph__Engine__Base() as _:
            with self.assertRaises(NotImplementedError) as context:
                _.export()
            assert 'Subclasses must implement export()' in str(context.exception)

    # ═══════════════════════════════════════════════════════════════════════════
    # Node/Edge Iteration Helper Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__nodes__returns_list(self):                                         # Test nodes returns list
        with MGraph__Engine__Base(mgraph=self.mgraph) as _:
            result = _.nodes()
            assert type(result)         is list
            assert len(result)          == 7                                               # Has nodes from HTML
            assert type(result[0])      is Domain__MGraph__Node
            assert result[0].node.obj() == __(data=__(node_data=None,
                                                      node_path=None,
                                                      node_type='mgraph_db.mgraph.schemas.Schema__MGraph__Node.Schema__MGraph__Node',
                                                      node_id='c0000003'))

    def test__nodes__empty_when_no_mgraph(self):                                 # Test nodes empty without MGraph
        with MGraph__Engine__Base() as _:
            assert _.nodes() == []

    def test__edges__returns_list(self):                                         # Test edges returns list
        with MGraph__Engine__Base(mgraph=self.mgraph) as _:
            result      = _.edges()
            domain_edge = result[0]
            assert type(result) is list
            assert len(result) == 5                                               # Has edges from HTML
            assert type(domain_edge) is Domain__MGraph__Edge
            assert domain_edge.edge.obj() == __(data=__(edge_data=None,
                                                        edge_type='mgraph_db.mgraph.schemas.Schema__MGraph__Edge.Schema__MGraph__Edge',
                                                        edge_label=__(incoming=None, outgoing=None, predicate='child'),
                                                        edge_path='0',
                                                        from_node_id='c0000016',
                                                        to_node_id='c0000018',
                                                        edge_id='e0000010'))


    def test__edges__empty_when_no_mgraph(self):                                 # Test edges empty without MGraph
        with MGraph__Engine__Base() as _:
            assert _.edges() == []

    def test__node_ids__returns_list(self):                                      # Test node_ids returns list
        with MGraph__Engine__Base(mgraph=self.mgraph) as _:
            result = _.node_ids()
            assert type(result) is list
            assert len(result) > 0

    def test__node_ids__empty_when_no_mgraph(self):                              # Test node_ids empty without MGraph
        with MGraph__Engine__Base() as _:
            assert _.node_ids() == []

    def test__edge_ids__returns_list(self):                                      # Test edge_ids returns list
        with MGraph__Engine__Base(mgraph=self.mgraph) as _:
            result = _.edge_ids()
            assert type(result) is list
            assert len(result) > 0

    def test__edge_ids__empty_when_no_mgraph(self):                              # Test edge_ids empty without MGraph
        with MGraph__Engine__Base() as _:
            assert _.edge_ids() == []

    # ═══════════════════════════════════════════════════════════════════════════
    # Node Data Access Helper Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__node_path__returns_path(self):                                     # Test node_path extracts path
        with MGraph__Engine__Base(mgraph=self.mgraph) as _:
            nodes = _.nodes()
            paths = [_.node_path(n) for n in nodes if _.node_path(n)]
            assert len(paths) > 0                                                # Has nodes with paths

    def test__node_path__returns_none_for_invalid(self):                         # Test node_path handles missing
        with MGraph__Engine__Base() as _:
            assert _.node_path(None)   is None
            assert _.node_path({})     is None
            assert _.node_path('test') is None

    def test__node_value__returns_value_for_text_nodes(self):                    # Test node_value extracts value
        with MGraph__Engine__Base(mgraph=self.mgraph) as _:
            nodes  = _.nodes()
            values = [_.node_value(n) for n in nodes if _.node_value(n)]
            assert 'Hello' in values or 'World' in values                        # Text content from HTML

    def test__node_value__returns_none_for_invalid(self):                        # Test node_value handles missing
        with MGraph__Engine__Base() as _:
            assert _.node_value(None) is None
            assert _.node_value({})   is None

    def test__node_id_str__returns_string(self):                                 # Test node_id_str returns string
        with MGraph__Engine__Base(mgraph=self.mgraph) as _:
            nodes = _.nodes()
            for node in nodes:
                node_id = _.node_id_str(node)
                assert type(node_id) is str
                assert len(node_id) > 0

    def test__node_id_str__fallback_to_id(self):                                 # Test node_id_str fallback
        with MGraph__Engine__Base() as _:
            obj = object()
            result = _.node_id_str(obj)
            assert result == str(id(obj))                                        # Falls back to object id

    # ═══════════════════════════════════════════════════════════════════════════
    # Edge Data Access Helper Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__edge_from_id__returns_source(self):                                # Test edge_from_id extracts source
        with MGraph__Engine__Base(mgraph=self.mgraph) as _:
            edges = _.edges()
            for edge in edges:
                from_id = _.edge_from_id(edge)
                assert type(from_id) is str
                assert len(from_id) > 0

    def test__edge_from_id__returns_empty_for_invalid(self):                     # Test edge_from_id handles missing
        with MGraph__Engine__Base() as _:
            assert _.edge_from_id(None) == ''
            assert _.edge_from_id({})   == ''

    def test__edge_to_id__returns_target(self):                                  # Test edge_to_id extracts target
        with MGraph__Engine__Base(mgraph=self.mgraph) as _:
            edges = _.edges()
            for edge in edges:
                to_id = _.edge_to_id(edge)
                assert type(to_id) is str
                assert len(to_id) > 0

    def test__edge_to_id__returns_empty_for_invalid(self):                       # Test edge_to_id handles missing
        with MGraph__Engine__Base() as _:
            assert _.edge_to_id(None) == ''
            assert _.edge_to_id({})   == ''

    def test__edge_predicate__returns_predicate(self):                           # Test edge_predicate extracts label
        with MGraph__Engine__Base(mgraph=self.mgraph) as _:
            edges      = _.edges()
            predicates = [_.edge_predicate(e) for e in edges if _.edge_predicate(e)]
            assert len(predicates) == 5                                           # Has edges with predicates
            assert predicates      == ['child', 'child', 'text', 'child', 'text']

    def test__edge_predicate__returns_none_for_invalid(self):                    # Test edge_predicate handles missing
        with MGraph__Engine__Base() as _:
            assert _.edge_predicate(None) is None
            assert _.edge_predicate({})   is None

    def test__edge_path__returns_none_for_invalid(self):                         # Test edge_path handles missing
        with MGraph__Engine__Base() as _:
            assert _.edge_path(None) is None
            assert _.edge_path({})   is None

    # ═══════════════════════════════════════════════════════════════════════════
    # Styling Metadata Access Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__get_node_style__returns_default(self):                             # Test get_node_style default
        with MGraph__Engine__Base(mgraph=self.mgraph) as _:
            nodes = _.nodes()
            if nodes:
                result = _.get_node_style(nodes[0], 'missing_key', 'default_value')
                assert result == 'default_value'

    def test__get_node_style__returns_default_for_invalid(self):                 # Test handles invalid node
        with MGraph__Engine__Base() as _:
            assert _.get_node_style(None, 'key', 'default') == 'default'

    def test__get_edge_style__returns_default(self):                             # Test get_edge_style default
        with MGraph__Engine__Base(mgraph=self.mgraph) as _:
            edges = _.edges()
            if edges:
                result = _.get_edge_style(edges[0], 'missing_key', 'default_value')
                assert result == 'default_value'

    def test__get_edge_style__returns_default_for_invalid(self):                 # Test handles invalid edge
        with MGraph__Engine__Base() as _:
            assert _.get_edge_style(None, 'key', 'default') == 'default'

    # ═══════════════════════════════════════════════════════════════════════════
    # Utility Method Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__truncate__no_truncation_needed(self):                              # Test truncate when under limit
        with MGraph__Engine__Base() as _:
            assert _.truncate('Hello', 10) == 'Hello'

    def test__truncate__exactly_at_limit(self):                                  # Test truncate at exact limit
        with MGraph__Engine__Base() as _:
            assert _.truncate('Hello', 5) == 'Hello'

    def test__truncate__truncates_with_ellipsis(self):                           # Test truncate adds ellipsis
        with MGraph__Engine__Base() as _:
            result = _.truncate('Hello World', 8)
            assert result == 'Hello...'
            assert len(result) == 8

    def test__truncate__handles_empty_string(self):                              # Test truncate empty string
        with MGraph__Engine__Base() as _:
            assert _.truncate('', 10) == ''

    def test__truncate__handles_none(self):                                      # Test truncate None
        with MGraph__Engine__Base() as _:
            assert _.truncate(None, 10) == ''

    def test__escape_quotes__escapes_double_quotes(self):                        # Test escape_quotes
        with MGraph__Engine__Base() as _:
            assert _.escape_quotes('Hello "World"') == 'Hello \\"World\\"'

    def test__escape_quotes__no_quotes(self):                                    # Test escape_quotes no quotes
        with MGraph__Engine__Base() as _:
            assert _.escape_quotes('Hello World') == 'Hello World'

    def test__escape_quotes__handles_empty(self):                                # Test escape_quotes empty
        with MGraph__Engine__Base() as _:
            assert _.escape_quotes('') == ''

    def test__escape_quotes__handles_none(self):                                 # Test escape_quotes None
        with MGraph__Engine__Base() as _:
            assert _.escape_quotes(None) == ''

    def test__safe_id__replaces_special_chars(self):                             # Test safe_id replaces chars
        with MGraph__Engine__Base() as _:
            assert _.safe_id('node-123')   == 'node_123'
            assert _.safe_id('node:456')   == 'node_456'
            assert _.safe_id('node.789')   == 'node_789'
            assert _.safe_id('a-b:c.d')    == 'a_b_c_d'

    def test__safe_id__handles_empty(self):                                      # Test safe_id empty
        with MGraph__Engine__Base() as _:
            assert _.safe_id('') == 'unknown'

    def test__safe_id__handles_none(self):                                       # Test safe_id None
        with MGraph__Engine__Base() as _:
            assert _.safe_id(None) == 'unknown'

    # ═══════════════════════════════════════════════════════════════════════════
    # Integration Tests with Real HTML
    # ═══════════════════════════════════════════════════════════════════════════

    def test__nodes_and_edges_consistent(self):                                  # Test node/edge consistency
        with MGraph__Engine__Base(mgraph=self.mgraph) as _:
            nodes    = _.nodes()
            edges    = _.edges()
            node_ids = set(_.node_id_str(n) for n in nodes)

            for edge in edges:                                                   # All edges reference valid nodes
                from_id = _.edge_from_id(edge)
                to_id   = _.edge_to_id(edge)
                assert from_id in node_ids
                assert to_id   in node_ids