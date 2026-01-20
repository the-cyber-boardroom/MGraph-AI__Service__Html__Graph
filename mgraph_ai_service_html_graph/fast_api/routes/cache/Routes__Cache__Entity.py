# ═══════════════════════════════════════════════════════════════════════════════
# Routes__Cache__Entity - REST API for cache entity operations
# Provides endpoints for entity CRUD: create, lookup, get, exists, delete
#
# Path pattern: /cache/{namespace}/entity/...
# ═══════════════════════════════════════════════════════════════════════════════

from fastapi                                                                                    import HTTPException
from mgraph_ai_service_cache_client.schemas.cache.file.Schema__Cache__File__Metadata            import Schema__Cache__File__Metadata
from mgraph_ai_service_cache_client.schemas.cache.file.Schema__Cache__File__Refs                import Schema__Cache__File__Refs
from mgraph_ai_service_cache_client.schemas.cache.safe_str.Safe_Str__Cache__Namespace           import Safe_Str__Cache__Namespace
from osbot_fast_api.api.decorators.route_path                                                   import route_path
from osbot_fast_api.api.routes.Fast_API__Routes                                                 import Fast_API__Routes
from mgraph_ai_service_cache_client.schemas.consts.consts__Cache_Client                         import ENV_VAR__URL__TARGET_SERVER__CACHE_SERVICE
from mgraph_ai_service_html_graph.schemas.cache.Schema__Route__Cache_Status__Response           import Schema__Route__Cache_Status__Response
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                              import Cache_Id
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Create__Request          import Schema__Entity__Create__Request
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Create__Response         import Schema__Entity__Create__Response
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Delete__Response         import Schema__Entity__Delete__Response
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Exists__Response         import Schema__Entity__Exists__Response
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Lookup__Request          import Schema__Entity__Lookup__Request
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Lookup__Response         import Schema__Entity__Lookup__Response
from mgraph_ai_service_html_graph.service.cache.Cache__Entity__Service                          import Cache__Entity__Service
from osbot_utils.utils.Env import get_env

TAG__ROUTES_CACHE_ENTITY = 'cache-entity'

ROUTES_PATHS__CACHE_ENTITY = [f'/{TAG__ROUTES_CACHE_ENTITY}' + '/{namespace}/entity/create'             ,
                              f'/{TAG__ROUTES_CACHE_ENTITY}' + '/{namespace}/entity/lookup'             ,
                              f'/{TAG__ROUTES_CACHE_ENTITY}' + '/{namespace}/entity/{cache_id}'         ,
                              f'/{TAG__ROUTES_CACHE_ENTITY}' + '/{namespace}/entity/{cache_id}/metadata',
                              f'/{TAG__ROUTES_CACHE_ENTITY}' + '/{namespace}/entity/{cache_id}/refs'    ,
                              f'/{TAG__ROUTES_CACHE_ENTITY}' + '/{namespace}/entity/{cache_id}/exists'  ]


