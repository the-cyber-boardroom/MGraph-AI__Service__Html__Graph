# ═══════════════════════════════════════════════════════════════════════════════
# Cache__Entity__Service - Service layer for cache entity operations
# Provides business logic for entity CRUD operations
# ═══════════════════════════════════════════════════════════════════════════════
from osbot_utils.type_safe.Type_Safe                                                            import Type_Safe
from mgraph_ai_service_cache_client.schemas.cache.file.Schema__Cache__File__Refs                import Schema__Cache__File__Refs
from mgraph_ai_service_cache_client.schemas.cache.file.Schema__Cache__File__Metadata            import Schema__Cache__File__Metadata
from mgraph_ai_service_cache_client.schemas.cache.safe_str.Safe_Str__Cache__Namespace           import Safe_Str__Cache__Namespace
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Create__Request          import Schema__Entity__Create__Request
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Create__Response         import Schema__Entity__Create__Response
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Delete__Response         import Schema__Entity__Delete__Response
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Exists__Response         import Schema__Entity__Exists__Response
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__List__By__Path__Response import Schema__Entity__List__By__Path__Response
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Lookup__Request          import Schema__Entity__Lookup__Request
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Lookup__Response         import Schema__Entity__Lookup__Response
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Client                      import Html_Cache__Client
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path               import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                              import Cache_Id
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                  import type_safe


class Cache__Entity__Service(Type_Safe):                                            # Service for entity operations
    cache_client : Html_Cache__Client                                               # Cache client for storage

    # ═══════════════════════════════════════════════════════════════════════════════
    # Create / Lookup Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def create(self                                            ,                    # Create or get existing entity
               namespace : Safe_Str__Cache__Namespace          ,                    # Cache namespace
               request   : Schema__Entity__Create__Request                          # Create request with cache_key
          ) -> Schema__Entity__Create__Response:
        result = self.cache_client.entry__store(namespace = namespace         ,
                                                cache_key = request.cache_key ,
                                                file_id   = request.file_id   )
        #result.print_obj()
        if result:
            return Schema__Entity__Create__Response(success    = True             ,
                                                    cache_id   = result.cache_id  ,
                                                    cache_hash = result.cache_hash)

        return Schema__Entity__Create__Response(success=False)

    @type_safe
    def lookup(self                                            ,                    # Lookup entity by key or hash
               namespace : Safe_Str__Cache__Namespace          ,                    # Cache namespace
               request   : Schema__Entity__Lookup__Request                          # Lookup request
          ) -> Schema__Entity__Lookup__Response:
        cache_id = None

        if request.cache_key:
            cache_id = self.cache_client.cache_id__from_key(namespace = namespace         ,
                                                            cache_key = request.cache_key )
        elif request.cache_hash:
            cache_id = self.cache_client.cache_id__from_hash(namespace  = namespace          ,
                                                            cache_hash = request.cache_hash )
        else:
            return Schema__Entity__Lookup__Response(success=False)

        if cache_id:
            return Schema__Entity__Lookup__Response(success  = True     ,
                                                    cache_id = cache_id ,
                                                    found    = True     )

        return Schema__Entity__Lookup__Response(success = True ,
                                                found   = False)







    def list_by_path(self, namespace  : Safe_Str__Cache__Namespace,
                           path_prefix: Safe_Str__File__Path
                      ) -> Schema__Entity__List__By__Path__Response:
        admin_storage = self.cache_client.cache_client.admin_storage()
        search_path   = f'{namespace}/data/key-based/{path_prefix}' if path_prefix else f'{namespace}/data/key-based'

        folders = admin_storage.folders(path             = search_path,
                                        recursive        = False      ,
                                        return_full_path = False      )

        return Schema__Entity__List__By__Path__Response(success     = True       ,                      # todo: review the use of success here
                                                        namespace   = namespace  ,
                                                        path_prefix = path_prefix,
                                                        count       = len(folders),
                                                        entities    = folders    )
    # ═══════════════════════════════════════════════════════════════════════════════
    # Get Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def get(self                                      ,                             # Get full entry data
            namespace : Safe_Str__Cache__Namespace    ,                             # Cache namespace
            cache_id  : Cache_Id                                                    # Entity cache ID
       ) -> dict:
        return self.cache_client.entry__retrieve(namespace = namespace ,
                                                 cache_id  = cache_id  )

    @type_safe
    def get_metadata(self                                      ,                    # Get entry metadata
                     namespace : Safe_Str__Cache__Namespace    ,                    # Cache namespace
                     cache_id  : Cache_Id                                           # Entity cache ID
                ) -> Schema__Cache__File__Metadata:
        return self.cache_client.cache__entry__metadata(namespace = namespace ,
                                                        cache_id  = cache_id  )

    @type_safe
    def get_refs(self                                      ,                        # Get entry refs
                 namespace : Safe_Str__Cache__Namespace    ,                        # Cache namespace
                 cache_id  : Cache_Id                                               # Entity cache ID
            ) -> Schema__Cache__File__Refs:
        return self.cache_client.cache__entry__refs(namespace = namespace ,
                                                    cache_id  = cache_id  )

    # ═══════════════════════════════════════════════════════════════════════════════
    # Exists / Delete Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def exists(self                                      ,                          # Check if entity exists
               namespace : Safe_Str__Cache__Namespace    ,                          # Cache namespace
               cache_id  : Cache_Id                                                 # Entity cache ID
          ) -> Schema__Entity__Exists__Response:
        result = self.cache_client.entry__exists(namespace = namespace ,
                                                 cache_id  = cache_id  )

        return Schema__Entity__Exists__Response(exists=result)

    @type_safe
    def delete(self                                      ,                          # Delete cache entity
               namespace : Safe_Str__Cache__Namespace    ,                          # Cache namespace
               cache_id  : Cache_Id                                                 # Entity cache ID
          ) -> Schema__Entity__Delete__Response:
        result = self.cache_client.entry__delete(namespace = namespace ,
                                                 cache_id  = cache_id  )

        return Schema__Entity__Delete__Response(success = True   ,
                                                deleted = result )