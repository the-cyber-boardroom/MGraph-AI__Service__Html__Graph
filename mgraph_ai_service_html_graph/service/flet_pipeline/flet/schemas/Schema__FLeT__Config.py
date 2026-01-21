# ═══════════════════════════════════════════════════════════════════════════════
# Schema__FLeT__Config - Configuration for FLeT steps
# ═══════════════════════════════════════════════════════════════════════════════


from osbot_utils.type_safe.Type_Safe                                                               import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                       import Safe_Str__Text
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.schemas.safe_str.Safe_Str__FLeT__Name import Safe_Str__FLeT__Name


class Schema__FLeT__Config(Type_Safe):                                                    # FLeT configuration
    name        : Safe_Str__FLeT__Name                                                   # FLeT identifier
    description : Safe_Str__Text                                                         # Human-readable description
