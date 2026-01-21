# ═══════════════════════════════════════════════════════════════════════════════
# Schema__IFD_Snapshot_Config - Configuration for snapshot generation
# Pure data container - NO methods
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                import List
from osbot_utils.type_safe.Type_Safe                                                       import Type_Safe
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path          import Safe_Str__File__Path
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Safe_Str__IFD               import Safe_Str__IFD_Version


class Schema__IFD_Snapshot_Config(Type_Safe):                                              # Configuration for snapshot generation
    version_root   : Safe_Str__File__Path                                                  # e.g., "/path/to/v0.2"
    target_version : Safe_Str__IFD_Version                                                 # e.g., "v0.2.10"
    web_root       : Safe_Str__File__Path  = None                                          # Optional web root for absolute paths
    html_folders   : List[Safe_Str__File__Path]                                            # Folders to search for HTML (default: root)
    output_folder  : Safe_Str__File__Path  = None                                          # Optional output folder path
