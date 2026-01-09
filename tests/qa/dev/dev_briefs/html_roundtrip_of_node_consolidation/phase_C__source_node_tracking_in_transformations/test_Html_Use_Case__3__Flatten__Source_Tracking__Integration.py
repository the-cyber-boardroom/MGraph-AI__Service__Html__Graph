from unittest                          import TestCase
from mgraph_db.mgraph.MGraph           import MGraph
from Html_Use_Case__3__Source_Tracking import Html_Use_Case__3__Source_Tracking


class test_Html_Use_Case__3__Flatten__Source_Tracking__Integration(TestCase):           # Integration tests requiring MGraph infrastructure.

    def test_transform_resets_mappings(self):

        with Html_Use_Case__3__Source_Tracking() as _:
            # Pre-populate mappings
            _.source_mapping  = {'old': ['data']}
            _.wrapper_mapping = {'old': {'data': 'here'}}

            # Create minimal graph
            mgraph = MGraph()

            # Transform should reset
            _.transform_mgraph(mgraph)

            assert _.source_mapping  == {}                                      # Reset to empty
            assert _.wrapper_mapping == {}                                      # Reset to empty

    def test_get_all_source_mappings__returns_copy(self):                       # Should return a copy, not the original.

        with Html_Use_Case__3__Source_Tracking() as _:
            _.source_mapping = {'merged_1': ['source_a', 'source_b']}

            result = _.get_all_source_mappings()
            result['new_key'] = ['new_value']                                   # Modify the copy

            assert 'new_key' not in _.source_mapping                            # Original unchanged

    def test_get_all_wrapper_mappings__returns_copy(self):                      # Should return a copy, not the original.

        with Html_Use_Case__3__Source_Tracking() as _:
            _.wrapper_mapping = {'wrapper_1': {'parent': 'p1', 'child': 'c1'}}

            result = _.get_all_wrapper_mappings()
            result['new_key'] = {'new': 'value'}                                # Modify the copy

            assert 'new_key' not in _.wrapper_mapping                           # Original unchanged