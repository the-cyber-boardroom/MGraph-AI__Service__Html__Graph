# ═══════════════════════════════════════════════════════════════════════════════
# Perf__Phase_E__Scalability - Analyze scaling behavior across HTML sizes
# Part of Phase E_1: Performance Analysis
#
# Tests from tiny (~10 nodes) to massive (~10,000 nodes) to detect bottlenecks
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                     import List, Dict, Optional
from osbot_utils.helpers.Print_Table                                            import Print_Table
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                  import type_safe
from osbot_utils.type_safe.primitives.core.Safe_Int                             import Safe_Int
from osbot_utils.type_safe.primitives.core.Safe_Float                           import Safe_Float
from osbot_utils.type_safe.primitives.core.Safe_Str                             import Safe_Str
from phase_e.performance.Html_Generator__For_Benchmarks                         import Html_Generator__For_Benchmarks
from phase_e.performance.Perf__Phase_E__Conversion                              import Perf__Phase_E__Conversion
from phase_e.performance.Perf__Phase_E__Conversion                              import Schema__Conversion_Timing
from phase_e.performance.Perf__Storage__Base                                    import Perf__Storage__Base


class Schema__Scale_Point(Type_Safe):                                           # Single data point in scaling analysis
    name              : Safe_Str                                                # Size name (tiny, small, etc.)
    target_nodes      : Safe_Int                                                # Target node count
    actual_html_bytes : Safe_Int                                                # Actual HTML size in bytes
    timing            : Schema__Conversion_Timing                               # Timing results
    ns_per_node       : Safe_Float                                              # Nanoseconds per node (efficiency)


class Schema__Scaling_Analysis(Type_Safe):                                      # Full scaling analysis
    points            : List[Schema__Scale_Point]                               # All data points
    bottleneck_stage  : Safe_Str                                                # Which stage takes most time
    scaling_behavior  : Safe_Str                                                # Linear, quadratic, etc.
    timestamp         : Safe_Str                                                # When analysis was run


