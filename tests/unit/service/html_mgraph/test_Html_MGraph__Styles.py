from unittest                                                               import TestCase
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph__Styles   import Html_MGraph__Styles
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph__Base     import Html_MGraph__Base
from mgraph_db.mgraph.schemas.identifiers.Node_Path                         import Node_Path
from osbot_utils.type_safe.Type_Safe                                        import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id           import Node_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Obj_Id            import Obj_Id
from osbot_utils.utils.Objects                                              import base_classes


class test_Html_MGraph__Styles(TestCase):                                       # Test styles graph for CSS content

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                     # Test default initialization
        with Html_MGraph__Styles() as _:
            assert type(_)              is Html_MGraph__Styles
            assert base_classes(_)      == [Html_MGraph__Base, Type_Safe, object]
            assert _.PREDICATE_STYLE    is not None
            assert _.PREDICATE_CONTENT  is not None
            assert _.PREDICATE_AST      is not None
            assert _.PATH_ROOT          == 'styles'

    def test_setup(self):                                                       # Test setup creates root and initializes counter
        with Html_MGraph__Styles().setup() as _:
            assert _.mgraph      is not None
            assert _.root_id     is not None
            assert _.style_order == 0

    def test_setup_creates_root(self):                                          # Test setup creates root with correct path
        with Html_MGraph__Styles().setup() as _:
            root_path = _.node_path(_.root_id)
            assert root_path == Node_Path('styles')

    # ═══════════════════════════════════════════════════════════════════════════
    # Register Style Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_register_style__inline(self):                                      # Test inline style registration
        with Html_MGraph__Styles().setup() as _:
            node_id    = Node_Id(Obj_Id())
            content_id = _.register_style(node_id, content=".container { display: flex; }")

            assert content_id is not None
            assert _.get_style_content(node_id) == ".container { display: flex; }"

    def test_register_style__external(self):                                    # Test external style registration (no content)
        with Html_MGraph__Styles().setup() as _:
            node_id    = Node_Id(Obj_Id())
            content_id = _.register_style(node_id, content=None)

            assert content_id is None
            assert _.get_style_content(node_id) is None

    def test_register_style__increments_order(self):                            # Test style order counter increments
        with Html_MGraph__Styles().setup() as _:
            assert _.style_order == 0

            _.register_style(Node_Id(Obj_Id()), content="a")
            assert _.style_order == 1

            _.register_style(Node_Id(Obj_Id()), content="b")
            assert _.style_order == 2

            _.register_style(Node_Id(Obj_Id()), content=None)
            assert _.style_order == 3

    def test_register_style__creates_anchor(self):                              # Test style registration creates anchor node
        with Html_MGraph__Styles().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.register_style(node_id, content="body { margin: 0; }")

            node = _.node(node_id)                                              # Anchor node should exist
            assert node is not None

    def test_register_style__multiple_inline(self):                             # Test multiple inline styles
        with Html_MGraph__Styles().setup() as _:
            style1_id = Node_Id(Obj_Id())
            style2_id = Node_Id(Obj_Id())
            style3_id = Node_Id(Obj_Id())

            _.register_style(style1_id, content="/* style 1 */")
            _.register_style(style2_id, content="/* style 2 */")
            _.register_style(style3_id, content="/* style 3 */")

            assert _.get_style_content(style1_id) == "/* style 1 */"
            assert _.get_style_content(style2_id) == "/* style 2 */"
            assert _.get_style_content(style3_id) == "/* style 3 */"

    # ═══════════════════════════════════════════════════════════════════════════
    # Register Link Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_register_link(self):                                               # Test external stylesheet (link) registration
        with Html_MGraph__Styles().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.register_link(node_id)

            assert _.is_external_style(node_id) is True
            assert _.is_inline_style(node_id)   is False
            assert _.get_style_content(node_id) is None

    def test_register_link__in_all_styles(self):                                # Test link appears in all_styles
        with Html_MGraph__Styles().setup() as _:
            link_id = Node_Id(Obj_Id())
            _.register_link(link_id)

            all_styles = _.get_all_styles()
            assert link_id in all_styles

    def test_register_link__increments_order(self):                             # Test link increments order counter
        with Html_MGraph__Styles().setup() as _:
            assert _.style_order == 0

            _.register_link(Node_Id(Obj_Id()))
            assert _.style_order == 1

    # ═══════════════════════════════════════════════════════════════════════════
    # _add_content Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__add_content(self):                                                # Test adding content to style element
        with Html_MGraph__Styles().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.register_style(node_id, content=None)                             # First register without content

            content_id = _._add_content(node_id, "/* added later */", position=0)

            assert content_id is not None
            assert _.get_style_content(node_id) == "/* added later */"

    def test__add_content__with_position(self):                                 # Test content with specific position
        with Html_MGraph__Styles().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.register_style(node_id, content=None)

            content_id = _._add_content(node_id, "positioned content", position=5)

            assert content_id is not None

    # ═══════════════════════════════════════════════════════════════════════════
    # Get Style Content Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_style_content(self):                                           # Test getting style content
        with Html_MGraph__Styles().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.register_style(node_id, content="p { color: red; }")

            content = _.get_style_content(node_id)
            assert content == "p { color: red; }"

    def test_get_style_content__external(self):                                 # Test getting content for external style
        with Html_MGraph__Styles().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.register_link(node_id)

            content = _.get_style_content(node_id)
            assert content is None

    def test_get_style_content__not_registered(self):                           # Test getting content for non-registered style
        with Html_MGraph__Styles().setup() as _:
            fake_id = Node_Id(Obj_Id())
            content = _.get_style_content(fake_id)

            assert content is None

    def test_get_style_content__empty_string(self):                             # Test style with empty content
        with Html_MGraph__Styles().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.register_style(node_id, content="")

            content = _.get_style_content(node_id)
            assert content is None                                              # Empty string treated as no content

    # ═══════════════════════════════════════════════════════════════════════════
    # Is Inline/External Style Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_is_inline_style(self):                                             # Test inline style detection
        with Html_MGraph__Styles().setup() as _:
            inline_id   = Node_Id(Obj_Id())
            external_id = Node_Id(Obj_Id())

            _.register_style(inline_id  , content="/* inline */")
            _.register_style(external_id, content=None)

            assert _.is_inline_style(inline_id)   is True
            assert _.is_inline_style(external_id) is False

    def test_is_external_style(self):                                           # Test external style detection
        with Html_MGraph__Styles().setup() as _:
            inline_id   = Node_Id(Obj_Id())
            external_id = Node_Id(Obj_Id())

            _.register_style(inline_id  , content="/* inline */")
            _.register_link(external_id)

            assert _.is_external_style(inline_id)   is False
            assert _.is_external_style(external_id) is True

    def test_is_inline_style__not_registered(self):                             # Test inline check for non-registered style
        with Html_MGraph__Styles().setup() as _:
            fake_id = Node_Id(Obj_Id())

            assert _.is_inline_style(fake_id) is False

    def test_is_external_style__not_registered(self):                           # Test external check for non-registered style
        with Html_MGraph__Styles().setup() as _:
            fake_id = Node_Id(Obj_Id())

            assert _.is_external_style(fake_id) is True                         # No content = external

    # ═══════════════════════════════════════════════════════════════════════════
    # Get All Styles Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_all_styles(self):                                              # Test getting all styles
        with Html_MGraph__Styles().setup() as _:
            style1_id = Node_Id(Obj_Id())
            style2_id = Node_Id(Obj_Id())

            _.register_style(style1_id, content="/* first */")
            _.register_style(style2_id, content="/* second */")

            all_styles = _.get_all_styles()
            assert len(all_styles) == 2
            assert style1_id in all_styles
            assert style2_id in all_styles

    def test_get_all_styles__empty(self):                                       # Test getting styles when none registered
        with Html_MGraph__Styles().setup() as _:
            all_styles = _.get_all_styles()
            assert all_styles == []

    def test_get_all_styles__preserves_order(self):                             # Test styles are returned in registration order
        with Html_MGraph__Styles().setup() as _:
            first_id  = Node_Id(Obj_Id())
            second_id = Node_Id(Obj_Id())
            third_id  = Node_Id(Obj_Id())

            _.register_style(first_id , content="/* 1 */")
            _.register_style(second_id, content="/* 2 */")
            _.register_style(third_id , content="/* 3 */")

            all_styles = _.get_all_styles()
            assert all_styles == [first_id, second_id, third_id]

    def test_get_all_styles__mixed_inline_external(self):                       # Test getting mixed inline and external styles
        with Html_MGraph__Styles().setup() as _:
            inline1_id  = Node_Id(Obj_Id())
            external_id = Node_Id(Obj_Id())
            inline2_id  = Node_Id(Obj_Id())

            _.register_style(inline1_id , content="/* inline 1 */")
            _.register_link(external_id)
            _.register_style(inline2_id , content="/* inline 2 */")

            all_styles = _.get_all_styles()
            assert len(all_styles) == 3
            assert all_styles == [inline1_id, external_id, inline2_id]

    # ═══════════════════════════════════════════════════════════════════════════
    # Get Inline/External Styles Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_inline_styles(self):                                           # Test getting only inline styles
        with Html_MGraph__Styles().setup() as _:
            inline1_id  = Node_Id(Obj_Id())
            external_id = Node_Id(Obj_Id())
            inline2_id  = Node_Id(Obj_Id())

            _.register_style(inline1_id , content="/* inline 1 */")
            _.register_link(external_id)
            _.register_style(inline2_id , content="/* inline 2 */")

            inline_styles = _.get_inline_styles()
            assert len(inline_styles) == 2
            assert inline1_id in inline_styles
            assert inline2_id in inline_styles
            assert external_id not in inline_styles

    def test_get_inline_styles__empty(self):                                    # Test getting inline styles when all external
        with Html_MGraph__Styles().setup() as _:
            _.register_link(Node_Id(Obj_Id()))
            _.register_link(Node_Id(Obj_Id()))

            inline_styles = _.get_inline_styles()
            assert inline_styles == []

    def test_get_external_styles(self):                                         # Test getting only external styles
        with Html_MGraph__Styles().setup() as _:
            inline_id    = Node_Id(Obj_Id())
            external1_id = Node_Id(Obj_Id())
            external2_id = Node_Id(Obj_Id())

            _.register_style(inline_id   , content="/* inline */")
            _.register_link(external1_id)
            _.register_link(external2_id)

            external_styles = _.get_external_styles()
            assert len(external_styles) == 2
            assert external1_id in external_styles
            assert external2_id in external_styles
            assert inline_id not in external_styles

    def test_get_external_styles__empty(self):                                  # Test getting external styles when all inline
        with Html_MGraph__Styles().setup() as _:
            _.register_style(Node_Id(Obj_Id()), content="/* a */")
            _.register_style(Node_Id(Obj_Id()), content="/* b */")

            external_styles = _.get_external_styles()
            assert external_styles == []

    # ═══════════════════════════════════════════════════════════════════════════
    # Stats Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_stats(self):                                                       # Test statistics with mixed styles
        with Html_MGraph__Styles().setup() as _:
            _.register_style(Node_Id(Obj_Id()), content="/* 1 */")
            _.register_style(Node_Id(Obj_Id()), content="/* 2 */")
            _.register_link(Node_Id(Obj_Id()))
            _.register_link(Node_Id(Obj_Id()))
            _.register_link(Node_Id(Obj_Id()))

            stats = _.stats()

            assert stats['total_styles']    == 5
            assert stats['inline_styles']   == 2
            assert stats['external_styles'] == 3

    def test_stats__empty(self):                                                # Test statistics with no styles
        with Html_MGraph__Styles().setup() as _:
            stats = _.stats()

            assert stats['total_styles']    == 0
            assert stats['inline_styles']   == 0
            assert stats['external_styles'] == 0

    def test_stats__only_inline(self):                                          # Test statistics with only inline styles
        with Html_MGraph__Styles().setup() as _:
            _.register_style(Node_Id(Obj_Id()), content="/* a */")
            _.register_style(Node_Id(Obj_Id()), content="/* b */")

            stats = _.stats()

            assert stats['total_styles']    == 2
            assert stats['inline_styles']   == 2
            assert stats['external_styles'] == 0

    def test_stats__only_external(self):                                        # Test statistics with only external styles
        with Html_MGraph__Styles().setup() as _:
            _.register_link(Node_Id(Obj_Id()))
            _.register_link(Node_Id(Obj_Id()))

            stats = _.stats()

            assert stats['total_styles']    == 2
            assert stats['inline_styles']   == 0
            assert stats['external_styles'] == 2

    def test_stats__base_stats_included(self):                                  # Test base stats are included
        with Html_MGraph__Styles().setup() as _:
            _.register_style(Node_Id(Obj_Id()), content="test")

            stats = _.stats()

            assert 'total_nodes' in stats
            assert 'total_edges' in stats
            assert 'root_id'     in stats

    # ═══════════════════════════════════════════════════════════════════════════
    # Integration Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_full_workflow(self):                                               # Test complete workflow
        with Html_MGraph__Styles().setup() as _:
            # Register various styles
            reset_style_id  = Node_Id(Obj_Id())
            main_style_id   = Node_Id(Obj_Id())
            external_css_id = Node_Id(Obj_Id())
            print_style_id  = Node_Id(Obj_Id())

            _.register_style(reset_style_id , content="* { margin: 0; padding: 0; }")
            _.register_style(main_style_id  , content=".container { max-width: 1200px; }")
            _.register_link(external_css_id)                                    # External CSS
            _.register_style(print_style_id , content="@media print { body { color: black; } }")

            # Verify content retrieval
            assert _.get_style_content(reset_style_id)  == "* { margin: 0; padding: 0; }"
            assert _.get_style_content(main_style_id)   == ".container { max-width: 1200px; }"
            assert _.get_style_content(external_css_id) is None
            assert _.get_style_content(print_style_id)  == "@media print { body { color: black; } }"

            # Verify type detection
            assert _.is_inline_style(reset_style_id)    is True
            assert _.is_external_style(external_css_id) is True

            # Verify ordering
            all_styles = _.get_all_styles()
            assert all_styles == [reset_style_id, main_style_id, external_css_id, print_style_id]

            # Verify filtered lists
            inline_styles   = _.get_inline_styles()
            external_styles = _.get_external_styles()
            assert len(inline_styles)   == 3
            assert len(external_styles) == 1

            # Verify stats
            stats = _.stats()
            assert stats['total_styles']    == 4
            assert stats['inline_styles']   == 3
            assert stats['external_styles'] == 1