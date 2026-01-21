# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Flow__Durations__Response - Response containing task durations
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe import Type_Safe


class Schema__Flow__Durations__Response(Type_Safe):
    success        : bool  = False                                                # Whether retrieval succeeded
    flet_name      : str   = ''                                                   # Name of the FLeT
    durations      : dict  = None                                                 # Task name -> duration mapping
    total_duration : float = 0.0                                                  # Total execution time in seconds
