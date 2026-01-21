# ═══════════════════════════════════════════════════════════════════════════════
# Cache__Namespace - Helper class for namespace-scoped cache operations
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                                         import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                           import Cache_Id
from mgraph_ai_service_cache_client.client.client_entities.Cache__Entity                     import Cache__Entity
from mgraph_ai_service_cache_client.client.client_entities.Cache__Entity__Data_File          import Cache__Entity__Data_File
from mgraph_ai_service_cache_client.schemas.cache.safe_str.Safe_Str__Cache__File__Cache_Hash import Safe_Str__Cache__File__Cache_Hash
from mgraph_ai_service_cache_client.schemas.cache.safe_str.Safe_Str__Cache__File__Cache_Key  import Safe_Str__Cache__File__Cache_Key
from mgraph_ai_service_cache_client.schemas.cache.safe_str.Safe_Str__Cache__Namespace        import Safe_Str__Cache__Namespace
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Client                   import Html_Cache__Client

# todo: refactor the non-entity methods and logic to an Cache_Namespace class
class Html_Cache__Namespace(Type_Safe):                                                  # Namespace-scoped cache helper
    html_cache_client : Html_Cache__Client                                          # Cache client for storage
    namespace         : Safe_Str__Cache__Namespace                                  # Target namespace

    # ═══════════════════════════════════════════════════════════════════════════════
    # Entity Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    def entity(self                  ,                                              # Get Cache__Entity for cache_id
               cache_id : Cache_Id                                                  # Entity cache ID
          ) -> Cache__Entity:
        return Cache__Entity(cache_client = self.html_cache_client.cache_client ,
                             cache_id     = cache_id                            ,
                             namespace    = self.namespace                      )

    def entity__create(self                        ,                                # Create new entity, return object
                       cache_key : str             ,                                # Cache key for entity
                       file_id   : str = 'root'                                     # Root file ID
                  ) -> Cache__Entity:
        result = self.html_cache_client.entry__store(namespace = self.namespace ,
                                                     cache_key = cache_key      ,
                                                     file_id   = file_id        )
        if result:
            return self.entity(cache_id=result.cache_id)

        return None

    def entity__via__cache_key(self                  ,                                      # Lookup entity by cache_key
                       cache_key : Safe_Str__Cache__File__Cache_Key                 # Cache key to lookup
                  ) -> Cache__Entity:
        cache_id = self.html_cache_client.cache_id__from_key(namespace = self.namespace ,
                                                            cache_key = cache_key       )
        if cache_id:
            return self.entity(cache_id=cache_id)

        return None

    def entity__via__cache_hash(self                   ,                             # Lookup entity by cache_hash
                               cache_hash : Safe_Str__Cache__File__Cache_Hash       # Cache hash to lookup
                          ) -> Cache__Entity:
        cache_id = self.html_cache_client.cache_id__from_hash(namespace  = self.namespace ,
                                                              cache_hash = cache_hash     )
        if cache_id:
            return self.entity(cache_id=cache_id)

        return None

    def entity__get_or_create(self                        ,                         # Get existing or create new
                              cache_key : str             ,                         # Cache key for entity
                              file_id   : str = 'root'                              # Root file ID
                         ) -> Cache__Entity:
        entity = self.entity__via__cache_key(cache_key=cache_key)
        if entity:
            return entity

        return self.entity__create(cache_key = cache_key ,
                                   file_id   = file_id   )

    def entity__exists(self                  ,                                      # Check if entity exists
                       cache_id : Cache_Id                                          # Entity cache ID
                  ) -> bool:
        return self.html_cache_client.entry__exists(namespace = self.namespace ,
                                                    cache_id  = cache_id       )

    def entity__delete(self                  ,                                      # Delete entity from namespace
                       cache_id : Cache_Id                                          # Entity cache ID
                  ) -> bool:
        return self.html_cache_client.entry__delete(namespace = self.namespace ,
                                                    cache_id  = cache_id       )

    # ═══════════════════════════════════════════════════════════════════════════════
    # Data File Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    def data_file(self                       ,                                      # Get data file object
                  cache_id     : Cache_Id    ,                                      # Entity cache ID
                  data_key     : str         ,                                      # Data key path
                  data_file_id : str                                                # File identifier
             ) -> Cache__Entity__Data_File:
        return self.entity(cache_id=cache_id).data_file(data_key     = data_key     ,
                                                        data_file_id = data_file_id )

    # ═══════════════════════════════════════════════════════════════════════════════
    # Bulk/List Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    def entities__list(self                            ,                            # List data files for entity
                       cache_id  : Cache_Id            ,                            # Entity cache ID
                       data_key  : str  = None         ,                            # Optional data key filter
                       recursive : bool = True                                      # Include subdirectories
                  ):
        return self.html_cache_client.data__list(namespace = self.namespace ,
                                                 cache_id  = cache_id       ,
                                                 data_key  = data_key       ,
                                                 recursive = recursive      )