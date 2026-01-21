# # ═══════════════════════════════════════════════════════════════════════════════
# # Dict__Perf_Report__Legend - Typed dict for category legend
# # Pure type definition - no methods
# # Maps category ID to description
# # ═══════════════════════════════════════════════════════════════════════════════
#
# from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__Dict                           import Type_Safe__Dict
# from osbot_utils.helpers.performance.benchmark.schemas.safe_str.Safe_Str__Benchmark__Section    import Safe_Str__Benchmark__Section
# from osbot_utils.helpers.performance.benchmark.schemas.safe_str.Safe_Str__Benchmark__Description import Safe_Str__Benchmark__Description
#
#
# class Dict__Perf_Report__Legend(Type_Safe__Dict):                 # Category ID → Description
#     expected_key_type   = Safe_Str__Benchmark__Section
#     expected_value_type = Safe_Str__Benchmark__Description
