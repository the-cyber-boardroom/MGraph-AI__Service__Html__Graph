from unittest                                                                       import TestCase
from mgraph_ai_service_html_graph.schemas.html.Schema__Html_MGraph                  import Schema__Html_MGraph__Stats__Scripts
from mgraph_ai_service_html_graph.service.html_mgraph.graphs.Html_MGraph__Scripts   import Html_MGraph__Scripts
from mgraph_ai_service_html_graph.service.html_mgraph.graphs.Html_MGraph__Base      import Html_MGraph__Base
from mgraph_db.mgraph.schemas.identifiers.Node_Path                                 import Node_Path
from mgraph_db.utils.testing.mgraph_test_ids                                        import mgraph_test_ids
from osbot_utils.testing.__                                                         import __
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id                   import Node_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Obj_Id                    import Obj_Id
from osbot_utils.utils.Objects                                                      import base_classes


class test_Html_MGraph__Scripts(TestCase):                                      # Test scripts graph for JavaScript content

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                     # Test default initialization
        with Html_MGraph__Scripts() as _:
            assert type(_)              is Html_MGraph__Scripts
            assert base_classes(_)      == [Html_MGraph__Base, Type_Safe, object]
            assert _.PREDICATE_SCRIPT   is not None
            assert _.PREDICATE_CONTENT  is not None
            assert _.PREDICATE_AST      is not None
            assert _.PATH_ROOT          == 'scripts'

    def test_setup(self):                                                       # Test setup creates root and initializes counter
        with Html_MGraph__Scripts().setup() as _:
            assert _.mgraph       is not None
            assert _.root_id      is not None
            assert _.script_order == 0

    def test_setup_creates_root(self):                                          # Test setup creates root with correct path
        with Html_MGraph__Scripts().setup() as _:
            root_path = _.node_path(_.root_id)
            assert root_path == Node_Path('scripts')

    # ═══════════════════════════════════════════════════════════════════════════
    # Register Script Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_register_script__inline(self):                                     # Test inline script registration
        with Html_MGraph__Scripts().setup() as _:
            node_id    = Node_Id(Obj_Id())
            content_id = _.register_script(node_id, content="console.log('hello');")

            assert content_id is not None
            assert _.get_script_content(node_id) == "console.log('hello');"

    def test_register_script__external(self):                                   # Test external script registration (no content)
        with Html_MGraph__Scripts().setup() as _:
            node_id    = Node_Id(Obj_Id())
            content_id = _.register_script(node_id, content=None)

            assert content_id is None
            assert _.get_script_content(node_id) is None

    def test_register_script__increments_order(self):                           # Test script order counter increments
        with Html_MGraph__Scripts().setup() as _:
            assert _.script_order == 0

            _.register_script(Node_Id(Obj_Id()), content="a")
            assert _.script_order == 1

            _.register_script(Node_Id(Obj_Id()), content="b")
            assert _.script_order == 2

            _.register_script(Node_Id(Obj_Id()), content=None)
            assert _.script_order == 3

    def test_register_script__creates_anchor(self):                             # Test script registration creates anchor node
        with Html_MGraph__Scripts().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.register_script(node_id, content="var x = 1;")

            node = _.node(node_id)                                              # Anchor node should exist
            assert node is not None

    def test_register_script__multiple_inline(self):                            # Test multiple inline scripts
        with Html_MGraph__Scripts().setup() as _:
            script1_id = Node_Id(Obj_Id())
            script2_id = Node_Id(Obj_Id())
            script3_id = Node_Id(Obj_Id())

            _.register_script(script1_id, content="/* script 1 */")
            _.register_script(script2_id, content="/* script 2 */")
            _.register_script(script3_id, content="/* script 3 */")

            assert _.get_script_content(script1_id) == "/* script 1 */"
            assert _.get_script_content(script2_id) == "/* script 2 */"
            assert _.get_script_content(script3_id) == "/* script 3 */"

    # ═══════════════════════════════════════════════════════════════════════════
    # _add_content Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__add_content(self):                                                # Test adding content to script element
        with Html_MGraph__Scripts().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.register_script(node_id, content=None)                            # First register without content

            content_id = _._add_content(node_id, "/* added later */", position=0)

            assert content_id is not None
            assert _.get_script_content(node_id) == "/* added later */"

    def test__add_content__with_position(self):                                 # Test content with specific position
        with Html_MGraph__Scripts().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.register_script(node_id, content=None)

            content_id = _._add_content(node_id, "positioned content", position=5)

            assert content_id is not None

    # ═══════════════════════════════════════════════════════════════════════════
    # Get Script Content Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_script_content(self):                                          # Test getting script content
        with Html_MGraph__Scripts().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.register_script(node_id, content="function test() { return 1; }")

            content = _.get_script_content(node_id)
            assert content == "function test() { return 1; }"

    def test_get_script_content__external(self):                                # Test getting content for external script
        with Html_MGraph__Scripts().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.register_script(node_id, content=None)

            content = _.get_script_content(node_id)
            assert content is None

    def test_get_script_content__not_registered(self):                          # Test getting content for non-registered script
        with Html_MGraph__Scripts().setup() as _:
            fake_id = Node_Id(Obj_Id())
            content = _.get_script_content(fake_id)

            assert content is None

    def test_get_script_content__empty_string(self):                            # Test script with empty content
        with Html_MGraph__Scripts().setup() as _:
            node_id = Node_Id(Obj_Id())
            _.register_script(node_id, content="")

            content = _.get_script_content(node_id)
            assert content is None                                              # Empty string treated as no content

    # ═══════════════════════════════════════════════════════════════════════════
    # Is Inline/External Script Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_is_inline_script(self):                                            # Test inline script detection
        with Html_MGraph__Scripts().setup() as _:
            inline_id   = Node_Id(Obj_Id())
            external_id = Node_Id(Obj_Id())

            _.register_script(inline_id  , content="/* inline */")
            _.register_script(external_id, content=None)

            assert _.is_inline_script(inline_id)   is True
            assert _.is_inline_script(external_id) is False

    def test_is_external_script(self):                                          # Test external script detection
        with Html_MGraph__Scripts().setup() as _:
            inline_id   = Node_Id(Obj_Id())
            external_id = Node_Id(Obj_Id())

            _.register_script(inline_id  , content="/* inline */")
            _.register_script(external_id, content=None)

            assert _.is_external_script(inline_id)   is False
            assert _.is_external_script(external_id) is True

    def test_is_inline_script__not_registered(self):                            # Test inline check for non-registered script
        with Html_MGraph__Scripts().setup() as _:
            fake_id = Node_Id(Obj_Id())

            assert _.is_inline_script(fake_id) is False

    def test_is_external_script__not_registered(self):                          # Test external check for non-registered script
        with Html_MGraph__Scripts().setup() as _:
            fake_id = Node_Id(Obj_Id())

            assert _.is_external_script(fake_id) is True                        # No content = external

    # ═══════════════════════════════════════════════════════════════════════════
    # Get All Scripts Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_all_scripts(self):                                             # Test getting all scripts
        with Html_MGraph__Scripts().setup() as _:
            script1_id = Node_Id(Obj_Id())
            script2_id = Node_Id(Obj_Id())

            _.register_script(script1_id, content="/* first */")
            _.register_script(script2_id, content="/* second */")

            all_scripts = _.get_all_scripts()
            assert len(all_scripts) == 2
            assert script1_id in all_scripts
            assert script2_id in all_scripts

    def test_get_all_scripts__empty(self):                                      # Test getting scripts when none registered
        with Html_MGraph__Scripts().setup() as _:
            all_scripts = _.get_all_scripts()
            assert all_scripts == []

    def test_get_all_scripts__preserves_order(self):                            # Test scripts are returned in registration order
        with Html_MGraph__Scripts().setup() as _:
            first_id  = Node_Id(Obj_Id())
            second_id = Node_Id(Obj_Id())
            third_id  = Node_Id(Obj_Id())

            _.register_script(first_id , content="/* 1 */")
            _.register_script(second_id, content="/* 2 */")
            _.register_script(third_id , content="/* 3 */")

            all_scripts = _.get_all_scripts()
            assert all_scripts == [first_id, second_id, third_id]

    def test_get_all_scripts__mixed_inline_external(self):                      # Test getting mixed inline and external scripts
        with Html_MGraph__Scripts().setup() as _:
            inline1_id  = Node_Id(Obj_Id())
            external_id = Node_Id(Obj_Id())
            inline2_id  = Node_Id(Obj_Id())

            _.register_script(inline1_id , content="/* inline 1 */")
            _.register_script(external_id, content=None)
            _.register_script(inline2_id , content="/* inline 2 */")

            all_scripts = _.get_all_scripts()
            assert len(all_scripts) == 3
            assert all_scripts == [inline1_id, external_id, inline2_id]

    # ═══════════════════════════════════════════════════════════════════════════
    # Get Inline/External Scripts Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_inline_scripts(self):                                          # Test getting only inline scripts
        with Html_MGraph__Scripts().setup() as _:
            inline1_id  = Node_Id(Obj_Id())
            external_id = Node_Id(Obj_Id())
            inline2_id  = Node_Id(Obj_Id())

            _.register_script(inline1_id , content="/* inline 1 */")
            _.register_script(external_id, content=None)
            _.register_script(inline2_id , content="/* inline 2 */")

            inline_scripts = _.get_inline_scripts()
            assert len(inline_scripts) == 2
            assert inline1_id in inline_scripts
            assert inline2_id in inline_scripts
            assert external_id not in inline_scripts

    def test_get_inline_scripts__empty(self):                                   # Test getting inline scripts when all external
        with Html_MGraph__Scripts().setup() as _:
            _.register_script(Node_Id(Obj_Id()), content=None)
            _.register_script(Node_Id(Obj_Id()), content=None)

            inline_scripts = _.get_inline_scripts()
            assert inline_scripts == []

    def test_get_external_scripts(self):                                        # Test getting only external scripts
        with Html_MGraph__Scripts().setup() as _:
            inline_id    = Node_Id(Obj_Id())
            external1_id = Node_Id(Obj_Id())
            external2_id = Node_Id(Obj_Id())

            _.register_script(inline_id   , content="/* inline */")
            _.register_script(external1_id, content=None)
            _.register_script(external2_id, content=None)

            external_scripts = _.get_external_scripts()
            assert len(external_scripts) == 2
            assert external1_id in external_scripts
            assert external2_id in external_scripts
            assert inline_id not in external_scripts

    def test_get_external_scripts__empty(self):                                 # Test getting external scripts when all inline
        with Html_MGraph__Scripts().setup() as _:
            _.register_script(Node_Id(Obj_Id()), content="/* a */")
            _.register_script(Node_Id(Obj_Id()), content="/* b */")

            external_scripts = _.get_external_scripts()
            assert external_scripts == []

    # ═══════════════════════════════════════════════════════════════════════════
    # Stats Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_stats(self):                                                       # Test statistics with mixed scripts
        with Html_MGraph__Scripts().setup() as _:
            _.register_script(Node_Id(Obj_Id()), content="/* 1 */")
            _.register_script(Node_Id(Obj_Id()), content="/* 2 */")
            _.register_script(Node_Id(Obj_Id()), content=None)
            _.register_script(Node_Id(Obj_Id()), content=None)
            _.register_script(Node_Id(Obj_Id()), content=None)

            stats = _.stats()

            assert stats.total_scripts    == 5
            assert stats.inline_scripts   == 2
            assert stats.external_scripts == 3

    def test_stats__empty(self):                                                # Test statistics with no scripts
        with Html_MGraph__Scripts().setup() as _:
            stats = _.stats()

            assert stats.total_scripts    == 0
            assert stats.inline_scripts   == 0
            assert stats.external_scripts == 0

    def test_stats__only_inline(self):                                          # Test statistics with only inline scripts
        with Html_MGraph__Scripts().setup() as _:
            _.register_script(Node_Id(Obj_Id()), content="/* a */")
            _.register_script(Node_Id(Obj_Id()), content="/* b */")

            stats = _.stats()

            assert stats.total_scripts    == 2
            assert stats.inline_scripts   == 2
            assert stats.external_scripts == 0

    def test_stats__only_external(self):                                        # Test statistics with only external scripts
        with Html_MGraph__Scripts().setup() as _:
            _.register_script(Node_Id(Obj_Id()), content=None)
            _.register_script(Node_Id(Obj_Id()), content=None)

            stats = _.stats()

            assert stats.total_scripts    == 2
            assert stats.inline_scripts   == 0
            assert stats.external_scripts == 2

    def test_stats__base_stats_included(self):                                  # Test base stats are included
        with mgraph_test_ids():
            with Html_MGraph__Scripts().setup() as _:
                _.register_script(Node_Id(Obj_Id()), content="test")

                stats = _.stats()
                assert stats.obj() == __(total_scripts=1,
                                         inline_scripts=1,
                                         external_scripts=0,
                                         total_nodes=4,
                                         total_edges=2,
                                         root_id='c0000002')

    # ═══════════════════════════════════════════════════════════════════════════
    # Integration Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_full_workflow(self):                                               # Test complete workflow
        with mgraph_test_ids():
            with Html_MGraph__Scripts().setup() as _:
                # Register various scripts
                init_script_id    = Node_Id(Obj_Id())
                app_script_id     = Node_Id(Obj_Id())
                external_lib_id   = Node_Id(Obj_Id())
                analytics_id      = Node_Id(Obj_Id())

                _.register_script(init_script_id   , content="window.APP = {};")
                _.register_script(app_script_id    , content="APP.init = function() { console.log('init'); };")
                _.register_script(external_lib_id  , content=None)                  # External library
                _.register_script(analytics_id     , content="ga('send', 'pageview');")

                # Verify content retrieval
                assert _.get_script_content(init_script_id)   == "window.APP = {};"
                assert _.get_script_content(app_script_id)    == "APP.init = function() { console.log('init'); };"
                assert _.get_script_content(external_lib_id)  is None
                assert _.get_script_content(analytics_id)     == "ga('send', 'pageview');"

                # Verify type detection
                assert _.is_inline_script(init_script_id)     is True
                assert _.is_external_script(external_lib_id)  is True

                # Verify ordering
                all_scripts = _.get_all_scripts()
                assert all_scripts == [init_script_id, app_script_id, external_lib_id, analytics_id]

                # Verify filtered lists
                inline_scripts   = _.get_inline_scripts()
                external_scripts = _.get_external_scripts()
                assert len(inline_scripts)   == 3
                assert len(external_scripts) == 1

                # Verify stats
                stats = _.stats()
                assert type(stats) is Schema__Html_MGraph__Stats__Scripts
                assert stats.obj() == __(total_scripts=4,
                                         inline_scripts=3,
                                         external_scripts=1,
                                         total_nodes=9,
                                         total_edges=7,
                                         root_id='c0000002')
                assert stats.total_scripts    == 4
                assert stats.inline_scripts   == 3
                assert stats.external_scripts == 1