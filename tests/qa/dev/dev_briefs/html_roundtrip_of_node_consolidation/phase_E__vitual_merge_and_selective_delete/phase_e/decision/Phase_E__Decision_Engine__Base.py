# ═══════════════════════════════════════════════════════════════════════════════
# Phase_E__Decision_Engine__Base - Abstract base for keep/discard decisions
# Part of Phase E: Virtual Merge and Selective Delete
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                     import Dict, List
from abc                                                                        import abstractmethod
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id import Node_Id
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                  import type_safe
from phase_e.schemas.Schema__Phase_E__Decision_Result import Schema__Phase_E__Decision_Result
from phase_e.schemas.Schema__Phase_E__Merged_Text_Info import Schema__Phase_E__Merged_Text_Info


class Phase_E__Decision_Engine__Base(Type_Safe):                                # Abstract base for content decisions

    # ═══════════════════════════════════════════════════════════════════════════
    # Abstract Methods (Must Override)
    # ═══════════════════════════════════════════════════════════════════════════

    @abstractmethod
    def should_keep(self                     ,                                  # Simple keep/discard decision
                    merged_text : str        ,                                  # The merged text content
                    parent_id   : Node_Id        ) -> bool:                         # True to keep, False to discard
        raise NotImplementedError

    @abstractmethod
    def classify(self                     ,                                     # Detailed classification with score
                 merged_text : str        ,                                     # The merged text content
                 parent_id   : Node_Id        ) -> Schema__Phase_E__Decision_Result:                  # Decision with keep, score, reason
        raise NotImplementedError

    # ═══════════════════════════════════════════════════════════════════════════
    # Batch Classification
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def classify_all(self                                  ,                    # Classify all merged texts
                     merged_texts: Dict[Node_Id, Schema__Phase_E__Merged_Text_Info]       ) -> Dict[Node_Id, Schema__Phase_E__Decision_Result]:
        decisions = {}

        for parent_id, info in merged_texts.items():
            merged_text          = info.merged_text
            decisions[parent_id] = self.classify(merged_text, parent_id)

        return decisions

    # ═══════════════════════════════════════════════════════════════════════════
    # Helper: Filter by Decision
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def get_parents_to_delete(self,  # Get parent_ids that should be deleted
                              decisions: Dict[Node_Id, Schema__Phase_E__Decision_Result]) -> List[Node_Id]:
        return [parent_id
                for parent_id, result in decisions.items()
                if result.keep is False]

    @type_safe
    def get_parents_to_keep(self,  # Get parent_ids that should be kept
                            decisions: Dict[Node_Id, Schema__Phase_E__Decision_Result]) -> List[Node_Id]:
        return [parent_id
                for parent_id, result in decisions.items()
                if result.keep is True]