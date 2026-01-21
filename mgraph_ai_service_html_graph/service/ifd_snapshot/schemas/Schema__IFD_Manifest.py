# ═══════════════════════════════════════════════════════════════════════════════
# Schema__IFD_Manifest - Complete snapshot manifest
# Pure data container - NO methods
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                import List
from osbot_utils.type_safe.Type_Safe                                                       import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                       import Safe_UInt
from osbot_utils.type_safe.primitives.domains.identifiers.Random_Guid                      import Random_Guid
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Safe_Str__IFD               import Safe_Str__IFD_Version
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Schema__IFD_Html_Entry      import Schema__IFD_Html_Entry
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Schema__IFD_Load_Chain      import Schema__IFD_Load_Chain
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now           import Timestamp_Now


class Schema__IFD_Manifest(Type_Safe):                                                     # Complete snapshot manifest
    snapshot_id         : Random_Guid                                                      # Unique ID for this snapshot
    snapshot_version    : Safe_Str__IFD_Version                                            # e.g., "v0.2.10__snapshot"
    source_version      : Safe_Str__IFD_Version                                            # e.g., "v0.2.10"
    created_at          : Timestamp_Now                                                    # Generation timestamp
    html_entry_points   : List[Schema__IFD_Html_Entry]                                     # All HTML files processed
    load_chains         : List[Schema__IFD_Load_Chain]                                     # Grouped dependencies
    versions_referenced : List[Safe_Str__IFD_Version]                                      # All versions used
    file_count          : Safe_UInt                                                        # Total unique files
