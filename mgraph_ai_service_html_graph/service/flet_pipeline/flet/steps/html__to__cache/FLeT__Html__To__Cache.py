# ═══════════════════════════════════════════════════════════════════════════════
# FLeT__Html__To__Cache - Store HTML in cache service
# Round-trip part 1: HTML → Cache (with hash-based deduplication)
# ═══════════════════════════════════════════════════════════════════════════════
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__to__cache.actions.action__html_to_cache__extract               import action__html_to_cache__extract
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__to__cache.actions.action__html_to_cache__load                  import action__html_to_cache__load
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__to__cache.actions.action__html_to_cache__save                  import action__html_to_cache__save
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__to__cache.actions.action__html_to_cache__transform             import action__html_to_cache__transform
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__to__cache.schemas.Schema__Html_To_Cache__Load__Input           import Schema__Html_To_Cache__Load__Input
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__to__cache.schemas.Schema__Html_To_Cache__Save__Output          import Schema__Html_To_Cache__Save__Output
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html                                                               import Safe_Str__Html
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Namespace                                                  import Safe_Str__Namespace
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.base.Html_FLeT__Base                                                       import Html_FLeT__Base
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.schemas.Schema__FLeT__Config                                               import Schema__FLeT__Config
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.schemas.safe_str.Safe_Str__FLeT__Name                                      import Safe_Str__FLeT__Name
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Client                                                              import Html_Cache__Client
from osbot_utils.type_safe.type_safe_core.decorators.type_safe import type_safe


# ═══════════════════════════════════════════════════════════════════════════════
# FLeT Implementation
# ═══════════════════════════════════════════════════════════════════════════════



    def setup(self) -> 'FLeT__Html__To__Cache':
        self.config = Schema__FLeT__Config(name        = Safe_Str__FLeT__Name('html-to-cache')    ,
                                           description = 'Store HTML in cache with hash-based deduplication')
        return self

    def run_pipeline(self                                          ,                  # Override to inject cache_client
                     input_data: Schema__Html_To_Cache__Load__Input
                ) -> Schema__Html_To_Cache__Save__Output:
        cls = type(self)                    # Get actual class for static method calls
        load_output      = cls.load     (input_data                                      )
        extract_output   = cls.extract  (load_output    , cache_client=self.cache_client )
        transform_output = cls.transform(extract_output , cache_client=self.cache_client )
        save_output      = cls.save     (transform_output, cache_client=self.cache_client)
        return save_output

    # ═══════════════════════════════════════════════════════════════════════════
    # Convenience Methods
    # ═══════════════════════════════════════════════════════════════════════════

    @classmethod
    def from_html(cls                                ,
                  html        : str                  ,
                  cache_client: Html_Cache__Client   ,
                  namespace   : str = 'html-cache'   ,
                  cache_key   : str = ''             ,
                  url         : str = ''
             ) -> Schema__Html_To_Cache__Save__Output:
        flet = cls(cache_client=cache_client).setup()
        input_data = Schema__Html_To_Cache__Load__Input(html      = Safe_Str__Html(html)        ,
                                                        namespace = Safe_Str__Namespace(namespace),
                                                        cache_key = cache_key                   ,
                                                        url       = url                         )
        flet.execute(input_data)
        flet.flow.print_log_messages()
        return flet.flow.flow_return_value

    @type_safe
    def execute(self, input_data: Schema__Html_To_Cache__Load__Input) -> Schema__Html_To_Cache__Save__Output:
        return super().execute(input_data=input_data)
