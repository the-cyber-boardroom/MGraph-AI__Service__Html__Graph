# ═══════════════════════════════════════════════════════════════════════════════
# Html_LETS__Base - Base class for all LETS transformations
# Defines the Load → Extract → Transform → Save pattern
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                                        import Type_Safe
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.Schema__LETS__Config   import Schema__LETS__Config
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.Schema__LETS__Input    import Schema__LETS__Load__Input
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.Schema__LETS__Input    import Schema__LETS__Extract__Input
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.Schema__LETS__Input    import Schema__LETS__Transform__Input
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.Schema__LETS__Input    import Schema__LETS__Save__Input
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.Schema__LETS__Output   import Schema__LETS__Load__Output
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.Schema__LETS__Output   import Schema__LETS__Extract__Output
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.Schema__LETS__Output   import Schema__LETS__Transform__Output
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.Schema__LETS__Output   import Schema__LETS__Save__Output


class Html_LETS__Base(Type_Safe):                                                # Base LETS transformation
    config : Schema__LETS__Config                                                # LETS configuration

    # ═══════════════════════════════════════════════════════════════════════════
    # The 4 LETS Phases - Override in subclasses
    # ═══════════════════════════════════════════════════════════════════════════

    def load(self                                   ,                            # Load input data
             load_input: Schema__LETS__Load__Input
        ) -> Schema__LETS__Load__Output:
        raise NotImplementedError

    def extract(self                                      ,                      # Extract relevant data
                extract_input: Schema__LETS__Extract__Input
           ) -> Schema__LETS__Extract__Output:
        raise NotImplementedError

    def transform(self                                        ,                  # Transform the data
                  transform_input: Schema__LETS__Transform__Input
             ) -> Schema__LETS__Transform__Output:
        raise NotImplementedError

    def save(self                                 ,                              # Save output
             save_input: Schema__LETS__Save__Input
        ) -> Schema__LETS__Save__Output:
        raise NotImplementedError

    def setup(self) -> 'Html_LETS__Base':
        raise NotImplementedError
