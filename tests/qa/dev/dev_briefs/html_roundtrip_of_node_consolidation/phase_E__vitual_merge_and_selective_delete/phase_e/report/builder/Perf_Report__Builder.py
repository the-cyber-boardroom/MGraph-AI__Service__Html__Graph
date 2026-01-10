# ═══════════════════════════════════════════════════════════════════════════════
# Perf_Report__Builder - Builds Schema__Perf_Report from benchmark results
# Contains all logic for running benchmarks and populating schemas
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                             import Callable
from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                                    import Safe_UInt
from osbot_utils.type_safe.primitives.core.Safe_Int                                                     import Safe_Int
from osbot_utils.type_safe.primitives.domains.numerical.safe_float.Safe_Float__Percentage_Change        import Safe_Float__Percentage_Change
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                          import type_safe
from osbot_utils.helpers.performance.benchmark.Perf_Benchmark__Timing                                   import Perf_Benchmark__Timing
from osbot_utils.helpers.performance.benchmark.schemas.timing.Schema__Perf_Benchmark__Timing__Config    import Schema__Perf_Benchmark__Timing__Config
from osbot_utils.helpers.performance.benchmark.schemas.safe_str.Safe_Str__Benchmark_Id                  import Safe_Str__Benchmark_Id
from osbot_utils.helpers.performance.benchmark.schemas.safe_str.Safe_Str__Benchmark__Section            import Safe_Str__Benchmark__Section
from osbot_utils.helpers.performance.benchmark.schemas.safe_str.Safe_Str__Benchmark__Description        import Safe_Str__Benchmark__Description
from osbot_utils.helpers.performance.benchmark.schemas.enums.Enum__Measure_Mode                         import Enum__Measure_Mode
from phase_e.report.schemas.Schema__Perf_Report                                                       import Schema__Perf_Report
from phase_e.report.schemas.Schema__Perf_Report__Metadata                                             import Schema__Perf_Report__Metadata
from phase_e.report.schemas.Schema__Perf_Report__Benchmark                                            import Schema__Perf_Report__Benchmark
from phase_e.report.schemas.Schema__Perf_Report__Category                                             import Schema__Perf_Report__Category
from phase_e.report.schemas.Schema__Perf_Report__Analysis                                             import Schema__Perf_Report__Analysis
from phase_e.report.collections.List__Perf_Report__Benchmarks                                         import List__Perf_Report__Benchmarks
from phase_e.report.collections.List__Perf_Report__Categories                                         import List__Perf_Report__Categories
from phase_e.report.collections.Dict__Perf_Report__Legend                                             import Dict__Perf_Report__Legend


