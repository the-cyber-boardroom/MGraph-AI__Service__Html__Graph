# ═══════════════════════════════════════════════════════════════════════════════
# Schema__LETS__Config - Configuration for a LETS transformation
# Defines the transformation's identity, schema expectations, and action config
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                           import Type
from osbot_utils.type_safe.Type_Safe                                                                  import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                          import Safe_Str__Text
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_input.Schema__LETS__Input   import Schema__LETS__Input
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_output.Schema__LETS__Output import Schema__LETS__Output
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.safe_str.Safe_Str__LETS__Name    import Safe_Str__LETS__Name


# todo: replace raw primitives below with Safe_* ones
class Schema__LETS__Config(Type_Safe):                                                  # LETS transformation config
    # Identity
    name           : Safe_Str__LETS__Name                                               # Unique transformation name
    description    : Safe_Str__Text                                                     # Human readable description

    # Schema types (optional, for validation)
    schema__input  : Type[Schema__LETS__Input ]      = None                             # Expected input schema
    schema__output : Type[Schema__LETS__Output]      = None                             # Expected output schema

    # Save action configuration
    save_layer     : str                             = None                             # Layer name for cache storage
    save_file_id   : str                             = None                             # File ID within layer
    save_type      : str                             = 'string'                         # 'string' or 'json'

    # Load action configuration
    load_layer     : str                             = None                             # Layer to load from
    load_file_id   : str                             = None                             # File ID to load

    # Transform configuration
    compute_stats  : bool                            = True                             # Whether to compute statistics
