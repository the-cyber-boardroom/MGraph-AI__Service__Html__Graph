from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html       import Safe_Str__Html


class Schema__LETS__Save__Input(Type_Safe):                                      # Save phase input
    html  : Safe_Str__Html = None                                                # Content to save
    stats : dict           = None                                                # Optional statistics
