# ═══════════════════════════════════════════════════════════════════════════════
# Routes__Cache__Document - Routes for cache document operations
# v1.0.0 - Document management and layer access
# ═══════════════════════════════════════════════════════════════════════════════

from fastapi                                                                                              import HTTPException
from osbot_fast_api.api.decorators.route_path                                                             import route_path
from osbot_fast_api.api.routes.Fast_API__Routes                                                           import Fast_API__Routes
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Namespace                    import Safe_Str__Namespace
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                                        import Cache_Id
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Client                                import Html_Cache__Client
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Document                              import Html_Cache__Document
from mgraph_ai_service_html_graph.service.cache_storage.safe_str.Safe_Str__Cache_Key                      import Safe_Str__Cache_Key
from mgraph_ai_service_html_graph.service.cache_storage.safe_str.Safe_Str__Layer_Name                     import Safe_Str__Layer_Name
from mgraph_ai_service_html_graph.schemas.routes.cache.Schema__Cache__Document__Find_Or_Create__Request   import Schema__Cache__Document__Find_Or_Create__Request
from mgraph_ai_service_html_graph.schemas.routes.cache.Schema__Cache__Document__Response                  import Schema__Cache__Document__Response
from mgraph_ai_service_html_graph.schemas.routes.cache.Schema__Cache__Document__Status__Response          import Schema__Cache__Document__Status__Response
from mgraph_ai_service_html_graph.schemas.routes.cache.Schema__Cache__Document__Layers__Response          import Schema__Cache__Document__Layers__Response
from mgraph_ai_service_html_graph.schemas.routes.cache.Schema__Cache__Document__Layer__Files__Response    import Schema__Cache__Document__Layer__Files__Response


TAG__ROUTES_CACHE = 'cache'

ROUTES_PATHS__CACHE = [
    '/cache/{namespace}/document/find-or-create',
    '/cache/{namespace}/document/{cache_id}',
    '/cache/{namespace}/document/{cache_id}/status',
    '/cache/{namespace}/document/{cache_id}/layers',
    '/cache/{namespace}/document/{cache_id}/layer/{layer_name}/files',
    '/cache/{namespace}/document/{cache_id}/layer/{layer_name}/{file_id}',
]


