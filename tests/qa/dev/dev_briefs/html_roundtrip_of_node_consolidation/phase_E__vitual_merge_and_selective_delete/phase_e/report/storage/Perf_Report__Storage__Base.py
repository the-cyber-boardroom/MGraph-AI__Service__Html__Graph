# # ═══════════════════════════════════════════════════════════════════════════════
# # Perf_Report__Storage__Base - Abstract base for report storage
# # Defines interface for saving/loading reports
# # ═══════════════════════════════════════════════════════════════════════════════
#
# from typing                                                                                             import List
# from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe
# from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                          import type_safe
# from osbot_utils.helpers.performance.benchmark.schemas.safe_str.Safe_Str__Benchmark_Id                  import Safe_Str__Benchmark_Id
# from phase_e.report.schemas.Schema__Perf_Report                                                       import Schema__Perf_Report
# from phase_e.report.renderers.Perf_Report__Renderer__Base                                             import Perf_Report__Renderer__Base
# from phase_e.report.renderers.Perf_Report__Renderer__Text                                             import Perf_Report__Renderer__Text
# from phase_e.report.renderers.Perf_Report__Renderer__Json                                             import Perf_Report__Renderer__Json
# from phase_e.report.renderers.Perf_Report__Renderer__Markdown                                         import Perf_Report__Renderer__Markdown
#
#
# class Perf_Report__Storage__Base(Type_Safe):                      # Abstract storage base
#     renderers : dict                                              # Format → Renderer mapping
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.renderers = {'txt' : Perf_Report__Renderer__Text()    ,
#                           'md'  : Perf_Report__Renderer__Markdown(),
#                           'json': Perf_Report__Renderer__Json()    }
#
#     # ═══════════════════════════════════════════════════════════════════════════
#     # Public Interface
#     # ═══════════════════════════════════════════════════════════════════════════
#
#     @type_safe
#     def save(self                                             ,   # Save report in formats
#              report  : Schema__Perf_Report                    ,
#              key     : str                                    ,
#              formats : List[str] = None
#         ) -> bool:
#         if formats is None:
#             formats = ['txt', 'json']
#
#         for format_type in formats:
#             renderer = self.renderers.get(format_type)
#             if renderer:
#                 content = renderer.render(report)
#                 self.save_content(key, content, format_type)
#
#         return True
#
#     @type_safe
#     def save_content(self                                     ,   # Override in subclasses
#                      key     : str                            ,
#                      content : str                            ,
#                      format_type : str
#                 ) -> bool:
#         raise NotImplementedError('Subclasses must implement save_content()')
#
#     @type_safe
#     def load(self, key: str) -> Schema__Perf_Report:              # Override in subclasses
#         raise NotImplementedError('Subclasses must implement load()')
#
#     @type_safe
#     def list_reports(self) -> List[str]:                          # Override in subclasses
#         raise NotImplementedError('Subclasses must implement list_reports()')
#
#     @type_safe
#     def exists(self, key: str) -> bool:                           # Override in subclasses
#         raise NotImplementedError('Subclasses must implement exists()')
