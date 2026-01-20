# ═══════════════════════════════════════════════════════════════════════════════
# Schema__IFD_Dependency - Single file dependency from HTML
# Pure data container - NO methods
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                                       import Type_Safe
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path          import Safe_Str__File__Path
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Safe_Str__IFD               import Safe_Str__IFD_Version
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Safe_Str__IFD               import Safe_Str__Logical_Name
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Safe_Str__IFD               import Safe_Str__Resource_Type
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Safe_Str__IFD               import Safe_Str__File_Type
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Safe_Str__IFD               import Safe_UInt__Load_Order


class Schema__IFD_Dependency(Type_Safe):                                                   # Single file dependency from HTML
    original_path  : Safe_Str__File__Path                                                  # Path as in HTML (e.g., "../v0.2.0/css/common.css")
    resolved_path  : Safe_Str__File__Path                                                  # Absolute/normalized path
    source_version : Safe_Str__IFD_Version                                                 # Extracted version (e.g., "v0.2.0")
    resource_type  : Safe_Str__Resource_Type                                               # 'css' or 'js'
    file_type      : Safe_Str__File_Type                                                   # 'base' or 'surgical'
    logical_name   : Safe_Str__Logical_Name                                                # Grouped name (e.g., "js/services/api-client")
    load_order     : Safe_UInt__Load_Order                                                 # Order in HTML (0-based)