class Routes__Cache__Entity(Fast_API__Routes):                                      # Cache entity routes
    tag     : str                    = TAG__ROUTES_CACHE_ENTITY                     # Route tag
    service : Cache__Entity__Service                                                # Entity service

    # ═══════════════════════════════════════════════════════════════════════════════
    # Create Operation
    # ═══════════════════════════════════════════════════════════════════════════════

    def cache__status(self) -> Schema__Route__Cache_Status__Response:
        target_server = get_env(ENV_VAR__URL__TARGET_SERVER__CACHE_SERVICE)
        cache_enabled = target_server is not None
        if cache_enabled:
            health_check = self.service.cache_client.health_check()
        else:
            health_check = False

        cache_status  = Schema__Route__Cache_Status__Response(cache_enabled = cache_enabled ,
                                                              health_check  = health_check  ,
                                                              target_server = target_server )
        return cache_status

    @route_path('/{namespace}/entity/create')
    def entity__create(self                                            ,            # Create or get existing entity
                       namespace : Safe_Str__Cache__Namespace          ,            # Cache namespace
                       request   : Schema__Entity__Create__Request                  # Create request
                  ) -> Schema__Entity__Create__Response:                            # POST /{namespace}/entity/create
        try:
            return self.service.create(namespace = namespace ,
                                       request   = request   )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ═══════════════════════════════════════════════════════════════════════════════
    # Lookup Operation
    # ═══════════════════════════════════════════════════════════════════════════════

    @route_path('/{namespace}/entity/lookup')
    def entity__lookup(self                                            ,            # Lookup entity by key or hash
                       namespace : Safe_Str__Cache__Namespace          ,            # Cache namespace
                       request   : Schema__Entity__Lookup__Request                  # Lookup request
                  ) -> Schema__Entity__Lookup__Response:                            # POST /{namespace}/entity/lookup
        try:
            return self.service.lookup(namespace = namespace ,
                                       request   = request   )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ═══════════════════════════════════════════════════════════════════════════════
    # Get Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    @route_path('/{namespace}/entity/{cache_id}')
    def entity__get(self                                      ,                     # Get full entry data
                    namespace : Safe_Str__Cache__Namespace    ,                     # Cache namespace
                    cache_id  : Cache_Id                                            # Entity cache ID
               ) -> dict:                                                           # GET /{namespace}/entity/{cache_id}
        try:
            result = self.service.get(namespace = namespace ,
                                      cache_id  = cache_id  )
            if result is None:
                raise HTTPException(status_code = 404                              ,
                                    detail      = f"Entity not found: {cache_id}" )
            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @route_path('/{namespace}/entity/{cache_id}/metadata')
    def entity__metadata(self                                      ,                # Get entry metadata
                         namespace : Safe_Str__Cache__Namespace    ,                # Cache namespace
                         cache_id  : Cache_Id                                       # Entity cache ID
                    ) -> Schema__Cache__File__Metadata:                             # GET /{namespace}/entity/{cache_id}/metadata
        try:
            result = self.service.get_metadata(namespace = namespace ,
                                               cache_id  = cache_id  )
            if result is None:
                raise HTTPException(status_code = 404                              ,
                                    detail      = f"Entity not found: {cache_id}" )
            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @route_path('/{namespace}/entity/{cache_id}/refs')
    def entity__refs(self                                      ,                    # Get entry refs
                     namespace : Safe_Str__Cache__Namespace    ,                    # Cache namespace
                     cache_id  : Cache_Id                                           # Entity cache ID
                ) -> Schema__Cache__File__Refs:                                     # GET /{namespace}/entity/{cache_id}/refs
        try:
            result = self.service.get_refs(namespace = namespace ,
                                           cache_id  = cache_id  )
            if result is None:
                raise HTTPException(status_code = 404                              ,
                                    detail      = f"Entity not found: {cache_id}" )
            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ═══════════════════════════════════════════════════════════════════════════════
    # Exists Operation
    # ═══════════════════════════════════════════════════════════════════════════════

    @route_path('/{namespace}/entity/{cache_id}/exists')
    def entity__exists(self                                      ,                  # Check if entity exists
                       namespace : Safe_Str__Cache__Namespace    ,                  # Cache namespace
                       cache_id  : Cache_Id                                         # Entity cache ID
                  ) -> Schema__Entity__Exists__Response:                            # GET /{namespace}/entity/{cache_id}/exists
        try:
            return self.service.exists(namespace = namespace ,
                                       cache_id  = cache_id  )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ═══════════════════════════════════════════════════════════════════════════════
    # Delete Operation
    # ═══════════════════════════════════════════════════════════════════════════════

    @route_path('/{namespace}/entity/{cache_id}')
    def entity__delete(self                                      ,                  # Delete cache entity
                       namespace : Safe_Str__Cache__Namespace    ,                  # Cache namespace
                       cache_id  : Cache_Id                                         # Entity cache ID
                  ) -> Schema__Entity__Delete__Response:                            # DELETE /{namespace}/entity/{cache_id}
        try:
            return self.service.delete(namespace = namespace ,
                                       cache_id  = cache_id  )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ═══════════════════════════════════════════════════════════════════════════════
    # Route Setup
    # ═══════════════════════════════════════════════════════════════════════════════

    def setup_routes(self):                                                         # Configure all routes
        self.add_route_get   (self.cache__status   )
        self.add_route_post  (self.entity__create  )
        self.add_route_post  (self.entity__lookup  )
        self.add_route_get   (self.entity__get     )
        self.add_route_get   (self.entity__metadata)
        self.add_route_get   (self.entity__refs    )
        self.add_route_get   (self.entity__exists  )
        self.add_route_delete(self.entity__delete  )

        return self