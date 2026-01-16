# ═══════════════════════════════════════════════════════════════════════════════
# Html Dict Schema (Type_Safe wrapper for dict structure)
# ═══════════════════════════════════════════════════════════════════════════════
from typing                          import Dict, Any
from osbot_utils.type_safe.Type_Safe import Type_Safe

class Schema__Html_Dict(Type_Safe):                                              # Parsed HTML dictionary
    html_dict : Dict[str, Any]                                                   # The dictionary structure
