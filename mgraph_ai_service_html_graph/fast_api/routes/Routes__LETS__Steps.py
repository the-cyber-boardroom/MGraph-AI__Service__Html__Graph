# ═══════════════════════════════════════════════════════════════════════════════
# Routes__LETS__Steps - Routes for LETS step discovery and execution
# v1.0.0 - Discovery, stateless execution, and cached execution
# ═══════════════════════════════════════════════════════════════════════════════

import time
from fastapi                                                                                         import HTTPException
from osbot_fast_api.api.decorators.route_path                                                        import route_path
from osbot_fast_api.api.routes.Fast_API__Routes                                                      import Fast_API__Routes
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.base.Html_LETS__Executor                import Html_LETS__Executor
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.enums.Enum__Html_LETS__Type     import Enum__Html_LETS__Type
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_input.Schema__LETS__Input  import Schema__LETS__Input
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Namespace               import Safe_Str__Namespace
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                                   import Cache_Id
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Client                           import Html_Cache__Client
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Document                         import Html_Cache__Document
from mgraph_ai_service_html_graph.schemas.routes.lets.Schema__LETS__Step__Info                       import Schema__LETS__Step__Info
from mgraph_ai_service_html_graph.schemas.routes.lets.Schema__LETS__Step__List__Response             import Schema__LETS__Step__List__Response
from mgraph_ai_service_html_graph.schemas.routes.lets.Schema__LETS__Step__List__Response             import List__LETS__Step__Info
from mgraph_ai_service_html_graph.schemas.routes.lets.Schema__LETS__Step__Execute__Request           import Schema__LETS__Step__Execute__Request
from mgraph_ai_service_html_graph.schemas.routes.lets.Schema__LETS__Step__Execute__Request           import Schema__LETS__Step__Execute__Cached__Request
from mgraph_ai_service_html_graph.schemas.routes.lets.Schema__LETS__Step__Execute__Response          import Schema__LETS__Step__Execute__Response
from mgraph_ai_service_html_graph.schemas.routes.lets.Schema__LETS__Step__Status__Response           import Schema__LETS__Step__Status__Response


TAG__ROUTES_LETS = 'lets'

ROUTES_PATHS__LETS = ['/lets/steps',
                      '/lets/steps/{step_type}',
                      '/lets/steps/{step_type}/execute',
                      '/lets/{namespace}/steps/{step_type}/execute/{cache_id}',
                      '/lets/{namespace}/steps/{step_type}/status/{cache_id}']


