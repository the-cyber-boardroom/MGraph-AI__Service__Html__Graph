# # ═══════════════════════════════════════════════════════════════════════════════
# # Schema__Perf_Report__Metadata - Report metadata
# # Pure data container for benchmark report metadata
# # ═══════════════════════════════════════════════════════════════════════════════
#
# from osbot_utils.type_safe.Type_Safe                                                            import Type_Safe
# from osbot_utils.type_safe.primitives.core.Safe_UInt                                            import Safe_UInt
# from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now                import Timestamp_Now
# from osbot_utils.helpers.performance.benchmark.schemas.safe_str.Safe_Str__Benchmark__Title      import Safe_Str__Benchmark__Title
# from osbot_utils.helpers.performance.benchmark.schemas.safe_str.Safe_Str__Benchmark__Description import Safe_Str__Benchmark__Description
# from osbot_utils.helpers.performance.benchmark.schemas.enums.Enum__Measure_Mode                 import Enum__Measure_Mode
#
#
# class Schema__Perf_Report__Metadata(Type_Safe):                   # Report metadata
#     timestamp       : Timestamp_Now                               # Auto-generates on creation
#     version         : Safe_Str__Benchmark__Title                  # Code version being tested
#     title           : Safe_Str__Benchmark__Title                  # Report title
#     description     : Safe_Str__Benchmark__Description            # What this report measures
#     test_input      : Safe_Str__Benchmark__Description            # Description of input data
#     measure_mode    : Enum__Measure_Mode                          # QUICK, FAST, DEFAULT
#     benchmark_count : Safe_UInt                                   # Number of benchmarks
