# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Perf_Report__Analysis - Bottleneck analysis
# Pure data container for performance analysis results
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Int                                                     import Safe_Int
from osbot_utils.type_safe.primitives.core.Safe_UInt                                                    import Safe_UInt
from osbot_utils.type_safe.primitives.domains.numerical.safe_float.Safe_Float__Percentage_Change        import Safe_Float__Percentage_Change
from osbot_utils.helpers.performance.benchmark.schemas.safe_str.Safe_Str__Benchmark_Id                  import Safe_Str__Benchmark_Id
from osbot_utils.helpers.performance.benchmark.schemas.safe_str.Safe_Str__Benchmark__Description        import Safe_Str__Benchmark__Description


class Schema__Perf_Report__Analysis(Type_Safe):                   # Bottleneck analysis
    bottleneck_id   : Safe_Str__Benchmark_Id                      # Slowest benchmark
    bottleneck_ns   : Safe_UInt                                   # Time of bottleneck
    bottleneck_pct  : Safe_Float__Percentage_Change               # Percentage of total
    total_ns        : Safe_UInt                                   # Total time across all
    overhead_ns     : Safe_Int                                    # Can be negative
    overhead_pct    : Safe_Float__Percentage_Change               # Overhead percentage
    key_insight     : Safe_Str__Benchmark__Description            # Auto-generated insight
