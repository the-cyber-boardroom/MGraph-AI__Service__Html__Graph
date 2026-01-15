# ═══════════════════════════════════════════════════════════════════════════════
# Schema__LETS__Config - Configuration for a LETS transformation
# Defines the transformation's identity and schema expectations
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                      import Type
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text     import Safe_Str__Text
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.safe_str.Safe_Str__LETS__Name             import Safe_Str__LETS__Name
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.Schema__LETS__Input               import Schema__LETS__Input
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.Schema__LETS__Output              import Schema__LETS__Output


class Schema__LETS__Config(Type_Safe):                                           # LETS transformation config
    name           : Safe_Str__LETS__Name                                        # Unique transformation name
    description    : Safe_Str__Text                                              # Human readable description
    schema__input  : Type[Schema__LETS__Input ]  = None                          # Expected input schema
    schema__output : Type[Schema__LETS__Output]  = None                          # Expected output schema
