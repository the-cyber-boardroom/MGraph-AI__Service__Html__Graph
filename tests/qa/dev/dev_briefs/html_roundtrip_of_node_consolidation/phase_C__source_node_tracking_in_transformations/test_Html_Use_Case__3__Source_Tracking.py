# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Html_Use_Case__3__Source_Tracking
# Verifies source tracking with minimal overrides pattern
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                           import TestCase
from mgraph_ai_service_html_graph.service.html_graph__transformations.html_use_cases.Html_Use_Case__3   import Html_Use_Case__3
from Html_Use_Case__3__Source_Tracking                                                                  import Html_Use_Case__3__Source_Tracking


class test_Html_Use_Case__3__Flatten__Source_Tracking(TestCase):

    # ═══════════════════════════════════════════════════════════════════════════
    # Inheritance Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_is_subclass_of_flatten(self):                                      # Verify inheritance
        assert issubclass(Html_Use_Case__3__Source_Tracking, Html_Use_Case__3)

    def test_inherits_base_methods(self):                                       # Verify inherited methods exist
        with Html_Use_Case__3__Source_Tracking() as _:
            # These should be inherited from base class
            assert hasattr(_, 'step_2___remove_wrapper_nodes')
            assert hasattr(_, 'step_4___collapse_single_parents')
            assert hasattr(_, 'update_node_labels')
            assert hasattr(_, 'create_dot_code')
            assert hasattr(_, 'extract_tag')
            assert hasattr(_, 'get_text_value')
            assert hasattr(_, 'merge_text_values')
            assert hasattr(_, 'create_merged_text_node')

    def test_has_tracking_attributes(self):                                     # Verify tracking attributes
        with Html_Use_Case__3__Source_Tracking() as _:
            assert hasattr(_, 'source_mapping')
            assert hasattr(_, 'wrapper_mapping')

    def test_has_query_methods(self):                                           # Verify query methods exist
        with Html_Use_Case__3__Source_Tracking() as _:
            assert hasattr(_, 'get_source_node_ids')
            assert hasattr(_, 'get_wrapper_info')
            assert hasattr(_, 'get_all_source_mappings')
            assert hasattr(_, 'get_all_wrapper_mappings')

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_mappings_none_before_transform(self):                              # Mappings are None initially
        with Html_Use_Case__3__Source_Tracking() as _:
            assert _.source_mapping  is None
            assert _.wrapper_mapping is None

    # ═══════════════════════════════════════════════════════════════════════════
    # Query Method Safety Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_source_node_ids__returns_empty_when_none(self):
        with Html_Use_Case__3__Source_Tracking() as _:
            result = _.get_source_node_ids('any_id')
            assert type(result) is list
            assert result == []

    def test_get_wrapper_info__returns_empty_when_none(self):
        with Html_Use_Case__3__Source_Tracking() as _:
            result = _.get_wrapper_info('any_id')
            assert type(result) is dict
            assert result == {}

    def test_get_all_source_mappings__returns_empty_when_none(self):
        with Html_Use_Case__3__Source_Tracking() as _:
            result = _.get_all_source_mappings()
            assert type(result) is dict
            assert result == {}

    def test_get_all_wrapper_mappings__returns_empty_when_none(self):
        with Html_Use_Case__3__Source_Tracking() as _:
            result = _.get_all_wrapper_mappings()
            assert type(result) is dict
            assert result == {}

    # ═══════════════════════════════════════════════════════════════════════════
    # Utility Method Tests (Inherited)
    # ═══════════════════════════════════════════════════════════════════════════

    def test_extract_tag__simple(self):
        with Html_Use_Case__3__Source_Tracking() as _:
            assert _.extract_tag('div')            == 'div'
            assert _.extract_tag('body.div')       == 'div'
            assert _.extract_tag('body.div.p')     == 'p'
            assert _.extract_tag('body.div[0].a')  == 'a'
            assert _.extract_tag('')               == ''

    # ═══════════════════════════════════════════════════════════════════════════
    # Base Class Comparison Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_base_class_has_no_tracking(self):                                  # Base class should NOT have tracking
        with Html_Use_Case__3() as _:
            assert not hasattr(_, 'source_mapping') or _.source_mapping is None
            assert not hasattr(_, 'wrapper_mapping') or _.wrapper_mapping is None
            assert not hasattr(_, 'get_source_node_ids')
            assert not hasattr(_, 'get_wrapper_info')


