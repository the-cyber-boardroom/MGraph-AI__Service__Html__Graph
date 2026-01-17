from mgraph_ai_service_html_graph.service.flet_pipeline.flet.schemas.flet_save.Schema__FLeT__Save__Output import Schema__FLeT__Save__Output
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Cache_Hash                  import Safe_Str__Cache_Hash
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path                         import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                                        import Cache_Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Namespace                    import Safe_Str__Namespace


class Schema__Html_To_Cache__Save__Output(Schema__FLeT__Save__Output):                      # Output from save phase
    success    : bool                                                                       # Whether save succeeded
    cache_id   : Cache_Id                                                                   # Cache entry ID
    html_hash  : Safe_Str__Cache_Hash                                                       # Hash of saved HTML
    cache_key  : Safe_Str__File__Path                                                       # Key used in cache
    namespace  : Safe_Str__Namespace                                                        # Namespace used
    from_cache : bool                                                                       # True if already existed
