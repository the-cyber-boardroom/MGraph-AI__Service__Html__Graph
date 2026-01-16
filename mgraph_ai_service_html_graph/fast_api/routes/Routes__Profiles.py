# ═══════════════════════════════════════════════════════════════════════════════
# Routes__Profiles - Routes for profile discovery and execution
# v1.0.0 - Discovery, stateless execution, and cached execution
# ═══════════════════════════════════════════════════════════════════════════════

import time
from fastapi                                                                                         import HTTPException
from osbot_fast_api.api.decorators.route_path                                                        import route_path
from osbot_fast_api.api.routes.Fast_API__Routes                                                      import Fast_API__Routes
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.base.Html_LETS__Executor                import Html_LETS__Executor
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_input.Schema__LETS__Input  import Schema__LETS__Input
from mgraph_ai_service_html_graph.service.lets_pipeline.profiles.Html_LETS__Profile__Registry        import Html_LETS__Profile__Registry
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Namespace               import Safe_Str__Namespace
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                                   import Cache_Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id                      import Safe_Str__Id
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Client                           import Html_Cache__Client
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Document                         import Html_Cache__Document
from mgraph_ai_service_html_graph.schemas.routes.profiles.Schema__Profile__Info                      import Schema__Profile__Info
from mgraph_ai_service_html_graph.schemas.routes.profiles.Schema__Profile__List__Response            import Schema__Profile__List__Response
from mgraph_ai_service_html_graph.schemas.routes.profiles.Schema__Profile__List__Response            import List__Profile__Info
from mgraph_ai_service_html_graph.schemas.routes.profiles.Schema__Profile__Execute__Request          import Schema__Profile__Execute__Request
from mgraph_ai_service_html_graph.schemas.routes.profiles.Schema__Profile__Execute__Request          import Schema__Profile__Execute__Cached__Request
from mgraph_ai_service_html_graph.schemas.routes.profiles.Schema__Profile__Execute__Response         import Schema__Profile__Execute__Response
from mgraph_ai_service_html_graph.schemas.routes.profiles.Schema__Profile__Execute__Response         import List__Step__Execute__Response
from mgraph_ai_service_html_graph.schemas.routes.lets.Schema__LETS__Step__Execute__Response          import Schema__LETS__Step__Execute__Response


TAG__ROUTES_PROFILES = 'profiles'

ROUTES_PATHS__PROFILES = ['/profiles/profiles',
                          '/profiles/{profile_id}',
                          '/profiles/{profile_id}/execute',
                          '/profiles/{namespace}/{profile_id}/execute/{cache_id}']


