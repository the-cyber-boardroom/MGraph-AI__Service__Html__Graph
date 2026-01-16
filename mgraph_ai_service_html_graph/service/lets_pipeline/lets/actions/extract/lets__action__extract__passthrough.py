# ═══════════════════════════════════════════════════════════════════════════════
# lets__action__extract__passthrough - Pass data through unchanged
# Used when no extraction/filtering is needed
# ═══════════════════════════════════════════════════════════════════════════════
from osbot_utils.helpers.flows.decorators.task                                                                  import task
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                                  import type_safe
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_extract.Schema__LETS__Extract__Output import Schema__LETS__Extract__Output
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_load.Schema__LETS__Load__Output       import Schema__LETS__Load__Output

@task()
@type_safe
def lets__action__extract__passthrough(input_data: Schema__LETS__Load__Output) -> Schema__LETS__Extract__Output:
    return Schema__LETS__Extract__Output(html=input_data.html)