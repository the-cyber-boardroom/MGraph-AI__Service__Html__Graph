# ═══════════════════════════════════════════════════════════════════════════════
# Html_Graph__Service__Client__Config
# Configuration schema for Html Graph service client (supports IN_MEMORY and REMOTE)
# ═══════════════════════════════════════════════════════════════════════════════

from fastapi                                                                                        import FastAPI
from mgraph_ai_service_cache_client.schemas.cache.safe_str.Safe_Str__Cache__Namespace               import Safe_Str__Cache__Namespace
from osbot_fast_api.services.schemas.registry.enums.Enum__Fast_API__Service__Registry__Client__Mode import Enum__Fast_API__Service__Registry__Client__Mode
from osbot_utils.type_safe.Type_Safe                                                                import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Float                                               import Safe_Float
from osbot_utils.type_safe.primitives.domains.http.safe_str.Safe_Str__Http__Header__Name            import Safe_Str__Http__Header__Name
from osbot_utils.type_safe.primitives.domains.http.safe_str.Safe_Str__Http__Header__Value           import Safe_Str__Http__Header__Value
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url                            import Safe_Str__Url
from mgraph_ai_service_html_graph.schemas.client.consts__html_graph_client                          import DEFAULT__HTML_GRAPH__NAMESPACE, DEFAULT__HTML_GRAPH__TIMEOUT

# todo: see if mode should not be None
class Html_Graph__Service__Client__Config(Type_Safe):                                                                           # Config for Html Graph client
    mode           : Enum__Fast_API__Service__Registry__Client__Mode = Enum__Fast_API__Service__Registry__Client__Mode.REMOTE   # Client mode (IN_MEMORY or REMOTE)
    base_url       : Safe_Str__Url                                                                                              # Base URL for remote service
    fast_api_app   : FastAPI                       = None                                                                       # FastAPI app for IN_MEMORY mode
    api_key_header : Safe_Str__Http__Header__Name                                                                               # API key header name
    api_key        : Safe_Str__Http__Header__Value                                                                              # API key value
    timeout        : Safe_Float                    = DEFAULT__HTML_GRAPH__TIMEOUT                                               # Request timeout in seconds
    namespace      : Safe_Str__Cache__Namespace    = DEFAULT__HTML_GRAPH__NAMESPACE                                             # Cache namespace
