from osbot_utils.type_safe.Type_Safe                                              import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html         import Safe_Str__Html


class Schema__FLeT__Transform__Input(Type_Safe):                                     # Base input for Transform phase
    html : Safe_Str__Html = ''                                                       # HTML from Extract phase