class Perf__Phase_E__Scalability(Type_Safe):                                    # Analyze scaling behavior

    generator : Html_Generator__For_Benchmarks
    converter : Perf__Phase_E__Conversion
    storage   : Perf__Storage__Base                                              # Optional storage backend


    # ═══════════════════════════════════════════════════════════════════════════
    # Main Analysis Methods
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def run_full_analysis(self                    ,                             # Run analysis across all sizes
                          auto_save : bool = False) -> Schema__Scaling_Analysis:
        from datetime import datetime

        sizes = [('tiny'   ,    10),
                 ('small'  ,   100),
                 ('medium' ,   500),
                 ('large'  ,  1000),
                 ('xlarge' ,  5000),
                 ('massive', 10000)]

        points = []

        for name, target in sizes:
            point = self.benchmark_size(name, target)
            points.append(point)

        bottleneck = self.identify_bottleneck(points)
        scaling    = self.analyze_scaling_behavior(points)
        timestamp  = datetime.now().isoformat()

        analysis = Schema__Scaling_Analysis(points           = points    ,
                                            bottleneck_stage = bottleneck,
                                            scaling_behavior = scaling   ,
                                            timestamp        = timestamp )

        if auto_save and self.storage is not None:
            self.save_analysis(analysis)

        return analysis

    @type_safe
    def run_quick_analysis(self                    ,                            # Quick analysis with fewer sizes
                           auto_save : bool = False) -> Schema__Scaling_Analysis:
        from datetime import datetime

        # sizes = [('small' ,  100),
        #          ('medium',  500),
        #          ('large' , 1000)]

        sizes = [('small' ,  1),
                 ('medium',  2),
                 ('large' , 3)]

        points = []

        for name, target in sizes:
            point = self.benchmark_size(name, target)
            points.append(point)

        bottleneck = self.identify_bottleneck(points)
        scaling    = self.analyze_scaling_behavior(points)
        timestamp  = datetime.now().isoformat()

        analysis = Schema__Scaling_Analysis(points           = points    ,
                                            bottleneck_stage = bottleneck,
                                            scaling_behavior = scaling   ,
                                            timestamp        = timestamp )

        if auto_save and self.storage is not None:
            self.save_analysis(analysis, key='scaling_analysis__quick')
            self.save_report  (analysis, key='scaling_analysis__quick')

        return analysis

    # ═══════════════════════════════════════════════════════════════════════════
    # Individual Size Benchmark
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def benchmark_size(self                   ,                                 # Benchmark a single size
                       name        : str      ,
                       target_nodes: int      ) -> Schema__Scale_Point:
        html   = self.generator.generate_with_target_nodes(target_nodes)
        timing = self.converter.benchmark_conversions(html)

        ns_per_node = float(timing.total_ns) / max(1, target_nodes)

        return Schema__Scale_Point(name              = name                ,
                                   target_nodes      = target_nodes        ,
                                   actual_html_bytes = len(html)           ,
                                   timing            = timing              ,
                                   ns_per_node       = round(ns_per_node, 2))

    # ═══════════════════════════════════════════════════════════════════════════
    # Analysis Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def identify_bottleneck(self, points: List[Schema__Scale_Point]) -> str:    # Find which stage takes most time
        if not points:
            return 'unknown'

        # Sum up times across all sizes
        total_html_to_dict   = sum(int(p.timing.html_to_dict_ns)   for p in points)
        total_dict_to_mgraph = sum(int(p.timing.dict_to_mgraph_ns) for p in points)
        total_mgraph_to_html = sum(int(p.timing.mgraph_to_html_ns) for p in points)

        stages = [('HTML→Dict'  , total_html_to_dict  ),
                  ('Dict→MGraph', total_dict_to_mgraph),
                  ('MGraph→HTML', total_mgraph_to_html)]

        bottleneck = max(stages, key=lambda x: x[1])

        return bottleneck[0]

    def analyze_scaling_behavior(self, points: List[Schema__Scale_Point]) -> str:  # Determine O(n), O(n²), etc.
        if len(points) < 2:
            return 'insufficient_data'

        # Compare ns_per_node across sizes
        # If constant → O(n) linear
        # If increasing → O(n²) or worse

        first_ns_per_node = float(points[0].ns_per_node)
        last_ns_per_node  = float(points[-1].ns_per_node)

        if first_ns_per_node == 0:
            return 'insufficient_data'

        ratio = last_ns_per_node / first_ns_per_node

        if ratio < 1.5:
            return 'O(n) linear - good'
        elif ratio < 3.0:
            return 'O(n log n) - acceptable'
        elif ratio < 10.0:
            return 'O(n²) quadratic - potential bottleneck'
        else:
            return 'worse than O(n²) - significant bottleneck'

    # ═══════════════════════════════════════════════════════════════════════════
    # Reporting (Print_Table based)
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def build_report(self, analysis: Schema__Scaling_Analysis) -> str:          # Build full report as string

        table = Print_Table()

        table.set_title('PHASE E SCALING ANALYSIS')
        table.add_headers('Size', 'Nodes', 'Total', 'ns/node', 'HTML→Dict', 'Dict→MGraph', 'MGraph→HTML')

        for point in analysis.points:
            timing = point.timing

            # Calculate percentages for each stage
            total = float(timing.total_ns) or 1.0
            html_pct   = float(timing.html_to_dict_ns)   / total * 100
            mgraph_pct = float(timing.dict_to_mgraph_ns) / total * 100
            rebuild_pct = float(timing.mgraph_to_html_ns) / total * 100

            table.add_row([str(point.name)                                              ,
                           f'{int(point.target_nodes):,}'                               ,
                           self.format_ns(int(timing.total_ns))                         ,
                           f'{float(point.ns_per_node):,.1f}'                           ,
                           f'{self.format_ns(int(timing.html_to_dict_ns))} ({html_pct:.0f}%)'    ,
                           f'{self.format_ns(int(timing.dict_to_mgraph_ns))} ({mgraph_pct:.0f}%)',
                           f'{self.format_ns(int(timing.mgraph_to_html_ns))} ({rebuild_pct:.0f}%)'])

        # Build footer with bottleneck and scaling info
        bottleneck = str(analysis.bottleneck_stage)
        scaling    = str(analysis.scaling_behavior)

        if 'linear' in scaling.lower():
            scaling_icon = '✅'
        elif 'acceptable' in scaling.lower():
            scaling_icon = '⚠️'
        else:
            scaling_icon = '❌'

        footer = f"Bottleneck: {bottleneck} | Scaling: {scaling} {scaling_icon}"
        table.set_footer(footer)

        return table.text()

    @type_safe
    def build_comparison_report(self                                ,           # Compare two analyses
                                before : Schema__Scaling_Analysis   ,
                                after  : Schema__Scaling_Analysis   ) -> str:

        table = Print_Table()

        table.set_title('SCALING COMPARISON REPORT')
        table.add_headers('Size', 'Before', 'After', 'Change', 'Before ns/n', 'After ns/n')

        for i, before_point in enumerate(before.points):
            if i >= len(after.points):
                continue

            after_point  = after.points[i]
            before_total = int(before_point.timing.total_ns)
            after_total  = int(after_point.timing.total_ns)
            diff         = after_total - before_total

            # Calculate change percentage
            if before_total > 0:
                change_pct = ((after_total - before_total) / before_total) * 100
                if change_pct > 0:
                    change_str = f"+{change_pct:.1f}% ▲"
                elif change_pct < 0:
                    change_str = f"{change_pct:.1f}% ▼"
                else:
                    change_str = "0%"
            else:
                change_str = "N/A"

            table.add_row([str(before_point.name)                       ,
                           self.format_ns(before_total)                 ,
                           self.format_ns(after_total)                  ,
                           change_str                                   ,
                           f'{float(before_point.ns_per_node):,.1f}'    ,
                           f'{float(after_point.ns_per_node):,.1f}'     ])

        # Footer with overall assessment
        before_scaling = str(before.scaling_behavior)
        after_scaling  = str(after.scaling_behavior)

        if before_scaling == after_scaling:
            footer = f"Scaling unchanged: {after_scaling}"
        else:
            footer = f"Scaling changed: {before_scaling} → {after_scaling}"

        table.set_footer(footer)

        return table.text()

    def save_report(self                               ,                        # Save report to file
                    analysis : Schema__Scaling_Analysis,
                    key = '') -> None:

        report =  self.build_report(analysis)
        if not key:
            key = self.storage.generate_timestamped_key('scaling_analysis')

        self.storage.save_report(key, report)

    def print_report(self, analysis: Schema__Scaling_Analysis) -> None:         # Print report to console
        print(self.build_report(analysis))

    @type_safe
    def format_analysis(self, analysis: Schema__Scaling_Analysis) -> str:       # Format analysis for display (legacy)
        return self.build_report(analysis)

    def print_analysis(self, analysis: Schema__Scaling_Analysis) -> None:       # Print formatted analysis (legacy)
        print(self.build_report(analysis))

    def format_ns(self, ns: int) -> str:                                        # Format nanoseconds for readability
        if ns >= 1_000_000_000:
            return f"{ns / 1_000_000_000:.2f}s"
        elif ns >= 1_000_000:
            return f"{ns / 1_000_000:.2f}ms"
        elif ns >= 1_000:
            return f"{ns / 1_000:.2f}µs"
        else:
            return f"{ns}ns"

    # ═══════════════════════════════════════════════════════════════════════════
    # Storage Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def save_analysis(self                               ,                      # Save analysis to storage
                      analysis : Schema__Scaling_Analysis,
                      key      : str = ''                ) -> Optional[str]:
        if self.storage is None:
            return None

        if not key:
            key = self.storage.generate_timestamped_key('scaling_analysis')

        self.storage.save_schema(key, analysis)

        return key

    def load_analysis(self, key: str) -> Optional[Schema__Scaling_Analysis]:    # Load analysis from storage
        if self.storage is None:
            return None

        data = self.storage.load(key)

        if data is None:
            return None

        return self.dict_to_analysis(data)

    def list_analyses(self) -> List[str]:                                       # List all stored analyses
        if self.storage is None:
            return []

        return self.storage.list_keys('scaling_analysis')

    def dict_to_analysis(self, data: dict) -> Schema__Scaling_Analysis:         # Convert dict to schema
        points = []

        for point_data in data.get('points', []):
            timing_data = point_data.get('timing', {})
            timing = Schema__Conversion_Timing(
                html_to_dict_ns   = timing_data.get('html_to_dict_ns', 0)  ,
                dict_to_mgraph_ns = timing_data.get('dict_to_mgraph_ns', 0),
                mgraph_to_html_ns = timing_data.get('mgraph_to_html_ns', 0),
                total_ns          = timing_data.get('total_ns', 0)        ,
                html_size_bytes   = timing_data.get('html_size_bytes', 0) ,
                node_count        = timing_data.get('node_count', 0)      )

            point = Schema__Scale_Point(
                name              = point_data.get('name', '')             ,
                target_nodes      = point_data.get('target_nodes', 0)      ,
                actual_html_bytes = point_data.get('actual_html_bytes', 0) ,
                timing            = timing                                 ,
                ns_per_node       = point_data.get('ns_per_node', 0.0)     )

            points.append(point)

        return Schema__Scaling_Analysis(
            points           = points                               ,
            bottleneck_stage = data.get('bottleneck_stage', '')     ,
            scaling_behavior = data.get('scaling_behavior', '')     ,
            timestamp        = data.get('timestamp', '')            )