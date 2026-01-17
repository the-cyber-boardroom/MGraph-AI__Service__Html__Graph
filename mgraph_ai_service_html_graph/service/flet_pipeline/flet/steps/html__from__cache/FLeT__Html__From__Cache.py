# ═══════════════════════════════════════════════════════════════════════════════
# FLeT__Html__From__Cache - Retrieve HTML from cache service
# Round-trip part 2: Cache → HTML (lookup by hash, URL, or cache key)
# ═══════════════════════════════════════════════════════════════════════════════
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                                                          import type_safe
from osbot_utils.helpers.flows.decorators.task                                                                                          import task
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html                                                               import Safe_Str__Html
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Cache_Hash                                                import Safe_Str__Cache_Hash
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                                                                      import Cache_Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Namespace                                                  import Safe_Str__Namespace
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.base.Html_FLeT__Base                                                       import Html_FLeT__Base
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.schemas.Schema__FLeT__Config                                               import Schema__FLeT__Config
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.schemas.safe_str.Safe_Str__FLeT__Name                                      import Safe_Str__FLeT__Name
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Client                                                              import Html_Cache__Client
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__from__cache.schemas.Schema__Html_From_Cache__Extract__Output     import Schema__Html_From_Cache__Extract__Output
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__from__cache.schemas.Schema__Html_From_Cache__Load__Input         import Schema__Html_From_Cache__Load__Input
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__from__cache.schemas.Schema__Html_From_Cache__Load__Output        import Schema__Html_From_Cache__Load__Output
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__from__cache.schemas.Schema__Html_From_Cache__Save__Output        import Schema__Html_From_Cache__Save__Output
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__from__cache.schemas.Schema__Html_From_Cache__Transform__Output   import Schema__Html_From_Cache__Transform__Output


@task()
@type_safe
def action__html_from_cache__load(input_data  : Schema__Html_From_Cache__Load__Input,
                                  cache_client: Html_Cache__Client = None
                             ) -> Schema__Html_From_Cache__Load__Output:
    namespace =  input_data.namespace
    cache_id    = None
    lookup_type = ''
    found       = False

    if cache_client is None:
        return Schema__Html_From_Cache__Load__Output(namespace   = namespace,
                                                     cache_id    = None     ,
                                                     lookup_type = 'none'   ,
                                                     found       = False    )

    # Priority: cache_id > html_hash > cache_key > url
    if input_data.cache_id:
        cache_id    = input_data.cache_id
        lookup_type = 'cache_id'
        found       = cache_client.entry__exists(namespace=namespace, cache_id=cache_id)

    elif input_data.html_hash:
        lookup_type = 'html_hash'
        if cache_client.entry__exists_by_hash(namespace=namespace, cache_hash=input_data.html_hash):
            cache_id = cache_client.cache_id__from_hash(namespace=namespace, cache_hash=input_data.html_hash)
            found    = cache_id is not None

    elif input_data.cache_key:
        lookup_type = 'cache_key'
        cache_id    = cache_client.cache_id__from_key(namespace=namespace, cache_key=input_data.cache_key)
        found       = cache_id is not None

    elif input_data.url:
        lookup_type = 'url'
        url_hash    = cache_client.hash_generator.from_string(input_data.url)
        if cache_client.entry__exists_by_hash(namespace=namespace, cache_hash=url_hash):
            cache_id = cache_client.cache_id__from_hash(namespace=namespace, cache_hash=url_hash)
            found    = cache_id is not None

    return Schema__Html_From_Cache__Load__Output(namespace   = namespace  ,
                                                 cache_id    = cache_id   ,
                                                 lookup_type = lookup_type,
                                                 found       = found      )


@task()
@type_safe
def action__html_from_cache__extract(input_data  : Schema__Html_From_Cache__Load__Output,
                                     cache_client: Html_Cache__Client = None
                                ) -> Schema__Html_From_Cache__Extract__Output:
    if not input_data.found or cache_client is None:
        return Schema__Html_From_Cache__Extract__Output(namespace  = input_data.namespace,
                                                        cache_id   = input_data.cache_id ,
                                                        found      = False               ,
                                                        entry_data = None                )

    entry_data = cache_client.entry__retrieve(namespace = input_data.namespace,
                                              cache_id  = input_data.cache_id )

    return Schema__Html_From_Cache__Extract__Output(namespace  = input_data.namespace,
                                                    cache_id   = input_data.cache_id ,
                                                    found      = entry_data is not None,
                                                    entry_data = entry_data          )