class Perf_Report__Builder(Type_Safe):                            # Builds Schema__Perf_Report
    metadata : Schema__Perf_Report__Metadata                      # Metadata template
    legend   : Dict__Perf_Report__Legend                          # Legend definitions
    config   : Schema__Perf_Benchmark__Timing__Config             # Timing configuration

    # ═══════════════════════════════════════════════════════════════════════════
    # Main Entry Point
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def run(self, benchmarks_fn: Callable) -> Schema__Perf_Report:  # Run benchmarks and build report
        with Perf_Benchmark__Timing(config=self.config) as timing:
            benchmarks_fn(timing)                                 # User's benchmark function

        results  = timing.results
        total_ns = self.calculate_total_ns(results)

        benchmarks = self.build_benchmarks(results, total_ns)
        categories = self.build_categories(benchmarks, total_ns)
        analysis   = self.build_analysis(benchmarks, categories, total_ns)

        self.metadata.benchmark_count = Safe_UInt(len(results))

        return Schema__Perf_Report(metadata   = self.metadata  ,
                                   benchmarks = benchmarks     ,
                                   categories = categories     ,
                                   analysis   = analysis       ,
                                   legend     = self.legend    )

    # ═══════════════════════════════════════════════════════════════════════════
    # Benchmark Building
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def calculate_total_ns(self, results: dict) -> Safe_UInt:     # Sum all benchmark times
        total = 0
        for result in results.values():
            total += int(result.final_score)
        return Safe_UInt(total)

    @type_safe
    def build_benchmarks(self                                 ,   # Convert timing results to schemas
                         results : dict                       ,
                         total_ns: Safe_UInt
                    ) -> List__Perf_Report__Benchmarks:
        benchmarks = List__Perf_Report__Benchmarks()

        for benchmark_id, result in sorted(results.items()):
            time_ns     = int(result.final_score)
            category_id = self.extract_category_id(benchmark_id)
            pct         = (time_ns / int(total_ns) * 100) if int(total_ns) > 0 else 0.0

            benchmark = Schema__Perf_Report__Benchmark(
                benchmark_id = Safe_Str__Benchmark_Id(benchmark_id)        ,
                time_ns      = Safe_UInt(time_ns)                          ,
                category_id  = category_id                                 ,
                pct_of_total = Safe_Float__Percentage_Change(pct)          )

            benchmarks.append(benchmark)

        return benchmarks

    # ═══════════════════════════════════════════════════════════════════════════
    # Category Building
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def build_categories(self                                     ,  # Group and summarize
                         benchmarks: List__Perf_Report__Benchmarks,
                         total_ns  : Safe_UInt
                    ) -> List__Perf_Report__Categories:
        categories = List__Perf_Report__Categories()

        # Group benchmarks by category
        category_data = {}                                        # category_id → {total_ns, count}
        for benchmark in benchmarks:
            cat_id = str(benchmark.category_id)
            if cat_id not in category_data:
                category_data[cat_id] = {'total_ns': 0, 'count': 0}
            category_data[cat_id]['total_ns'] += int(benchmark.time_ns)
            category_data[cat_id]['count']    += 1

        # Build category schemas
        for cat_id in sorted(category_data.keys()):
            data        = category_data[cat_id]
            cat_total   = data['total_ns']
            cat_count   = data['count']
            pct         = (cat_total / int(total_ns) * 100) if int(total_ns) > 0 else 0.0
            description = self.legend.get(cat_id, '') if self.legend else ''
            name        = self.extract_category_name(description)

            category = Schema__Perf_Report__Category(
                category_id     = Safe_Str__Benchmark__Section(cat_id)     ,
                name            = name                                     ,
                description     = Safe_Str__Benchmark__Description(description),
                total_ns        = Safe_UInt(cat_total)                     ,
                pct_of_total    = Safe_Float__Percentage_Change(pct)       ,
                benchmark_count = Safe_UInt(cat_count)                     )

            categories.append(category)

        return categories

    @type_safe
    def extract_category_name(self                                ,  # Extract name from description
                              description: str
                         ) -> str:
        if '=' in description:                                    # Format: "Name = Description"
            return description.split('=')[0].strip()
        return description[:30] if description else 'Unknown'

    # ═══════════════════════════════════════════════════════════════════════════
    # Analysis Building
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def build_analysis(self                                       ,  # Identify bottleneck
                       benchmarks : List__Perf_Report__Benchmarks ,
                       categories : List__Perf_Report__Categories ,
                       total_ns   : Safe_UInt
                  ) -> Schema__Perf_Report__Analysis:
        # Find bottleneck (slowest benchmark)
        bottleneck    = None
        bottleneck_ns = 0
        for benchmark in benchmarks:
            if int(benchmark.time_ns) > bottleneck_ns:
                bottleneck    = benchmark
                bottleneck_ns = int(benchmark.time_ns)

        bottleneck_id  = str(bottleneck.benchmark_id) if bottleneck else ''
        # Find the A category total
        full_ops_total = 0
        for category in categories:
            if str(category.category_id) == 'A':
                full_ops_total = int(category.total_ns)
                break

        bottleneck_pct = (bottleneck_ns / full_ops_total * 100) if full_ops_total > 0 else 0.0

        # Calculate overhead
        overhead_ns = self.calculate_overhead(categories)

        # Generate insight
        key_insight = self.generate_insight(bottleneck_pct, categories, overhead_ns, total_ns)

        return Schema__Perf_Report__Analysis(
            bottleneck_id  = Safe_Str__Benchmark_Id(bottleneck_id)             ,
            bottleneck_ns  = Safe_UInt(bottleneck_ns)                          ,
            bottleneck_pct = Safe_Float__Percentage_Change(bottleneck_pct)     ,
            total_ns       = total_ns                                         ,
            overhead_ns    = Safe_Int(overhead_ns)                            ,
            overhead_pct   = Safe_Float__Percentage_Change(
                               (overhead_ns / int(total_ns) * 100) if int(total_ns) > 0 else 0.0),
            key_insight    = Safe_Str__Benchmark__Description(key_insight)    )

    @type_safe
    def calculate_overhead(self                                   ,  # Calculate overhead from categories
                           categories: List__Perf_Report__Categories
                      ) -> int:
        # Overhead = Full Operations - (Creation + Conversion)
        # This assumes categories A=Full, B=Creation, C=Convert
        full_total    = 0
        create_total  = 0
        convert_total = 0

        for category in categories:
            cat_id = str(category.category_id)
            if cat_id == 'A':
                full_total = int(category.total_ns)
            elif cat_id == 'B':
                create_total = int(category.total_ns)
            elif cat_id == 'C':
                convert_total = int(category.total_ns)

        if full_total > 0:
            return full_total - create_total - convert_total
        return 0

    @type_safe
    def generate_insight(self                                     ,  # Create key insight text
                         bottleneck_pct : float                   ,
                         categories     : List__Perf_Report__Categories,
                         overhead_ns    : int                     ,
                         total_ns       : Safe_UInt
                    ) -> str:
        lines = []

        # Find creation category percentage
        create_pct = 0.0
        for category in categories:
            if str(category.category_id) == 'B':
                create_pct = float(category.pct_of_total)
                break

        if create_pct < 1.0:
            lines.append(f'Converter creation is {create_pct:.2f}% of total time → NEGLIGIBLE')
            lines.append('The bottleneck is INSIDE the conversion logic, not object creation.')
        else:
            lines.append(f'Converter creation is {create_pct:.1f}% of total time.')

        return ' '.join(lines)

    # ═══════════════════════════════════════════════════════════════════════════
    # Helpers
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def extract_category_id(self                                  ,  # Get category from benchmark ID
                            benchmark_id: str
                       ) -> Safe_Str__Benchmark__Section:
        if '_' in benchmark_id:                                   # Format: A_01__name → A
            return Safe_Str__Benchmark__Section(benchmark_id.split('_')[0])
        return Safe_Str__Benchmark__Section(benchmark_id[0] if benchmark_id else '')
