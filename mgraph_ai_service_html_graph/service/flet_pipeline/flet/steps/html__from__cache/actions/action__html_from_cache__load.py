# ═══════════════════════════════════════════════════════════════════════════════
# action__html_from_cache__load - Load HTML content from cache data layer
# This is the ONLY action in FLeT__Html__From__Cache (single responsibility)
#
# Requires:
#   - cache_client: For storage operations
#   - cache_id: Already-established entity ID (from orchestrator)
#   - namespace: Cache namespace
# ═══════════════════════════════════════════════════════════════════════════════

from mgraph_ai_service_cache_client.schemas.cache.enums.Enum__Cache__Data_Type                                              import Enum__Cache__Data_Type
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Client                                                  import Html_Cache__Client
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__from__cache.schemas.Schema__Html_From_Cache__Input import Schema__Html_From_Cache__Input
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__from__cache.schemas.Schema__Html_From_Cache__Output import Schema__Html_From_Cache__Output
from osbot_utils.helpers.flows.decorators.task                                                                              import task
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                                                          import Cache_Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Namespace                                      import Safe_Str__Namespace
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html                                                   import Safe_Str__Html
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                                              import type_safe


@task()
@type_safe
def action__html_from_cache__load(input_data   : Schema__Html_From_Cache__Input      ,    # Where to load from
                                  cache_client : Html_Cache__Client            = None,    # Cache client for storage
                                  cache_id     : Cache_Id                      = None,    # Entity cache_id
                                  namespace    : Safe_Str__Namespace           = None     # Cache namespace
                             ) -> Schema__Html_From_Cache__Output:                        # Load result
    data_key     = input_data.data_key
    data_file_id = input_data.data_file_id

    # Handle missing dependencies gracefully
    if cache_client is None or cache_id is None or namespace is None:
        return Schema__Html_From_Cache__Output(success = False            ,
                                               html    = Safe_Str__Html(''),
                                               found   = False            )

    # Check if data exists
    exists = cache_client.data__exists(namespace    = namespace                  ,
                                       cache_id     = cache_id                   ,
                                       data_key     = data_key                   ,
                                       data_file_id = data_file_id               ,
                                       data_type    = Enum__Cache__Data_Type.STRING)

    if exists is False:
        return Schema__Html_From_Cache__Output(success = True             ,       # Operation succeeded
                                               html    = Safe_Str__Html(''),
                                               found   = False            )       # But data not found

    # Retrieve from data layer
    html_str = cache_client.data__retrieve_string(namespace    = namespace   ,
                                                  cache_id     = cache_id    ,
                                                  data_key     = data_key    ,
                                                  data_file_id = data_file_id)

    if html_str is None:
        return Schema__Html_From_Cache__Output(success = False            ,
                                               html    = Safe_Str__Html(''),
                                               found   = False            )

    return Schema__Html_From_Cache__Output(success = True                    ,
                                           html    = Safe_Str__Html(html_str),
                                           found   = True                    )
