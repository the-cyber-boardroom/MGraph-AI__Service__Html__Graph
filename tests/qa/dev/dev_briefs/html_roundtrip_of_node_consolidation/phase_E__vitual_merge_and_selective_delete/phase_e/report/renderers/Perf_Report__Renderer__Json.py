# ═══════════════════════════════════════════════════════════════════════════════
# Perf_Report__Renderer__Json - Renders report to JSON
# Direct serialization of schema
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.utils.Json                                                                             import json_dumps
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                          import type_safe
from phase_e.report.renderers.Perf_Report__Renderer__Base                                             import Perf_Report__Renderer__Base
from phase_e.report.schemas.Schema__Perf_Report                                                       import Schema__Perf_Report


class Perf_Report__Renderer__Json(Perf_Report__Renderer__Base):   # Renders to .json

    @type_safe
    def render(self, report: Schema__Perf_Report) -> str:         # Serialize to JSON
        return json_dumps(report.json(), indent=2)
