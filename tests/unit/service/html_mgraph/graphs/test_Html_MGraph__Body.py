from unittest                                                            import TestCase
from mgraph_ai_service_html_graph.service.html_mgraph.graphs.Html_MGraph__Base  import Html_MGraph__Base
from mgraph_ai_service_html_graph.service.html_mgraph.graphs.Html_MGraph__Body  import Html_MGraph__Body
from mgraph_db.mgraph.schemas.identifiers.Node_Path                      import Node_Path
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id        import Node_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Obj_Id         import Obj_Id
from osbot_utils.utils.Objects                                           import base_classes


class test_Html_MGraph__Body(TestCase):                                         # Test body graph for HTML documents

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                     # Test default initialization
        with Html_MGraph__Body() as _:
            assert type(_)             is Html_MGraph__Body
            assert Html_MGraph__Base   in base_classes(_)
            assert _.mgraph            is None
            assert _.root_id           is None
            assert _.PREDICATE_CHILD   is not None
            assert _.PREDICATE_TEXT    is not None
            assert _.PATH_TEXT         == 'text'

    def test_setup(self):                                                       # Test setup creates MGraph
        with Html_MGraph__Body().setup() as _:
            assert _.mgraph is not None

    # ═══════════════════════════════════════════════════════════════════════════
    # Element Creation Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_create_element(self):                                              # Test element creation without node_id
        with Html_MGraph__Body().setup() as _:
            node_path = Node_Path('body.div')
            node_id   = _.create_element(node_path=node_path)

            assert node_id is not None
            assert _.node_path(node_id) == node_path

    def test_create_element__with_node_id(self):                                # Test element creation with specific node_id
        with Html_MGraph__Body().setup() as _:
            node_path = Node_Path('body.span')
            custom_id = Node_Id(Obj_Id())
            result_id = _.create_element(node_path=node_path, node_id=custom_id)

            assert result_id == custom_id
            assert _.node_path(custom_id) == node_path

    def test_set_root(self):                                                    # Test setting root node
        with Html_MGraph__Body().setup() as _:
            body_id = _.create_element(node_path=Node_Path('body'))
            _.set_root(body_id)

            assert _.root_id == body_id

    # ═══════════════════════════════════════════════════════════════════════════
    # Text Creation Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_create_text(self):                                                 # Test text node creation
        with Html_MGraph__Body().setup() as _:
            body_id = _.create_element(node_path=Node_Path('body'))
            text_id = _.create_text(text='Hello', parent_id=body_id)

            assert text_id is not None
            assert _.node_value(text_id)  == 'Hello'
            assert _.node_path(text_id)   == Node_Path('text')

    def test_create_text__with_position(self):                                  # Test text node with explicit position
        with Html_MGraph__Body().setup() as _:
            body_id  = _.create_element(node_path=Node_Path('body'))
            text_id1 = _.create_text(text='First' , parent_id=body_id, position=0)
            text_id2 = _.create_text(text='Second', parent_id=body_id, position=1)

            text_nodes = _.get_text_nodes(body_id)
            assert text_nodes == [text_id1, text_id2]                           # Ordered by position

    def test_create_text__multiple_same_parent(self):                           # Test multiple text nodes under same parent
        with Html_MGraph__Body().setup() as _:
            div_id   = _.create_element(node_path=Node_Path('body.div'))
            text_id1 = _.create_text(text='Part 1', parent_id=div_id, position=0)
            text_id2 = _.create_text(text='Part 2', parent_id=div_id, position=1)
            text_id3 = _.create_text(text='Part 3', parent_id=div_id, position=2)

            assert len(_.get_text_nodes(div_id)) == 3
            assert _.get_text_content(div_id)    == 'Part 1Part 2Part 3'

    # ═══════════════════════════════════════════════════════════════════════════
    # Child Linking Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_add_child(self):                                                   # Test adding child element
        with Html_MGraph__Body().setup() as _:
            body_id = _.create_element(node_path=Node_Path('body'))
            div_id  = _.create_element(node_path=Node_Path('body.div'))
            _.add_child(parent_id=body_id, child_id=div_id, position=0)

            children = _.get_element_children(body_id)
            assert children == [div_id]

    def test_add_child__multiple(self):                                         # Test adding multiple children
        with Html_MGraph__Body().setup() as _:
            body_id = _.create_element(node_path=Node_Path('body'))
            div_id  = _.create_element(node_path=Node_Path('body.div'))
            p_id    = _.create_element(node_path=Node_Path('body.p'))
            span_id = _.create_element(node_path=Node_Path('body.span'))

            _.add_child(parent_id=body_id, child_id=div_id , position=0)
            _.add_child(parent_id=body_id, child_id=p_id   , position=1)
            _.add_child(parent_id=body_id, child_id=span_id, position=2)

            children = _.get_element_children(body_id)
            assert children == [div_id, p_id, span_id]

    def test_add_child__out_of_order(self):                                     # Test adding children out of order
        with Html_MGraph__Body().setup() as _:
            body_id = _.create_element(node_path=Node_Path('body'))
            first   = _.create_element(node_path=Node_Path('first'))
            second  = _.create_element(node_path=Node_Path('second'))
            third   = _.create_element(node_path=Node_Path('third'))

            _.add_child(parent_id=body_id, child_id=third , position=2)         # Add out of order
            _.add_child(parent_id=body_id, child_id=first , position=0)
            _.add_child(parent_id=body_id, child_id=second, position=1)

            children = _.get_element_children(body_id)
            assert children == [first, second, third]                           # Should be sorted by position

    # ═══════════════════════════════════════════════════════════════════════════
    # Query Tests - Element Children
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_element_children(self):                                        # Test getting child elements
        with Html_MGraph__Body().setup() as _:
            body_id = _.create_element(node_path=Node_Path('body'))
            _.set_root(body_id)

            div_id = _.create_element(node_path=Node_Path('body.div'))
            _.add_child(body_id, div_id, position=0)

            children = _.get_element_children(body_id)
            assert children == [div_id]

    def test_get_element_children__empty(self):                                 # Test getting children from leaf element
        with Html_MGraph__Body().setup() as _:
            leaf = _.create_element(node_path=Node_Path('body.leaf'))
            children = _.get_element_children(leaf)

            assert children == []

    def test_get_element_children__excludes_text(self):                         # Test that text nodes are excluded
        with Html_MGraph__Body().setup() as _:
            div_id  = _.create_element(node_path=Node_Path('body.div'))
            p_id    = _.create_element(node_path=Node_Path('body.div.p'))
            text_id = _.create_text(text='Some text', parent_id=div_id, position=0)
            _.add_child(div_id, p_id, position=1)

            element_children = _.get_element_children(div_id)
            assert element_children == [p_id]                                   # Only element child, not text

    # ═══════════════════════════════════════════════════════════════════════════
    # Query Tests - Text Nodes
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_text_nodes(self):                                              # Test getting text nodes
        with Html_MGraph__Body().setup() as _:
            div_id  = _.create_element(node_path=Node_Path('body.div'))
            text_id = _.create_text(text='Hello', parent_id=div_id)

            text_nodes = _.get_text_nodes(div_id)
            assert text_nodes == [text_id]

    def test_get_text_nodes__empty(self):                                       # Test getting text from element without text
        with Html_MGraph__Body().setup() as _:
            div_id     = _.create_element(node_path=Node_Path('body.div'))
            text_nodes = _.get_text_nodes(div_id)

            assert text_nodes == []

    def test_get_text_nodes__ordered(self):                                     # Test text nodes are returned in order
        with Html_MGraph__Body().setup() as _:
            div_id  = _.create_element(node_path=Node_Path('body.div'))
            text3   = _.create_text(text='Third' , parent_id=div_id, position=2)
            text1   = _.create_text(text='First' , parent_id=div_id, position=0)
            text2   = _.create_text(text='Second', parent_id=div_id, position=1)

            text_nodes = _.get_text_nodes(div_id)
            assert text_nodes == [text1, text2, text3]

    def test_get_text_content(self):                                            # Test getting concatenated text
        with Html_MGraph__Body().setup() as _:
            div_id = _.create_element(node_path=Node_Path('body.div'))
            _.create_text(text='Hello ', parent_id=div_id, position=0)
            _.create_text(text='World' , parent_id=div_id, position=1)

            content = _.get_text_content(div_id)
            assert content == 'Hello World'

    def test_get_text_content__empty(self):                                     # Test getting text from element without text
        with Html_MGraph__Body().setup() as _:
            div_id  = _.create_element(node_path=Node_Path('body.div'))
            content = _.get_text_content(div_id)

            assert content == ''

    def test_get_text_content__single(self):                                    # Test getting single text node content
        with Html_MGraph__Body().setup() as _:
            p_id = _.create_element(node_path=Node_Path('body.p'))
            _.create_text(text='Single paragraph', parent_id=p_id)

            content = _.get_text_content(p_id)
            assert content == 'Single paragraph'

    # ═══════════════════════════════════════════════════════════════════════════
    # Query Tests - Recursive Text
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_all_text_recursive(self):                                      # Test getting all text including nested
        with Html_MGraph__Body().setup() as _:
            body_id = _.create_element(node_path=Node_Path('body'))
            _.set_root(body_id)

            div_id = _.create_element(node_path=Node_Path('body.div'))
            p_id   = _.create_element(node_path=Node_Path('body.div.p'))

            _.add_child(body_id, div_id, position=0)
            _.add_child(div_id , p_id  , position=0)

            _.create_text(text='Outer', parent_id=div_id, position=1)           # After p element
            _.create_text(text='Inner', parent_id=p_id  , position=0)

            all_text = _.get_all_text_recursive(div_id)
            assert 'Inner' in all_text
            assert 'Outer' in all_text

    def test_get_all_text_recursive__interleaved(self):                         # Test text interleaved with elements
        with Html_MGraph__Body().setup() as _:
            div_id  = _.create_element(node_path=Node_Path('body.div'))
            span_id = _.create_element(node_path=Node_Path('body.div.span'))

            _.create_text(text='Before ', parent_id=div_id, position=0)
            _.add_child(div_id, span_id, position=1)
            _.create_text(text=' After', parent_id=div_id, position=2)
            _.create_text(text='Inside', parent_id=span_id, position=0)

            all_text = _.get_all_text_recursive(div_id)
            assert all_text == 'Before Inside After'

    def test_get_all_text_recursive__empty(self):                               # Test recursive text on empty element
        with Html_MGraph__Body().setup() as _:
            empty_div = _.create_element(node_path=Node_Path('body.empty'))
            all_text  = _.get_all_text_recursive(empty_div)

            assert all_text == ''

    def test_get_all_text_recursive__deep_nesting(self):                        # Test deeply nested text
        with Html_MGraph__Body().setup() as _:
            level1 = _.create_element(node_path=Node_Path('level1'))
            level2 = _.create_element(node_path=Node_Path('level2'))
            level3 = _.create_element(node_path=Node_Path('level3'))

            _.add_child(level1, level2, position=0)
            _.add_child(level2, level3, position=0)

            _.create_text(text='L1', parent_id=level1, position=1)
            _.create_text(text='L2', parent_id=level2, position=1)
            _.create_text(text='L3', parent_id=level3, position=0)

            all_text = _.get_all_text_recursive(level1)
            assert 'L1' in all_text
            assert 'L2' in all_text
            assert 'L3' in all_text

    # ═══════════════════════════════════════════════════════════════════════════
    # Node Type Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_is_text_node(self):                                                # Test text node detection
        with Html_MGraph__Body().setup() as _:
            div_id  = _.create_element(node_path=Node_Path('body.div'))
            text_id = _.create_text(text='Hello', parent_id=div_id)

            assert _.is_text_node(text_id) is True
            assert _.is_text_node(div_id)  is False

    def test_is_text_node__various_paths(self):                                 # Test text detection with various node paths
        with Html_MGraph__Body().setup() as _:
            element1 = _.create_element(node_path=Node_Path('body'))
            element2 = _.create_element(node_path=Node_Path('body.div.p.span'))
            element3 = _.create_element(node_path=Node_Path('texty'))           # Node path contains 'text' but not equal
            text_id  = _.create_text(text='actual text', parent_id=element1)

            assert _.is_text_node(element1) is False
            assert _.is_text_node(element2) is False
            assert _.is_text_node(element3) is False
            assert _.is_text_node(text_id)  is True

    def test_is_element_node(self):                                             # Test element node detection
        with Html_MGraph__Body().setup() as _:
            div_id  = _.create_element(node_path=Node_Path('body.div'))
            text_id = _.create_text(text='Hello', parent_id=div_id)

            assert _.is_element_node(div_id)  is True
            assert _.is_element_node(text_id) is False

    def test_is_element_node__various_paths(self):                              # Test element detection with various paths
        with Html_MGraph__Body().setup() as _:
            body_id   = _.create_element(node_path=Node_Path('body'))
            nested_id = _.create_element(node_path=Node_Path('body.div.p'))
            text_id   = _.create_text(text='x', parent_id=body_id)

            assert _.is_element_node(body_id)   is True
            assert _.is_element_node(nested_id) is True
            assert _.is_element_node(text_id)   is False

    # ═══════════════════════════════════════════════════════════════════════════
    # Iteration Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_all_element_nodes(self):                                           # Test getting all element nodes
        with Html_MGraph__Body().setup() as _:
            body_id = _.create_element(node_path=Node_Path('body'))
            div_id  = _.create_element(node_path=Node_Path('body.div'))
            p_id    = _.create_element(node_path=Node_Path('body.p'))
            text_id = _.create_text(text='ignored', parent_id=body_id)

            elements = _.all_element_nodes()

            assert len(elements) == 3
            assert body_id in elements
            assert div_id  in elements
            assert p_id    in elements
            assert text_id not in elements

    def test_all_element_nodes__empty(self):                                    # Test getting elements from empty graph
        with Html_MGraph__Body().setup() as _:
            elements = _.all_element_nodes()

            assert elements == []

    def test_all_text_nodes(self):                                              # Test getting all text nodes
        with Html_MGraph__Body().setup() as _:
            body_id = _.create_element(node_path=Node_Path('body'))
            div_id  = _.create_element(node_path=Node_Path('body.div'))
            text1   = _.create_text(text='First' , parent_id=body_id, position=0)
            text2   = _.create_text(text='Second', parent_id=div_id , position=0)
            text3   = _.create_text(text='Third' , parent_id=div_id , position=1)

            text_nodes = _.all_text_nodes()

            assert len(text_nodes) == 3
            assert text1    in text_nodes
            assert text2    in text_nodes
            assert text3    in text_nodes
            assert body_id  not in text_nodes
            assert div_id   not in text_nodes

    def test_all_text_nodes__empty(self):                                       # Test getting text nodes from graph without text
        with Html_MGraph__Body().setup() as _:
            _.create_element(node_path=Node_Path('body'))
            text_nodes = _.all_text_nodes()

            assert text_nodes == []

    # ═══════════════════════════════════════════════════════════════════════════
    # Stats Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_stats(self):                                                       # Test statistics
        with Html_MGraph__Body().setup() as _:
            body_id = _.create_element(node_path=Node_Path('body'))
            _.set_root(body_id)
            div_id  = _.create_element(node_path=Node_Path('body.div'))
            _.add_child(body_id, div_id, position=0)
            _.create_text(text='text1', parent_id=body_id, position=1)
            _.create_text(text='text2', parent_id=div_id , position=0)

            stats = _.stats()

            assert stats['element_nodes'] == 2
            assert stats['text_nodes']    == 2
            assert stats['total_nodes']   == 5                                  # 2 elements + 2 text
            assert stats['total_edges']   == 3                                  # 1 child + 2 text edges
            assert stats['root_id']       == str(body_id)

    def test_stats__empty(self):                                                # Test statistics on empty graph
        with Html_MGraph__Body().setup() as _:
            stats = _.stats()

            assert stats['element_nodes'] == 0
            assert stats['text_nodes' ]   == 0
            assert stats['total_nodes']   == 1
            assert stats['total_edges']   == 0

    def test_stats__only_elements(self):                                        # Test stats with only elements
        with Html_MGraph__Body().setup() as _:
            body = _.create_element(node_path=Node_Path('body'))
            div  = _.create_element(node_path=Node_Path('div'))
            _.add_child(body, div, position=0)

            stats = _.stats()

            assert stats['element_nodes'] == 2
            assert stats['text_nodes']    == 0

    def test_stats__only_text(self):                                            # Test stats behavior - text always needs parent
        with Html_MGraph__Body().setup() as _:
            parent = _.create_element(node_path=Node_Path('parent'))
            _.create_text(text='only text', parent_id=parent)

            stats = _.stats()

            assert stats['element_nodes'] == 1                                  # Parent element
            assert stats['text_nodes']    == 1

    # ═══════════════════════════════════════════════════════════════════════════
    # Integration Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_create_element_and_text(self):                                     # Test full element + text workflow
        with Html_MGraph__Body().setup() as _:
            body_id = _.create_element(node_path=Node_Path('body'))
            _.set_root(body_id)

            div_id = _.create_element(node_path=Node_Path('body.div'))
            _.add_child(body_id, div_id, position=0)

            text_id = _.create_text(text='Hello World', parent_id=div_id)

            assert _.root_id                       == body_id
            assert _.get_element_children(body_id) == [div_id]
            assert _.get_text_nodes(div_id)        == [text_id]
            assert _.get_text_content(div_id)      == 'Hello World'

    def test_complex_structure(self):                                           # Test complex nested structure
        with Html_MGraph__Body().setup() as _:
            # Build structure:
            # body
            #   ├── header
            #   │   └── "Header Text"
            #   ├── main
            #   │   ├── article
            #   │   │   └── "Article content"
            #   │   └── aside
            #   │       └── "Sidebar"
            #   └── footer
            #       └── "Footer Text"

            body    = _.create_element(node_path=Node_Path('body'))
            header  = _.create_element(node_path=Node_Path('body.header'))
            main    = _.create_element(node_path=Node_Path('body.main'))
            footer  = _.create_element(node_path=Node_Path('body.footer'))
            article = _.create_element(node_path=Node_Path('body.main.article'))
            aside   = _.create_element(node_path=Node_Path('body.main.aside'))

            _.set_root(body)
            _.add_child(body, header , position=0)
            _.add_child(body, main   , position=1)
            _.add_child(body, footer , position=2)
            _.add_child(main, article, position=0)
            _.add_child(main, aside  , position=1)

            _.create_text(text='Header Text'     , parent_id=header , position=0)
            _.create_text(text='Article content' , parent_id=article, position=0)
            _.create_text(text='Sidebar'         , parent_id=aside  , position=0)
            _.create_text(text='Footer Text'     , parent_id=footer , position=0)

            assert _.get_element_children(body) == [header, main, footer]
            assert _.get_element_children(main) == [article, aside]
            assert _.get_text_content(header)   == 'Header Text'
            assert _.get_text_content(footer)   == 'Footer Text'

            all_text = _.get_all_text_recursive(body)
            assert 'Header Text'      in all_text
            assert 'Article content'  in all_text
            assert 'Sidebar'          in all_text
            assert 'Footer Text'      in all_text

            stats = _.stats()
            assert stats['element_nodes'] == 6
            assert stats['text_nodes']    == 4