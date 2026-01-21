# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Phase E - Pipeline (Integration)
# ═══════════════════════════════════════════════════════════════════════════════
from unittest                                                import TestCase
from phase_e.decision.Phase_E__Decision_Engine__Hash_Based   import Phase_E__Decision_Engine__Hash_Based
from phase_e.Phase_E__Pipeline                               import Phase_E__Pipeline, Schema__Phase_E__Process_Result
from osbot_utils.testing.Graph__Deterministic__Ids           import graph_deterministic_ids
from osbot_utils.testing.__                                  import __


class test_Phase_E__Pipeline(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pipeline = Phase_E__Pipeline()

    def test__init__(self):                                                     # Test auto-initialization
        with self.pipeline as _:
            assert type(_).__name__                     == 'Phase_E__Pipeline'
            assert type(_.decision_engine).__name__     == 'Phase_E__Decision_Engine__Hash_Based'

    def test_process__returns_string(self):                                     # Process returns string
        with self.pipeline as _:
            html   = "<div>Test</div>"
            result = _.process(html)

            assert type(result) is str
            assert result == '<!DOCTYPE html>\n<html></html>\n'

    def test_process_with_details__returns_all_steps(self):                     # Details has all fields
        with self.pipeline as _:
            html   = "<div>Test content here</div>"
            result = _.process_with_details(html)

            assert str(result.html)       != ''
            assert result.text_nodes      is not None
            assert result.merged_texts    is not None
            assert result.decisions       is not None
            assert result.parents_deleted is not None
            assert str(result.clean_html) != ''
            assert type(result)           is Schema__Phase_E__Process_Result
            assert result.obj()           == __(html='<div>Test content here</div>',
                                                text_nodes=__(),
                                                merged_texts=__(),
                                                decisions=__(),
                                                parents_deleted=[],
                                                deleted_count=0,
                                                clean_html='<!DOCTYPE html>\n<html></html>')

    def test_process_with_details__text_nodes_extracted(self):                  # Text nodes extracted
        with self.pipeline as _:
            html   = "<html><body><div>Hello World</div></body></html>"
            with graph_deterministic_ids():
                result = _.process_with_details(html)

            assert len(result.text_nodes) >= 1

            node_id = list(result.text_nodes.keys())[0]
            assert str(result.text_nodes[node_id].text)      != ''
            assert str(result.text_nodes[node_id].parent_id) != ''
            assert result.obj()                              == __(html='<html><body><div>Hello World</div></body></html>',
                                                                   text_nodes=__(f0000004=__(text='Hello World', parent_id='f0000003')),
                                                                   merged_texts=__(f0000003=__(merged_text='Hello World',
                                                                                               source_node_ids=['f0000004'])),
                                                                   decisions=__(f0000003=__(keep=False,
                                                                                            score=0.0721,
                                                                                            reason='hash_below_threshold')),
                                                                   parents_deleted=['f0000003'],
                                                                   deleted_count=1,
                                                                   clean_html='<!DOCTYPE html>\n<html>\n    <body></body>\n</html>')

    def test_process_with_details__merged_texts_computed(self):                 # Merged texts computed
        with self.pipeline as _:
            html   = "<html><body><div>Hello World</div></body></html>"
            with graph_deterministic_ids():
                result = _.process_with_details(html)

            assert len(result.merged_texts) >= 1

            parent_id = list(result.merged_texts.keys())[0]
            assert str(result.merged_texts[parent_id].merged_text)     != ''
            assert len(result.merged_texts[parent_id].source_node_ids) >= 1
            assert result.obj()                                        == __(html='<html><body><div>Hello World</div></body></html>',
                                                                             text_nodes=__(f0000004=__(text='Hello World', parent_id='f0000003')),
                                                                             merged_texts=__(f0000003=__(merged_text='Hello World',
                                                                                                         source_node_ids=['f0000004'])),
                                                                             decisions=__(f0000003=__(keep=False,
                                                                                                      score=0.0721,
                                                                                                      reason='hash_below_threshold')),
                                                                             parents_deleted=['f0000003'],
                                                                             deleted_count=1,
                                                                             clean_html='<!DOCTYPE html>\n<html>\n    <body></body>\n</html>')


    def test_process_with_details__decisions_made(self):                        # Decisions made
        with self.pipeline as _:
            html   = "<html><body><div>Hello World</div></body></html>"
            with graph_deterministic_ids():
                result = _.process_with_details(html)

            assert len(result.decisions) >= 1

            parent_id = list(result.decisions.keys())[0]
            assert type(result.decisions[parent_id].keep) is bool
            assert result.obj()                                        == __(html='<html><body><div>Hello World</div></body></html>',
                                                                             text_nodes=__(f0000004=__(text='Hello World', parent_id='f0000003')),
                                                                             merged_texts=__(f0000003=__(merged_text='Hello World',
                                                                                                         source_node_ids=['f0000004'])),
                                                                             decisions=__(f0000003=__(keep=False,
                                                                                                      score=0.0721,
                                                                                                      reason='hash_below_threshold')),
                                                                             parents_deleted=['f0000003'],
                                                                             deleted_count=1,
                                                                             clean_html='<!DOCTYPE html>\n<html>\n    <body></body>\n</html>')

    def test_custom_engine__keep_all(self):                                     # Custom engine: keep all

        keep_all_engine = Phase_E__Decision_Engine__Hash_Based(threshold=0.0)

        with Phase_E__Pipeline(decision_engine=keep_all_engine) as _:
            html   = "<html><body><div>Test</div></body></html>"
            with graph_deterministic_ids():
                result = _.process_with_details(html)

            assert len(result.parents_deleted) == 0
            assert result.obj()                == __(  html='<html><body><div>Test</div></body></html>',
                                                       text_nodes=__(f0000004=__(text='Test', parent_id='f0000003')),
                                                       merged_texts=__(f0000003=__(merged_text='Test',
                                                                                   source_node_ids=['f0000004'])),
                                                       decisions=__(f0000003=__(keep=True,
                                                                                score=0.1712,
                                                                                reason='hash_above_threshold')),
                                                       parents_deleted=[],
                                                       deleted_count=0,
                                                       clean_html='<!DOCTYPE html>\n'
                                                                  '<html>\n'
                                                                  '    <body>\n'
                                                                  '        <div>Test</div>\n'
                                                                  '    </body>\n'
                                                                  '</html>')

    def test_custom_engine__delete_all(self):                                   # Custom engine: delete all
        delete_all_engine = Phase_E__Decision_Engine__Hash_Based(threshold=1.0)

        with Phase_E__Pipeline(decision_engine=delete_all_engine) as _:
            html   = "<html><body><div><p>Test</p></div></body></html>"
            with graph_deterministic_ids():
                result = _.process_with_details(html)

            assert len(result.parents_deleted) >= 1
            assert result.obj()                == __(  html='<html><body><div><p>Test</p></div></body></html>',
                                                       text_nodes=__(f0000005=__(text='Test', parent_id='f0000004')),
                                                       merged_texts=__(f0000004=__(merged_text='Test',
                                                                                   source_node_ids=['f0000005'])),
                                                       decisions=__(f0000004=__(keep=False,
                                                                                score=0.1712,
                                                                                reason='hash_below_threshold')),
                                                       parents_deleted=['f0000004'],
                                                       deleted_count=1,
                                                       clean_html='<!DOCTYPE html>\n'
                                                                  '<html>\n'
                                                                  '    <body>\n'
                                                                  '        <div></div>\n'
                                                                  '    </body>\n'
                                                                  '</html>')