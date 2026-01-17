from osbot_utils.type_safe.Type_Safe                                              import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html         import Safe_Str__Html


class Schema__FLeT__Extract__Output(Type_Safe):                                      # Base output from Extract phase
    html : Safe_Str__Html = ''                                                       # Extracted HTML
