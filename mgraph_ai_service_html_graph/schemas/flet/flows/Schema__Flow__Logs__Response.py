# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Flow__Logs__Response - Response with flow execution logs
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                        import List
from osbot_utils.type_safe.Type_Safe                                                               import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                               import Safe_UInt
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                       import Safe_Str__Text
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.schemas.safe_str.Safe_Str__FLeT__Name import Safe_Str__FLeT__Name



class Schema__Flow__Logs__Response(Type_Safe):                                    # Response with flow logs
    success   : bool                                                              # Whether retrieval succeeded
    flet_name : Safe_Str__FLeT__Name                                              # FLeT name
    logs      : List[Safe_Str__Text]                                              # Log entries
    count     : Safe_UInt                                                         # Number of log entries
