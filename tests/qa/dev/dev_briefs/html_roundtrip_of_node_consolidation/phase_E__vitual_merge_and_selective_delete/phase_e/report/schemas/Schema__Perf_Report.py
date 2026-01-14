# # ═══════════════════════════════════════════════════════════════════════════════
# # Schema__Perf_Report - Main report schema
# # Pure data container - THE SINGLE SOURCE OF TRUTH
# # ═══════════════════════════════════════════════════════════════════════════════
#
# from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
# from phase_e.report.schemas.Schema__Perf_Report__Metadata                     import Schema__Perf_Report__Metadata
# from phase_e.report.schemas.Schema__Perf_Report__Analysis                     import Schema__Perf_Report__Analysis
# from phase_e.report.collections.List__Perf_Report__Benchmarks                 import List__Perf_Report__Benchmarks
# from phase_e.report.collections.List__Perf_Report__Categories                 import List__Perf_Report__Categories
# from phase_e.report.collections.Dict__Perf_Report__Legend                     import Dict__Perf_Report__Legend
#
#
# class Schema__Perf_Report(Type_Safe):                             # Main report schema
#     metadata        : Schema__Perf_Report__Metadata               # Report metadata
#     benchmarks      : List__Perf_Report__Benchmarks               # All benchmark results
#     categories      : List__Perf_Report__Categories               # Category summaries
#     analysis        : Schema__Perf_Report__Analysis               # Bottleneck analysis
#     legend          : Dict__Perf_Report__Legend                   # Category explanations
