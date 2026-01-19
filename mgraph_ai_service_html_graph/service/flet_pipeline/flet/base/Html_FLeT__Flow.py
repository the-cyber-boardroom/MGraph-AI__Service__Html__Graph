# ═══════════════════════════════════════════════════════════════════════════════
# Html_FLeT__Flow - Extended Flow with FLeT-specific typed dependencies
# Provides type-safe dependency injection for FLeT actions via task_dependencies()
# ═══════════════════════════════════════════════════════════════════════════════

from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Client                import Html_Cache__Client
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.schemas.Schema__FLeT__Config import Schema__FLeT__Config
from osbot_utils.helpers.flows.Flow                                                       import Flow
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                        import Cache_Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Namespace    import Safe_Str__Namespace

# todo, if the cache_id and namespace where in Schema__FLeT__Config , we wouldn't need to also need to set it here

class Html_FLeT__Flow(Flow):                                                              # Flow extended with FLeT typed attributes
    cache_client : Html_Cache__Client   = None                                            # Cache client for storage operations
    cache_id     : Cache_Id             = None                                            # Established cache_id (from orchestrator)
    namespace    : Safe_Str__Namespace  = None                                            # Namespace for cache operations
    config       : Schema__FLeT__Config = None                                            # FLeT configuration

    def task_dependencies(self) -> dict:                                                  # Provide dependencies for task injection
        return { 'cache_client': self.cache_client ,
                 'cache_id'    : self.cache_id     ,
                 'namespace'   : self.namespace    ,
                 'config'      : self.config       }
