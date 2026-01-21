# ═══════════════════════════════════════════════════════════════════════════════
# Routes__Cache__Data - REST API for cache data file operations
# Provides endpoints for data file CRUD: list, get, store, update, exists, delete
#
# Path pattern: /cache/{namespace}/data/{cache_id}/...
# ═══════════════════════════════════════════════════════════════════════════════

from fastapi                                                                                import HTTPException
from osbot_fast_api.api.decorators.route_path                                               import route_path
from mgraph_ai_service_cache_client.schemas.cache.data.Schema__Cache__Data__List__Response  import Schema__Cache__Data__List__Response
from mgraph_ai_service_cache_client.schemas.cache.data.Schema__Cache__Data__Store__Response import Schema__Cache__Data__Store__Response
from mgraph_ai_service_html_graph.schemas.cache.data.Schema__Data__Delete__Response         import Schema__Data__Delete__Response
from mgraph_ai_service_html_graph.schemas.cache.data.Schema__Data__Exists__Response         import Schema__Data__Exists__Response
from mgraph_ai_service_html_graph.schemas.cache.data.Schema__Data__Paths__Response          import Schema__Data__Paths__Response
from mgraph_ai_service_html_graph.schemas.cache.data.Schema__Data__Store__Json__Request     import Schema__Data__Store__Json__Request
from mgraph_ai_service_html_graph.schemas.cache.data.Schema__Data__Store__String__Request   import Schema__Data__Store__String__Request
from mgraph_ai_service_html_graph.schemas.cache.data.Schema__Data__Update__Response         import Schema__Data__Update__Response
from mgraph_ai_service_html_graph.service.cache.Cache__Data__Service                        import Cache__Data__Service
from osbot_fast_api.api.routes.Fast_API__Routes                                             import Fast_API__Routes

TAG__ROUTES_CACHE_DATA = 'cache-data'

ROUTES_PATHS__CACHE_DATA = [f'/{TAG__ROUTES_CACHE_DATA}' + '/{namespace}/data/{cache_id}'                                                  ,
                            f'/{TAG__ROUTES_CACHE_DATA}' + '/{namespace}/data/{cache_id}/exists/{data_type}/{data_key:path}/{data_file_id}',
                            f'/{TAG__ROUTES_CACHE_DATA}' + '/{namespace}/data/{cache_id}/paths'                                            ,
                            f'/{TAG__ROUTES_CACHE_DATA}' + '/{namespace}/data/{cache_id}/string/{data_key:path}/{data_file_id}'            ,
                            f'/{TAG__ROUTES_CACHE_DATA}' + '/{namespace}/data/{cache_id}/json/{data_key:path}/{data_file_id}'              ,
                            f'/{TAG__ROUTES_CACHE_DATA}' + '/{namespace}/data/{cache_id}/store/string/{data_key:path}/{data_file_id}'      ,
                            f'/{TAG__ROUTES_CACHE_DATA}' + '/{namespace}/data/{cache_id}/store/json/{data_key:path}/{data_file_id}'        ,
                            f'/{TAG__ROUTES_CACHE_DATA}' + '/{namespace}/data/{cache_id}/{data_type}/{data_key:path}/{data_file_id}'       ]


