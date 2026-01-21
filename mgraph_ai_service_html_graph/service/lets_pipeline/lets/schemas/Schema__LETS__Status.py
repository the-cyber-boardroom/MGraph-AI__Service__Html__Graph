# ═══════════════════════════════════════════════════════════════════════════════
# Schema__LETS__Status - Tracks execution status of a LETS transformation
# Stored in root document to track what has been computed
# ═══════════════════════════════════════════════════════════════════════════════
from osbot_utils.type_safe.Type_Safe                                                                   import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                                   import Safe_UInt
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now                       import Timestamp_Now
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id                        import Safe_Str__Id
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Hash                     import Safe_Str__Hash
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.safe_str.Safe_Str__LETS__Data_Key import Safe_Str__LETS__Data_Key
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.safe_str.Safe_Str__LETS__Name     import Safe_Str__LETS__Name



class Schema__LETS__Status(Type_Safe):                                           # Status of one LETS execution
    name         : Safe_Str__LETS__Name                                          # LETS transformation name
    completed    : bool                                                          # Has been executed
    data_key     : Safe_Str__LETS__Data_Key                                      # Cache path for output
    file_id      : Safe_Str__Id                                                  # Output file name
    timestamp    : Timestamp_Now                                                 # When executed
    duration_ms  : Safe_UInt                                                     # Execution time in ms
    input_hash   : Safe_Str__Hash                                                # For cache invalidation
    output_hash  : Safe_Str__Hash                                                # For verification
