from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__to__cache.schemas.Schema__Html_To_Cache__Extract__Output       import Schema__Html_To_Cache__Extract__Output
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__to__cache.schemas.Schema__Html_To_Cache__Transform__Output     import Schema__Html_To_Cache__Transform__Output
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                                                          import type_safe
from osbot_utils.helpers.flows.decorators.task                                                                                          import task
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Cache_Hash                                                import Safe_Str__Cache_Hash
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Client                                                              import Html_Cache__Client


@task()
@type_safe
def action__html_to_cache__transform(input_data  : Schema__Html_To_Cache__Extract__Output,
                                     cache_client: Html_Cache__Client = None
                                ) -> Schema__Html_To_Cache__Transform__Output:
    html_str   = str(input_data.html)
    char_count = len(html_str)

    if cache_client:                                                                  # Use cache client's hash generator
        html_hash = cache_client.hash_generator.from_string(html_str)
    else:
        html_hash = Safe_Str__Cache_Hash('')                                          # Empty hash if no client

    cache_key = input_data.cache_key or str(html_hash)                               # Use hash as key if no explicit key

    return Schema__Html_To_Cache__Transform__Output(html       = input_data.html     ,
                                                    html_hash  = html_hash           ,
                                                    namespace  = input_data.namespace,
                                                    cache_key  = cache_key           ,
                                                    char_count = char_count          )