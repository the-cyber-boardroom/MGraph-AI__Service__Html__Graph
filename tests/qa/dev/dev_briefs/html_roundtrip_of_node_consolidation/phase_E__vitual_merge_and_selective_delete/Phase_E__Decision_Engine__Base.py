# ═══════════════════════════════════════════════════════════════════════════════
# Phase_E__Decision_Engine__Base - Abstract base for keep/discard decisions
# Part of Phase E: Virtual Merge and Selective Delete
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                     import Dict, List
from abc                                                                        import abstractmethod
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                  import type_safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                             import Safe_Str__Text
from osbot_utils.type_safe.primitives.core.Safe_Float                           import Safe_Float


class DecisionResult(Type_Safe):                                                # Result of a keep/discard decision
    keep   : bool                                                               # True to keep, False to discard
    score  : Safe_Float                                                         # Confidence/relevance score (0.0 to 1.0)
    reason : Safe_Str__Text                                                           # Human-readable reason for decision


class Phase_E__Decision_Engine__Base(Type_Safe):                                # Abstract base for content decisions

    # ═══════════════════════════════════════════════════════════════════════════
    # Abstract Methods (Must Override)
    # ═══════════════════════════════════════════════════════════════════════════

    @abstractmethod
    def should_keep(self                     ,                                  # Simple keep/discard decision
                    merged_text : str        ,                                  # The merged text content
                    parent_id   : str        ) -> bool:                         # True to keep, False to discard
        raise NotImplementedError

    @abstractmethod
    def classify(self                     ,                                     # Detailed classification with score
                 merged_text : str        ,                                     # The merged text content
                 parent_id   : str        ) -> DecisionResult:                  # Decision with keep, score, reason
        raise NotImplementedError

    # ═══════════════════════════════════════════════════════════════════════════
    # Batch Classification
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def classify_all(self                                  ,                    # Classify all merged texts
                     merged_texts: Dict[str, object]       ) -> Dict[str, DecisionResult]:
        decisions = {}

        for parent_id, info in merged_texts.items():
            merged_text          = str(info.merged_text)
            decisions[parent_id] = self.classify(merged_text, parent_id)

        return decisions

    # ═══════════════════════════════════════════════════════════════════════════
    # Helper: Filter by Decision
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def get_parents_to_delete(self                                   ,          # Get parent_ids that should be deleted
                              decisions: Dict[str, DecisionResult]   ) -> List[str]:
        return [parent_id
                for parent_id, result in decisions.items()
                if result.keep is False]

    @type_safe
    def get_parents_to_keep(self                                   ,            # Get parent_ids that should be kept
                            decisions: Dict[str, DecisionResult]   ) -> List[str]:
        return [parent_id
                for parent_id, result in decisions.items()
                if result.keep is True]