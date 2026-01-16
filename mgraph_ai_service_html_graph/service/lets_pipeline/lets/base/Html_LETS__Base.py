# ═══════════════════════════════════════════════════════════════════════════════
# Html_LETS__Base - Base class for all LETS transformations
# Uses Flow/Task system for execution with declarative action wiring
# ═══════════════════════════════════════════════════════════════════════════════
from typing import Callable

from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Document import Html_Cache__Document
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.base.Html_LETS__Flow                         import Html_LETS__Flow
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.Schema__LETS__Config                 import Schema__LETS__Config
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_extract.Schema__LETS__Extract__Output import Schema__LETS__Extract__Output
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_load.Schema__LETS__Load__Input import Schema__LETS__Load__Input
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_load.Schema__LETS__Load__Output import Schema__LETS__Load__Output
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_save.Schema__LETS__Save__Output import Schema__LETS__Save__Output
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_transform.Schema__LETS__Transform__Output import Schema__LETS__Transform__Output
from osbot_utils.type_safe.Type_Safe                                                                      import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                            import type_safe


class Html_LETS__Base(Type_Safe):                                                       # Base class with declarative action wiring

    # Configuration
    config   : Schema__LETS__Config       = None                                        # Step configuration (set in setup)
    document : Html_Cache__Document       = None                                        # Html_Cache__Document for storage

    # Execution state (available after execute)
    flow     : Html_LETS__Flow            = None                                        # Flow instance for observability
    output   : Schema__LETS__Save__Output = None                                        # Final output


    def load(self, input_data: Schema__LETS__Load__Input) -> Schema__LETS__Load__Output:
        raise NotImplementedError()

    def extract(self, input_data: Schema__LETS__Load__Output) -> Schema__LETS__Extract__Output:
        raise NotImplementedError()

    def transform(self, input_data: Schema__LETS__Extract__Output) -> Schema__LETS__Transform__Output:
        raise NotImplementedError()

    def save(self, input_data: Schema__LETS__Transform__Output) -> Schema__LETS__Save__Output:
        raise NotImplementedError()

    def setup(self) -> 'Html_LETS__Base':                                               # Initialize configuration
        raise NotImplementedError("Subclasses must implement setup()")

    @type_safe
    def execute(self, input_data: Schema__LETS__Load__Input) -> Schema__LETS__Save__Output:
        self.validate_actions()

        with Html_LETS__Flow() as flow:
            self.flow     = flow
            flow.document = self.document
            flow.config   = self.config

            flow.setup(self.run_pipeline, input_data)
            flow.execute()

            self.output = flow.flow_return_value
            return self.output

    def validate_actions(self):                                                         # Ensure all L-E-T-S actions are wired
        missing = []
        if self.load      is None: missing.append('load')
        if self.extract   is None: missing.append('extract')
        if self.transform is None: missing.append('transform')
        if self.save      is None: missing.append('save')

        if missing:
            class_name = self.__class__.__name__
            raise ValueError(f"Step {class_name} missing actions: {missing}")

    def run_pipeline(self                                    ,                          # Execute L-E-T-S sequence
                     input_data: Schema__LETS__Load__Input
                ) -> Schema__LETS__Save__Output:
        load_output      = self.load(input_data)
        extract_output   = self.extract(load_output)
        transform_output = self.transform(extract_output)
        save_output      = self.save(transform_output)
        return save_output

    # ═══════════════════════════════════════════════════════════════════════════
    # Observability (available after execute)
    # ═══════════════════════════════════════════════════════════════════════════

    def durations(self) -> dict:                                                        # Get timing for all actions
        if self.flow:
            return self.flow.durations()
        return {}

    def captured_logs(self) -> list:                                                    # Get captured log messages
        if self.flow:
            return self.flow.captured_logs()
        return []

    def flow_data(self) -> dict:                                                        # Get flow execution data
        if self.flow:
            return self.flow.json()
        return {}