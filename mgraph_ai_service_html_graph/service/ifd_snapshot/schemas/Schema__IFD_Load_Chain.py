# ═══════════════════════════════════════════════════════════════════════════════
# Schema__IFD_Load_Chain - Ordered sequence forming a logical component
# Pure data container - NO methods
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                import List
from osbot_utils.type_safe.Type_Safe                                                       import Type_Safe
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Safe_Str__IFD               import Safe_Str__Logical_Name
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Safe_Str__IFD               import Safe_Str__Resource_Type
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Schema__IFD_Dependency      import Schema__IFD_Dependency


class Schema__IFD_Load_Chain(Type_Safe):                                                   # Ordered sequence forming a logical component
    logical_name  : Safe_Str__Logical_Name                                                 # e.g., "js/services/api-client"
    resource_type : Safe_Str__Resource_Type                                                # 'css' or 'js'
    files         : List[Schema__IFD_Dependency]                                           # Ordered: base first, then surgical by version
