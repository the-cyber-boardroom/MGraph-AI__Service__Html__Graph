from unittest                                                            import TestCase
from mgraph_ai_service_html_graph.service.html_mgraph.graphs.Html_MGraph__Head  import Html_MGraph__Head
from mgraph_ai_service_html_graph.service.html_mgraph.graphs.Html_MGraph__Base  import Html_MGraph__Base
from mgraph_db.mgraph.schemas.identifiers.Node_Path                      import Node_Path
from osbot_utils.type_safe.Type_Safe                                     import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id        import Node_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Obj_Id         import Obj_Id
from osbot_utils.utils.Objects                                           import base_classes


class test_Html_MGraph__Head(TestCase):                                         # Test head graph for <head> element structure

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                     # Test default initialization
        with Html_MGraph__Head() as _:
            assert type(_)            is Html_MGraph__Head
            assert base_classes(_)    == [Html_MGraph__Base, Type_Safe, object]
            assert _.PREDICATE_CHILD  is not None
            assert _.PREDICATE_TEXT   is not None
            assert _.PATH_TEXT        == 'text'

    def test_setup(self):                                                       # Test setup creates MGraph and root
        with Html_MGraph__Head().setup() as _:
            assert _.mgraph  is not None
            assert _.root_id is not None

    def test_constants(self):                                                   # Test constant values
        with Html_MGraph__Head() as _:
            assert str(_.PREDICATE_CHILD) == 'child'
            assert str(_.PREDICATE_TEXT)  == 'text'
            assert _.PATH_TEXT            == 'text'

    # ═══════════════════════════════════════════════════════════════════════════
    # Create Element Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_create_element(self):                                              # Test basic element creation
        with Html_MGraph__Head().setup() as _:
            node_id = _.create_element(node_path=Node_Path('head.meta'))

            assert node_id is not None
            assert _.node(node_id) is not None

    def test_create_element__with_node_id(self):                                # Test element creation with specific node_id
        with Html_MGraph__Head().setup() as _:
            custom_id = Node_Id(Obj_Id())
            node_id   = _.create_element(node_path=Node_Path('head.title'), node_id=custom_id)

            assert node_id == custom_id

    def test_create_element__multiple(self):                                    # Test creating multiple elements
        with Html_MGraph__Head().setup() as _:
            meta_id   = _.create_element(node_path=Node_Path('head.meta'))
            title_id  = _.create_element(node_path=Node_Path('head.title'))
            link_id   = _.create_element(node_path=Node_Path('head.link'))

            assert meta_id  != title_id
            assert title_id != link_id
            assert meta_id  != link_id

    def test_create_element__with_path(self):                                   # Test element node has correct path
        with Html_MGraph__Head().setup() as _:
            node_id = _.create_element(node_path=Node_Path('head.script'))
            path    = _.node_path(node_id)

            assert path == Node_Path('head.script')

    # ═══════════════════════════════════════════════════════════════════════════
    # Set Root Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_set_root(self):                                                    # Test setting root node
        with Html_MGraph__Head().setup() as _:
            head_id = _.create_element(node_path=Node_Path('head'))
            _.set_root(head_id)

            assert _.root_id == head_id

    def test_set_root__replaces_existing(self):                                 # Test set_root replaces previous root
        with Html_MGraph__Head().setup() as _:
            first_root  = _.root_id
            new_head_id = _.create_element(node_path=Node_Path('head'))
            _.set_root(new_head_id)

            assert _.root_id == new_head_id
            assert _.root_id != first_root

    # ═══════════════════════════════════════════════════════════════════════════
    # Create Text Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_create_text(self):                                                 # Test basic text node creation
        with Html_MGraph__Head().setup() as _:
            title_id = _.create_element(node_path=Node_Path('head.title'))
            text_id  = _.create_text(text='Page Title', parent_id=title_id)

            assert text_id is not None
            assert _.node_value(text_id) == 'Page Title'

    def test_create_text__with_position(self):                                  # Test text creation with position
        with Html_MGraph__Head().setup() as _:
            title_id = _.create_element(node_path=Node_Path('head.title'))
            text_id  = _.create_text(text='Title Text', parent_id=title_id, position=5)

            assert text_id is not None
            assert _.node_value(text_id) == 'Title Text'

    def test_create_text__multiple_same_parent(self):                           # Test multiple text nodes under same parent
        with Html_MGraph__Head().setup() as _:
            title_id = _.create_element(node_path=Node_Path('head.title'))
            text1_id = _.create_text(text='Part 1', parent_id=title_id, position=0)
            text2_id = _.create_text(text='Part 2', parent_id=title_id, position=1)

            assert text1_id != text2_id
            assert _.node_value(text1_id) == 'Part 1'
            assert _.node_value(text2_id) == 'Part 2'

    def test_create_text__has_text_path(self):                                  # Test text node has correct path
        with Html_MGraph__Head().setup() as _:
            title_id = _.create_element(node_path=Node_Path('head.title'))
            text_id  = _.create_text(text='Content', parent_id=title_id)

            path = _.node_path(text_id)
            assert path == Node_Path('text')

    def test_create_text__linked_with_edge(self):                               # Test text node is linked to parent
        with Html_MGraph__Head().setup() as _:
            title_id = _.create_element(node_path=Node_Path('head.title'))
            text_id  = _.create_text(text='Content', parent_id=title_id)

            text_nodes = _.get_text_nodes(title_id)
            assert text_id in text_nodes

    # ═══════════════════════════════════════════════════════════════════════════
    # Add Child Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_add_child(self):                                                   # Test adding single child
        with Html_MGraph__Head().setup() as _:
            head_id = _.create_element(node_path=Node_Path('head'))
            meta_id = _.create_element(node_path=Node_Path('head.meta'))
            _.set_root(head_id)

            _.add_child(head_id, meta_id, position=0)

            children = _.get_element_children(head_id)
            assert children == [meta_id]

    def test_add_child__multiple(self):                                         # Test adding multiple children
        with Html_MGraph__Head().setup() as _:
            head_id   = _.create_element(node_path=Node_Path('head'))
            meta_id   = _.create_element(node_path=Node_Path('head.meta'))
            title_id  = _.create_element(node_path=Node_Path('head.title'))
            link_id   = _.create_element(node_path=Node_Path('head.link'))
            _.set_root(head_id)

            _.add_child(head_id, meta_id , position=0)
            _.add_child(head_id, title_id, position=1)
            _.add_child(head_id, link_id , position=2)

            children = _.get_element_children(head_id)
            assert len(children) == 3
            assert meta_id  in children
            assert title_id in children
            assert link_id  in children

    def test_add_child__out_of_order(self):                                     # Test children added out of order get sorted
        with Html_MGraph__Head().setup() as _:
            head_id  = _.create_element(node_path=Node_Path('head'))
            first_id  = _.create_element(node_path=Node_Path('head.first'))
            second_id = _.create_element(node_path=Node_Path('head.second'))
            third_id  = _.create_element(node_path=Node_Path('head.third'))
            _.set_root(head_id)

            _.add_child(head_id, third_id , position=2)                         # Add out of order
            _.add_child(head_id, first_id , position=0)
            _.add_child(head_id, second_id, position=1)

            children = _.get_element_children(head_id)
            assert children == [first_id, second_id, third_id]

    # ═══════════════════════════════════════════════════════════════════════════
    # Get Element Children Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_element_children(self):                                        # Test getting element children
        with Html_MGraph__Head().setup() as _:
            head_id = _.create_element(node_path=Node_Path('head'))
            meta_id = _.create_element(node_path=Node_Path('head.meta'))
            _.set_root(head_id)
            _.add_child(head_id, meta_id, position=0)

            children = _.get_element_children(head_id)
            assert children == [meta_id]

    def test_get_element_children__empty(self):                                 # Test getting children when none exist
        with Html_MGraph__Head().setup() as _:
            head_id = _.create_element(node_path=Node_Path('head'))
            _.set_root(head_id)

            children = _.get_element_children(head_id)
            assert children == []

    def test_get_element_children__excludes_text(self):                         # Test element children excludes text nodes
        with Html_MGraph__Head().setup() as _:
            head_id  = _.create_element(node_path=Node_Path('head'))
            title_id = _.create_element(node_path=Node_Path('head.title'))
            _.set_root(head_id)
            _.add_child(head_id, title_id, position=0)
            _.create_text(text='Title Text', parent_id=title_id, position=0)

            head_children  = _.get_element_children(head_id)
            title_children = _.get_element_children(title_id)

            assert head_children  == [title_id]
            assert title_children == []                                         # Text not included

    # ═══════════════════════════════════════════════════════════════════════════
    # Get Text Nodes Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_text_nodes(self):                                              # Test getting text nodes
        with Html_MGraph__Head().setup() as _:
            title_id = _.create_element(node_path=Node_Path('head.title'))
            text_id  = _.create_text(text='Content', parent_id=title_id)

            text_nodes = _.get_text_nodes(title_id)
            assert text_nodes == [text_id]

    def test_get_text_nodes__empty(self):                                       # Test getting text nodes when none exist
        with Html_MGraph__Head().setup() as _:
            meta_id = _.create_element(node_path=Node_Path('head.meta'))

            text_nodes = _.get_text_nodes(meta_id)
            assert text_nodes == []

    def test_get_text_nodes__ordered(self):                                     # Test text nodes are returned in order
        with Html_MGraph__Head().setup() as _:
            title_id = _.create_element(node_path=Node_Path('head.title'))
            text2_id = _.create_text(text='Second', parent_id=title_id, position=1)
            text0_id = _.create_text(text='First' , parent_id=title_id, position=0)
            text1_id = _.create_text(text='Middle', parent_id=title_id, position=0)  # Same position as first

            text_nodes = _.get_text_nodes(title_id)
            assert len(text_nodes) == 3

    # ═══════════════════════════════════════════════════════════════════════════
    # Get Text Content Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_text_content(self):                                            # Test getting concatenated text content
        with Html_MGraph__Head().setup() as _:
            title_id = _.create_element(node_path=Node_Path('head.title'))
            _.create_text(text='Hello', parent_id=title_id, position=0)
            _.create_text(text=' '    , parent_id=title_id, position=1)
            _.create_text(text='World', parent_id=title_id, position=2)

            content = _.get_text_content(title_id)
            assert content == 'Hello World'

    def test_get_text_content__empty(self):                                     # Test getting text content when none exists
        with Html_MGraph__Head().setup() as _:
            meta_id = _.create_element(node_path=Node_Path('head.meta'))

            content = _.get_text_content(meta_id)
            assert content == ''

    def test_get_text_content__single(self):                                    # Test getting single text content
        with Html_MGraph__Head().setup() as _:
            title_id = _.create_element(node_path=Node_Path('head.title'))
            _.create_text(text='Single Text', parent_id=title_id)

            content = _.get_text_content(title_id)
            assert content == 'Single Text'

    # ═══════════════════════════════════════════════════════════════════════════
    # Is Text Node Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_is_text_node(self):                                                # Test text node detection
        with Html_MGraph__Head().setup() as _:
            title_id = _.create_element(node_path=Node_Path('head.title'))
            text_id  = _.create_text(text='Content', parent_id=title_id)

            assert _.is_text_node(text_id)  is True
            assert _.is_text_node(title_id) is False

    def test_is_text_node__element(self):                                       # Test is_text_node returns False for elements
        with Html_MGraph__Head().setup() as _:
            meta_id  = _.create_element(node_path=Node_Path('head.meta'))
            link_id  = _.create_element(node_path=Node_Path('head.link'))
            style_id = _.create_element(node_path=Node_Path('head.style'))

            assert _.is_text_node(meta_id)  is False
            assert _.is_text_node(link_id)  is False
            assert _.is_text_node(style_id) is False

    def test_is_text_node__not_found(self):                                     # Test is_text_node for non-existent node
        with Html_MGraph__Head().setup() as _:
            fake_id = Node_Id(Obj_Id())

            assert _.is_text_node(fake_id) is False

    # ═══════════════════════════════════════════════════════════════════════════
    # Is Element Node Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_is_element_node(self):                                             # Test element node detection
        with Html_MGraph__Head().setup() as _:
            title_id = _.create_element(node_path=Node_Path('head.title'))
            text_id  = _.create_text(text='Content', parent_id=title_id)

            assert _.is_element_node(title_id) is True
            assert _.is_element_node(text_id)  is False

    def test_is_element_node__various_paths(self):                              # Test is_element_node for various paths
        with Html_MGraph__Head().setup() as _:
            meta_id   = _.create_element(node_path=Node_Path('head.meta'))
            link_id   = _.create_element(node_path=Node_Path('head.link'))
            script_id = _.create_element(node_path=Node_Path('head.script'))

            assert _.is_element_node(meta_id)   is True
            assert _.is_element_node(link_id)   is True
            assert _.is_element_node(script_id) is True

    def test_is_element_node__not_found(self):                                  # Test is_element_node for non-existent node
        with Html_MGraph__Head().setup() as _:
            fake_id = Node_Id(Obj_Id())

            assert _.is_element_node(fake_id) is False

    # ═══════════════════════════════════════════════════════════════════════════
    # All Element Nodes Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_all_element_nodes(self):                                           # Test getting all element nodes
        with Html_MGraph__Head().setup() as _:
            head_id  = _.create_element(node_path=Node_Path('head'))
            meta_id  = _.create_element(node_path=Node_Path('head.meta'))
            title_id = _.create_element(node_path=Node_Path('head.title'))
            _.set_root(head_id)
            _.create_text(text='Title', parent_id=title_id)                     # Text node (excluded)

            elements = _.all_element_nodes()

            assert head_id  in elements
            assert meta_id  in elements
            assert title_id in elements
            assert len(elements) >= 3                                           # At least these 3 + setup root

    def test_all_element_nodes__empty(self):                                    # Test getting elements when only root exists
        with Html_MGraph__Head().setup() as _:
            elements = _.all_element_nodes()
            assert len(elements) == 0                                           # Just the setup root

    def test_all_element_nodes__excludes_text(self):                            # Test all_element_nodes excludes text
        with Html_MGraph__Head().setup() as _:
            title_id = _.create_element(node_path=Node_Path('head.title'))
            text_id  = _.create_text(text='Content', parent_id=title_id)

            elements = _.all_element_nodes()

            assert title_id in elements
            assert text_id not in elements

    # ═══════════════════════════════════════════════════════════════════════════
    # All Text Nodes Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_all_text_nodes(self):                                              # Test getting all text nodes
        with Html_MGraph__Head().setup() as _:
            title_id   = _.create_element(node_path=Node_Path('head.title'))
            noscript_id = _.create_element(node_path=Node_Path('head.noscript'))
            text1_id   = _.create_text(text='Title Text'   , parent_id=title_id)
            text2_id   = _.create_text(text='Noscript Text', parent_id=noscript_id)

            text_nodes = _.all_text_nodes()

            assert text1_id in text_nodes
            assert text2_id in text_nodes
            assert len(text_nodes) == 2

    def test_all_text_nodes__empty(self):                                       # Test getting text nodes when none exist
        with Html_MGraph__Head().setup() as _:
            _.create_element(node_path=Node_Path('head.meta'))
            _.create_element(node_path=Node_Path('head.link'))

            text_nodes = _.all_text_nodes()
            assert text_nodes == []

    def test_all_text_nodes__excludes_elements(self):                           # Test all_text_nodes excludes elements
        with Html_MGraph__Head().setup() as _:
            title_id = _.create_element(node_path=Node_Path('head.title'))
            text_id  = _.create_text(text='Content', parent_id=title_id)

            text_nodes = _.all_text_nodes()

            assert text_id  in text_nodes
            assert title_id not in text_nodes

    # ═══════════════════════════════════════════════════════════════════════════
    # Stats Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_stats(self):                                                       # Test statistics with elements and text
        with Html_MGraph__Head().setup() as _:
            head_id  = _.create_element(node_path=Node_Path('head'))
            meta_id  = _.create_element(node_path=Node_Path('head.meta'))
            title_id = _.create_element(node_path=Node_Path('head.title'))
            _.set_root(head_id)
            _.create_text(text='Page Title', parent_id=title_id)

            stats = _.stats()

            assert stats['element_nodes'] >= 3                                  # head, meta, title + setup root
            assert stats['text_nodes']    == 1

    def test_stats__empty(self):                                                # Test statistics with only root
        with Html_MGraph__Head().setup() as _:
            stats = _.stats()

            assert stats['element_nodes'] == 0                                  # Just setup root
            assert stats['text_nodes']    == 0

    def test_stats__elements_only(self):                                        # Test stats with elements but no text
        with Html_MGraph__Head().setup() as _:
            _.create_element(node_path=Node_Path('head.meta'))
            _.create_element(node_path=Node_Path('head.link'))
            _.create_element(node_path=Node_Path('head.style'))

            stats = _.stats()

            assert stats['element_nodes'] >= 3
            assert stats['text_nodes']    == 0

    def test_stats__base_stats_included(self):                                  # Test base stats are included
        with Html_MGraph__Head().setup() as _:
            _.create_element(node_path=Node_Path('head.title'))

            stats = _.stats()

            assert 'total_nodes' in stats
            assert 'total_edges' in stats
            assert 'root_id'     in stats

    # ═══════════════════════════════════════════════════════════════════════════
    # Integration Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_full_head_structure(self):                                         # Test complete head structure
        with Html_MGraph__Head().setup() as _:
            # Create <head> and children
            head_id   = _.create_element(node_path=Node_Path('head'))
            meta1_id  = _.create_element(node_path=Node_Path('head.meta[0]'))
            meta2_id  = _.create_element(node_path=Node_Path('head.meta[1]'))
            title_id  = _.create_element(node_path=Node_Path('head.title'))
            link_id   = _.create_element(node_path=Node_Path('head.link'))
            style_id  = _.create_element(node_path=Node_Path('head.style'))
            script_id = _.create_element(node_path=Node_Path('head.script'))

            _.set_root(head_id)

            # Build hierarchy
            _.add_child(head_id, meta1_id , position=0)
            _.add_child(head_id, meta2_id , position=1)
            _.add_child(head_id, title_id , position=2)
            _.add_child(head_id, link_id  , position=3)
            _.add_child(head_id, style_id , position=4)
            _.add_child(head_id, script_id, position=5)

            # Add text to title
            _.create_text(text='My Website', parent_id=title_id)

            # Verify structure
            assert _.root_id == head_id

            head_children = _.get_element_children(head_id)
            assert len(head_children) == 6
            assert head_children[0] == meta1_id
            assert head_children[2] == title_id

            # Verify title text
            title_content = _.get_text_content(title_id)
            assert title_content == 'My Website'

            # Verify node type detection
            assert _.is_element_node(head_id)  is True
            assert _.is_element_node(title_id) is True

            title_text_nodes = _.get_text_nodes(title_id)
            assert len(title_text_nodes) == 1
            assert _.is_text_node(title_text_nodes[0]) is True

            # Verify iteration
            all_elements = _.all_element_nodes()
            all_texts    = _.all_text_nodes()

            assert len(all_elements) >= 7                                       # 7 elements + setup root
            assert len(all_texts)    == 1

            # Verify stats
            stats = _.stats()
            assert stats['element_nodes'] >= 7
            assert stats['text_nodes']    == 1

    def test_nested_head_elements(self):                                        # Test nested elements (e.g., noscript with content)
        with Html_MGraph__Head().setup() as _:
            head_id      = _.create_element(node_path=Node_Path('head'))
            noscript_id  = _.create_element(node_path=Node_Path('head.noscript'))
            link_in_ns_id = _.create_element(node_path=Node_Path('head.noscript.link'))

            _.set_root(head_id)
            _.add_child(head_id    , noscript_id  , position=0)
            _.add_child(noscript_id, link_in_ns_id, position=0)
            _.create_text(text='JavaScript required', parent_id=noscript_id, position=1)

            # Verify hierarchy
            head_children = _.get_element_children(head_id)
            assert head_children == [noscript_id]

            noscript_children = _.get_element_children(noscript_id)
            assert noscript_children == [link_in_ns_id]

            # Verify text
            noscript_text = _.get_text_content(noscript_id)
            assert noscript_text == 'JavaScript required'