# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Phase E - Decision Engine (Hash Based)
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                   import TestCase
from phase_e.decision.Phase_E__Decision_Engine__Hash_Based      import (Phase_E__Decision_Engine__Hash_Based)
from phase_e.core.Phase_E__Virtual_Merger                       import Schema__Phase_E__Merged_Text_Info
from phase_e.schemas.Schema__Phase_E__Decision_Result import Schema__Phase_E__Decision_Result


class test_Phase_E__Decision_Engine__Hash_Based(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = Phase_E__Decision_Engine__Hash_Based()

    def test__init__(self):                                                     # Test auto-initialization
        with self.engine as _:
            assert type(_).__name__  == 'Phase_E__Decision_Engine__Hash_Based'
            assert float(_.threshold) == 0.5

    def test_hash_deterministic(self):                                          # Same text produces same result
        with self.engine as _:
            result1 = _.classify("Hello World", "p001")
            result2 = _.classify("Hello World", "p001")

            assert float(result1.score) == float(result2.score)
            assert result1.keep         == result2.keep

    def test_hash_different_text_different_score(self):                         # Different text → different score
        with self.engine as _:
            result1 = _.classify("Hello", "p001")
            result2 = _.classify("Goodbye", "p001")

            assert float(result1.score) != float(result2.score)

    def test_threshold_boundary__keep_all(self):                                # Threshold=0.0 keeps everything

        with Phase_E__Decision_Engine__Hash_Based(threshold=0.0) as _:
            assert _.should_keep("any text", "p001") is True

    def test_threshold_boundary__delete_all(self):                              # Threshold=1.0 deletes everything
        with Phase_E__Decision_Engine__Hash_Based(threshold=1.0) as _:
            assert _.should_keep("any text", "p001") is False

    def test_classify_returns_decision_result(self):                            # Classify returns proper result
        with self.engine as _:
            result = _.classify("Test text", "p001")

            assert type(result)                 is Schema__Phase_E__Decision_Result
            assert type(result.keep)            is bool
            assert 0.0 <= float(result.score)   <= 1.0
            assert str(result.reason)           != ''

    def test_classify_all(self):                                                # Batch classification

        with self.engine as _:
            merged_texts = {'p001': Schema__Phase_E__Merged_Text_Info(merged_text='Hello World', source_node_ids=['n1']),
                           'p002': Schema__Phase_E__Merged_Text_Info(merged_text='Goodbye', source_node_ids=['n2'])}

            decisions = _.classify_all(merged_texts)

            assert len(decisions) == 2
            assert 'p001' in decisions
            assert 'p002' in decisions

    def test_empty_text_score_zero(self):                                       # Empty text gets score 0
        with self.engine as _:
            result = _.classify("", "p001")

            assert float(result.score) == 0.0
            assert result.keep         is False
