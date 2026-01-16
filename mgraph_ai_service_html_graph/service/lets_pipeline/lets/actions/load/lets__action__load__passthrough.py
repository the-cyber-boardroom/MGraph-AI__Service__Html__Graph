# ═══════════════════════════════════════════════════════════════════════════════
# lets__action__load__passthrough - Pass input through unchanged
# Used when no loading/fetching is needed (data provided directly)
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.helpers.flows.decorators.task                                                            import task
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                            import type_safe
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_load.Schema__LETS__Load__Input  import Schema__LETS__Load__Input
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_load.Schema__LETS__Load__Output import Schema__LETS__Load__Output


@task()
@type_safe
def lets__action__load__passthrough(input_data: Schema__LETS__Load__Input) -> Schema__LETS__Load__Output:
    return Schema__LETS__Load__Output(html=input_data.html)