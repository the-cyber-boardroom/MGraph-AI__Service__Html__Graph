# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Profile__Execute__Request - Request for profile execution
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html       import Safe_Str__Html


class Schema__Profile__Execute__Request(Type_Safe):                              # Stateless execution request
    html : Safe_Str__Html                                                        # Raw HTML input


class Schema__Profile__Execute__Cached__Request(Type_Safe):                      # Cached execution request
    html        : Safe_Str__Html = None                                          # Optional - uses cached if not provided
    force_rerun : bool           = False                                         # Re-execute all steps
