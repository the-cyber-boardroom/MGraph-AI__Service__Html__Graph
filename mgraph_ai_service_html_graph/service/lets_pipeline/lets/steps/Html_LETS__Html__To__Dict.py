# ═══════════════════════════════════════════════════════════════════════════════
# Html_LETS__Html__To__Dict - LETS for converting HTML to dictionary
# Parses HTML and creates a structured dictionary with node IDs
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                                         import Dict, Any
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.colections.Schema__Html_Dict                   import Schema__Html_Dict
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_load.Schema__LETS__Load__Input            import Schema__LETS__Load__Input
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_load.Schema__LETS__Load__Output           import Schema__LETS__Load__Output
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_save.Schema__LETS__Save__Input            import Schema__LETS__Save__Input
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_save.Schema__LETS__Save__Output           import Schema__LETS__Save__Output
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_transform.Schema__LETS__Transform__Input  import Schema__LETS__Transform__Input
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_transform.Schema__LETS__Transform__Output import Schema__LETS__Transform__Output
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.safe_str.Safe_Str__LETS__Name                  import Safe_Str__LETS__Name
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                                      import type_safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html                                           import Safe_Str__Html
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.base.Html_LETS__Base                                   import Html_LETS__Base
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.Schema__LETS__Config                           import Schema__LETS__Config




# ═══════════════════════════════════════════════════════════════════════════════
# LETS-Specific Input/Output Schemas
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__Html_To_Dict__Load__Input(Schema__LETS__Load__Input):              # Load input
    html : Safe_Str__Html                                                        # HTML to parse


class Schema__Html_To_Dict__Load__Output(Schema__LETS__Load__Output):            # Load output
    html : Safe_Str__Html                                                        # Loaded HTML


class Schema__Html_To_Dict__Transform__Input(Schema__LETS__Transform__Input):    # Transform input
    html : Safe_Str__Html                                                        # HTML to convert


class Schema__Html_To_Dict__Transform__Output(Schema__LETS__Transform__Output):  # Transform output
    html_dict : Schema__Html_Dict                                                # Parsed dictionary


class Schema__Html_To_Dict__Save__Input(Schema__LETS__Save__Input):              # Save input
    html_dict : Schema__Html_Dict                                                # Dict to save


# ═══════════════════════════════════════════════════════════════════════════════
# LETS Implementation
# ═══════════════════════════════════════════════════════════════════════════════

class Html_LETS__Html__To__Dict(Html_LETS__Base):                                # HTML to Dict LETS
    config : Schema__LETS__Config = None                                         # Will be set in setup

    def setup(self) -> 'Html_LETS__Html__To__Dict':                              # Initialize config
        self.config = Schema__LETS__Config(name        = Safe_Str__LETS__Name('html-to-dict')      ,
                                           description = 'Parse HTML into dictionary with node IDs')
        return self

    @type_safe
    def load(self                                           ,                    # Load HTML
             load_input: Schema__Html_To_Dict__Load__Input
        ) -> Schema__Html_To_Dict__Load__Output:
        return Schema__Html_To_Dict__Load__Output(html = load_input.html)

    @type_safe
    def transform(self                                                ,          # Convert to dict
                  transform_input: Schema__Html_To_Dict__Transform__Input
             ) -> Schema__Html_To_Dict__Transform__Output:
        # Placeholder - actual implementation would use Html__To__Html_Dict
        html_dict_data = self.parse_html_to_dict(transform_input.html)
        html_dict      = Schema__Html_Dict(html_dict = html_dict_data)
        return Schema__Html_To_Dict__Transform__Output(html_dict = html_dict)

    @type_safe
    def save(self                                         ,                      # Prepare for save
             save_input: Schema__Html_To_Dict__Save__Input
        ) -> Schema__LETS__Save__Output:
        return Schema__LETS__Save__Output(success = True)

    # ═══════════════════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def parse_html_to_dict(self, html: Safe_Str__Html) -> Dict[str, Any]:        # Parse HTML to dict
        # Placeholder implementation
        # In real code, this would call Html__To__Html_Dict from the html-graph service
        return {'tag'     : 'html'     ,
                'children': []         ,
                'node_id' : 'root-node'}
