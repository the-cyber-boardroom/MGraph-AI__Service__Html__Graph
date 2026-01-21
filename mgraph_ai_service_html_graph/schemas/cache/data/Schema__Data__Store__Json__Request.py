# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Data__Store__Json__Request - Request to store JSON data
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe               import Type_Safe



class Schema__Data__Store__Json__Request(Type_Safe):                              # Request to store JSON
    content : dict                                                                # JSON content to store
