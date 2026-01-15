# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Cache__Document__Find_Or_Create__Request - Request to find or create doc
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                                         import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html                    import Safe_Str__Html
from mgraph_ai_service_html_graph.service.cache_storage.safe_str.Safe_Str__Cache_Key         import Safe_Str__Cache_Key


class Schema__Cache__Document__Find_Or_Create__Request(Type_Safe):               # Find or create request
    cache_key : Safe_Str__Cache_Key                                              # Semantic path
    html      : Safe_Str__Html = None                                            # Optional raw HTML to store
