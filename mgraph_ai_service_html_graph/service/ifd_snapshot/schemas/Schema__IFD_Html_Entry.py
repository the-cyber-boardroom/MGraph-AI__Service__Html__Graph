# ═══════════════════════════════════════════════════════════════════════════════
# Schema__IFD_Html_Entry - HTML entry point with its dependencies
# Pure data container - NO methods
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                import List
from osbot_utils.type_safe.Type_Safe                                                       import Type_Safe
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path          import Safe_Str__File__Path
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Schema__IFD_Dependency      import Schema__IFD_Dependency


class Schema__IFD_Html_Entry(Type_Safe):                                                   # HTML entry point with its dependencies
    file_name    : Safe_Str__File__Path                                                    # e.g., "playground.html"
    file_path    : Safe_Str__File__Path                                                    # Full path to HTML file
    dependencies : List[Schema__IFD_Dependency]                                            # All dependencies from this HTML
