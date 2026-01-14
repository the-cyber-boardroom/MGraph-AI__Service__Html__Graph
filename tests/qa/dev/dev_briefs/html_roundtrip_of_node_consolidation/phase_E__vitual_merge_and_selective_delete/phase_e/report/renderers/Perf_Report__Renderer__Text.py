# # ═══════════════════════════════════════════════════════════════════════════════
# # Perf_Report__Renderer__Text - Renders report to plain text
# # Produces the formatted .txt output
# # ═══════════════════════════════════════════════════════════════════════════════
#
# from datetime                                                                                           import datetime
# from osbot_utils.helpers.Print_Table                                                                    import Print_Table
# from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                          import type_safe
# from phase_e.report.renderers.Perf_Report__Renderer__Base                                             import Perf_Report__Renderer__Base
# from phase_e.report.schemas.Schema__Perf_Report                                                       import Schema__Perf_Report
# from phase_e.report.schemas.Schema__Perf_Report__Metadata                                             import Schema__Perf_Report__Metadata
# from phase_e.report.schemas.Schema__Perf_Report__Analysis                                             import Schema__Perf_Report__Analysis
# from phase_e.report.collections.List__Perf_Report__Benchmarks                                         import List__Perf_Report__Benchmarks
# from phase_e.report.collections.List__Perf_Report__Categories                                         import List__Perf_Report__Categories
# from phase_e.report.collections.Dict__Perf_Report__Legend                                             import Dict__Perf_Report__Legend
#
#
# class Perf_Report__Renderer__Text(Perf_Report__Renderer__Base):   # Renders to .txt
#
#     @type_safe
#     def render(self, report: Schema__Perf_Report) -> str:         # Main render method
#         lines = []
#
#         lines.append(self.render_header(report))
#         lines.append(self.render_metadata_table(report.metadata))
#         lines.append(self.render_description(report.metadata))
#         lines.append(self.render_legend(report.legend))
#         lines.append(self.render_benchmarks_table(report.benchmarks, report.categories))
#         lines.append(self.render_category_summary(report.categories))
#         lines.append(self.render_percentage_analysis(report.categories))
#         lines.append(self.render_stage_breakdown(report.benchmarks, report.categories))
#         lines.append(self.render_bottleneck_analysis(report.analysis))
#         lines.append(self.render_key_insight(report.analysis))
#         lines.append(self.render_footer(report.metadata))
#
#         return '\n'.join(lines)
#
#     # ═══════════════════════════════════════════════════════════════════════════
#     # Section Renderers
#     # ═══════════════════════════════════════════════════════════════════════════
#
#     @type_safe
#     def render_header(self, report: Schema__Perf_Report) -> str:  # Report header
#         lines = []
#         lines.append('═' * 80)
#         lines.append(str(report.metadata.title).upper())
#         lines.append('═' * 80)
#         lines.append('')
#         return '\n'.join(lines)
#
#     @type_safe
#     def render_metadata_table(self                            ,   # Metadata table
#                               metadata: Schema__Perf_Report__Metadata
#                          ) -> str:
#         table = Print_Table()
#         table.set_title('BENCHMARK METADATA')
#         table.add_headers('Property', 'Value')
#         table.add_row(['Date'            , datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
#         table.add_row(['Version'         , str(metadata.version)                       ])
#         table.add_row(['Test Input'      , str(metadata.test_input)[:50]               ])
#         table.add_row(['Measurement Mode', str(metadata.measure_mode)                  ])
#         table.add_row(['Total Benchmarks', str(metadata.benchmark_count)               ])
#         return table.text()
#
#     @type_safe
#     def render_description(self                               ,   # Description section
#                            metadata: Schema__Perf_Report__Metadata
#                       ) -> str:
#         lines = []
#         lines.append('')
#         lines.append('DESCRIPTION')
#         lines.append('─' * 60)
#         lines.append(str(metadata.description))
#         lines.append('')
#         return '\n'.join(lines)
#
#     @type_safe
#     def render_legend(self, legend: Dict__Perf_Report__Legend) -> str:  # Legend section
#         lines = []
#         lines.append('LEGEND')
#         lines.append('─' * 60)
#
#         if legend:
#             for cat_id, description in sorted(legend.items()):
#                 lines.append(f'  {cat_id}_xx  {description}')
#
#         lines.append('')
#         return '\n'.join(lines)
#
#     @type_safe
#     def render_benchmarks_table(self                                      ,  # Main data table
#                                 benchmarks: List__Perf_Report__Benchmarks ,
#                                 categories: List__Perf_Report__Categories
#                            ) -> str:
#         table = Print_Table()
#         table.set_title('DETAILED CONVERSION BREAKDOWN')
#         table.add_headers('Benchmark', 'Time', 'Category', '% of Total')
#
#         # Build category name lookup
#         cat_names = {}
#         for cat in categories:
#             cat_names[str(cat.category_id)] = str(cat.name)
#
#         current_section = None
#         for benchmark in benchmarks:
#             cat_id = str(benchmark.category_id)
#
#             # Add section separator
#             if cat_id != current_section:
#                 if current_section is not None:
#                     table.add_row(['─' * 32, '─' * 10, '─' * 18, '─' * 10])
#                 current_section = cat_id
#
#             cat_name = cat_names.get(cat_id, 'Unknown')
#             pct_str  = self.format_pct(float(benchmark.pct_of_total))
#
#             table.add_row([str(benchmark.benchmark_id)         ,
#                            self.format_ns(int(benchmark.time_ns)),
#                            cat_name                             ,
#                            pct_str                              ])
#
#         table.set_footer(f'Total: {len(benchmarks)} benchmarks')
#         return table.text()
#
#     @type_safe
#     def render_category_summary(self                              ,  # Category totals
#                                 categories: List__Perf_Report__Categories
#                            ) -> str:
#         lines = []
#         lines.append('')
#         lines.append('=' * 60)
#         lines.append('CATEGORY SUMMARY')
#         lines.append('=' * 60)
#
#         for category in categories:
#             name     = f'{str(category.name)}:'
#             time_str = self.format_ns_padded(int(category.total_ns), 12)
#             cat_id   = str(category.category_id)
#             lines.append(f'  {name:<20} {time_str}  ({cat_id}_xx benchmarks)')
#
#         # Calculate and show overhead if we have A, B, C categories
#         overhead = self.calculate_overhead(categories)
#         if overhead is not None:
#             lines.append(f'  ─────────────────────────────────────────────')
#             lines.append(f'  {"Overhead:":<20} {self.format_ns_padded(overhead, 12)}  (full - create - convert)')
#
#         return '\n'.join(lines)
#
#     @type_safe
#     def render_percentage_analysis(self                           ,
#                                    categories: List__Perf_Report__Categories
#                               ) -> str:
#         lines = []
#         lines.append('')
#         lines.append('=' * 60)
#         lines.append('PERCENTAGE ANALYSIS (relative to Full Operations)')
#         lines.append('=' * 60)
#
#         # Find totals by category
#         full_total    = 0
#         create_total  = 0
#         convert_total = 0
#
#         for category in categories:
#             cat_id = str(category.category_id)
#             if cat_id == 'A':
#                 full_total = int(category.total_ns)
#             elif cat_id == 'B':
#                 create_total = int(category.total_ns)
#             elif cat_id == 'C':
#                 convert_total = int(category.total_ns)
#
#         if full_total > 0:
#             create_pct   = create_total / full_total * 100
#             convert_pct  = convert_total / full_total * 100
#             overhead_pct = (full_total - create_total - convert_total) / full_total * 100
#
#             lines.append(f'  Converter Creation: {create_pct:>6.2f}% of full operation time')
#             lines.append(f'  Convert Only:       {convert_pct:>6.1f}% of full operation time')
#             lines.append(f'  Overhead:           {overhead_pct:>6.2f}% of full operation time')
#
#         return '\n'.join(lines)
#
#     @type_safe
#     def render_stage_breakdown(self                               ,
#                                benchmarks: List__Perf_Report__Benchmarks,
#                                categories: List__Perf_Report__Categories
#                           ) -> str:
#         lines = []
#         lines.append('')
#         lines.append('=' * 60)
#         lines.append('STAGE BREAKDOWN (Full Operations)')
#         lines.append('=' * 60)
#
#         # Find A category total
#         full_ops_total = 0
#         for category in categories:
#             if str(category.category_id) == 'A':
#                 full_ops_total = int(category.total_ns)
#                 break
#
#         # Show only A_xx benchmarks with percentage relative to A total
#         for benchmark in benchmarks:
#             if str(benchmark.category_id) != 'A':
#                 continue
#
#             name     = str(benchmark.benchmark_id).replace('A_01__', '').replace('A_02__', '').replace('A_03__', '').replace('__full', '')
#             time_ns  = int(benchmark.time_ns)
#             time_str = self.format_ns_padded(time_ns, 10)
#             pct      = (time_ns / full_ops_total * 100) if full_ops_total > 0 else 0.0
#             pct_str  = f'({pct:>5.1f}%)'
#             bar_len  = int(pct / 2)
#             bar      = '█' * bar_len
#
#             lines.append(f'  {name:<20} {time_str} {pct_str} {bar}')
#
#         return '\n'.join(lines)
#
#     @type_safe
#     def render_bottleneck_analysis(self                           ,  # Bottleneck section
#                                    analysis: Schema__Perf_Report__Analysis
#                               ) -> str:
#         lines = []
#         lines.append('')
#         lines.append('=' * 60)
#         lines.append('BOTTLENECK ANALYSIS')
#         lines.append('=' * 60)
#         lines.append(f'  Primary Bottleneck: {str(analysis.bottleneck_id)}')
#         lines.append(f'  Time:               {self.format_ns(int(analysis.bottleneck_ns))}')
#         lines.append(f'  Percentage:         {self.format_pct(float(analysis.bottleneck_pct))} of total')
#         return '\n'.join(lines)
#
#     @type_safe
#     def render_key_insight(self                                   ,  # Key insight section
#                            analysis: Schema__Perf_Report__Analysis
#                       ) -> str:
#         lines = []
#         lines.append('')
#         lines.append('=' * 60)
#         lines.append('KEY INSIGHT')
#         lines.append('=' * 60)
#         lines.append(f'  {str(analysis.key_insight)}')
#         return '\n'.join(lines)
#
#     @type_safe
#     def render_footer(self                                        ,  # Report footer
#                       metadata: Schema__Perf_Report__Metadata
#                  ) -> str:
#         lines = []
#         lines.append('')
#         lines.append('═' * 80)
#         lines.append(f'Report generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
#         lines.append(f'Version: {str(metadata.version)}')
#         lines.append('═' * 80)
#         return '\n'.join(lines)
#
#     # ═══════════════════════════════════════════════════════════════════════════
#     # Helpers
#     # ═══════════════════════════════════════════════════════════════════════════
#
#     @type_safe
#     def calculate_overhead(self                                   ,  # Calculate overhead
#                            categories: List__Perf_Report__Categories
#                       ) -> int:
#         full_total    = 0
#         create_total  = 0
#         convert_total = 0
#
#         for category in categories:
#             cat_id = str(category.category_id)
#             if cat_id == 'A':
#                 full_total = int(category.total_ns)
#             elif cat_id == 'B':
#                 create_total = int(category.total_ns)
#             elif cat_id == 'C':
#                 convert_total = int(category.total_ns)
#
#         if full_total > 0:
#             return full_total - create_total - convert_total
#         return None
