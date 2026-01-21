# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Flow__Data__Response - Response with full flow execution data
# ═══════════════════════════════════════════════════════════════════════════════
from osbot_utils.type_safe.Type_Safe                                                               import Type_Safe
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.schemas.safe_str.Safe_Str__FLeT__Name import Safe_Str__FLeT__Name



class Schema__Flow__Data__Response(Type_Safe):                                    # Response with flow data
    success     : bool                                                            # Whether retrieval succeeded
    flet_name   : Safe_Str__FLeT__Name                                            # FLeT name
    flow_data   : dict                                                            # Flow data dictionary
    flow_events : list                                                            # Flow events list
