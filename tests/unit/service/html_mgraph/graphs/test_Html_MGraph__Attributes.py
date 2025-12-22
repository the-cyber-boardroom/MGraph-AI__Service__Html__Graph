from unittest                                                                           import TestCase

from mgraph_ai_service_html_graph.schemas.html.Schema__Html_MGraph import Schema__Html_MGraph__Stats__Attributes
from mgraph_ai_service_html_graph.service.html_mgraph.graphs.Html_MGraph__Attributes    import Html_MGraph__Attributes
from mgraph_ai_service_html_graph.service.html_mgraph.graphs.Html_MGraph__Base          import Html_MGraph__Base
from mgraph_db.mgraph.schemas.identifiers.Node_Path                                     import Node_Path
from mgraph_db.utils.testing.mgraph_test_ids                                            import mgraph_test_ids
from osbot_utils.testing.__                                                             import __
from osbot_utils.type_safe.Type_Safe                                                    import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id                       import Node_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Obj_Id                        import Obj_Id
from osbot_utils.utils.Objects                                                          import base_classes


class test_Html_MGraph__Attributes(TestCase):                                   # Test attributes graph for tags and attributes

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                     # Test default initialization
        with Html_MGraph__Attributes() as _:
            assert type(_)           is Html_MGraph__Attributes
            assert base_classes(_)   == [Html_MGraph__Base, Type_Safe, object]
            assert _.PREDICATE_TAG   is not None
            assert _.PREDICATE_ELEMENT is not None
            assert _.PREDICATE_ATTR  is not None
            assert _.PATH_ROOT       == 'attributes'

    def test_setup(self):                                                       # Test setup creates root and initializes cache
        with Html_MGraph__Attributes().setup() as _:
            assert _.mgraph         is not None
            assert _.root_id        is not None
            assert _.tag_node_cache == {}

    def test_setup_creates_root(self):                                          # Test setup creates root with correct path
        with Html_MGraph__Attributes().setup() as _:
            root_path = _.node_path(_.root_id)
            assert root_path == Node_Path('attributes')

    # ═══════════════════════════════════════════════════════════════════════════
    # Register Element Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_register_element(self):                                            # Test basic element registration
        with Html_MGraph__Attributes().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.register_element(node_id, 'div')

            assert _.get_tag(node_id) == 'div'

    def test_register_element__creates_tag_node(self):                          # Test that registering creates tag node
        with Html_MGraph__Attributes().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.register_element(node_id, 'span')

            tags = _.get_all_tags()
            assert 'span' in tags

    def test_register_element__reuses_tag_node(self):                           # Test that same tag reuses tag node
        with Html_MGraph__Attributes().setup() as _:
            node1 = Node_Id(Obj_Id())
            node2 = Node_Id(Obj_Id())
            _.register_element(node1, 'div')
            _.register_element(node2, 'div')

            tags = _.get_all_tags()
            assert tags.count('div') == 1                                       # Only one tag node

            divs = _.get_elements_by_tag('div')
            assert len(divs) == 2                                               # Both elements registered

    def test_register_element__multiple_tags(self):                             # Test registering elements with different tags
        with Html_MGraph__Attributes().setup() as _:
            _.register_element(Node_Id(Obj_Id()), 'div')
            _.register_element(Node_Id(Obj_Id()), 'p')
            _.register_element(Node_Id(Obj_Id()), 'span')
            _.register_element(Node_Id(Obj_Id()), 'a')

            tags = _.get_all_tags()
            assert set(tags) == {'div', 'p', 'span', 'a'}

    # ═══════════════════════════════════════════════════════════════════════════
    # Add Attribute Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_add_attribute(self):                                               # Test basic attribute addition
        with Html_MGraph__Attributes().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.register_element(node_id, 'div')
            attr_node_id = _.add_attribute(node_id, 'class', 'container', position=0)

            assert attr_node_id is not None
            assert _.get_attribute(node_id, 'class') == 'container'

    def test_add_attribute__multiple(self):                                     # Test adding multiple attributes
        with Html_MGraph__Attributes().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.register_element(node_id, 'div')
            _.add_attribute(node_id, 'class', 'container', position=0)
            _.add_attribute(node_id, 'id'   , 'main'     , position=1)
            _.add_attribute(node_id, 'data-x', 'value'   , position=2)

            attrs = _.get_attributes(node_id)
            assert attrs == {'class': 'container', 'id': 'main', 'data-x': 'value'}

    def test_add_attribute__preserves_order(self):                              # Test attribute order is preserved
        with Html_MGraph__Attributes().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.register_element(node_id, 'input')
            _.add_attribute(node_id, 'type' , 'text'  , position=0)
            _.add_attribute(node_id, 'name' , 'field' , position=1)
            _.add_attribute(node_id, 'value', 'hello' , position=2)

            attrs = _.get_attributes(node_id)
            keys  = list(attrs.keys())
            assert keys == ['type', 'name', 'value']                            # Order preserved

    def test_add_attribute__out_of_order_positions(self):                       # Test attributes added out of order get sorted
        with Html_MGraph__Attributes().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.register_element(node_id, 'div')
            _.add_attribute(node_id, 'third' , 'c', position=2)                 # Add out of order
            _.add_attribute(node_id, 'first' , 'a', position=0)
            _.add_attribute(node_id, 'second', 'b', position=1)

            attrs = _.get_attributes(node_id)
            keys  = list(attrs.keys())
            assert keys == ['first', 'second', 'third']

    # ═══════════════════════════════════════════════════════════════════════════
    # _get_or_create_tag_node Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__get_or_create_tag_node__creates_new(self):                        # Test creating new tag node
        with Html_MGraph__Attributes().setup() as _:
            assert 'div' not in _.tag_node_cache

            node_id = Node_Id(Obj_Id())
            _.register_element(node_id, 'div')

            assert 'div' in _.tag_node_cache

    def test__get_or_create_tag_node__returns_cached(self):                     # Test returning cached tag node
        with Html_MGraph__Attributes().setup() as _:
            node1 = Node_Id(Obj_Id())
            node2 = Node_Id(Obj_Id())

            _.register_element(node1, 'p')
            first_tag_node = _.tag_node_cache['p']

            _.register_element(node2, 'p')
            second_tag_node = _.tag_node_cache['p']

            assert first_tag_node == second_tag_node                            # Same tag node reused

    # ═══════════════════════════════════════════════════════════════════════════
    # Get Tag Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_tag(self):                                                     # Test getting tag for element
        with Html_MGraph__Attributes().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.register_element(node_id, 'div')

            assert _.get_tag(node_id) == 'div'

    def test_get_tag__not_found(self):                                          # Test getting tag for non-registered element
        with Html_MGraph__Attributes().setup() as _:
            fake_id = Node_Id(Obj_Id())
            result  = _.get_tag(fake_id)

            assert result is None

    def test_get_tag__different_tags(self):                                     # Test getting tags for multiple elements
        with Html_MGraph__Attributes().setup() as _:
            div_id  = Node_Id(Obj_Id())
            p_id    = Node_Id(Obj_Id())
            span_id = Node_Id(Obj_Id())

            _.register_element(div_id , 'div')
            _.register_element(p_id   , 'p')
            _.register_element(span_id, 'span')

            assert _.get_tag(div_id)  == 'div'
            assert _.get_tag(p_id)    == 'p'
            assert _.get_tag(span_id) == 'span'

    # ═══════════════════════════════════════════════════════════════════════════
    # Get Elements By Tag Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_elements_by_tag(self):                                         # Test getting elements by tag
        with Html_MGraph__Attributes().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.register_element(node_id, 'div')

            divs = _.get_elements_by_tag('div')
            assert divs == [node_id]

    def test_get_elements_by_tag__multiple(self):                               # Test getting multiple elements with same tag
        with Html_MGraph__Attributes().setup() as _:
            div1 = Node_Id(Obj_Id())
            div2 = Node_Id(Obj_Id())
            div3 = Node_Id(Obj_Id())
            p1   = Node_Id(Obj_Id())

            _.register_element(div1, 'div')
            _.register_element(div2, 'div')
            _.register_element(div3, 'div')
            _.register_element(p1  , 'p')

            divs = _.get_elements_by_tag('div')
            assert len(divs) == 3
            assert div1 in divs
            assert div2 in divs
            assert div3 in divs
            assert p1 not in divs

    def test_get_elements_by_tag__not_found(self):                              # Test getting elements for non-existent tag
        with Html_MGraph__Attributes().setup() as _:
            _.register_element(Node_Id(Obj_Id()), 'div')

            result = _.get_elements_by_tag('nonexistent')
            assert result == []

    def test_get_elements_by_tag__from_path_lookup(self):                       # Test getting elements when tag not in cache
        with Html_MGraph__Attributes().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.register_element(node_id, 'aside')

            _.tag_node_cache.clear()                                            # Clear cache to force path lookup

            result = _.get_elements_by_tag('aside')
            assert node_id in result

    def test_get_elements_by_tag__empty_cache(self):                            # Test with empty cache for non-existent tag
        with Html_MGraph__Attributes().setup() as _:
            _.register_element(Node_Id(Obj_Id()), 'div')
            _.tag_node_cache.clear()

            result = _.get_elements_by_tag('nonexistent')
            assert result == []

    # ═══════════════════════════════════════════════════════════════════════════
    # Get All Tags Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_all_tags(self):                                                # Test getting all unique tags
        with Html_MGraph__Attributes().setup() as _:
            _.register_element(Node_Id(Obj_Id()), 'div')
            _.register_element(Node_Id(Obj_Id()), 'p')
            _.register_element(Node_Id(Obj_Id()), 'div')                        # Second div

            tags = _.get_all_tags()
            assert set(tags) == {'div', 'p'}                                    # Unique tags

    def test_get_all_tags__empty(self):                                         # Test getting tags when none registered
        with Html_MGraph__Attributes().setup() as _:
            tags = _.get_all_tags()
            assert tags == []

    def test_get_all_tags__single(self):                                        # Test getting single tag
        with Html_MGraph__Attributes().setup() as _:
            _.register_element(Node_Id(Obj_Id()), 'main')

            tags = _.get_all_tags()
            assert tags == ['main']

    # ═══════════════════════════════════════════════════════════════════════════
    # Get Attributes Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_attributes(self):                                              # Test getting all attributes
        with Html_MGraph__Attributes().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.register_element(node_id, 'div')
            _.add_attribute(node_id, 'class', 'container', position=0)
            _.add_attribute(node_id, 'id'   , 'main'     , position=1)

            attrs = _.get_attributes(node_id)
            assert attrs == {'class': 'container', 'id': 'main'}

    def test_get_attributes__empty(self):                                       # Test getting attributes when none set
        with Html_MGraph__Attributes().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.register_element(node_id, 'br')

            attrs = _.get_attributes(node_id)
            assert attrs == {}

    def test_get_attributes__non_existent_element(self):                        # Test getting attributes for non-registered element
        with Html_MGraph__Attributes().setup() as _:
            fake_id = Node_Id(Obj_Id())
            attrs   = _.get_attributes(fake_id)

            assert attrs == {}

    def test_get_attributes__with_empty_value(self):                            # Test attribute with empty value
        with Html_MGraph__Attributes().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.register_element(node_id, 'input')
            _.add_attribute(node_id, 'disabled', '', position=0)

            attrs = _.get_attributes(node_id)
            assert attrs == {'disabled': ''}

    # ═══════════════════════════════════════════════════════════════════════════
    # Get Attribute (Single) Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_attribute(self):                                               # Test getting single attribute
        with Html_MGraph__Attributes().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.register_element(node_id, 'a')
            _.add_attribute(node_id, 'href', 'https://example.com', position=0)

            assert _.get_attribute(node_id, 'href') == 'https://example.com'

    def test_get_attribute__not_found(self):                                    # Test getting non-existent attribute
        with Html_MGraph__Attributes().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.register_element(node_id, 'div')
            _.add_attribute(node_id, 'class', 'test', position=0)

            assert _.get_attribute(node_id, 'id') is None

    def test_get_attribute__from_non_registered_element(self):                  # Test getting attribute from non-registered element
        with Html_MGraph__Attributes().setup() as _:
            fake_id = Node_Id(Obj_Id())
            result  = _.get_attribute(fake_id, 'class')

            assert result is None

    # ═══════════════════════════════════════════════════════════════════════════
    # Get Elements With Attribute Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_elements_with_attribute(self):                                 # Test finding elements by attribute name
        with Html_MGraph__Attributes().setup() as _:
            div1 = Node_Id(Obj_Id())
            div2 = Node_Id(Obj_Id())
            div3 = Node_Id(Obj_Id())

            _.register_element(div1, 'div')
            _.register_element(div2, 'div')
            _.register_element(div3, 'div')

            _.add_attribute(div1, 'class', 'a', position=0)
            _.add_attribute(div2, 'class', 'b', position=0)
            _.add_attribute(div3, 'id'   , 'c', position=0)                     # No class attribute

            elements = _.get_elements_with_attribute('class')
            assert len(elements) == 2
            assert div1 in elements
            assert div2 in elements
            assert div3 not in elements

    def test_get_elements_with_attribute__with_value(self):                     # Test finding elements by attribute name and value
        with Html_MGraph__Attributes().setup() as _:
            div1 = Node_Id(Obj_Id())
            div2 = Node_Id(Obj_Id())
            div3 = Node_Id(Obj_Id())

            _.register_element(div1, 'div')
            _.register_element(div2, 'div')
            _.register_element(div3, 'div')

            _.add_attribute(div1, 'class', 'active'  , position=0)
            _.add_attribute(div2, 'class', 'inactive', position=0)
            _.add_attribute(div3, 'class', 'active'  , position=0)

            elements = _.get_elements_with_attribute('class', 'active')
            assert len(elements) == 2
            assert div1 in elements
            assert div3 in elements
            assert div2 not in elements

    def test_get_elements_with_attribute__not_found(self):                      # Test finding elements with non-existent attribute
        with Html_MGraph__Attributes().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.register_element(node_id, 'div')
            _.add_attribute(node_id, 'class', 'test', position=0)

            elements = _.get_elements_with_attribute('data-nonexistent')
            assert elements == []

    def test_get_elements_with_attribute__value_no_match(self):                 # Test finding elements with value that doesn't match
        with Html_MGraph__Attributes().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.register_element(node_id, 'div')
            _.add_attribute(node_id, 'class', 'actual', position=0)

            elements = _.get_elements_with_attribute('class', 'expected')
            assert elements == []

    # ═══════════════════════════════════════════════════════════════════════════
    # Helper Method Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__is_element_anchor(self):                                          # Test element anchor detection
        with Html_MGraph__Attributes().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.register_element(node_id, 'div')

            assert _._is_element_anchor(node_id) is True
            assert _._is_element_anchor(_.root_id) is False

    def test__is_element_anchor__not_found(self):                               # Test element anchor for non-existent node
        with Html_MGraph__Attributes().setup() as _:
            fake_id = Node_Id(Obj_Id())
            assert _._is_element_anchor(fake_id) is False

    def test__is_tag_node(self):                                                # Test tag node detection
        with Html_MGraph__Attributes().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.register_element(node_id, 'div')

            tag_node_id = _.tag_node_cache['div']
            assert _._is_tag_node(tag_node_id) is True
            assert _._is_tag_node(node_id)     is False

    def test__is_tag_node__not_found(self):                                     # Test tag node for non-existent node
        with Html_MGraph__Attributes().setup() as _:
            fake_id = Node_Id(Obj_Id())
            assert _._is_tag_node(fake_id) is False

    def test__is_attr_value_node(self):                                         # Test attribute value node detection
        with Html_MGraph__Attributes().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.register_element(node_id, 'div')
            attr_node_id = _.add_attribute(node_id, 'class', 'test', position=0)

            assert _._is_attr_value_node(attr_node_id) is True
            assert _._is_attr_value_node(node_id)      is False

    def test__is_attr_value_node__not_found(self):                              # Test attr value node for non-existent node
        with Html_MGraph__Attributes().setup() as _:
            fake_id = Node_Id(Obj_Id())
            assert _._is_attr_value_node(fake_id) is False

    def test__is_attr_value_node__non_numeric_path(self):                       # Test attr value node with non-numeric path
        with Html_MGraph__Attributes().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.register_element(node_id, 'div')

            assert _._is_attr_value_node(node_id) is False                      # element: prefix is not numeric

    # ═══════════════════════════════════════════════════════════════════════════
    # Stats Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_stats(self):                                                       # Test statistics with populated graph
        with mgraph_test_ids():
            with Html_MGraph__Attributes().setup() as _:
                div_id = Node_Id(Obj_Id())
                p_id   = Node_Id(Obj_Id())

                _.register_element(div_id, 'div')
                _.register_element(p_id  , 'p')

                _.add_attribute(div_id, 'class', 'container', position=0)
                _.add_attribute(div_id, 'id'   , 'main'     , position=1)
                _.add_attribute(p_id  , 'class', 'text'     , position=0)

                stats = _.stats()
                assert type(stats) is Schema__Html_MGraph__Stats__Attributes
                assert stats.obj() == __(registered_elements=2,
                                         total_attributes=3,
                                         unique_tags=2,
                                         total_nodes=9,
                                         total_edges=7,
                                         root_id='c0000002')
                assert stats.unique_tags         == 2                                  # div, p
                assert stats.registered_elements == 2                                  # 2 registered elements
                assert stats.total_attributes    == 3                                  # 3 attributes

    def test_stats__empty(self):                                                # Test statistics with no elements
        with Html_MGraph__Attributes().setup() as _:
            stats = _.stats()

            assert stats.unique_tags     == 0
            assert stats.registered_elements == 0
            assert stats.total_attributes    == 0

    def test_stats__elements_only(self):                                        # Test stats with elements but no attributes
        with Html_MGraph__Attributes().setup() as _:
            _.register_element(Node_Id(Obj_Id()), 'div')
            _.register_element(Node_Id(Obj_Id()), 'span')

            stats = _.stats()

            assert stats.unique_tags     == 2
            assert stats.registered_elements == 2
            assert stats.total_attributes    == 0

    # ═══════════════════════════════════════════════════════════════════════════
    # Integration Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_full_workflow(self):                                               # Test complete workflow
        with mgraph_test_ids():
            with Html_MGraph__Attributes().setup() as _:
                # Register elements
                html_id = Node_Id(Obj_Id())
                head_id = Node_Id(Obj_Id())
                body_id = Node_Id(Obj_Id())
                div_id  = Node_Id(Obj_Id())

                _.register_element(html_id, 'html')
                _.register_element(head_id, 'head')
                _.register_element(body_id, 'body')
                _.register_element(div_id , 'div')

                # Add attributes
                _.add_attribute(html_id, 'lang' , 'en'       , position=0)
                _.add_attribute(body_id, 'class', 'container', position=0)
                _.add_attribute(div_id , 'class', 'content'  , position=0)
                _.add_attribute(div_id , 'id'   , 'main'     , position=1)

                # Verify tags
                assert _.get_tag(html_id) == 'html'
                assert _.get_tag(head_id) == 'head'
                assert _.get_tag(body_id) == 'body'
                assert _.get_tag(div_id)  == 'div'

                # Verify attributes
                assert _.get_attributes(html_id) == {'lang': 'en'}
                assert _.get_attributes(head_id) == {}
                assert _.get_attributes(body_id) == {'class': 'container'}
                assert _.get_attributes(div_id)  == {'class': 'content', 'id': 'main'}

                # Verify lookups
                assert _.get_elements_by_tag('div') == [div_id]
                assert len(_.get_all_tags())        == 4

                containers = _.get_elements_with_attribute('class', 'container')
                assert containers == [body_id]

                stats = _.stats()
                assert stats.obj() == __(registered_elements=4,
                                         total_attributes=4,
                                         unique_tags=4,
                                         total_nodes=14,
                                         total_edges=12,
                                         root_id='c0000002')
                assert stats.unique_tags     == 4
                assert stats.registered_elements == 4
                assert stats.total_attributes    == 4