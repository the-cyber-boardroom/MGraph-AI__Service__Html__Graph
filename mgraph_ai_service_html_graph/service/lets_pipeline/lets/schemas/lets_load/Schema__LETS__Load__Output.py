from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html       import Safe_Str__Html

class Schema__LETS__Load__Output(Type_Safe):                                     # Load phase output
    html : Safe_Str__Html = None                                                 # Loaded content
