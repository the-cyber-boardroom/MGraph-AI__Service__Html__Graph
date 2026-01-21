# ═══════════════════════════════════════════════════════════════════════════════
# Schema__LETS__Profile - Defines a pipeline of LETS transformations
# Profiles enable composable, reusable transformation pipelines
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                       import Type, List
from osbot_utils.type_safe.Type_Safe                                              import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text      import Safe_Str__Text
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id   import Safe_Str__Id
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.base.Html_LETS__Base import Html_LETS__Base


class Schema__LETS__Profile(Type_Safe):                                          # LETS pipeline definition
    profile_id    : Safe_Str__Id                                                 # Unique identifier
    profile_name  : Safe_Str__Text                                               # Human readable name
    description   : Safe_Str__Text                                               # What this profile does
    lets_pipeline : List[Type[Html_LETS__Base]]                                  # Ordered LETS classes
