from unittest                                                           import TestCase
from osbot_utils.type_safe.Type_Safe                                    import Type_Safe
from osbot_utils.utils.Objects                                          import base_classes
from mgraph_ai_service_html_graph.service.html_graph.Html_MGraph__Path  import Html_MGraph__Path


class test_Html_MGraph__Path(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.path_utils = Html_MGraph__Path()

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                     # Test auto-initialization
        with Html_MGraph__Path() as _:
            assert type(_)           is Html_MGraph__Path
            assert base_classes(_)   == [Type_Safe, object]
            assert _.PATH_SEPARATOR  == '.'

    # ═══════════════════════════════════════════════════════════════════════════════
    # compute_element_path Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_compute_element_path__root_element(self):                          # Test path for root element (no parent)
        with self.path_utils as _:
            path = _.compute_element_path(parent_path    = None         ,
                                          tag            = 'html'       ,
                                          sibling_index  = 0            ,
                                          sibling_counts = {'html': 1}  )
            assert path == 'html'

    def test_compute_element_path__single_child(self):                          # Test path with single child (no index needed)
        with self.path_utils as _:
            path = _.compute_element_path(parent_path    = 'html'       ,
                                          tag            = 'body'       ,
                                          sibling_index  = 0            ,
                                          sibling_counts = {'body': 1}  )
            assert path == 'html.body'

    def test_compute_element_path__multiple_siblings_same_tag(self):            # Test path with multiple siblings of same tag
        with self.path_utils as _:
            path_first = _.compute_element_path(parent_path    = 'html.body'  ,
                                                tag            = 'div'        ,
                                                sibling_index  = 0            ,
                                                sibling_counts = {'div': 3}   )
            path_second = _.compute_element_path(parent_path    = 'html.body' ,
                                                 tag            = 'div'       ,
                                                 sibling_index  = 1           ,
                                                 sibling_counts = {'div': 3}  )
            path_third = _.compute_element_path(parent_path    = 'html.body'  ,
                                                tag            = 'div'        ,
                                                sibling_index  = 2            ,
                                                sibling_counts = {'div': 3}   )
            assert path_first  == 'html.body.div[0]'
            assert path_second == 'html.body.div[1]'
            assert path_third  == 'html.body.div[2]'

    def test_compute_element_path__nested_elements(self):                       # Test deeply nested path
        with self.path_utils as _:
            path = _.compute_element_path(parent_path    = 'html.body.div[0].ul' ,
                                          tag            = 'li'                  ,
                                          sibling_index  = 2                     ,
                                          sibling_counts = {'li': 5}             )
            assert path == 'html.body.div[0].ul.li[2]'

    # ═══════════════════════════════════════════════════════════════════════════════
    # parse_path Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_parse_path__empty(self):                                           # Test parsing empty path
        with self.path_utils as _:
            result = _.parse_path('')
            assert result == []

    def test_parse_path__simple(self):                                          # Test parsing simple path without indices
        with self.path_utils as _:
            result = _.parse_path('html.body.div.p')
            assert result == [('html', None), ('body', None), ('div', None), ('p', None)]

    def test_parse_path__with_indices(self):                                    # Test parsing path with indices
        with self.path_utils as _:
            result = _.parse_path('html.body.div[0].p[2]')
            assert result == [('html', None), ('body', None), ('div', 0), ('p', 2)]

    def test_parse_path__mixed(self):                                           # Test parsing path with mixed indexed and non-indexed
        with self.path_utils as _:
            result = _.parse_path('html.body.div[1].ul.li[3]')
            assert result == [('html', None), ('body', None), ('div', 1), ('ul', None), ('li', 3)]

    # ═══════════════════════════════════════════════════════════════════════════════
    # get_parent_path Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_get_parent_path__root(self):                                       # Test parent of root element
        with self.path_utils as _:
            result = _.get_parent_path('html')
            assert result is None

    def test_get_parent_path__simple(self):                                     # Test parent of simple path
        with self.path_utils as _:
            result = _.get_parent_path('html.body.div')
            assert result == 'html.body'

    def test_get_parent_path__with_index(self):                                 # Test parent of path with index
        with self.path_utils as _:
            result = _.get_parent_path('html.body.div[0].p[2]')
            assert result == 'html.body.div[0]'

    def test_get_parent_path__empty(self):                                      # Test parent of empty path
        with self.path_utils as _:
            result = _.get_parent_path('')
            assert result is None

    # ═══════════════════════════════════════════════════════════════════════════════
    # get_depth Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_get_depth__empty(self):                                            # Test depth of empty path
        with self.path_utils as _:
            assert _.get_depth('') == 0

    def test_get_depth__root(self):                                             # Test depth of root element
        with self.path_utils as _:
            assert _.get_depth('html') == 1

    def test_get_depth__nested(self):                                           # Test depth of nested path
        with self.path_utils as _:
            assert _.get_depth('html.body')           == 2
            assert _.get_depth('html.body.div')       == 3
            assert _.get_depth('html.body.div[0].p')  == 4

    # ═══════════════════════════════════════════════════════════════════════════════
    # is_ancestor_of Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_is_ancestor_of__true(self):                                        # Test valid ancestor relationship
        with self.path_utils as _:
            assert _.is_ancestor_of('html'     , 'html.body'          ) is True
            assert _.is_ancestor_of('html.body', 'html.body.div'      ) is True
            assert _.is_ancestor_of('html'     , 'html.body.div[0].p' ) is True

    def test_is_ancestor_of__false(self):                                       # Test non-ancestor relationship
        with self.path_utils as _:
            assert _.is_ancestor_of('html.body', 'html'          ) is False     # Descendant not ancestor
            assert _.is_ancestor_of('html.head', 'html.body.div' ) is False     # Different branch
            assert _.is_ancestor_of('html'     , 'html'          ) is False     # Same path

    def test_is_ancestor_of__empty(self):                                       # Test with empty paths
        with self.path_utils as _:
            assert _.is_ancestor_of(''    , 'html') is False
            assert _.is_ancestor_of('html', ''    ) is False
            assert _.is_ancestor_of(''    , ''    ) is False

    # ═══════════════════════════════════════════════════════════════════════════════
    # value_node_path Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_value_node_path__tag(self):                                        # Test value node path for tags
        with self.path_utils as _:
            assert _.value_node_path('tag', 'div')  == 'tag:div'
            assert _.value_node_path('tag', 'p')    == 'tag:p'
            assert _.value_node_path('tag', 'html') == 'tag:html'

    def test_value_node_path__attr(self):                                       # Test value node path for attributes
        with self.path_utils as _:
            assert _.value_node_path('attr', 'class') == 'attr:class'
            assert _.value_node_path('attr', 'id')    == 'attr:id'
            assert _.value_node_path('attr', 'href')  == 'attr:href'

    def test_value_node_path__text(self):                                       # Test value node path for text (no identifier)
        with self.path_utils as _:
            assert _.value_node_path('text')       == 'text'
            assert _.value_node_path('text', None) == 'text'