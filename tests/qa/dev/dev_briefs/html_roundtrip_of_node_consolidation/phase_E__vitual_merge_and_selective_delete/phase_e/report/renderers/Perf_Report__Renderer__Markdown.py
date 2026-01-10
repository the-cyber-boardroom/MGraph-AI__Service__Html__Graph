# ═══════════════════════════════════════════════════════════════════════════════
# Perf_Report__Renderer__Markdown - Renders report to Markdown
# Produces formatted .md output with tables
# ═══════════════════════════════════════════════════════════════════════════════

from datetime                                                                                           import datetime
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                          import type_safe
from phase_e.report.renderers.Perf_Report__Renderer__Base                                             import Perf_Report__Renderer__Base
from phase_e.report.schemas.Schema__Perf_Report                                                       import Schema__Perf_Report
from phase_e.report.schemas.Schema__Perf_Report__Metadata                                             import Schema__Perf_Report__Metadata
from phase_e.report.schemas.Schema__Perf_Report__Analysis                                             import Schema__Perf_Report__Analysis
from phase_e.report.collections.List__Perf_Report__Benchmarks                                         import List__Perf_Report__Benchmarks
from phase_e.report.collections.List__Perf_Report__Categories                                         import List__Perf_Report__Categories
from phase_e.report.collections.Dict__Perf_Report__Legend                                             import Dict__Perf_Report__Legend


class Perf_Report__Renderer__Markdown(Perf_Report__Renderer__Base):  # Renders to .md

    @type_safe
    def render(self, report: Schema__Perf_Report) -> str:         # Main render method
        lines = []

        lines.append(self.render_header(report))
        lines.append(self.render_metadata_table(report.metadata))
        lines.append(self.render_description(report.metadata))
        lines.append(self.render_legend(report.legend))
        lines.append(self.render_benchmarks_table(report.benchmarks, report.categories))
        lines.append(self.render_category_summary(report.categories))
        lines.append(self.render_bottleneck_analysis(report.analysis))
        lines.append(self.render_key_insight(report.analysis))
        lines.append(self.render_footer(report.metadata))

        return '\n'.join(lines)

    # ═══════════════════════════════════════════════════════════════════════════
    # Section Renderers
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def render_header(self, report: Schema__Perf_Report) -> str:  # Report header
        lines = []
        lines.append(f'# {str(report.metadata.title)}')
        lines.append('')
        return '\n'.join(lines)

    @type_safe
    def render_metadata_table(self                            ,   # Metadata table
                              metadata: Schema__Perf_Report__Metadata
                         ) -> str:
        lines = []
        lines.append('## Metadata')
        lines.append('')
        lines.append('| Property | Value |')
        lines.append('|----------|-------|')
        lines.append(f'| Date | {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} |')
        lines.append(f'| Version | {str(metadata.version)} |')
        test_input_escaped = (str(metadata.test_input)[:50]
                        .replace('<', '&lt;')
                        .replace('>', '&gt;'))
        lines.append(f'| Test Input | `{test_input_escaped}` |')
        lines.append(f'| Measurement Mode | {str(metadata.measure_mode)} |')
        lines.append(f'| Total Benchmarks | {str(metadata.benchmark_count)} |')
        lines.append('')
        return '\n'.join(lines)

    @type_safe
    def render_description(self                               ,   # Description section
                           metadata: Schema__Perf_Report__Metadata
                      ) -> str:
        lines = []
        lines.append('## Description')
        lines.append('')
        lines.append(str(metadata.description))
        lines.append('')
        return '\n'.join(lines)

    @type_safe
    def render_legend(self, legend: Dict__Perf_Report__Legend) -> str:  # Legend section
        lines = []
        lines.append('## Legend')
        lines.append('')

        if legend:
            for cat_id, description in sorted(legend.items()):
                lines.append(f'- **{cat_id}_xx**: {description}')

        lines.append('')
        return '\n'.join(lines)

    @type_safe
    def render_benchmarks_table(self                                      ,  # Main data table
                                benchmarks: List__Perf_Report__Benchmarks ,
                                categories: List__Perf_Report__Categories
                           ) -> str:
        lines = []
        lines.append('## Benchmark Results')
        lines.append('')
        lines.append('| Benchmark | Time | Category | % of Total |')
        lines.append('|-----------|------|----------|------------|')

        # Build category name lookup
        cat_names = {}
        for cat in categories:
            cat_names[str(cat.category_id)] = str(cat.name)

        for benchmark in benchmarks:
            cat_id   = str(benchmark.category_id)
            cat_name = cat_names.get(cat_id, 'Unknown')
            pct_str  = self.format_pct(float(benchmark.pct_of_total))

            lines.append(f'| {str(benchmark.benchmark_id)} | '
                        f'{self.format_ns(int(benchmark.time_ns))} | '
                        f'{cat_name} | {pct_str} |')

        lines.append('')
        return '\n'.join(lines)

    @type_safe
    def render_category_summary(self                              ,  # Category totals
                                categories: List__Perf_Report__Categories
                           ) -> str:
        lines = []
        lines.append('## Category Summary')
        lines.append('')
        lines.append('| Category | Time | % of Total |')
        lines.append('|----------|------|------------|')

        for category in categories:
            lines.append(f'| {str(category.name)} | '
                        f'{self.format_ns(int(category.total_ns))} | '
                        f'{self.format_pct(float(category.pct_of_total))} |')

        lines.append('')
        return '\n'.join(lines)

    @type_safe
    def render_bottleneck_analysis(self                           ,  # Bottleneck section
                                   analysis: Schema__Perf_Report__Analysis
                              ) -> str:
        lines = []
        lines.append('## Bottleneck Analysis')
        lines.append('')
        lines.append(f'- **Primary Bottleneck**: `{str(analysis.bottleneck_id)}`')
        lines.append(f'- **Time**: {self.format_ns(int(analysis.bottleneck_ns))}')
        lines.append(f'- **Percentage**: {self.format_pct(float(analysis.bottleneck_pct))} of total')
        lines.append('')
        return '\n'.join(lines)

    @type_safe
    def render_key_insight(self                                   ,  # Key insight section
                           analysis: Schema__Perf_Report__Analysis
                      ) -> str:
        lines = []
        lines.append('## Key Insight')
        lines.append('')
        lines.append(f'> {str(analysis.key_insight)}')
        lines.append('')
        return '\n'.join(lines)

    @type_safe
    def render_footer(self                                        ,  # Report footer
                      metadata: Schema__Perf_Report__Metadata
                 ) -> str:
        lines = []
        lines.append('---')
        lines.append('')
        lines.append(f'*Report generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*')
        lines.append(f'*Version: {str(metadata.version)}*')
        return '\n'.join(lines)
