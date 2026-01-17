from mgraph_ai_service_html_graph.service.flet_pipeline.flet.schemas.flet_save.Schema__FLeT__Save__Output import Schema__FLeT__Save__Output
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html                                 import Safe_Str__Html
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Cache_Hash                  import Safe_Str__Cache_Hash
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                                        import Cache_Id

class Schema__Html_From_Cache__Save__Output(Schema__FLeT__Save__Output):            # Output from save phase (passthrough)
    success    : bool                                                               # Whether retrieval succeeded
    html       : Safe_Str__Html                                                     # Retrieved HTML content
    html_hash  : Safe_Str__Cache_Hash                                               # Hash of HTML
    cache_id   : Cache_Id                                                           # Cache entry ID
    found      : bool                                                               # Whether entry was found
