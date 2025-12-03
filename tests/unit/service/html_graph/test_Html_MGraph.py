from unittest                                                           import TestCase
from osbot_utils.type_safe.Type_Safe                                    import Type_Safe
from osbot_utils.utils.Objects                                          import base_classes
from mgraph_db.mgraph.MGraph                                            import MGraph
from mgraph_ai_service_html_graph.service.html_graph.Html_MGraph        import Html_MGraph
from mgraph_ai_service_html_graph.service.html_graph.Html_MGraph__Path  import Html_MGraph__Path


class test_Html_MGraph(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.simple_html_dict = { 'tag'        : 'div'                                      ,
                                 'attrs'      : {'class': 'main', 'id': 'content'}         ,
                                 'child_nodes': []                                         ,
                                 'text_nodes' : [{'data': 'Hello World', 'position': 0}]   }

        cls.nested_html_dict = { 'tag'        : 'div'                                      ,
                                 'attrs'      : {'class': 'container'}                     ,
                                 'child_nodes': [
                                     { 'tag'        : 'h1'                                 ,
                                       'attrs'      : {}                                   ,
                                       'child_nodes': []                                   ,
                                       'text_nodes' : [{'data': 'Title', 'position': 0}]   ,
                                       'position'   : 0                                    },
                                     { 'tag'        : 'p'                                  ,
                                       'attrs'      : {'class': 'intro'}                   ,
                                       'child_nodes': []                                   ,
                                       'text_nodes' : [{'data': 'Intro text', 'position': 0}],
                                       'position'   : 1                                    },
                                     { 'tag'        : 'p'                                  ,
                                       'attrs'      : {}                                   ,
                                       'child_nodes': []                                   ,
                                       'text_nodes' : [{'data': 'More text', 'position': 0}],
                                       'position'   : 2                                    }
                                 ],
                                 'text_nodes' : []                                         }

        cls.html_graph_simple = Html_MGraph.from_html_dict(cls.simple_html_dict)
        cls.html_graph_nested = Html_MGraph.from_html_dict(cls.nested_html_dict)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                     # Test auto-initialization
        with Html_MGraph() as _:
            assert type(_)            is Html_MGraph
            assert base_classes(_)    == [Type_Safe, object]
            assert _.mgraph           is None
            assert type(_.path_utils) is Html_MGraph__Path

    def test__init__with_mgraph(self):                                          # Test initialization with mgraph
        mgraph = MGraph()
        with Html_MGraph(mgraph=mgraph) as _:
            assert _.mgraph is mgraph

    # ═══════════════════════════════════════════════════════════════════════════════
    # Factory Method Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_from_html_dict__returns_html_mgraph(self):                         # Test from_html_dict returns Html_MGraph
        result = Html_MGraph.from_html_dict(self.simple_html_dict)

        assert type(result)        is Html_MGraph
        assert type(result.mgraph) is MGraph

    def test_from_html_dict__creates_valid_graph(self):                         # Test from_html_dict creates valid graph
        result = Html_MGraph.from_html_dict(self.simple_html_dict)
        stats  = result.stats()

        assert stats['element_nodes'] >= 1
        assert stats['total_nodes']   > 0
        assert stats['total_edges']   > 0

    # ═══════════════════════════════════════════════════════════════════════════════
    # to_html_dict Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_to_html_dict__returns_dict(self):                                  # Test to_html_dict returns dict
        result = self.html_graph_simple.to_html_dict()

        assert type(result) is dict
        assert 'tag'        in result
        assert 'attrs'      in result
        assert 'child_nodes' in result
        assert 'text_nodes' in result

    def test_to_html_dict__preserves_tag(self):                                 # Test to_html_dict preserves tag
        result = self.html_graph_simple.to_html_dict()

        assert result['tag'] == 'div'

    def test_to_html_dict__preserves_attrs(self):                               # Test to_html_dict preserves attributes
        result = self.html_graph_simple.to_html_dict()

        assert result['attrs']['class'] == 'main'
        assert result['attrs']['id']    == 'content'

    # ═══════════════════════════════════════════════════════════════════════════════
    # get_element_by_path Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_get_element_by_path__root(self):                                   # Test getting root element by path
        node_id = self.html_graph_simple.get_element_by_path('div')

        assert node_id is not None

    def test_get_element_by_path__nested(self):                                 # Test getting nested element by path
        node_id = self.html_graph_nested.get_element_by_path('div.h1')

        assert node_id is not None

    def test_get_element_by_path__not_found(self):                              # Test getting non-existent path
        node_id = self.html_graph_simple.get_element_by_path('nonexistent')

        assert node_id is None

    # ═══════════════════════════════════════════════════════════════════════════════
    # get_elements_by_tag Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_get_elements_by_tag__single(self):                                 # Test getting elements by tag (single match)
        elements = self.html_graph_nested.get_elements_by_tag('h1')

        assert len(elements) == 1

    def test_get_elements_by_tag__multiple(self):                               # Test getting elements by tag (multiple matches)
        elements = self.html_graph_nested.get_elements_by_tag('p')

        assert len(elements) == 2

    def test_get_elements_by_tag__not_found(self):                              # Test getting elements by non-existent tag
        elements = self.html_graph_nested.get_elements_by_tag('table')

        assert len(elements) == 0

    # ═══════════════════════════════════════════════════════════════════════════════
    # get_elements_with_attribute Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_get_elements_with_attribute__by_name(self):                        # Test getting elements by attribute name only
        elements = self.html_graph_simple.get_elements_with_attribute('class')

        assert len(elements) >= 1

    def test_get_elements_with_attribute__by_name_and_value(self):              # Test getting elements by attribute name and value
        elements = self.html_graph_simple.get_elements_with_attribute('class', 'main')

        assert len(elements) >= 1

    def test_get_elements_with_attribute__value_mismatch(self):                 # Test getting elements with wrong attribute value
        elements = self.html_graph_simple.get_elements_with_attribute('class', 'nonexistent')

        assert len(elements) == 0

    # ═══════════════════════════════════════════════════════════════════════════════
    # get_text_content Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_get_text_content__simple(self):                                    # Test getting text content from element
        node_id = self.html_graph_simple.get_element_by_path('div')
        text    = self.html_graph_simple.get_text_content(node_id)

        assert text == 'Hello World'

    def test_get_text_content__recursive(self):                                 # Test getting recursive text content
        node_id = self.html_graph_nested.get_element_by_path('div')
        text    = self.html_graph_nested.get_text_content(node_id, recursive=True)

        assert 'Title'      in text
        assert 'Intro text' in text
        assert 'More text'  in text

    def test_get_text_content__no_text(self):                                   # Test getting text from element without text
        empty_dict = {'tag': 'div', 'attrs': {}, 'child_nodes': [], 'text_nodes': []}
        html_graph = Html_MGraph.from_html_dict(empty_dict)
        node_id    = html_graph.get_element_by_path('div')
        text       = html_graph.get_text_content(node_id)

        assert text == ''

    # ═══════════════════════════════════════════════════════════════════════════════
    # get_element_tag Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_get_element_tag__valid(self):                                      # Test getting tag from element
        node_id = self.html_graph_simple.get_element_by_path('div')
        tag     = self.html_graph_simple.get_element_tag(node_id)

        assert tag == 'div'

    def test_get_element_tag__nested(self):                                     # Test getting tag from nested element
        node_id = self.html_graph_nested.get_element_by_path('div.h1')
        tag     = self.html_graph_nested.get_element_tag(node_id)

        assert tag == 'h1'

    # ═══════════════════════════════════════════════════════════════════════════════
    # get_element_attributes Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_get_element_attributes__multiple(self):                            # Test getting multiple attributes
        node_id = self.html_graph_simple.get_element_by_path('div')
        attrs   = self.html_graph_simple.get_element_attributes(node_id)

        assert attrs['class'] == 'main'
        assert attrs['id']    == 'content'

    def test_get_element_attributes__empty(self):                               # Test getting attributes from element without attrs
        node_id = self.html_graph_nested.get_element_by_path('div.h1')
        attrs   = self.html_graph_nested.get_element_attributes(node_id)

        assert attrs == {}

    # ═══════════════════════════════════════════════════════════════════════════════
    # get_children Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_get_children__returns_ordered_list(self):                          # Test get_children returns ordered list
        node_id  = self.html_graph_nested.get_element_by_path('div')
        children = self.html_graph_nested.get_children(node_id)

        assert len(children) == 3

    def test_get_children__order_preserved(self):                               # Test children are in correct order
        node_id  = self.html_graph_nested.get_element_by_path('div')
        children = self.html_graph_nested.get_children(node_id)

        tags = [self.html_graph_nested.get_element_tag(child_id) for child_id in children]
        assert tags == ['h1', 'p', 'p']

    def test_get_children__no_children(self):                                   # Test getting children from leaf element
        node_id  = self.html_graph_nested.get_element_by_path('div.h1')
        children = self.html_graph_nested.get_children(node_id)

        assert children == []

    # ═══════════════════════════════════════════════════════════════════════════════
    # stats Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_stats__returns_dict(self):                                         # Test stats returns dict
        stats = self.html_graph_simple.stats()

        assert type(stats) is dict
        assert 'total_nodes'   in stats
        assert 'total_edges'   in stats
        assert 'element_nodes' in stats
        assert 'value_nodes'   in stats
        assert 'tag_nodes'     in stats
        assert 'text_nodes'    in stats
        assert 'attr_nodes'    in stats

    def test_stats__simple_graph(self):                                         # Test stats for simple graph
        stats = self.html_graph_simple.stats()

        assert stats['element_nodes'] == 1                                      # One div
        assert stats['tag_nodes']     == 1                                      # One unique tag
        assert stats['text_nodes']    == 1                                      # One text
        assert stats['attr_nodes']    == 2                                      # Two attributes

    def test_stats__nested_graph(self):                                         # Test stats for nested graph
        stats = self.html_graph_nested.stats()

        assert stats['element_nodes'] == 4                                      # div + h1 + 2 p
        assert stats['tag_nodes']     == 3                                      # div, h1, p (unique)
        assert stats['text_nodes']    == 3                                      # Three text nodes