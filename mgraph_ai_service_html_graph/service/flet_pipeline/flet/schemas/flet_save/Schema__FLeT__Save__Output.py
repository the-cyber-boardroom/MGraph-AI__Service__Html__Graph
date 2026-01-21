# ═══════════════════════════════════════════════════════════════════════════════
# Schema__FLeT__Save - Input/Output schemas for Save phase
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                                     import Type_Safe
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Cache_Hash import Safe_Str__Cache_Hash
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                       import Cache_Id


class Schema__FLeT__Save__Output(Type_Safe):                                         # Base output from Save phase
    success    : bool                 = False                                        # Whether save succeeded
    cache_id   : Cache_Id             = None                                         # Cache entry ID (if saved)
    html_hash  : Safe_Str__Cache_Hash = ''                                           # Hash of saved HTML
    data_key   : Safe_Str__File__Path = ''                                           # Key in cache storage
