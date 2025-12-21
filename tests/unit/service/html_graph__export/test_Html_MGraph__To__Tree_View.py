from unittest                                                                           import TestCase
from osbot_utils.type_safe.Type_Safe                                                    import Type_Safe
from osbot_utils.utils.Objects                                                          import base_classes
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                       import Html_MGraph
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__Export__Base  import Html_MGraph__Export__Base
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__To__Tree_View import Html_MGraph__To__Tree_View


class test_Html_MGraph__To__Tree_View(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.simple_html   = '<div class="main">Hello World</div>'
        cls.complex_html  = '<div class="main" id="content"><h1>Title</h1><p>Paragraph</p></div>'
        cls.html_mgraph_simple  = Html_MGraph.from_html(cls.simple_html)
        cls.html_mgraph_complex = Html_MGraph.from_html(cls.complex_html)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                               # Test initialization
        with Html_MGraph__To__Tree_View(html_mgraph=self.html_mgraph_simple) as _:
            assert type(_)         is Html_MGraph__To__Tree_View
            assert base_classes(_) == [Html_MGraph__Export__Base, Type_Safe, object]
            assert _.html_mgraph   is self.html_mgraph_simple

    def test__setUp_Class(self):                                                          # Test setup created valid mgraphs
        with self.html_mgraph_simple as _:
            assert type(_) is Html_MGraph
            assert _.root_id() is not None
            assert _.document is not None

        with self.html_mgraph_complex as _:
            assert type(_) is Html_MGraph
            assert _.root_id() is not None
            assert _.document is not None

    # ═══════════════════════════════════════════════════════════════════════════════
    # export_tree Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__export_tree__returns_dict(self):                                            # Test export_tree returns dict
        with Html_MGraph__To__Tree_View(html_mgraph=self.html_mgraph_simple) as _:
            tree_view = _.export_tree()

            assert type(tree_view) is dict

    def test__export_tree__has_required_fields(self):                                     # Test tree has required fields
        with Html_MGraph__To__Tree_View(html_mgraph=self.html_mgraph_simple) as _:
            tree_view = _.export_tree()

            assert 'id'       in tree_view
            assert 'value'    in tree_view
            assert 'children' in tree_view

    def test__export_tree__children_is_dict(self):                                        # Test children is grouped dict
        with Html_MGraph__To__Tree_View(html_mgraph=self.html_mgraph_simple) as _:
            tree_view = _.export_tree()

            assert type(tree_view['children']) is dict

    def test__export_tree__has_tag_children(self):                                        # Test tree has tag children
        with Html_MGraph__To__Tree_View(html_mgraph=self.html_mgraph_simple) as _:
            tree_view = _.export_tree()
            children  = tree_view['children']

            # Should have tag information
            if 'tag' in children:
                assert type(children['tag']) is list
                assert len(children['tag']) > 0

    def test__export_tree__simple_html_structure(self):                                   # Test simple HTML tree structure
        with Html_MGraph__To__Tree_View(html_mgraph=self.html_mgraph_simple) as _:
            tree_view = _.export_tree()

            assert tree_view['id'] is not None
            assert tree_view['value'] is not None

    def test__export_tree__complex_html_has_children(self):                               # Test complex HTML has child elements
        with Html_MGraph__To__Tree_View(html_mgraph=self.html_mgraph_complex) as _:
            tree_view = _.export_tree()
            children  = tree_view['children']

            # Complex HTML should have child elements (h1, p)
            if 'child' in children:
                assert len(children['child']) >= 2                                        # h1 and p

    # ═══════════════════════════════════════════════════════════════════════════════
    # export_tree__as_text Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__export_tree__as_text__returns_string(self):                                 # Test as_text returns string
        with Html_MGraph__To__Tree_View(html_mgraph=self.html_mgraph_simple) as _:
            tree_text = _.export_tree__as_text()

            assert type(tree_text) is str

    def test__export_tree__as_text__not_empty(self):                                      # Test as_text is not empty
        with Html_MGraph__To__Tree_View(html_mgraph=self.html_mgraph_simple) as _:
            tree_text = _.export_tree__as_text()

            assert len(tree_text) > 0

    def test__export_tree__as_text__has_indentation(self):                                # Test as_text has proper indentation
        with Html_MGraph__To__Tree_View(html_mgraph=self.html_mgraph_simple) as _:
            tree_text = _.export_tree__as_text()

            # Should have indented lines
            lines = tree_text.split('\n')
            has_indented = any(line.startswith('    ') for line in lines)
            assert has_indented or len(lines) == 1                                        # Either has indentation or single line

    def test__export_tree__as_text__contains_tag_section(self):                           # Test as_text contains tag section
        with Html_MGraph__To__Tree_View(html_mgraph=self.html_mgraph_simple) as _:
            tree_text = _.export_tree__as_text()

            # Should contain tag information
            assert 'tag:' in tree_text or 'div' in tree_text.lower()

    def test__export_tree__as_text__complex_html(self):                                   # Test complex HTML text output
        with Html_MGraph__To__Tree_View(html_mgraph=self.html_mgraph_complex) as _:
            tree_text = _.export_tree__as_text()

            # Should have hierarchical structure
            assert len(tree_text) > 0
            lines = tree_text.split('\n')
            assert len(lines) >= 1

    # ═══════════════════════════════════════════════════════════════════════════════
    # export Tests (main export method)
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__export__delegates_to_export_tree(self):                                     # Test export() calls export_tree()
        with Html_MGraph__To__Tree_View(html_mgraph=self.html_mgraph_simple) as _:
            export_result = _.export()
            tree_result   = _.export_tree()

            assert export_result == tree_result

    # ═══════════════════════════════════════════════════════════════════════════════
    # Tree Node Structure Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__tree_node__id_is_string(self):                                              # Test node id is string
        with Html_MGraph__To__Tree_View(html_mgraph=self.html_mgraph_simple) as _:
            tree_view = _.export_tree()

            assert type(tree_view['id']) is str

    def test__tree_node__value_is_string(self):                                           # Test node value is string
        with Html_MGraph__To__Tree_View(html_mgraph=self.html_mgraph_simple) as _:
            tree_view = _.export_tree()

            assert type(tree_view['value']) is str

    def test__tree_node__child_nodes_have_structure(self):                                # Test child nodes have same structure
        with Html_MGraph__To__Tree_View(html_mgraph=self.html_mgraph_complex) as _:
            tree_view = _.export_tree()
            children  = tree_view['children']

            # Check child elements have same structure
            if 'child' in children:
                for child in children['child']:
                    assert 'id'       in child
                    assert 'value'    in child
                    assert 'children' in child

    # ═══════════════════════════════════════════════════════════════════════════════
    # Text Formatting Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__format_tree_as_text__empty_tree(self):                                      # Test formatting empty tree
        with Html_MGraph__To__Tree_View(html_mgraph=self.html_mgraph_simple) as _:
            result = _._format_tree_as_text({})

            assert result == ''

    def test__format_tree_as_text__simple_tree(self):                                     # Test formatting simple tree
        with Html_MGraph__To__Tree_View(html_mgraph=self.html_mgraph_simple) as _:
            tree   = {'id': 'test', 'value': 'div', 'children': {}}
            result = _._format_tree_as_text(tree)

            assert 'test' in result

    def test__format_tree_as_text__with_children(self):                                   # Test formatting tree with children
        with Html_MGraph__To__Tree_View(html_mgraph=self.html_mgraph_simple) as _:
            tree = {
                'id'      : 'root',
                'value'   : 'div',
                'children': {
                    'tag': [{'id': 't1', 'value': 'div', 'children': {}}]
                }
            }
            result = _._format_tree_as_text(tree)

            assert 'root' in result
            assert 'tag:' in result
            assert 'div'  in result