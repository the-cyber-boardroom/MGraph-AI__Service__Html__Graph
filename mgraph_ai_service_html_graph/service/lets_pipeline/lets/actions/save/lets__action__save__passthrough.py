# ═══════════════════════════════════════════════════════════════════════════════
# lets__action__save__passthrough - No-op save action
# Used when no persistence is needed (stateless execution)
# ═══════════════════════════════════════════════════════════════════════════════
from osbot_utils.helpers.flows.decorators.task                                                                      import task
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                                      import type_safe
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_save.Schema__LETS__Save__Output           import Schema__LETS__Save__Output
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_transform.Schema__LETS__Transform__Output import Schema__LETS__Transform__Output



@task()
@type_safe
def lets__action__save__passthrough(input_data: Schema__LETS__Transform__Output) -> Schema__LETS__Save__Output:
    return Schema__LETS__Save__Output(success = True  ,
                                      cached  = False )