class Routes__LETS__Steps(Fast_API__Routes):                                     # Routes for LETS step operations
    tag          : str               = TAG__ROUTES_LETS
    cache_client : Html_Cache__Client                                            # For cached operations

    # ═══════════════════════════════════════════════════════════════════════════
    # Discovery Endpoints
    # ═══════════════════════════════════════════════════════════════════════════

    def steps(self) -> Schema__LETS__Step__List__Response:                       # GET /lets/steps
        """List all available LETS step types."""
        steps = List__LETS__Step__Info()

        for step_enum in Enum__Html_LETS__Type:
            step_class    = step_enum.value
            step_instance = step_class()
            step_instance.setup()

            step_info = Schema__LETS__Step__Info(step_type   = step_enum.name               ,
                                                 name        = step_instance.config.name    ,
                                                 description = step_instance.config.description)
            steps.append(step_info)

        return Schema__LETS__Step__List__Response(steps = steps     ,
                                                  count = len(steps))

    @route_path("/steps/{step_type}")
    def step__info(self, step_type: str) -> Schema__LETS__Step__Info:            # GET /lets/steps/{step_type}
        """Get details about a specific LETS step."""
        step_class = self._get_step_class(step_type)
        if step_class is None:
            raise HTTPException(status_code=404, detail={"error_type": "NOT_FOUND",
                                                         "message"   : f"Step type '{step_type}' not found"})

        step_instance = step_class()
        step_instance.setup()

        return Schema__LETS__Step__Info(step_type   = step_type                      ,
                                        name        = step_instance.config.name      ,
                                        description = step_instance.config.description)

    # ═══════════════════════════════════════════════════════════════════════════
    # Stateless Execution
    # ═══════════════════════════════════════════════════════════════════════════

    @route_path("/steps/{step_type}/execute")
    def step__execute(self                                         ,             # POST /lets/steps/{step_type}/execute
                      step_type : str                              ,
                      request   : Schema__LETS__Step__Execute__Request
                     ) -> Schema__LETS__Step__Execute__Response:
        """Execute a LETS step on raw input (stateless, no caching)."""
        step_class = self._get_step_class(step_type)
        if step_class is None:
            raise HTTPException(status_code=404, detail={"error_type": "NOT_FOUND",
                                                         "message"   : f"Step type '{step_type}' not found"})

        executor = Html_LETS__Executor()                                         # No document = no caching
        context  = Schema__LETS__Input()                                         # Build context from request

        # Add input_data to context if provided
        if request.input_data:
            for key, value in request.input_data.items():
                setattr(context, key, value)

        try:
            start_time = time.time()
            result     = executor.execute_single(lets_class = step_class,
                                                 context    = context   ,
                                                 force      = True      )        # Always execute (stateless)
            duration_ms = (time.time() - start_time) * 1000

            return Schema__LETS__Step__Execute__Response(step_type   = step_type            ,
                                                         success     = result.success       ,
                                                         from_cache  = False                ,
                                                         duration_ms = duration_ms          ,
                                                         output      = {}                   ,  # TODO: capture output
                                                         error       = result.error         )
        except Exception as e:
            return Schema__LETS__Step__Execute__Response(step_type   = step_type,
                                                         success     = False    ,
                                                         from_cache  = False    ,
                                                         duration_ms = 0        ,
                                                         error       = str(e)   )

    # ═══════════════════════════════════════════════════════════════════════════
    # Cached Execution
    # ═══════════════════════════════════════════════════════════════════════════

    @route_path("/{namespace}/steps/{step_type}/execute/{cache_id}")
    def step__execute__cached(self                                                ,  # POST /lets/{namespace}/steps/{step_type}/execute/{cache_id}
                              namespace : Safe_Str__Namespace                     ,
                              step_type : str                                     ,
                              cache_id  : Cache_Id                                ,
                              request   : Schema__LETS__Step__Execute__Cached__Request
                             ) -> Schema__LETS__Step__Execute__Response:
        """Execute a LETS step and store results in cache."""
        step_class = self._get_step_class(step_type)
        if step_class is None:
            raise HTTPException(status_code=404, detail={"error_type": "NOT_FOUND",
                                                         "message"   : f"Step type '{step_type}' not found"})

        # Verify cache entry exists
        if not self.cache_client.entry__exists(namespace=namespace, cache_id=cache_id):
            raise HTTPException(status_code=404, detail={"error_type": "NOT_FOUND",
                                                         "message"   : f"Cache entry '{cache_id}' not found"})

        # Create document for cached execution
        document = Html_Cache__Document(client    = self.cache_client,
                                        namespace = namespace        ,
                                        cache_key = ''               ,  # Not needed when cache_id provided
                                        cache_id  = cache_id         )

        executor = Html_LETS__Executor(document=document)
        context  = Schema__LETS__Input()

        # If HTML provided, add to context
        if request.html:
            context.html = request.html

        try:
            start_time = time.time()
            result     = executor.execute_single(lets_class = step_class        ,
                                                 context    = context           ,
                                                 force      = request.force_rerun)
            duration_ms = (time.time() - start_time) * 1000

            return Schema__LETS__Step__Execute__Response(step_type   = step_type            ,
                                                         success     = result.success       ,
                                                         from_cache  = result.from_cache    ,
                                                         duration_ms = duration_ms          ,
                                                         output      = {}                   ,
                                                         error       = result.error         )
        except Exception as e:
            return Schema__LETS__Step__Execute__Response(step_type   = step_type,
                                                         success     = False    ,
                                                         from_cache  = False    ,
                                                         duration_ms = 0        ,
                                                         error       = str(e)   )

    @route_path("/{namespace}/steps/{step_type}/status/{cache_id}")
    def step__status(self                                ,                       # GET /lets/{namespace}/steps/{step_type}/status/{cache_id}
                     namespace : Safe_Str__Namespace     ,
                     step_type : str                     ,
                     cache_id  : Cache_Id
                    ) -> Schema__LETS__Step__Status__Response:
        """Check if a LETS step has been completed for a cache document."""
        # Validate step type
        step_class = self._get_step_class(step_type)
        if step_class is None:
            raise HTTPException(status_code=404, detail={"error_type": "NOT_FOUND",
                                                         "message"   : f"Step type '{step_type}' not found"})

        # Get step name from class
        step_instance = step_class()
        step_instance.setup()
        step_name = step_instance.config.name

        # Verify cache entry exists
        if not self.cache_client.entry__exists(namespace=namespace, cache_id=cache_id):
            raise HTTPException(status_code=404, detail={"error_type": "NOT_FOUND",
                                                         "message"   : f"Cache entry '{cache_id}' not found"})

        # Create document and check status
        document = Html_Cache__Document(client    = self.cache_client,
                                        namespace = namespace        ,
                                        cache_key = ''               ,
                                        cache_id  = cache_id         )

        status = document.get_lets_status(name=step_name)

        if status:
            return Schema__LETS__Step__Status__Response(step_type    = step_type             ,
                                                        cache_id     = cache_id              ,
                                                        namespace    = namespace             ,
                                                        completed    = status.completed      ,
                                                        duration_ms  = status.duration_ms    ,
                                                        completed_at = str(status.timestamp) if status.timestamp else None)
        else:
            return Schema__LETS__Step__Status__Response(step_type = step_type,
                                                        cache_id  = cache_id ,
                                                        namespace = namespace,
                                                        completed = False    )

    # ═══════════════════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def _get_step_class(self, step_type: str):                                   # Get step class from type name
        """Get LETS step class from step type name."""
        try:
            step_enum = Enum__Html_LETS__Type[step_type.upper()]
            return step_enum.value
        except KeyError:
            # Try case-insensitive match
            for enum_member in Enum__Html_LETS__Type:
                if enum_member.name.lower() == step_type.lower():
                    return enum_member.value
            return None

    # ═══════════════════════════════════════════════════════════════════════════
    # Route Setup
    # ═══════════════════════════════════════════════════════════════════════════

    def setup_routes(self):
        # Discovery
        self.add_route_get(self.steps)
        self.add_route_get(self.step__info)

        # Stateless execution
        self.add_route_post(self.step__execute)

        # Cached execution
        self.add_route_post(self.step__execute__cached)
        self.add_route_get(self.step__status)

        return self
