from osbot_utils.type_safe.primitives.core.Safe_UInt                                        import Safe_UInt
from osbot_utils.type_safe.primitives.domains.http.safe_str.Safe_Str__Http__Content_Type    import Safe_Str__Http__Content_Type
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url                    import Safe_Str__Url
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html                   import Safe_Str__Html
from osbot_utils.type_safe.Type_Safe                                                        import Type_Safe


class Schema__Html__From_Url__Response(Type_Safe):                                                # Response schema for fetched HTML
    html          : Safe_Str__Html                                                                # The fetched HTML content
    url           : Safe_Str__Url                                                                 # The URL that was fetched
    content_type  : Safe_Str__Http__Content_Type                                                  # Content-Type header from response
    status_code   : Safe_UInt  = 200                                                              # HTTP status code