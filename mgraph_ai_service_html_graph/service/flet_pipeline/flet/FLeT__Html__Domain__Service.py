# ═══════════════════════════════════════════════════════════════════════════════
# FLeT__Html__Domain__Service - Service layer for domain-level HTML operations
# ═══════════════════════════════════════════════════════════════════════════════

from mgraph_ai_service_cache_client.schemas.cache.safe_str.Safe_Str__Cache__File__Cache_Key         import Safe_Str__Cache__File__Cache_Key
from mgraph_ai_service_cache_client.schemas.cache.safe_str.Safe_Str__Cache__Namespace               import Safe_Str__Cache__Namespace
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Create__Request              import Schema__Entity__Create__Request
from mgraph_ai_service_html_graph.schemas.cache.entity.Schema__Entity__Lookup__Request              import Schema__Entity__Lookup__Request
from mgraph_ai_service_html_graph.schemas.flet.domain.Schema__Html__Load__Hash__Request             import Schema__Html__Load__Hash__Request
from mgraph_ai_service_html_graph.schemas.flet.domain.Schema__Html__Load__Id__Request               import Schema__Html__Load__Id__Request
from mgraph_ai_service_html_graph.schemas.flet.domain.Schema__Html__Load__Response                  import Schema__Html__Load__Response
from mgraph_ai_service_html_graph.schemas.flet.domain.Schema__Html__Load__Url__Request              import Schema__Html__Load__Url__Request
from mgraph_ai_service_html_graph.schemas.flet.domain.Schema__Html__Store__Key__Request             import Schema__Html__Store__Key__Request
from mgraph_ai_service_html_graph.schemas.flet.domain.Schema__Html__Store__Raw__Request             import Schema__Html__Store__Raw__Request
from mgraph_ai_service_html_graph.schemas.flet.domain.Schema__Html__Store__Response                 import Schema__Html__Store__Response
from mgraph_ai_service_html_graph.schemas.flet.domain.Schema__Html__Store__Url__Request             import Schema__Html__Store__Url__Request
from mgraph_ai_service_html_graph.schemas.flet.html.Schema__FLeT__Html__From__Cache__Request        import Schema__FLeT__Html__From__Cache__Request
from mgraph_ai_service_html_graph.schemas.flet.html.Schema__FLeT__Html__To__Cache__Request          import Schema__FLeT__Html__To__Cache__Request
from mgraph_ai_service_html_graph.schemas.routes.Schema__Html__From_Url__Request                    import Schema__Html__From_Url__Request
from mgraph_ai_service_html_graph.service.cache.Cache__Entity__Service                              import Cache__Entity__Service
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Client                          import Html_Cache__Client
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.FLeT__Html__Execute__Service           import FLeT__Html__Execute__Service
from mgraph_ai_service_html_graph.service.html_url.Html__Url__Fetcher                               import Html__Url__Fetcher
from mgraph_ai_service_html_graph.service.html_url.Url__To__Cache_Key                               import Url__To__Cache_Key
from osbot_utils.helpers.cache.Cache__Hash__Generator                                               import Cache__Hash__Generator
from osbot_utils.type_safe.Type_Safe                                                                import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                                  import Cache_Id
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html                           import Safe_Str__Html
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                      import type_safe


