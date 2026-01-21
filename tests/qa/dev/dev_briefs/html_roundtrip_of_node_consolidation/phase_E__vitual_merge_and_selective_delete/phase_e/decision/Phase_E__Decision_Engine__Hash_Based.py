# ═══════════════════════════════════════════════════════════════════════════════
# Phase_E__Decision_Engine__Hash_Based - Deterministic hash-based decisions
# Part of Phase E: Virtual Merge and Selective Delete
#
# Uses MD5 hash of text to generate deterministic scores.
# Same text always produces same decision - useful for testing.
# Pattern based on Semantic_Text__Engine__Hash_Based
# ═══════════════════════════════════════════════════════════════════════════════

from hashlib                                                            import md5
from osbot_utils.type_safe.type_safe_core.decorators.type_safe          import type_safe
from osbot_utils.type_safe.primitives.core.Safe_Float                   import Safe_Float
from phase_e.decision.Phase_E__Decision_Engine__Base                    import Phase_E__Decision_Engine__Base
from phase_e.decision.Phase_E__Decision_Engine__Base                    import Schema__Phase_E__Decision_Result


class Phase_E__Decision_Engine__Hash_Based(Phase_E__Decision_Engine__Base):     # Hash-based decision engine

    threshold: Safe_Float = 0.5                                                 # Score >= threshold → keep

    # ═══════════════════════════════════════════════════════════════════════════
    # Decision Methods
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def should_keep(self                     ,                                  # Hash-based keep decision
                    merged_text : str        ,                                  # Text to evaluate
                    parent_id   : str        ) -> bool:                         # True if hash score >= threshold
        result = self.classify(merged_text, parent_id)
        return result.keep

    @type_safe
    def classify(self                     ,                                     # Generate classification from text hash
                 merged_text : str        ,                                     # Text to evaluate
                 parent_id   : str        ) -> Schema__Phase_E__Decision_Result:                  # Decision with keep, score, reason
        score = self.hash_score(merged_text)
        keep  = score >= float(self.threshold)

        return Schema__Phase_E__Decision_Result(keep   = keep,
                                                score  = score,
                                                reason = 'hash_above_threshold' if keep else 'hash_below_threshold')

    # ═══════════════════════════════════════════════════════════════════════════
    # Hash Score Calculation
    # ═══════════════════════════════════════════════════════════════════════════

    def hash_score(self, text: str) -> float:                                   # Generate deterministic score from hash
        if not text:
            return 0.0

        full_hash = md5(text.encode()).hexdigest()
        hash_int  = int(full_hash[:16], 16)
        score     = (hash_int % 10000) / 10000.0

        return score