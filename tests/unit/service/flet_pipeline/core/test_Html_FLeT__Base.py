# ═══════════════════════════════════════════════════════════════════════════════
# test_Html_FLeT__Base - Tests for FLeT Base class
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                               import TestCase
from osbot_utils.utils.Objects                                                              import base_types
from osbot_utils.type_safe.Type_Safe                                                        import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                          import Cache_Id
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.base.Html_FLeT__Base           import Html_FLeT__Base
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Namespace      import Safe_Str__Namespace


class test_Html_FLeT__Base(TestCase):

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                               # Test auto-initialization
        with Html_FLeT__Base() as _:
            assert type(_)          is Html_FLeT__Base
            assert base_types(_)    == [Type_Safe, object]
            assert _.config         is None
            assert _.cache_client   is None
            assert _.cache_id       is None
            assert _.namespace      is None
            assert _.flow           is None
            assert _.flow_output    is None

    def test__init____with_values(self):                                                    # Test with values provided
        cache_id  = Cache_Id.new()
        with Html_FLeT__Base(namespace = 'test-ns'   ,
                             cache_id  = cache_id   ) as _:
            assert _.namespace == 'test-ns'
            assert _.cache_id  == cache_id
            assert type(_          ) is Html_FLeT__Base
            assert type(_.namespace) is Safe_Str__Namespace                                 # config autocasting by Type_Safe
            assert type(_.cache_id ) is Cache_Id

    # ═══════════════════════════════════════════════════════════════════════════
    # Abstract Method Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_setup__not_implemented(self):                                                # Test setup raises NotImplementedError
        with Html_FLeT__Base() as _:
            with self.assertRaises(NotImplementedError) as context:
                _.setup()
            assert 'setup' in str(context.exception)

    def test_run_actions__not_implemented(self):                                          # Test run_actions raises NotImplementedError
        with Html_FLeT__Base() as _:
            with self.assertRaises(NotImplementedError) as context:
                _.run_actions(input_data=None)
            assert 'run_actions' in str(context.exception)

    # ═══════════════════════════════════════════════════════════════════════════
    # Observability Method Tests (before execute)
    # ═══════════════════════════════════════════════════════════════════════════

    def test_durations__before_execute(self):                                             # Test durations returns empty dict
        with Html_FLeT__Base() as _:
            result = _.durations()
            assert type(result) is dict
            assert result       == {}

    def test_captured_logs__before_execute(self):                                         # Test captured_logs returns empty list
        with Html_FLeT__Base() as _:
            result = _.captured_logs()
            assert type(result) is list
            assert result       == []
