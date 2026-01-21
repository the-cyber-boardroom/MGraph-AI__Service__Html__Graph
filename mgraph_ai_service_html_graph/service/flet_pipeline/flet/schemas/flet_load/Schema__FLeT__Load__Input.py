from osbot_utils.type_safe.Type_Safe                                              import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html         import Safe_Str__Html


# todo: review why we have html here, this is not usable in all FLeT steps
class Schema__FLeT__Load__Input(Type_Safe):                                          # Base input for Load phase
    html : Safe_Str__Html = ''                                                       # HTML content to process
