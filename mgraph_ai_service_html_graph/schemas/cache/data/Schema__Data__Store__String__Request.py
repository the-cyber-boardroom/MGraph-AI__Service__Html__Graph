# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Data__Store__String__Request - Request to store string data
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                         import Type_Safe


class Schema__Data__Store__String__Request(Type_Safe):                 # Request to store string
    content : str                                                      # String content to store
