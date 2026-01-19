# ═══════════════════════════════════════════════════════════════════════════════
# FLeT__Html__To__Cache - Save HTML content to cache
# Single responsibility: take HTML and save it to the document's data layer
#
# What this FLeT does:
#   - Receives HTML content
#   - Saves it to cache data layer under specified data_key
#
# What this FLeT does NOT do (moved to orchestrator):
#   - Entity creation (cache_id must be provided)
#   - cache_key resolution
#   - cache_hash computation
#   - Deduplication checks
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                                           import type_safe
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.base.Html_FLeT__Base                                        import Html_FLeT__Base
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.schemas.Schema__FLeT__Config                                import Schema__FLeT__Config
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.schemas.Schema__FLeT__Execution__Result                     import Schema__FLeT__Execution__Result
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__to__cache.actions.action__html_to_cache__save   import action__html_to_cache__save
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__to__cache.schemas.Schema__Html_To_Cache__Input  import Schema__Html_To_Cache__Input
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__to__cache.schemas.Schema__Html_To_Cache__Output import Schema__Html_To_Cache__Output



class FLeT__Html__To__Cache(Html_FLeT__Base):                                             # Save HTML to cache

    def setup(self) -> 'FLeT__Html__To__Cache':                                           # Initialize configuration
        self.config = Schema__FLeT__Config(name        = 'html-to-cache'                        ,
                                           description = 'Save HTML content to cache data layer')
        return self

    def run_actions(self                                          ,                       # Execute single save action
                    input_data: Schema__Html_To_Cache__Input
               ) -> Schema__Html_To_Cache__Output:
        return action__html_to_cache__save(input_data   = input_data       ,
                                           cache_client = self.cache_client,
                                           cache_id     = self.cache_id    ,
                                           namespace    = self.namespace   )

    @type_safe
    def execute(self                                              ,                       # Type-safe execute override
                input_data: Schema__Html_To_Cache__Input
           ) -> Schema__FLeT__Execution__Result:

        return super().execute(input_data=input_data)
