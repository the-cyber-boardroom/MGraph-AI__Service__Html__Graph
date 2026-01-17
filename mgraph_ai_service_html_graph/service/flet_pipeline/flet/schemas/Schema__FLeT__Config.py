# ═══════════════════════════════════════════════════════════════════════════════
# Schema__FLeT__Config - Configuration schema for FLeT steps
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe import Type_Safe
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.schemas.safe_str.Safe_Str__FLeT__Name import Safe_Str__FLeT__Name


class Schema__FLeT__Config(Type_Safe):                                               # FLeT step configuration
    name          : Safe_Str__FLeT__Name = ''                                        # Step identifier
    description   : str                  = ''                                        # Human-readable description
    schema__input : type                 = None                                      # Input schema type
    schema__output: type                 = None                                      # Output schema type
