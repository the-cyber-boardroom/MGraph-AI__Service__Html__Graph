from osbot_utils.type_safe.primitives.domains.http.safe_str.Safe_Str__Http__User_Agent import Safe_Str__Http__User_Agent
from osbot_utils.type_safe.primitives.domains.numerical.safe_int.Safe_Int__Positive    import Safe_Int__Positive
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url               import Safe_Str__Url
from osbot_utils.type_safe.Type_Safe                                                   import Type_Safe


class Schema__Html__From_Url__Request(Type_Safe):                                                 # Request schema for fetching HTML from URL
    url         : Safe_Str__Url               = None                                              # URL to fetch HTML from
    timeout     : Safe_Int__Positive          = 30                                                # Request timeout in seconds
    user_agent  : Safe_Str__Http__User_Agent  = ''                                                # Optional custom user agent