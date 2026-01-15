# ═══════════════════════════════════════════════════════════════════════════════
# Html_LETS__Html__From__Raw - LETS for receiving raw HTML input
# This is typically the first LETS in a pipeline
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                   import type_safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html        import Safe_Str__Html
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.base.Html_LETS__Base                      import Html_LETS__Base
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.Schema__LETS__Config              import Schema__LETS__Config
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.Schema__LETS__Input               import Schema__LETS__Load__Input
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.Schema__LETS__Input               import Schema__LETS__Transform__Input
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.Schema__LETS__Input               import Schema__LETS__Save__Input
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.Schema__LETS__Output              import Schema__LETS__Load__Output
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.Schema__LETS__Output              import Schema__LETS__Transform__Output
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.Schema__LETS__Output              import Schema__LETS__Save__Output
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.safe_str.Safe_Str__LETS__Name             import Safe_Str__LETS__Name


# ═══════════════════════════════════════════════════════════════════════════════
# LETS-Specific Input/Output Schemas
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__Html_From_Raw__Load__Input(Schema__LETS__Load__Input):             # Load input for raw HTML
    html : Safe_Str__Html                                                        # Raw HTML content


class Schema__Html_From_Raw__Load__Output(Schema__LETS__Load__Output):           # Load output
    html : Safe_Str__Html                                                        # Loaded HTML


class Schema__Html_From_Raw__Transform__Input(Schema__LETS__Transform__Input):   # Transform input
    html : Safe_Str__Html                                                        # HTML to process


class Schema__Html_From_Raw__Transform__Output(Schema__LETS__Transform__Output): # Transform output
    html : Safe_Str__Html                                                        # Processed HTML


class Schema__Html_From_Raw__Save__Input(Schema__LETS__Save__Input):             # Save input
    html : Safe_Str__Html                                                        # HTML to save


# ═══════════════════════════════════════════════════════════════════════════════
# LETS Implementation
# ═══════════════════════════════════════════════════════════════════════════════

class Html_LETS__Html__From__Raw(Html_LETS__Base):                               # Raw HTML input LETS
    config : Schema__LETS__Config = None                                         # Will be set in setup

    def setup(self) -> 'Html_LETS__Html__From__Raw':                             # Initialize config
        self.config = Schema__LETS__Config(name        = Safe_Str__LETS__Name('html-from-raw'),
                                           description = 'Load raw HTML from input context'   )
        return self

    @type_safe
    def load(self                                            ,                   # Load raw HTML from input
             load_input: Schema__Html_From_Raw__Load__Input
        ) -> Schema__Html_From_Raw__Load__Output:
        return Schema__Html_From_Raw__Load__Output(html = load_input.html)

    @type_safe
    def transform(self                                                 ,         # Pass through (no transform)
                  transform_input: Schema__Html_From_Raw__Transform__Input
             ) -> Schema__Html_From_Raw__Transform__Output:
        return Schema__Html_From_Raw__Transform__Output(html = transform_input.html)

    @type_safe
    def save(self                                          ,                     # Prepare for save
             save_input: Schema__Html_From_Raw__Save__Input
        ) -> Schema__LETS__Save__Output:
        return Schema__LETS__Save__Output(success = True)
