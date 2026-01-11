# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Perf__Entry - Performance entry metadata schema
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now import Timestamp_Now
from phase_e.storage.safe_str.Safe_Str__Session_Name                            import Safe_Str__Session_Name
from phase_e.storage.safe_str.Safe_Str__Target_Name                             import Safe_Str__Target_Name


# todo: replace dicts below with Type_Safe__Dict classes
class Schema__Perf__Entry(Type_Safe):                                               # Performance entry metadata
    cache_key       : Safe_Str__File__Path                                          # the cache_key used to create the cache_hash
    session_name    : Safe_Str__Session_Name                                        # Session identifier
    target_name     : Safe_Str__Target_Name                                         # Target identifier
    timestamp       : Timestamp_Now                                                 # Auto-generated timestamp
    config          : dict                                                          # Test configuration
    summary         : dict                                                          # Summary metrics