@task()
@type_safe
def action__html_from_cache__transform(input_data: Schema__Html_From_Cache__Extract__Output
                                  ) -> Schema__Html_From_Cache__Transform__Output:
    if not input_data.found or input_data.entry_data is None:
        return Schema__Html_From_Cache__Transform__Output(html       = Safe_Str__Html('')      ,
                                                          html_hash  = Safe_Str__Cache_Hash(''),
                                                          found      = False                   ,
                                                          char_count = 0                       )

    entry = input_data.entry_data
    html_str   = entry.get('html', '')
    html_hash  = entry.get('cache_hash', '')
    char_count = entry.get('char_count', len(html_str))

    return Schema__Html_From_Cache__Transform__Output(html       = Safe_Str__Html(html_str)       ,
                                                      html_hash  = Safe_Str__Cache_Hash(html_hash),
                                                      found      = True                           ,
                                                      char_count = char_count                     )


@task()
@type_safe
def action__html_from_cache__save(input_data: Schema__Html_From_Cache__Transform__Output,
                                  cache_id  : Cache_Id = None
                             ) -> Schema__Html_From_Cache__Save__Output:
    return Schema__Html_From_Cache__Save__Output(success   = input_data.found    ,
                                                 html      = input_data.html     ,
                                                 html_hash = input_data.html_hash,
                                                 cache_id  = cache_id            ,
                                                 found     = input_data.found    )


# ═══════════════════════════════════════════════════════════════════════════════
# FLeT Implementation
# ═══════════════════════════════════════════════════════════════════════════════

class FLeT__Html__From__Cache(Html_FLeT__Base):                                      # Retrieve HTML from cache

    cache_client : Html_Cache__Client = None                                         # Cache client for retrieval

    load      = action__html_from_cache__load
    extract   = action__html_from_cache__extract
    transform = action__html_from_cache__transform
    save      = action__html_from_cache__save

    def setup(self) -> 'FLeT__Html__From__Cache':
        self.config = Schema__FLeT__Config(name        = Safe_Str__FLeT__Name('html-from-cache')    ,
                                           description = 'Retrieve HTML from cache by hash, URL, or key')
        return self

    def run_pipeline(self                                            ,                # Override to inject cache_client
                     input_data: Schema__Html_From_Cache__Load__Input
                ) -> Schema__Html_From_Cache__Save__Output:
        cls = type(self)
        load_output      = cls.load     (input_data, cache_client=self.cache_client)
        extract_output   = cls.extract  (load_output, cache_client=self.cache_client)
        transform_output = cls.transform(extract_output)
        save_output      = cls.save     (transform_output, cache_id=load_output.cache_id)
        return save_output

    # ═══════════════════════════════════════════════════════════════════════════
    # Convenience Methods
    # ═══════════════════════════════════════════════════════════════════════════

    @classmethod
    def by_hash(cls                                ,
                html_hash   : str                  ,
                cache_client: Html_Cache__Client   ,
                namespace   : str = 'html-cache'
           ) -> Schema__Html_From_Cache__Save__Output:
        flet = cls(cache_client=cache_client).setup()
        input_data = Schema__Html_From_Cache__Load__Input(namespace = Safe_Str__Namespace(namespace)  ,
                                                          html_hash = Safe_Str__Cache_Hash(html_hash))
        flet.print_obj()
        return flet.execute(input_data)

    @classmethod
    def by_url(cls                                ,
               url         : str                  ,
               cache_client: Html_Cache__Client   ,
               namespace   : str = 'html-cache'
          ) -> Schema__Html_From_Cache__Save__Output:
        flet = cls(cache_client=cache_client).setup()
        input_data = Schema__Html_From_Cache__Load__Input(namespace = Safe_Str__Namespace(namespace),
                                                          url       = url                          )
        return flet.execute(input_data)

    @classmethod
    def by_cache_id(cls                                ,
                    cache_id    : str                  ,
                    cache_client: Html_Cache__Client   ,
                    namespace   : str = 'html-cache'
               ) -> Schema__Html_From_Cache__Save__Output:
        flet = cls(cache_client=cache_client).setup()
        input_data = Schema__Html_From_Cache__Load__Input(namespace = Safe_Str__Namespace(namespace),
                                                          cache_id  = Cache_Id(cache_id)           )
        return flet.execute(input_data)
