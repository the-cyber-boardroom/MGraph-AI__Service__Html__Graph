# ═══════════════════════════════════════════════════════════════════════════════
# Html_FLeT__Base - Base class for all FLeT transformations
# Uses Flow/Task system for execution with flexible action composition
#
# Key design principles:
# - FLeTs operate WITHIN an already-established entity (cache_id provided)
# - FLeTs handle Tier 2 (data operations) only, NOT entity creation
# - Actions can be as few as one - no mandatory L-E-T-S pattern
# - Each action receives only the data it needs
# ═══════════════════════════════════════════════════════════════════════════════
from mgraph_ai_service_cache_client.client.client_entities.Cache__Entity                             import Cache__Entity
from mgraph_ai_service_cache_client.client.client_entities.Cache__Entity__Json_File                  import Cache__Entity__Json_File
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Client                           import Html_Cache__Client
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.base.Html_FLeT__Flow                    import Html_FLeT__Flow
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.schemas.Schema__FLeT__Config            import Schema__FLeT__Config
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.schemas.Schema__FLeT__Execution__Result import Schema__FLeT__Execution__Result
from osbot_utils.decorators.methods.cache_on_self                                                    import cache_on_self
from osbot_utils.helpers.duration.decorators.capture_duration                                        import capture_duration
from osbot_utils.type_safe.Type_Safe                                                                 import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                                   import Cache_Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Namespace               import Safe_Str__Namespace
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                       import type_safe

DEFAULT__FLET__DATA_FILE__FOLDER   = 'flows'
DEFAULT__FLET__DATA_FILE__FILE_ID  = 'flow-data'

# todo: see if the cache_id and namespace should not be moved into the Schema__FLeT__Config class
class Html_FLeT__Base(Type_Safe):                                                         # Base class for FLeT operations

    # Configuration (set during construction or setup)
    config       : Schema__FLeT__Config = None                                            # FLeT configuration
    cache_client : Html_Cache__Client   = None                                            # Cache client for storage
    cache_id     : Cache_Id             = None                                            # Entity cache_id (from orchestrator)
    namespace    : Safe_Str__Namespace  = None                                            # Namespace for cache operations

    # Execution state (available after execute)
    flow         : Html_FLeT__Flow      = None                                            # Flow instance for observability
    flow_output  : Type_Safe            = None                                            # Final output (FLeT-specific type)

    # ═══════════════════════════════════════════════════════════════════════════
    # Setup - must be implemented by subclasses
    # ═══════════════════════════════════════════════════════════════════════════

    def setup(self) -> 'Html_FLeT__Base':                                                 # Initialize configuration
        raise NotImplementedError("Subclasses must implement setup()")

    # ═══════════════════════════════════════════════════════════════════════════
    # Actions - must be implemented by subclasses
    # ═══════════════════════════════════════════════════════════════════════════

    def run_actions(self, input_data: Type_Safe) -> Type_Safe:                            # Execute FLeT-specific actions
        raise NotImplementedError("Subclasses must implement run_actions()")

    # ═══════════════════════════════════════════════════════════════════════════
    # Execution
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def execute(self, input_data: Type_Safe) -> Schema__FLeT__Execution__Result:                                # Execute FLeT within Flow context
        with capture_duration() as duration:
            with Html_FLeT__Flow() as flow:
                self.flow          = flow
                flow.cache_client  = self.cache_client
                flow.cache_id      = self.cache_id
                flow.namespace     = self.namespace
                flow.config        = self.config

                try:
                    flow.setup(self.run_actions, input_data)
                    flow.execute()

                    self.flow_output = flow.flow_return_value
                    success  = True
                    message  = 'Flow executed ok'

                except Exception as error:
                    success  = False
                    message = str(error)

                self.save_flow_data()

            return Schema__FLeT__Execution__Result(success     = success         ,
                                                   message     = message         ,
                                                   duration    = duration.seconds,
                                                   flow_output = self.flow_output)

    def save_flow_data(self):
        if self.cache_client:
            self.flow_data().store(self.flow.json())           # save the flow execution data

    # ═══════════════════════════════════════════════════════════════════════════
    # Entity files
    # ═══════════════════════════════════════════════════════════════════════════

    @cache_on_self
    def cache_entity(self):
        return Cache__Entity(cache_client = self.cache_client.cache_client,
                             cache_id     = self.cache_id                 ,
                             namespace    = self.namespace                )

    @cache_on_self
    def flow_data(self) -> Cache__Entity__Json_File:
        data_key     = f'{DEFAULT__FLET__DATA_FILE__FOLDER}/{self.config.name}'
        data_file_id = DEFAULT__FLET__DATA_FILE__FILE_ID
        return Cache__Entity__Json_File(cache_client = self.cache_client.cache_client,
                                        cache_id     = self.cache_id                 ,
                                        namespace    = self.namespace                ,
                                        data_key     = data_key                      ,
                                        data_file_id = data_file_id                  )

    # ═══════════════════════════════════════════════════════════════════════════
    # Observability (available after execute)
    # ═══════════════════════════════════════════════════════════════════════════

    def durations(self) -> dict:                                                          # Get timing for all actions
        if self.flow:
            return self.flow.durations()
        return {}

    def captured_logs(self) -> list:                                                      # Get captured log messages
        if self.flow:
            return self.flow.captured_logs()
        return []
