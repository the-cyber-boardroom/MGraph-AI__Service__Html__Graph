# ═══════════════════════════════════════════════════════════════════════════════
# MGraph HTML Graph - PlantUML Proxy Routes
# Reverse proxy for PlantUML core files from GitHub releases
# ═══════════════════════════════════════════════════════════════════════════════

import requests
from osbot_fast_api.api.decorators.route_path   import route_path
from osbot_fast_api.api.routes.Fast_API__Routes import Fast_API__Routes
from starlette.responses                        import Response

# GitHub release URLs
PLANTUML_VERSION     = "v0.0.2"
PLANTUML_BASE_URL    = f"https://github.com/plantuml/plantuml-core/releases/download/{PLANTUML_VERSION}"
PLANTUML_JAR_URL     = f"{PLANTUML_BASE_URL}/plantuml-core.jar"
PLANTUML_JAR_JS_URL  = f"{PLANTUML_BASE_URL}/plantuml-core.jar.js"

TAG__ROUTES_PLANTUML = "jars"

ROUTES_PATHS__PLANTUML = [
    f'/{TAG__ROUTES_PLANTUML}/plantuml-core.jar',
    f'/{TAG__ROUTES_PLANTUML}/plantuml-core.jar.js',
]


class Routes__PlantUML(Fast_API__Routes):
    """Reverse proxy routes for PlantUML core files."""

    tag    : str  = TAG__ROUTES_PLANTUML
    _cache : dict

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._cache = {}

    # ═══════════════════════════════════════════════════════════════════════════
    # Routes
    # ═══════════════════════════════════════════════════════════════════════════

    @route_path('/plantuml-core.jar')
    def plantuml_core_jar(self) -> Response:                                            # GET /plantuml/plantuml-core.jar
        """Proxy for plantuml-core.jar from GitHub releases."""
        return self._proxy_file(url          = PLANTUML_JAR_URL              ,
                                cache_key    = 'jar'                         ,
                                content_type = 'application/java-archive'    ,
                                filename     = 'plantuml-core.jar'           )

    @route_path('/plantuml-core.jar.js')
    def plantuml_core_jar_js(self) -> Response:                                         # GET /plantuml/plantuml-core.jar.js
        """Proxy for plantuml-core.jar.js from GitHub releases."""
        return self._proxy_file(url          = PLANTUML_JAR_JS_URL           ,
                                cache_key    = 'jar_js'                      ,
                                content_type = 'application/javascript'      ,
                                filename     = 'plantuml-core.jar.js'        )

    # ═══════════════════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def _proxy_file(self, url: str, cache_key: str, content_type: str, filename: str) -> Response:
        """Fetch file from URL and return as response, with caching."""

        # Check cache first
        if cache_key in self._cache:
            return Response(content    = self._cache[cache_key]                         ,
                            media_type = content_type                                   ,
                            headers    = { 'Content-Disposition' : f'inline; filename="{filename}"',
                                           'Cache-Control'       : 'public, max-age=86400'         ,
                                           'X-Proxy-Cache'       : 'HIT'                           })

        try:
            # Fetch from GitHub (follow redirects)
            response = requests.get(url, timeout=30, allow_redirects=True)
            response.raise_for_status()

            content = response.content
            self._cache[cache_key] = content                                            # Cache the content

            return Response(content    = content                                        ,
                            media_type = content_type                                   ,
                            headers    = { 'Content-Disposition' : f'inline; filename="{filename}"',
                                           'Cache-Control'       : 'public, max-age=86400'         ,
                                           'X-Proxy-Cache'       : 'MISS'                          })

        except requests.RequestException as e:
            return Response(content     = f"Error fetching {filename}: {str(e)}"        ,
                            status_code = 502                                           ,
                            media_type  = 'text/plain'                                  )

    # ═══════════════════════════════════════════════════════════════════════════
    # Route Registration
    # ═══════════════════════════════════════════════════════════════════════════

    def setup_routes(self):
        self.add_route_get(self.plantuml_core_jar   )
        self.add_route_get(self.plantuml_core_jar_js)

        # HEAD route - returns headers only (no body)
        self.router.add_api_route(path     = '/plantuml-core.jar',
                                  endpoint = self.plantuml_core_jar_head,
                                  methods  = ['HEAD']       )
        return self

    def plantuml_core_jar_head(self) -> Response:       # HEAD request - returns headers only for plantuml-core.jar.
        # Get the file (from cache or fetch) to know the size
        if 'jar' in self._cache:
            content_length = len(self._cache['jar'])
        else:
            # Fetch to populate cache and get size
            response = self._proxy_file(url          = PLANTUML_JAR_URL,
                                        cache_key    = 'jar',
                                        content_type = 'application/java-archive',
                                        filename     = 'plantuml-core.jar'       )
            content_length = len(response.body)

        return Response(content    = b'',  # Empty body for HEAD
                        media_type = 'application/java-archive',
                        headers    = {
                            'Content-Length'      : str(content_length),
                            'Content-Disposition' : 'inline; filename="plantuml-core.jar"',
                            'Cache-Control'       : 'public, max-age=86400',
                            'Accept-Ranges'       : 'bytes'
                        })