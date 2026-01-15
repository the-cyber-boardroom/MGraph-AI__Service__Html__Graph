# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Html_Cache__Root - Root document that manages cached HTML state
# This is the "index" that tracks all transformation states for a document
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                                        import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now            import Timestamp_Now
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id             import Safe_Str__Id
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url                    import Safe_Str__Url
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Hash          import Safe_Str__Hash
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__Dict                       import Type_Safe__Dict
from mgraph_ai_service_html_graph.service.cache_storage.safe_str.Safe_Str__Cache_Key        import Safe_Str__Cache_Key
from mgraph_ai_service_html_graph.service.cache_storage.enums.Enum__Source_Type             import Enum__Source_Type
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.safe_str.Safe_Str__LETS__Name  import Safe_Str__LETS__Name
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.Schema__LETS__Status   import Schema__LETS__Status


# ═══════════════════════════════════════════════════════════════════════════════
# Typed Collection for LETS Status
# ═══════════════════════════════════════════════════════════════════════════════

class Dict__LETS__Status__By_Name(Type_Safe__Dict):                              # Status dict by LETS name
    expected_key_type   = Safe_Str__LETS__Name
    expected_value_type = Schema__LETS__Status


# ═══════════════════════════════════════════════════════════════════════════════
# Root Document Schema
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__Html_Cache__Root(Type_Safe):                                       # Root document - state manager
    # Identity
    cache_key       : Safe_Str__Cache_Key                                        # Semantic path for lookup

    # Source information
    source_type     : Enum__Source_Type     = Enum__Source_Type.RAW_HTML         # How HTML was sourced
    source_url      : Safe_Str__Url         = None                               # Original URL if from URL
    source_hash     : Safe_Str__Hash        = None                               # Hash of source HTML

    # Profile
    profile_id      : Safe_Str__Id          = 'default'                          # Which LETS profile

    # Transformation state
    transformations : Dict__LETS__Status__By_Name                                # Status of each LETS

    # Timestamps
    created_at      : Timestamp_Now
    updated_at      : Timestamp_Now         = None
