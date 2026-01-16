# ═══════════════════════════════════════════════════════════════════════════════
# Html_LETS__Flow - Extended Flow with LETS-specific typed dependencies
# Provides type-safe dependency injection for LETS actions via task_dependencies()
# ═══════════════════════════════════════════════════════════════════════════════
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Document                import Html_Cache__Document
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.Schema__LETS__Config   import Schema__LETS__Config
from osbot_utils.helpers.flows.Flow                                                         import Flow


class Html_LETS__Flow(Flow):                                                            # Flow extended with LETS typed attributes
    document : Html_Cache__Document = None                                              # Html_Cache__Document for storage
    config   : Schema__LETS__Config = None                                              # Schema__LETS__Config for step config

    def task_dependencies(self) -> dict:                                                # Provide dependencies for task injection
        return { 'document': self.document ,
                 'config'  : self.config   }