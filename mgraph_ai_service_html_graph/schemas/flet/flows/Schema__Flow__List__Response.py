# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Flow__List__Response - Response listing FLeTs that have executed
# ═══════════════════════════════════════════════════════════════════════════════
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.schemas.safe_str.Safe_Str__FLeT__Name import Safe_Str__FLeT__Name
from osbot_utils.type_safe.Type_Safe                                                               import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                               import Safe_UInt
from typing                                                                                        import List


class Schema__Flow__List__Response(Type_Safe):                                    # Response listing FLeTs
    success : bool                                                                # Whether list succeeded
    flets   : List[Safe_Str__FLeT__Name]                                          # FLeT names that have executed
    count   : Safe_UInt                                                           # Number of FLeTs
