# ═══════════════════════════════════════════════════════════════════════════════
# Html_FLeT__Base - Base class for all FLeT transformations
# Uses Flow/Task system for execution with method-based action wiring
# ═══════════════════════════════════════════════════════════════════════════════

from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Document                                        import Html_Cache__Document
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.base.Html_FLeT__Flow                                   import Html_FLeT__Flow
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.schemas.Schema__FLeT__Config                           import Schema__FLeT__Config
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.schemas.flet_extract.Schema__FLeT__Extract__Output     import Schema__FLeT__Extract__Output
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.schemas.flet_load.Schema__FLeT__Load__Input            import Schema__FLeT__Load__Input
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.schemas.flet_load.Schema__FLeT__Load__Output           import Schema__FLeT__Load__Output
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.schemas.flet_save.Schema__FLeT__Save__Output           import Schema__FLeT__Save__Output
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.schemas.flet_transform.Schema__FLeT__Transform__Output import Schema__FLeT__Transform__Output
from osbot_utils.type_safe.Type_Safe                                                                                import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                                      import type_safe


class Html_FLeT__Base(Type_Safe):                                                         # Base class with method-based action wiring

    # Configuration
    config   : Schema__FLeT__Config       = None                                          # Step configuration (set in setup)
    document : Html_Cache__Document       = None                                          # Html_Cache__Document for storage

    # Execution state (available after execute)
    flow     : Html_FLeT__Flow            = None                                          # Flow instance for observability
    output   : Schema__FLeT__Save__Output = None                                          # Final output

    # ═══════════════════════════════════════════════════════════════════════════
    # Actions - override in subclasses
    # ═══════════════════════════════════════════════════════════════════════════

    @staticmethod
    def load(input_data: Schema__FLeT__Load__Input) -> Schema__FLeT__Load__Output:
        raise NotImplementedError()

    @staticmethod
    def extract(input_data: Schema__FLeT__Load__Output) -> Schema__FLeT__Extract__Output:
        raise NotImplementedError()

    @staticmethod
    def transform(input_data: Schema__FLeT__Extract__Output) -> Schema__FLeT__Transform__Output:
        raise NotImplementedError()

    @staticmethod
    def save(input_data: Schema__FLeT__Transform__Output) -> Schema__FLeT__Save__Output:
        raise NotImplementedError()

    def setup(self) -> 'Html_FLeT__Base':                                                 # Initialize configuration
        raise NotImplementedError("Subclasses must implement setup()")

    # ═══════════════════════════════════════════════════════════════════════════
    # Execution
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def execute(self, input_data: Schema__FLeT__Load__Input) -> Schema__FLeT__Save__Output:
        with Html_FLeT__Flow() as flow:
            self.flow     = flow
            flow.document = self.document
            flow.config   = self.config

            flow.setup(self.run_pipeline, input_data)
            flow.execute()

            self.output = flow.flow_return_value
            return self.output

    def run_pipeline(self                                   ,                             # Execute L-E-T-S sequence
                     input_data: Schema__FLeT__Load__Input
                ) -> Schema__FLeT__Save__Output:
        cls = type(self)                                                # Get actual class for static method calls
        load_output      = cls.load      (input_data)
        extract_output   = cls.extract   (load_output)
        transform_output = cls.transform (extract_output)
        save_output      = cls.save      (transform_output)
        return save_output

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

    def flow_data(self) -> dict:                                                          # Get flow execution data
        if self.flow:
            return self.flow.json()
        return {}