class Routes__Cache__Document(Fast_API__Routes):                                 # Routes for cache document operations
    tag          : str               = TAG__ROUTES_CACHE
    cache_client : Html_Cache__Client                                            # Cache service client

    # ═══════════════════════════════════════════════════════════════════════════
    # Document Operations
    # ═══════════════════════════════════════════════════════════════════════════

    @route_path("/{namespace}/document/find-or-create")
    def document__find_or_create(self                                             ,  # POST /cache/{namespace}/document/find-or-create
                                 namespace : Safe_Str__Namespace                  ,
                                 request   : Schema__Cache__Document__Find_Or_Create__Request
                                ) -> Schema__Cache__Document__Response:
        """Find existing document by cache_key or create new one."""
        if not request.cache_key:
            raise HTTPException(status_code=400, detail={"error_type": "INVALID_INPUT",
                                                         "message"   : "cache_key is required"})

        document = Html_Cache__Document(client    = self.cache_client         ,
                                        namespace = namespace                 ,
                                        cache_key = Safe_Str__Cache_Key(request.cache_key))

        cache_id = document.ensure_cache_id()                                    # Creates if not exists

        # Store HTML if provided
        if request.html:
            layer = document.layer(layer_name=Safe_Str__Layer_Name('raw-html'))
            layer.save_string(file_id='source', content=request.html)

        # Load root to get timestamps
        root = document.load_root()

        return Schema__Cache__Document__Response(cache_id   = cache_id                                 ,
                                                 namespace  = namespace                                ,
                                                 cache_key  = str(request.cache_key)                   ,
                                                 created_at = str(root.created_at) if root.created_at else None,
                                                 updated_at = str(root.updated_at) if root.updated_at else None,
                                                 exists     = True                                     )

    @route_path("/{namespace}/document/{cache_id}")
    def document__get(self                               ,                       # GET /cache/{namespace}/document/{cache_id}
                      namespace : Safe_Str__Namespace    ,
                      cache_id  : Cache_Id
                     ) -> Schema__Cache__Document__Response:
        """Get document metadata."""
        if not self.cache_client.entry__exists(namespace=namespace, cache_id=cache_id):
            raise HTTPException(status_code=404, detail={"error_type": "NOT_FOUND",
                                                         "message"   : f"Cache entry '{cache_id}' not found"})

        document = Html_Cache__Document(client    = self.cache_client,
                                        namespace = namespace        ,
                                        cache_key = ''               ,
                                        cache_id  = cache_id         )

        root = document.load_root()

        return Schema__Cache__Document__Response(cache_id   = cache_id                                 ,
                                                 namespace  = namespace                                ,
                                                 cache_key  = str(root.cache_key) if root.cache_key else None,
                                                 created_at = str(root.created_at) if root.created_at else None,
                                                 updated_at = str(root.updated_at) if root.updated_at else None,
                                                 exists     = True                                     )

    @route_path("/{namespace}/document/{cache_id}/status")
    def document__status(self                            ,                       # GET /cache/{namespace}/document/{cache_id}/status
                         namespace : Safe_Str__Namespace ,
                         cache_id  : Cache_Id
                        ) -> Schema__Cache__Document__Status__Response:
        """Get all step completion statuses for a document."""
        if not self.cache_client.entry__exists(namespace=namespace, cache_id=cache_id):
            raise HTTPException(status_code=404, detail={"error_type": "NOT_FOUND",
                                                         "message"   : f"Cache entry '{cache_id}' not found"})

        document = Html_Cache__Document(client    = self.cache_client,
                                        namespace = namespace        ,
                                        cache_key = ''               ,
                                        cache_id  = cache_id         )

        # Get status for all steps
        status_dict = document.layer_status()

        # Convert Safe_Str keys to regular strings
        steps = {str(k): v for k, v in status_dict.items()}

        return Schema__Cache__Document__Status__Response(cache_id  = cache_id ,
                                                         namespace = namespace,
                                                         steps     = steps    )

    @route_path("/{namespace}/document/{cache_id}")
    def document__delete(self                            ,                       # DELETE /cache/{namespace}/document/{cache_id}
                         namespace : Safe_Str__Namespace ,
                         cache_id  : Cache_Id
                        ) -> dict:
        """Delete a document and all its layers."""
        if not self.cache_client.entry__exists(namespace=namespace, cache_id=cache_id):
            raise HTTPException(status_code=404, detail={"error_type": "NOT_FOUND",
                                                         "message"   : f"Cache entry '{cache_id}' not found"})

        document = Html_Cache__Document(client    = self.cache_client,
                                        namespace = namespace        ,
                                        cache_key = ''               ,
                                        cache_id  = cache_id         )

        deleted = document.delete()

        if deleted:
            return {"status"   : "success"                        ,
                    "message"  : "Document deleted successfully"  ,
                    "cache_id" : str(cache_id)                    ,
                    "namespace": str(namespace)                   }
        else:
            raise HTTPException(status_code=500, detail={"error_type": "DELETE_FAILED",
                                                         "message"   : "Failed to delete document"})

    # ═══════════════════════════════════════════════════════════════════════════
    # Layer Operations
    # ═══════════════════════════════════════════════════════════════════════════

    @route_path("/{namespace}/document/{cache_id}/layers")
    def document__layers(self                            ,                       # GET /cache/{namespace}/document/{cache_id}/layers
                         namespace : Safe_Str__Namespace ,
                         cache_id  : Cache_Id
                        ) -> Schema__Cache__Document__Layers__Response:
        """List all layers in a document."""
        if not self.cache_client.entry__exists(namespace=namespace, cache_id=cache_id):
            raise HTTPException(status_code=404, detail={"error_type": "NOT_FOUND",
                                                         "message"   : f"Cache entry '{cache_id}' not found"})

        # List data files to extract layer names
        result = self.cache_client.data__list(namespace = namespace,
                                              cache_id  = cache_id ,
                                              recursive = True     )

        # Extract unique layer names from file paths
        layers = set()
        if result and result.files:
            for file_info in result.files:
                if hasattr(file_info, 'data_key') and file_info.data_key:
                    # data_key is the layer name (first path component)
                    layer_name = str(file_info.data_key).split('/')[0]
                    if layer_name:
                        layers.add(layer_name)

        return Schema__Cache__Document__Layers__Response(cache_id  = cache_id    ,
                                                         namespace = namespace   ,
                                                         layers    = list(layers))

    @route_path("/{namespace}/document/{cache_id}/layer/{layer_name}/files")
    def layer__files(self                            ,                           # GET /cache/{namespace}/document/{cache_id}/layer/{layer_name}/files
                     namespace  : Safe_Str__Namespace,
                     cache_id   : Cache_Id           ,
                     layer_name : str
                    ) -> Schema__Cache__Document__Layer__Files__Response:
        """List all files in a layer."""
        if not self.cache_client.entry__exists(namespace=namespace, cache_id=cache_id):
            raise HTTPException(status_code=404, detail={"error_type": "NOT_FOUND",
                                                         "message"   : f"Cache entry '{cache_id}' not found"})

        # List files in this specific layer
        result = self.cache_client.data__list(namespace = namespace                       ,
                                              cache_id  = cache_id                        ,
                                              data_key  = Safe_Str__Layer_Name(layer_name),
                                              recursive = True                            )

        files = []
        if result and result.files:
            for file_info in result.files:
                files.append({"file_id"  : str(file_info.file_id) if hasattr(file_info, 'file_id') else None  ,
                              "data_type": str(file_info.data_type) if hasattr(file_info, 'data_type') else None,
                              "size"     : file_info.size if hasattr(file_info, 'size') else 0                })

        return Schema__Cache__Document__Layer__Files__Response(cache_id   = cache_id  ,
                                                               namespace  = namespace ,
                                                               layer_name = layer_name,
                                                               files      = files     )

    @route_path("/{namespace}/document/{cache_id}/layer/{layer_name}/{file_id}")
    def layer__file(self                            ,                            # GET /cache/{namespace}/document/{cache_id}/layer/{layer_name}/{file_id}
                    namespace  : Safe_Str__Namespace,
                    cache_id   : Cache_Id           ,
                    layer_name : str                ,
                    file_id    : str
                   ) -> dict:
        """Get file content from a layer."""
        if not self.cache_client.entry__exists(namespace=namespace, cache_id=cache_id):
            raise HTTPException(status_code=404, detail={"error_type": "NOT_FOUND",
                                                         "message"   : f"Cache entry '{cache_id}' not found"})

        document = Html_Cache__Document(client    = self.cache_client,
                                        namespace = namespace        ,
                                        cache_key = ''               ,
                                        cache_id  = cache_id         )

        layer = document.layer(layer_name=Safe_Str__Layer_Name(layer_name))

        # Try JSON first, then string
        content = layer.load_json(file_id=file_id)
        if content is not None:
            return {"cache_id"   : str(cache_id) ,
                    "namespace"  : str(namespace),
                    "layer_name" : layer_name    ,
                    "file_id"    : file_id       ,
                    "data_type"  : "json"        ,
                    "content"    : content       }

        content = layer.load_string(file_id=file_id)
        if content is not None:
            return {"cache_id"   : str(cache_id) ,
                    "namespace"  : str(namespace),
                    "layer_name" : layer_name    ,
                    "file_id"    : file_id       ,
                    "data_type"  : "string"      ,
                    "content"    : content       }

        raise HTTPException(status_code=404, detail={"error_type": "NOT_FOUND",
                                                     "message"   : f"File '{file_id}' not found in layer '{layer_name}'"})

    # ═══════════════════════════════════════════════════════════════════════════
    # Route Setup
    # ═══════════════════════════════════════════════════════════════════════════

    def setup_routes(self):
        # Document operations
        self.add_route_post(self.document__find_or_create)
        self.add_route_get(self.document__get)
        self.add_route_get(self.document__status)
        self.add_route_delete(self.document__delete)

        # Layer operations
        self.add_route_get(self.document__layers)
        self.add_route_get(self.layer__files)
        self.add_route_get(self.layer__file)

        return self
