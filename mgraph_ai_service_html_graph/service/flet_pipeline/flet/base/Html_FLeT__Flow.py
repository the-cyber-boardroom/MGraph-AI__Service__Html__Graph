# ═══════════════════════════════════════════════════════════════════════════════
# Html_FLeT__Flow - Extended Flow with FLeT-specific typed dependencies
# Provides type-safe dependency injection for FLeT actions via task_dependencies()
# ═══════════════════════════════════════════════════════════════════════════════

from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Document              import Html_Cache__Document
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.schemas.Schema__FLeT__Config import Schema__FLeT__Config
from osbot_utils.helpers.flows.Flow                                                       import Flow


class Html_FLeT__Flow(Flow):                                                              # Flow extended with FLeT typed attributes
    document : Html_Cache__Document = None                                                # Html_Cache__Document for storage
    config   : Schema__FLeT__Config = None                                                # Schema__FLeT__Config for step config

    def task_dependencies(self) -> dict:                                                  # Provide dependencies for task injection
        return { 'document': self.document ,
                 'config'  : self.config   }