class FLeT__Html__Domain__Service(Type_Safe):                                         # Domain service for HTML operations
    html_cache_client : Html_Cache__Client                                            # Cache client for storage
    entity_service    : Cache__Entity__Service       = None                           # Entity management service
    execute_service   : FLeT__Html__Execute__Service = None                           # FLeT execution service
    hash_generator    : Cache__Hash__Generator                                        # Hash generator for cache keys
    url_fetcher       : Html__Url__Fetcher                                            # URL fetcher for remote HTML
    url_to_cache_key  : Url__To__Cache_Key                                            # Util to convert URLs into cache_keys


    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.entity_service = Cache__Entity__Service       (html_cache_client=self.html_cache_client)
        self.execute_service = FLeT__Html__Execute__Service(html_cache_client=self.html_cache_client)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Store Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def store_raw(self                                              ,               # Store raw HTML with auto-hash key
                  namespace : Safe_Str__Cache__Namespace            ,               # Cache namespace
                  request   : Schema__Html__Store__Raw__Request                     # Request with HTML content
             ) -> Schema__Html__Store__Response:
        html = request.html
        if not html:
            return Schema__Html__Store__Response(success=False)

        cache_hash = self.hash_generator.from_string(html)
        cache_key  = f'html/raw/{cache_hash}'

        return self.store_html(namespace = namespace ,
                               cache_key = cache_key ,
                               html      = html      )

    @type_safe
    def store_from_url(self                                              ,          # Fetch and store HTML from URL
                       namespace : Safe_Str__Cache__Namespace            ,          # Cache namespace
                       request   : Schema__Html__Store__Url__Request                # Request with URL
                  ) -> Schema__Html__Store__Response:
        url = request.url
        if not url:
            return Schema__Html__Store__Response(success=False)
        try:
            fetch_request  = Schema__Html__From_Url__Request(url     = url            ,
                                                             timeout = request.timeout)
            fetch_response = self.url_fetcher.fetch_html(fetch_request)
            html           = fetch_response.html
            final_url      = fetch_response.url
            cache_key      = self.url_to_cache_key.cache_key(url = final_url)

            result           = self.store_html(namespace = namespace ,
                                               cache_key = cache_key ,
                                               html      = html      )
            result.final_url = final_url
            return result
        except Exception:
            return Schema__Html__Store__Response(success=False)

    @type_safe
    def store_with_key(self                                                    ,    # Store HTML with explicit key
                       namespace : Safe_Str__Cache__Namespace                  ,    # Cache namespace
                       cache_key : Safe_Str__Cache__File__Cache_Key            ,    # Explicit cache key
                       request   : Schema__Html__Store__Key__Request                # Request with HTML
                  ) -> Schema__Html__Store__Response:
        html = request.html
        if not html or not cache_key:
            return Schema__Html__Store__Response(success=False)

        return self.store_html(namespace = namespace ,
                               cache_key = cache_key ,
                               html      = html      )

    def store_html(self                                                  ,          # Store HTML with entity create/lookup
                   namespace : Safe_Str__Cache__Namespace                ,          # Cache namespace
                   cache_key : Safe_Str__Cache__File__Cache_Key          ,          # Cache key for storage
                   html      : Safe_Str__Html                                       # HTML content to store
              ) -> Schema__Html__Store__Response:
        cache_id = self.get_or_create_entity(namespace = namespace ,
                                             cache_key = cache_key )
        if not cache_id:
            return Schema__Html__Store__Response(success=False)

        execute_request  = Schema__FLeT__Html__To__Cache__Request(html=html)
        execute_response = self.execute_service.execute_to_cache(namespace = namespace ,
                                                                 cache_id  = cache_id  ,
                                                                 request   = execute_request)

        cache_hash = self.hash_generator.from_string(cache_key)

        return Schema__Html__Store__Response(success        = execute_response.success   ,
                                             cache_id       = cache_id                   ,
                                             cache_key      = cache_key                  ,
                                             cache_hash     = cache_hash                 ,
                                             char_count     = execute_response.char_count)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Load Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def load_by_id(self                                              ,              # Load HTML by cache_id
                   namespace : Safe_Str__Cache__Namespace            ,              # Cache namespace
                   request   : Schema__Html__Load__Id__Request                      # Request with cache_id
              ) -> Schema__Html__Load__Response:
        cache_id = request.cache_id
        if not cache_id:
            return Schema__Html__Load__Response(success=False)

        return self.load_html(namespace = namespace ,
                              cache_id  = cache_id  )

    @type_safe
    def load_by_hash(self                                              ,            # Load HTML by cache_hash
                     namespace : Safe_Str__Cache__Namespace            ,            # Cache namespace
                     request   : Schema__Html__Load__Hash__Request                  # Request with cache_hash
                ) -> Schema__Html__Load__Response:
        cache_hash = request.cache_hash
        if not cache_hash:
            return Schema__Html__Load__Response(success=False)

        lookup_request  = Schema__Entity__Lookup__Request(cache_hash=cache_hash)
        lookup_response = self.entity_service.lookup(namespace = namespace     ,
                                                     request   = lookup_request)
        if lookup_response.found is False:
            return Schema__Html__Load__Response(success = True ,
                                                found   = False)

        return self.load_html(namespace = namespace              ,
                              cache_id  = lookup_response.cache_id)

    @type_safe
    def load_by_key(self                                                  ,         # Load HTML by cache_key
                    namespace : Safe_Str__Cache__Namespace                ,         # Cache namespace
                    cache_key : Safe_Str__Cache__File__Cache_Key                    # Cache key to lookup
               ) -> Schema__Html__Load__Response:
        if not cache_key:
            return Schema__Html__Load__Response(success=False)

        lookup_request  = Schema__Entity__Lookup__Request(cache_key=cache_key)
        lookup_response = self.entity_service.lookup(namespace = namespace     ,
                                                     request   = lookup_request)
        if lookup_response.found is False:
            return Schema__Html__Load__Response(success   = True     ,
                                                found     = False    ,
                                                cache_key = cache_key)

        result           = self.load_html(namespace = namespace               ,
                                          cache_id  = lookup_response.cache_id)
        result.cache_key = cache_key
        return result

    @type_safe
    def load_by_url(self                                              ,             # Load HTML by URL as cache_key
                    namespace : Safe_Str__Cache__Namespace            ,             # Cache namespace
                    request   : Schema__Html__Load__Url__Request                    # Request with URL
               ) -> Schema__Html__Load__Response:
        url = request.url
        if not url:
            return Schema__Html__Load__Response(success=False)
        cache_key = self.url_to_cache_key.cache_key(url=url)
        return self.load_by_key(namespace = namespace ,
                                cache_key = cache_key )

    def load_html(self                                      ,                       # Load HTML from cache
                  namespace : Safe_Str__Cache__Namespace    ,                       # Cache namespace
                  cache_id  : Cache_Id                                              # Cache ID to load
             ) -> Schema__Html__Load__Response:
        execute_request  = Schema__FLeT__Html__From__Cache__Request()
        execute_response = self.execute_service.execute_from_cache(namespace = namespace       ,
                                                                   cache_id  = cache_id        ,
                                                                   request   = execute_request )

        return Schema__Html__Load__Response(success    = execute_response.success   ,
                                            cache_id   = cache_id                   ,
                                            html       = execute_response.html      ,
                                            found      = execute_response.found     ,
                                            char_count = execute_response.char_count)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Entity Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    def get_or_create_entity(self                                                  ,# Get or create cache entity
                             namespace : Safe_Str__Cache__Namespace                ,# Cache namespace
                             cache_key : Safe_Str__Cache__File__Cache_Key           # Cache key for entity
                        ) -> Cache_Id:                                              # Returns cache_id
        lookup_request  = Schema__Entity__Lookup__Request(cache_key=cache_key)
        lookup_response = self.entity_service.lookup(namespace = namespace     ,
                                                     request   = lookup_request)
        if lookup_response.found is True:
            return lookup_response.cache_id

        create_request  = Schema__Entity__Create__Request(cache_key=cache_key)
        create_response = self.entity_service.create(namespace = namespace     ,
                                                     request   = create_request)
        if create_response.success is True:
            return create_response.cache_id
        else:
            return None