class Routes__Cache__Data(Fast_API__Routes):                                        # Cache data file routes
    tag     : str                  = TAG__ROUTES_CACHE_DATA                         # Route tag
    service : Cache__Data__Service                                                  # Data service

    # ═══════════════════════════════════════════════════════════════════════════════
    # List Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    @route_path('/{namespace}/data/{cache_id}')
    def data__list(self                         ,                                   # List all data files for entity
                   namespace  : str             ,                                   # Cache namespace
                   cache_id   : str             ,                                   # Entity cache ID
                   recursive  : bool = True                                         # Include subdirectories
              ) -> Schema__Cache__Data__List__Response:                             # GET /{namespace}/data/{cache_id}
        try:
            return self.service.list_files(namespace = namespace ,
                                           cache_id  = cache_id  ,
                                           recursive = recursive )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @route_path('/{namespace}/data/{cache_id}/paths')
    def data__paths(self                         ,                                  # List data file paths
                    namespace  : str             ,                                  # Cache namespace
                    cache_id   : str             ,                                  # Entity cache ID
                    recursive  : bool = True                                        # Include subdirectories
               ) -> Schema__Data__Paths__Response:                                  # GET /{namespace}/data/{cache_id}/paths
        try:
            return self.service.list_paths(namespace = namespace ,
                                           cache_id  = cache_id  ,
                                           recursive = recursive )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ═══════════════════════════════════════════════════════════════════════════════
    # Get Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    @route_path('/{namespace}/data/{cache_id}/string/{data_key:path}/{data_file_id}')
    def data__get_string(self                   ,                                   # Get string content from file
                         namespace    : str     ,                                   # Cache namespace
                         cache_id     : str     ,                                   # Entity cache ID
                         data_key     : str     ,                                   # Data key path
                         data_file_id : str                                         # File identifier
                    ) -> str:                                                       # GET /{namespace}/data/{cache_id}/string/{data_key}/{data_file_id}
        try:
            result = self.service.get_string(namespace    = namespace    ,
                                             cache_id     = cache_id     ,
                                             data_key     = data_key     ,
                                             data_file_id = data_file_id )
            if result is None:
                raise HTTPException(status_code = 404                                        ,
                                    detail      = f"Data file not found: {data_key}/{data_file_id}")
            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @route_path('/{namespace}/data/{cache_id}/json/{data_key:path}/{data_file_id}')
    def data__get_json(self                   ,                                     # Get JSON content from file
                       namespace    : str     ,                                     # Cache namespace
                       cache_id     : str     ,                                     # Entity cache ID
                       data_key     : str     ,                                     # Data key path
                       data_file_id : str                                           # File identifier
                  ) -> dict:                                                        # GET /{namespace}/data/{cache_id}/json/{data_key}/{data_file_id}
        try:
            result = self.service.get_json(namespace    = namespace    ,
                                           cache_id     = cache_id     ,
                                           data_key     = data_key     ,
                                           data_file_id = data_file_id )
            if result is None:
                raise HTTPException(status_code = 404                                        ,
                                    detail      = f"Data file not found: {data_key}/{data_file_id}")
            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ═══════════════════════════════════════════════════════════════════════════════
    # Store Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    @route_path('/{namespace}/data/{cache_id}/store/string/{data_key:path}/{data_file_id}')
    def data__store_string(self                                           ,         # Store string content as file
                           namespace    : str                             ,         # Cache namespace
                           cache_id     : str                             ,         # Entity cache ID
                           data_key     : str                             ,         # Data key path
                           data_file_id : str                             ,         # File identifier
                           request      : Schema__Data__Store__String__Request      # Request with content
                      ) -> Schema__Cache__Data__Store__Response:                    # POST /{namespace}/data/{cache_id}/store/string/{data_key}/{data_file_id}
        try:
            return self.service.store_string(namespace    = namespace        ,
                                             cache_id     = cache_id         ,
                                             data_key     = data_key         ,
                                             data_file_id = data_file_id     ,
                                             content      = request.content  )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @route_path('/{namespace}/data/{cache_id}/store/json/{data_key:path}/{data_file_id}')
    def data__store_json(self                                           ,           # Store JSON content as file
                         namespace    : str                             ,           # Cache namespace
                         cache_id     : str                             ,           # Entity cache ID
                         data_key     : str                             ,           # Data key path
                         data_file_id : str                             ,           # File identifier
                         request      : Schema__Data__Store__Json__Request          # Request with content
                    ) -> Schema__Cache__Data__Store__Response:                      # POST /{namespace}/data/{cache_id}/store/json/{data_key}/{data_file_id}
        try:
            return self.service.store_json(namespace    = namespace        ,
                                           cache_id     = cache_id         ,
                                           data_key     = data_key         ,
                                           data_file_id = data_file_id     ,
                                           content      = request.content  )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ═══════════════════════════════════════════════════════════════════════════════
    # Update Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    @route_path('/{namespace}/data/{cache_id}/string/{data_key:path}/{data_file_id}')
    def data__update_string(self                                           ,        # Update string content in file
                            namespace    : str                             ,        # Cache namespace
                            cache_id     : str                             ,        # Entity cache ID
                            data_key     : str                             ,        # Data key path
                            data_file_id : str                             ,        # File identifier
                            request      : Schema__Data__Store__String__Request     # Request with content
                       ) -> Schema__Data__Update__Response:                         # PUT /{namespace}/data/{cache_id}/string/{data_key}/{data_file_id}
        try:
            return self.service.update_string(namespace    = namespace        ,
                                              cache_id     = cache_id         ,
                                              data_key     = data_key         ,
                                              data_file_id = data_file_id     ,
                                              content      = request.content  )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @route_path('/{namespace}/data/{cache_id}/json/{data_key:path}/{data_file_id}')
    def data__update_json(self                                           ,          # Update JSON content in file
                          namespace    : str                             ,          # Cache namespace
                          cache_id     : str                             ,          # Entity cache ID
                          data_key     : str                             ,          # Data key path
                          data_file_id : str                             ,          # File identifier
                          request      : Schema__Data__Store__Json__Request         # Request with content
                     ) -> Schema__Data__Update__Response:                           # PUT /{namespace}/data/{cache_id}/json/{data_key}/{data_file_id}
        try:
            return self.service.update_json(namespace    = namespace        ,
                                            cache_id     = cache_id         ,
                                            data_key     = data_key         ,
                                            data_file_id = data_file_id     ,
                                            content      = request.content  )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ═══════════════════════════════════════════════════════════════════════════════
    # Exists Operation
    # ═══════════════════════════════════════════════════════════════════════════════

    @route_path('/{namespace}/data/{cache_id}/exists/{data_type}/{data_key:path}/{data_file_id}')
    def data__exists(self                   ,                                       # Check if data file exists
                     namespace    : str     ,                                       # Cache namespace
                     cache_id     : str     ,                                       # Entity cache ID
                     data_type    : str     ,                                       # Data type (string/json)
                     data_key     : str     ,                                       # Data key path
                     data_file_id : str                                             # File identifier
                ) -> Schema__Data__Exists__Response:                                # GET /{namespace}/data/{cache_id}/exists/{data_type}/{data_key}/{data_file_id}
        try:
            return self.service.exists(namespace    = namespace    ,
                                       cache_id     = cache_id     ,
                                       data_key     = data_key     ,
                                       data_file_id = data_file_id ,
                                       data_type    = data_type    )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ═══════════════════════════════════════════════════════════════════════════════
    # Delete Operation
    # ═══════════════════════════════════════════════════════════════════════════════

    @route_path('/{namespace}/data/{cache_id}/{data_type}/{data_key:path}/{data_file_id}')
    def data__delete(self                   ,                                       # Delete data file
                     namespace    : str     ,                                       # Cache namespace
                     cache_id     : str     ,                                       # Entity cache ID
                     data_type    : str     ,                                       # Data type (string/json)
                     data_key     : str     ,                                       # Data key path
                     data_file_id : str                                             # File identifier
                ) -> Schema__Data__Delete__Response:                                # DELETE /{namespace}/data/{cache_id}/{data_type}/{data_key}/{data_file_id}
        try:
            return self.service.delete(namespace    = namespace    ,
                                       cache_id     = cache_id     ,
                                       data_key     = data_key     ,
                                       data_file_id = data_file_id ,
                                       data_type    = data_type    )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ═══════════════════════════════════════════════════════════════════════════════
    # Route Setup
    # ═══════════════════════════════════════════════════════════════════════════════

    def setup_routes(self):                                                         # Configure all routes
        self.add_route_get(self.data__list          )
        self.add_route_get(self.data__paths         )
        self.add_route_get(self.data__get_string    )
        self.add_route_get(self.data__get_json      )

        self.add_route_post(self.data__store_string )
        self.add_route_post(self.data__store_json   )

        self.add_route_put(self.data__update_string )
        self.add_route_put(self.data__update_json   )

        self.add_route_get(self.data__exists        )

        self.add_route_delete(self.data__delete     )

        return self