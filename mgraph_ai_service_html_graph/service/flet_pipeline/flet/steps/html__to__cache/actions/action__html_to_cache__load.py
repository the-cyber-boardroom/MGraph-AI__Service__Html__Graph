from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__to__cache.schemas.Schema__Html_To_Cache__Load__Input           import Schema__Html_To_Cache__Load__Input
from mgraph_ai_service_html_graph.service.flet_pipeline.flet.steps.html__to__cache.schemas.Schema__Html_To_Cache__Load__Output          import Schema__Html_To_Cache__Load__Output
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                                                          import type_safe
from osbot_utils.helpers.flows.decorators.task                                                                                          import task


@task()
@type_safe
def action__html_to_cache__load(input_data: Schema__Html_To_Cache__Load__Input
                           ) -> Schema__Html_To_Cache__Load__Output:
    cache_key = input_data.cache_key or input_data.url or ''                         # Use explicit key, URL, or empty (will use hash)
    return Schema__Html_To_Cache__Load__Output(html      = input_data.html     ,
                                               namespace = input_data.namespace,
                                               cache_key = cache_key           )
