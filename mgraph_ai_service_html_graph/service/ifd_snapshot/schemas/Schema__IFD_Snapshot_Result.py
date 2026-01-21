# ═══════════════════════════════════════════════════════════════════════════════
# Schema__IFD_Snapshot_Result - Result of snapshot generation
# Pure data container - NO methods
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                                       import Type_Safe
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Schema__IFD_Manifest        import Schema__IFD_Manifest


class Schema__IFD_Snapshot_Result(Type_Safe):                                              # Result of snapshot generation
    manifest     : Schema__IFD_Manifest                                                    # The manifest
    content_text : str                                                                     # Formatted text dump
    zip_bytes    : bytes = None                                                            # In-memory zip (optional)