class Routes__Profiles(Fast_API__Routes):                                        # Routes for profile operations
    tag          : str                         = TAG__ROUTES_PROFILES
    registry     : Html_LETS__Profile__Registry                                  # Profile definitions
    cache_client : Html_Cache__Client                                            # For cached operations

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.registry.setup()                                                    # Register built-in profiles

    # ═══════════════════════════════════════════════════════════════════════════
    # Discovery Endpoints
    # ═══════════════════════════════════════════════════════════════════════════

    def profiles(self) -> Schema__Profile__List__Response:                       # GET /profiles   | List all registered profiles
        profiles = List__Profile__Info()

        for profile_id in self.registry.list_profiles():
            profile = self.registry.get(Safe_Str__Id(profile_id))
            if profile:
                step_names = [cls.__name__ for cls in profile.lets_pipeline]
                profile_info = Schema__Profile__Info(profile_id  = profile.profile_id  ,
                                                     name        = profile.profile_name,
                                                     description = profile.description ,
                                                     steps       = step_names          )
                profiles.append(profile_info)

        return Schema__Profile__List__Response(profiles = profiles     ,
                                               count    = len(profiles))

    @route_path("/{profile_id}")
    def profile__info(self, profile_id: str) -> Schema__Profile__Info:           # GET /profiles/{profile_id}   | Get details about a specific profile.
        profile = self.registry.get(Safe_Str__Id(profile_id))
        if profile is None:
            raise HTTPException(status_code=404, detail={"error_type": "NOT_FOUND",
                                                         "message"   : f"Profile '{profile_id}' not found"})

        step_names = [cls.__name__ for cls in profile.lets_pipeline]

        return Schema__Profile__Info(profile_id  = profile.profile_id  ,
                                     name        = profile.profile_name,
                                     description = profile.description ,
                                     steps       = step_names          )

    # ═══════════════════════════════════════════════════════════════════════════
    # Stateless Execution
    # ═══════════════════════════════════════════════════════════════════════════

    @route_path("/{profile_id}/execute")
    def profile__execute(self                                      ,             # POST /profiles/{profile_id}/execute
                         profile_id : str                          ,
                         request    : Schema__Profile__Execute__Request
                        ) -> Schema__Profile__Execute__Response:                 # Execute a profile on raw HTML (stateless, no caching).
        profile = self.registry.get(Safe_Str__Id(profile_id))
        if profile is None:
            raise HTTPException(status_code=404, detail={"error_type": "NOT_FOUND",
                                                         "message"   : f"Profile '{profile_id}' not found"})

        executor = Html_LETS__Executor()                                         # No document = no caching
        context  = Schema__LETS__Input()

        # Add HTML to context
        if request.html:
            context.html = request.html

        try:
            start_time = time.time()
            results    = executor.execute_profile(profile = profile,
                                                  context = context)
            total_duration_ms = (time.time() - start_time) * 1000

            # Convert results to response format
            step_results = List__Step__Execute__Response()
            all_success  = True

            for result in results:
                step_response = Schema__LETS__Step__Execute__Response(step_type   = str(result.lets_name),
                                                                      success     = result.success       ,
                                                                      from_cache  = result.from_cache    ,
                                                                      duration_ms = result.duration_ms   ,
                                                                      output      = {}                   ,
                                                                      error       = result.error         )
                step_results.append(step_response)
                if not result.success:
                    all_success = False

            return Schema__Profile__Execute__Response(
                profile_id        = profile_id                               ,
                success           = all_success                              ,
                total_duration_ms = total_duration_ms                        ,
                steps_completed   = len([r for r in results if r.success])   ,
                steps_total       = len(profile.lets_pipeline)               ,
                step_results      = step_results                             ,
                final_output      = {}                                       ,
                error             = None if all_success else "One or more steps failed"
            )
        except Exception as e:
            return Schema__Profile__Execute__Response(
                profile_id        = profile_id                 ,
                success           = False                      ,
                total_duration_ms = 0                          ,
                steps_completed   = 0                          ,
                steps_total       = len(profile.lets_pipeline) ,
                step_results      = List__Step__Execute__Response(),
                error             = str(e)
            )

    # ═══════════════════════════════════════════════════════════════════════════
    # Cached Execution
    # ═══════════════════════════════════════════════════════════════════════════

    @route_path("/{namespace}/{profile_id}/execute/{cache_id}")
    def profile__execute__cached(self                                             ,  # POST /profiles/{namespace}/{profile_id}/execute/{cache_id}
                                 namespace  : Safe_Str__Namespace                 ,
                                 profile_id : str                                 ,
                                 cache_id   : Cache_Id                            ,
                                 request    : Schema__Profile__Execute__Cached__Request
                                ) -> Schema__Profile__Execute__Response:
        """Execute a profile and store results in cache."""
        profile = self.registry.get(Safe_Str__Id(profile_id))
        if profile is None:
            raise HTTPException(status_code=404, detail={"error_type": "NOT_FOUND",
                                                         "message"   : f"Profile '{profile_id}' not found"})

        # Verify cache entry exists
        if not self.cache_client.entry__exists(namespace=namespace, cache_id=cache_id):
            raise HTTPException(status_code=404, detail={"error_type": "NOT_FOUND",
                                                         "message"   : f"Cache entry '{cache_id}' not found"})

        # Create document for cached execution
        document = Html_Cache__Document(client    = self.cache_client,
                                        namespace = namespace        ,
                                        cache_key = ''               ,
                                        cache_id  = cache_id         )

        executor = Html_LETS__Executor(document=document)
        context  = Schema__LETS__Input()

        # Add HTML to context if provided
        if request.html:
            context.html = request.html

        # Determine which layers to force
        force_layers = [] if not request.force_rerun else None                   # None = force all

        try:
            start_time = time.time()
            results    = executor.execute_profile(profile      = profile     ,
                                                  context      = context     ,
                                                  force_layers = force_layers)
            total_duration_ms = (time.time() - start_time) * 1000

            # Convert results to response format
            step_results = List__Step__Execute__Response()
            all_success  = True

            for result in results:
                step_response = Schema__LETS__Step__Execute__Response(
                    step_type   = str(result.lets_name),
                    success     = result.success       ,
                    from_cache  = result.from_cache    ,
                    duration_ms = result.duration_ms   ,
                    output      = {}                   ,
                    error       = result.error
                )
                step_results.append(step_response)
                if not result.success:
                    all_success = False

            return Schema__Profile__Execute__Response(
                profile_id        = profile_id                               ,
                success           = all_success                              ,
                total_duration_ms = total_duration_ms                        ,
                steps_completed   = len([r for r in results if r.success])   ,
                steps_total       = len(profile.lets_pipeline)               ,
                step_results      = step_results                             ,
                final_output      = {}                                       ,
                error             = None if all_success else "One or more steps failed"
            )
        except Exception as e:
            return Schema__Profile__Execute__Response(
                profile_id        = profile_id                 ,
                success           = False                      ,
                total_duration_ms = 0                          ,
                steps_completed   = 0                          ,
                steps_total       = len(profile.lets_pipeline) ,
                step_results      = List__Step__Execute__Response(),
                error             = str(e)
            )

    # ═══════════════════════════════════════════════════════════════════════════
    # Route Setup
    # ═══════════════════════════════════════════════════════════════════════════

    def setup_routes(self):
        # Discovery
        self.add_route_get(self.profiles)
        self.add_route_get(self.profile__info)

        # Stateless execution
        self.add_route_post(self.profile__execute)

        # Cached execution
        self.add_route_post(self.profile__execute__cached)

        return self
