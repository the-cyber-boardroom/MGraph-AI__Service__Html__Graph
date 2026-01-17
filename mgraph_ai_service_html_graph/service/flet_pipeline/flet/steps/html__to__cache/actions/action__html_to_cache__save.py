from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__to__cache.schemas.Schema__Html_To_Cache__Save__Output          import Schema__Html_To_Cache__Save__Output
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__to__cache.schemas.Schema__Html_To_Cache__Transform__Output     import Schema__Html_To_Cache__Transform__Output
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                                                          import type_safe
from osbot_utils.helpers.flows.decorators.task                                                                                          import task
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                                                                      import Cache_Id
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.schemas.Schema__Html_Entry                                                 import Schema__Html_Entry
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Client                                                              import Html_Cache__Client


@task()
@type_safe
def action__html_to_cache__save(input_data  : Schema__Html_To_Cache__Transform__Output,
                                cache_client: Html_Cache__Client = None
                           ) -> Schema__Html_To_Cache__Save__Output:
    if cache_client is None:                                                          # No cache client - return success without saving
        return Schema__Html_To_Cache__Save__Output(success    = True                 ,
                                                   html_hash  = input_data.html_hash ,
                                                   cache_key  = input_data.cache_key ,
                                                   namespace  = input_data.namespace ,
                                                   from_cache = False                )

    namespace = input_data.namespace
    cache_key = input_data.cache_key

    # Check if already exists by hash
    if cache_client.entry__exists_by_hash(namespace  = namespace           ,
                                          cache_hash = input_data.html_hash):
        cache_id = cache_client.cache_id__from_hash(namespace  = namespace           ,
                                                    cache_hash = input_data.html_hash)
        return Schema__Html_To_Cache__Save__Output(success    = True                 ,
                                                   cache_id   = cache_id             ,
                                                   html_hash  = input_data.html_hash ,
                                                   cache_key  = cache_key            ,
                                                   namespace  = namespace            ,
                                                   from_cache = True                 )

    # Store new entry


    entry = Schema__Html_Entry(html       = input_data.html     ,
                               cache_hash = input_data.html_hash,
                               char_count = input_data.char_count)

    response = cache_client.entry__store(namespace       = namespace           ,
                                         cache_key       = cache_key           ,
                                         file_id         = 'html-content'      ,
                                         json_field_path = 'cache_hash'        ,
                                         entry           = entry               )
    if response:
        cache_id = response.cache_id
        print('here!!!!!')
        response.print_obj()
        return Schema__Html_To_Cache__Save__Output(success    = True,
                                                   cache_id   = cache_id            ,
                                                   html_hash  = input_data.html_hash,
                                                   cache_key  = cache_key           ,
                                                   namespace  = namespace           )
    else:
        return Schema__Html_To_Cache__Save__Output(success    = False,
                                                   html_hash  = input_data.html_hash,
                                                   cache_key  = cache_key           ,
                                                   namespace  = namespace           )
