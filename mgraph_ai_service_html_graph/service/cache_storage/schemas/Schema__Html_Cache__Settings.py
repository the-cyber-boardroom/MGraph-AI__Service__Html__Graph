# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Html_Cache__Settings - Cache settings for API requests
# Kept separate from main request to avoid mixing concerns
# ═══════════════════════════════════════════════════════════════════════════════
from osbot_utils.type_safe.Type_Safe                                                        import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                          import Cache_Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id             import Safe_Str__Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Namespace      import Safe_Str__Namespace
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__List                       import Type_Safe__List
from mgraph_ai_service_html_graph.service.cache_storage.safe_str.Safe_Str__Data_File_Id     import Safe_Str__Data_File_Id
from mgraph_ai_service_cache_client.schemas.cache.safe_str.Safe_Str__Cache__File__Cache_Key        import Safe_Str__Cache__File__Cache_Key
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.safe_str.Safe_Str__LETS__Name  import Safe_Str__LETS__Name



# ═══════════════════════════════════════════════════════════════════════════════
# Typed Collection for LETS Names
# ═══════════════════════════════════════════════════════════════════════════════

class List__LETS__Names(Type_Safe__List):                                        # List of LETS names
    expected_type = Safe_Str__LETS__Name


# ═══════════════════════════════════════════════════════════════════════════════
# Cache Settings Schema
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__Html_Cache__Settings(Type_Safe):                                   # API cache settings
    enabled      : bool                      = False                             # Enable caching
    namespace    : Safe_Str__Namespace       = 'html-graph'                      # Cache namespace
    cache_key    : Safe_Str__Cache__File__Cache_Key       = None                              # Semantic path
    cache_id     : Cache_Id                  = None                              # Direct cache_id (optional)
    file_id      : Safe_Str__Data_File_Id    = 'html-entry'                      # Root document name
    profile_id   : Safe_Str__Id              = 'default'                         # LETS profile to use
    force_layers : List__LETS__Names         = None                              # Layers to force-rebuild
