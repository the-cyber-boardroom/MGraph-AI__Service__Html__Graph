# ═══════════════════════════════════════════════════════════════════════════════
# Cache__Entity__Service - Service layer for cache entity operations
# Provides business logic for entity CRUD operations
# ═══════════════════════════════════════════════════════════════════════════════
from osbot_utils.type_safe.Type_Safe                                                            import Type_Safe
from mgraph_ai_service_cache_client.schemas.cache.file.Schema__Cache__File__Refs                import Schema__Cache__File__Refs
from mgraph_ai_service_cache_client.schemas.cache.file.Schema__Cache__File__Metadata            import Schema__Cache__File__Metadata
from mgraph_ai_service_cache_client.schemas.cache.safe_str.Safe_Str__Cache__Namespace           import Safe_Str__Cache__Namespace
from mgraph_ai_service_cache_client.client.client_entities.Cache__Entity                        import Cache__Entity
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Create__Request          import Schema__Entity__Create__Request
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Create__Response         import Schema__Entity__Create__Response
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Delete__Response         import Schema__Entity__Delete__Response
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Exists__Response         import Schema__Entity__Exists__Response
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Info                     import Schema__Entity__Info
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__List__Response           import Schema__Entity__List__Response
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Lookup__Request          import Schema__Entity__Lookup__Request
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Lookup__Response         import Schema__Entity__Lookup__Response
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Client                      import Html_Cache__Client
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                              import Cache_Id
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                  import type_safe


class Cache__Entity__Service(Type_Safe):                                            # Service for entity operations
    html_cache_client : Html_Cache__Client                                               # Cache client for storage

    # ═══════════════════════════════════════════════════════════════════════════════
    # Create / Lookup Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def create(self                                            ,                    # Create or get existing entity
               namespace : Safe_Str__Cache__Namespace          ,                    # Cache namespace
               request   : Schema__Entity__Create__Request                          # Create request with cache_key
          ) -> Schema__Entity__Create__Response:
        result = self.html_cache_client.entry__store(namespace = namespace,
                                                     cache_key = request.cache_key,
                                                     file_id   = request.file_id)
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
            cache_id = self.html_cache_client.cache_id__from_key(namespace = namespace,
                                                                 cache_key = request.cache_key)
        elif request.cache_hash:
            cache_id = self.html_cache_client.cache_id__from_hash(namespace  = namespace,
                                                                  cache_hash = request.cache_hash)
        else:
            return Schema__Entity__Lookup__Response(success=False)

        if cache_id:
            return Schema__Entity__Lookup__Response(success  = True     ,
                                                    cache_id = cache_id ,
                                                    found    = True     )

        return Schema__Entity__Lookup__Response(success = True ,
                                                found   = False)




    @type_safe
    def list_entities(self,
                      namespace         : Safe_Str__Cache__Namespace ,
                      include_data_files: bool                       = False
                 ) -> Schema__Entity__List__Response:

        cache_ids = self.html_cache_client.cache_client.namespace().cache_ids(namespace=namespace)

        entities = []
        for cache_id in cache_ids:
            entity = Cache__Entity(cache_client = self.html_cache_client.cache_client,
                                   cache_id     = cache_id,
                                   namespace    = namespace)

            entry = entity.entry__with_metadata()

            if entry and entry.metadata:
                meta = entry.metadata
                entity_info = Schema__Entity__Info(cache_id         = meta.cache_id        ,
                                                   cache_key        = meta.cache_key       ,
                                                   cache_hash       = meta.cache_hash      ,
                                                   file_id          = meta.file_id         ,
                                                   namespace        = meta.namespace       ,
                                                   strategy         = meta.strategy        ,
                                                   stored_at        = meta.stored_at       ,
                                                   file_type        = meta.file_type       ,
                                                   content_encoding = meta.content_encoding,
                                                   content_size     = meta.content_size    )

                if include_data_files:
                    data_list = entity.data__files(recursive=True)
                    if data_list and data_list.files:
                        entity_info.data_files = [file.json() for file in data_list.files]

                entities.append(entity_info)

        return Schema__Entity__List__Response(namespace = namespace     ,
                                              count     = len(entities) ,
                                              entities  = entities      )
    # ═══════════════════════════════════════════════════════════════════════════════
    # Get Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def get(self                                      ,                             # Get full entry data
            namespace : Safe_Str__Cache__Namespace    ,                             # Cache namespace
            cache_id  : Cache_Id                                                    # Entity cache ID
       ) -> dict:
        return self.html_cache_client.entry__retrieve(namespace = namespace,
                                                      cache_id  = cache_id)

    @type_safe
    def get_metadata(self                                      ,                    # Get entry metadata
                     namespace : Safe_Str__Cache__Namespace    ,                    # Cache namespace
                     cache_id  : Cache_Id                                           # Entity cache ID
                ) -> Schema__Cache__File__Metadata:
        return self.html_cache_client.cache__entry__metadata(namespace = namespace,
                                                             cache_id  = cache_id)

    @type_safe
    def get_refs(self                                      ,                        # Get entry refs
                 namespace : Safe_Str__Cache__Namespace    ,                        # Cache namespace
                 cache_id  : Cache_Id                                               # Entity cache ID
            ) -> Schema__Cache__File__Refs:
        return self.html_cache_client.cache__entry__refs(namespace = namespace,
                                                         cache_id  = cache_id)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Exists / Delete Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def exists(self                                      ,                          # Check if entity exists
               namespace : Safe_Str__Cache__Namespace    ,                          # Cache namespace
               cache_id  : Cache_Id                                                 # Entity cache ID
          ) -> Schema__Entity__Exists__Response:
        result = self.html_cache_client.entry__exists(namespace = namespace,
                                                      cache_id  = cache_id)

        return Schema__Entity__Exists__Response(exists=result)

    @type_safe
    def delete(self                                      ,                          # Delete cache entity
               namespace : Safe_Str__Cache__Namespace    ,                          # Cache namespace
               cache_id  : Cache_Id                                                 # Entity cache ID
          ) -> Schema__Entity__Delete__Response:
        result = self.html_cache_client.entry__delete(namespace = namespace,
                                                      cache_id  = cache_id)

        return Schema__Entity__Delete__Response(success = True   ,
                                                deleted = result )