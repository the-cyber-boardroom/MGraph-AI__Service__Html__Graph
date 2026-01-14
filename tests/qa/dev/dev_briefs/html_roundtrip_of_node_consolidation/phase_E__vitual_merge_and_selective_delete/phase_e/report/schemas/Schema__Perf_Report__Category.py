# # ═══════════════════════════════════════════════════════════════════════════════
# # Schema__Perf_Report__Category - Category summary
# # Pure data container for benchmark category aggregation
# # ═══════════════════════════════════════════════════════════════════════════════
#
# from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe
# from osbot_utils.type_safe.primitives.core.Safe_UInt                                                    import Safe_UInt
# from osbot_utils.type_safe.primitives.domains.numerical.safe_float.Safe_Float__Percentage_Change        import Safe_Float__Percentage_Change
# from osbot_utils.helpers.performance.benchmark.schemas.safe_str.Safe_Str__Benchmark__Section            import Safe_Str__Benchmark__Section
# from osbot_utils.helpers.performance.benchmark.schemas.safe_str.Safe_Str__Benchmark__Title              import Safe_Str__Benchmark__Title
# from osbot_utils.helpers.performance.benchmark.schemas.safe_str.Safe_Str__Benchmark__Description        import Safe_Str__Benchmark__Description
#
#
# class Schema__Perf_Report__Category(Type_Safe):                   # Category summary
#     category_id     : Safe_Str__Benchmark__Section                # e.g., 'A', 'B', 'C'
#     name            : Safe_Str__Benchmark__Title                  # e.g., 'Full Operation'
#     description     : Safe_Str__Benchmark__Description            # From legend
#     total_ns        : Safe_UInt                                   # Sum of all benchmarks
#     pct_of_total    : Safe_Float__Percentage_Change               # Percentage of total time
#     benchmark_count : Safe_UInt                                   # Number of benchmarks
