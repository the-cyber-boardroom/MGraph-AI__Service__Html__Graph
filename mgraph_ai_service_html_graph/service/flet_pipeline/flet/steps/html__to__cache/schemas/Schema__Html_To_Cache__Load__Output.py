from mgraph_ai_service_html_graph.service.flet_pipeline.flet.schemas.flet_load.Schema__FLeT__Load__Output import Schema__FLeT__Load__Output
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html                             import Safe_Str__Html
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Namespace                import Safe_Str__Namespace


class Schema__Html_To_Cache__Load__Output(Schema__FLeT__Load__Output):                  # Output from load phase
    html      : Safe_Str__Html                                                          # HTML content
    namespace : Safe_Str__Namespace                                                     # Namespace for storage
    cache_key : Safe_Str__File__Path                                                    # Cache key to use
