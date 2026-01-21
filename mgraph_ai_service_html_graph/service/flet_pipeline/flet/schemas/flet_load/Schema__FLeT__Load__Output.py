from osbot_utils.type_safe.Type_Safe                                              import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html         import Safe_Str__Html


class Schema__FLeT__Load__Output(Type_Safe):                                         # Base output from Load phase
    html : Safe_Str__Html = ''                                                       # Loaded HTML content
