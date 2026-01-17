from mgraph_ai_service_html_graph.service.flet_pipeline.flet.schemas.flet_load.Schema__FLeT__Load__Input import Schema__FLeT__Load__Input
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Cache_Hash                 import Safe_Str__Cache_Hash
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path                        import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                                       import Cache_Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Namespace                   import Safe_Str__Namespace
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url                                 import Safe_Str__Url

DEFAULT__HTML_FROM_CACHE__NAMESPACE = 'html-cache'

class Schema__Html_From_Cache__Load__Input(Schema__FLeT__Load__Input):                               # Input for cache lookup
    namespace  : Safe_Str__Namespace  = DEFAULT__HTML_FROM_CACHE__NAMESPACE          # Cache namespace
    cache_id   : Cache_Id             = None                                         # Direct cache ID lookup
    cache_key  : Safe_Str__File__Path = ''                                           # Cache key lookup
    html_hash  : Safe_Str__Cache_Hash = ''                                           # Hash-based lookup
    url        : Safe_Str__Url        = ''                                           # URL-based lookup (hashed)
