# ═══════════════════════════════════════════════════════════════════════════════
# action__html_to_cache__save - Save HTML content to cache data layer
# This is the ONLY action in FLeT__Html__To__Cache (single responsibility)
#
# Requires:
#   - cache_client: For storage operations
#   - cache_id: Already-established entity ID (from orchestrator)
#   - namespace: Cache namespace
# ═══════════════════════════════════════════════════════════════════════════════

from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Client                                                   import Html_Cache__Client
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__to__cache.schemas.Schema__Html_To_Cache__Input      import Schema__Html_To_Cache__Input
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__to__cache.schemas.Schema__Html_To_Cache__Output     import Schema__Html_To_Cache__Output
from osbot_utils.helpers.flows.decorators.task                                                                               import task
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                                                           import Cache_Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Namespace                                       import Safe_Str__Namespace
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                                               import type_safe


@task()
@type_safe
def action__html_to_cache__save(input_data   : Schema__Html_To_Cache__Input       ,       # HTML content to save
                                cache_client : Html_Cache__Client            = None,      # Cache client for storage
                                cache_id     : Cache_Id                      = None,      # Entity cache_id
                                namespace    : Safe_Str__Namespace           = None       # Cache namespace
                           ) -> Schema__Html_To_Cache__Output:                            # Save result
    html_str     = str(input_data.html)
    char_count   = len(html_str)
    data_key     = input_data.data_key
    data_file_id = input_data.data_file_id

    # Handle missing dependencies gracefully
    if cache_client is None or cache_id is None or namespace is None:
        return Schema__Html_To_Cache__Output(success      = False       ,
                                             data_key     = data_key    ,
                                             data_file_id = data_file_id,
                                             char_count   = char_count  )

    # Store to data layer
    response = cache_client.data__store_string(namespace    = namespace   ,
                                               cache_id     = cache_id    ,
                                               data_key     = data_key    ,
                                               data_file_id = data_file_id,
                                               content      = html_str    )
    if response:
        return Schema__Html_To_Cache__Output(success        = True        ,
                                             data_key       = data_key    ,
                                             data_file_id   = data_file_id,
                                             char_count     = char_count  ,
                                             store_response = response    )
    else:
        return Schema__Html_To_Cache__Output(success      = False       ,
                                             data_key     = data_key    ,
                                             data_file_id = data_file_id,
                                             char_count   = char_count  )