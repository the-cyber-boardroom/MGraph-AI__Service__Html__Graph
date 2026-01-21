# ═══════════════════════════════════════════════════════════════════════════════
# Typed Collection for LETS Status
# ═══════════════════════════════════════════════════════════════════════════════
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.Schema__LETS__Status           import Schema__LETS__Status
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.safe_str.Safe_Str__LETS__Name  import Safe_Str__LETS__Name
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__Dict                               import Type_Safe__Dict


class Dict__LETS__Status__By_Name(Type_Safe__Dict):                              # Status dict by LETS name
    expected_key_type   = Safe_Str__LETS__Name
    expected_value_type = Schema__LETS__Status
