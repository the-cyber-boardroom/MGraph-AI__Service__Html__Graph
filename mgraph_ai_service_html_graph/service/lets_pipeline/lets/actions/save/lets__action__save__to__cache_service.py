# ═══════════════════════════════════════════════════════════════════════════════
# lets__action__save__to__cache_service - Save content to cache storage
# Stores data in a cache layer using the cache service
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.helpers.flows.decorators.task                                                                      import task
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                                      import type_safe
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.base.Html_LETS__Flow                                   import Html_LETS__Flow
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_save.Schema__LETS__Save__Output           import Schema__LETS__Save__Output
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_transform.Schema__LETS__Transform__Output import Schema__LETS__Transform__Output


# todo: with the new dependency injection feature we don't need to use the this_flow to find the document and config objects
#       also this way we lost type safety and make the code below much more complex than it needs to be
@task()
@type_safe
def lets__action__save__to__cache_service(input_data : Schema__LETS__Transform__Output ,
                                          this_flow  : Html_LETS__Flow          = None ) -> Schema__LETS__Save__Output:
    document = this_flow.document if this_flow else None
    config   = this_flow.config   if this_flow else None

    if document is None:                                                                # No document = stateless execution
        return Schema__LETS__Save__Output(success = True  ,
                                          cached  = False )

    if config is None or config.save_layer is None:                                     # No config = can't determine where to save
        return Schema__LETS__Save__Output(success = False ,
                                          cached  = False )

    layer   = document.layer(layer_name=config.save_layer)
    content = str(input_data.html) if input_data.html else ''

    if config.save_type == 'json':
        layer.save_json(file_id=config.save_file_id, content=content)
    else:
        layer.save_string(file_id=config.save_file_id, content=content)

    return Schema__LETS__Save__Output(success = True               ,
                                      cached  = True               ,
                                      layer   = config.save_layer  ,
                                      file_id = config.save_file_id)