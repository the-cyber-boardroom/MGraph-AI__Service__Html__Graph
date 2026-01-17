from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path                                                 import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html                                                         import Safe_Str__Html
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Namespace                                            import Safe_Str__Namespace
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url                                                          import Safe_Str__Url
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.schemas.flet_load.Schema__FLeT__Load__Input                          import Schema__FLeT__Load__Input
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__from__cache.schemas.Schema__Html_From_Cache__Load__Input import DEFAULT__HTML_FROM_CACHE__NAMESPACE



class Schema__Html_To_Cache__Load__Input(Schema__FLeT__Load__Input):                 # Input for HTML to cache
    html      : Safe_Str__Html
    namespace : Safe_Str__Namespace  = 'html-cache'                                  # Cache namespace
    cache_key : Safe_Str__File__Path = DEFAULT__HTML_FROM_CACHE__NAMESPACE           # Optional: explicit cache key (uses hash if empty)
    url       : Safe_Str__Url        = None                                          # Optional: source URL (can be used as cache key)
