# ═══════════════════════════════════════════════════════════════════════════════
# Schema__LETS__Input - Base input schema for LETS transformations
# All LETS-specific input schemas should inherit from this
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html       import Safe_Str__Html


class Schema__LETS__Input(Type_Safe):                                            # Base LETS input schema
    html : Safe_Str__Html = None                                                 # HTML content
