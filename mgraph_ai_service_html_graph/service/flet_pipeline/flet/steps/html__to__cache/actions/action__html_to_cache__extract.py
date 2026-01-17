from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__to__cache.schemas.Schema__Html_To_Cache__Extract__Output       import Schema__Html_To_Cache__Extract__Output
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__to__cache.schemas.Schema__Html_To_Cache__Load__Output          import Schema__Html_To_Cache__Load__Output
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                                                          import type_safe
from osbot_utils.helpers.flows.decorators.task                                                                                          import task
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Client                                                              import Html_Cache__Client


@task()
@type_safe
def action__html_to_cache__extract(input_data : Schema__Html_To_Cache__Load__Output,
                                   cache_client: Html_Cache__Client = None
                              ) -> Schema__Html_To_Cache__Extract__Output:
    return Schema__Html_To_Cache__Extract__Output(html      = input_data.html     ,
                                                  namespace = input_data.namespace,
                                                  cache_key = input_data.cache_key)
