# ═══════════════════════════════════════════════════════════════════════════════
# FLeT__Html__From__Cache - Load HTML content from cache
# Single responsibility: retrieve HTML from the document's data layer
#
# What this FLeT does:
#   - Retrieves HTML from cache data layer at specified data_key
#
# What this FLeT does NOT do (moved to orchestrator):
#   - Entity lookup (cache_id must be provided)
#   - cache_key → cache_id resolution
#   - cache_hash lookup
# ═══════════════════════════════════════════════════════════════════════════════

from mgraph_ai_service_html_graph.service.flet_pipeline.flet.base.Html_FLeT__Base                                            import Html_FLeT__Base
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.schemas.Schema__FLeT__Config                                    import Schema__FLeT__Config
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.schemas.Schema__FLeT__Execution__Result                         import Schema__FLeT__Execution__Result
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.schemas.safe_str.Safe_Str__FLeT__Name                           import Safe_Str__FLeT__Name
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__from__cache.actions.action__html_from_cache__load   import action__html_from_cache__load
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__from__cache.schemas.Schema__Html_From_Cache__Input  import Schema__Html_From_Cache__Input
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__from__cache.schemas.Schema__Html_From_Cache__Output import Schema__Html_From_Cache__Output
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                                               import type_safe


class FLeT__Html__From__Cache(Html_FLeT__Base):                                           # Load HTML from cache

    def setup(self) -> 'FLeT__Html__From__Cache':                                         # Initialize configuration
        self.config = Schema__FLeT__Config(name        = Safe_Str__FLeT__Name('html-from-cache'),
                                           description = 'Load HTML content from cache data layer')
        return self

    def run_actions(self                                           ,                      # Execute single load action
                    input_data: Schema__Html_From_Cache__Input
               ) -> Schema__Html_From_Cache__Output:
        return action__html_from_cache__load(input_data   = input_data       ,
                                             cache_client = self.cache_client,
                                             cache_id     = self.cache_id    ,
                                             namespace    = self.namespace   )

    @type_safe
    def execute(self                                               ,                      # Type-safe execute override
                input_data: Schema__Html_From_Cache__Input
           ) -> Schema__FLeT__Execution__Result:
        return super().execute(input_data=input_data)