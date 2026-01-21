# """
# Html_MGraph Performance Profiler
# ================================
#
# A comprehensive profiling framework to measure and analyze performance
# of the Html_MGraph transformation pipeline.
#
# Key metrics tracked:
# - Time per transformation phase
# - Memory usage per phase
# - Operation counts (nodes, edges, lookups)
# - Scalability characteristics (O(n) analysis)
#
# Usage:
#     profiler = Html_MGraph__Performance__Profiler()
#     results  = profiler.profile_transformation(html_string)
#     profiler.print_report(results)
# """
#
# import time
# import tracemalloc
# import cProfile
# import pstats
# import io
# from dataclasses       import dataclass, field
# from typing            import Dict, List, Any, Optional, Callable
# from functools         import wraps
# from contextlib        import contextmanager
# from osbot_utils.type_safe.Type_Safe import Type_Safe
#
#
# # ═══════════════════════════════════════════════════════════════════════════════
# # Performance Metrics Data Classes
# # ═══════════════════════════════════════════════════════════════════════════════
#
# @dataclass
# class Phase_Metrics:
#     """Metrics for a single transformation phase"""
#     phase_name     : str
#     duration_ms    : float           = 0.0
#     memory_delta_kb: float           = 0.0
#     peak_memory_kb : float           = 0.0
#     node_count     : int             = 0
#     edge_count     : int             = 0
#     extra_metrics  : Dict[str, Any]  = field(default_factory=dict)
#
#
# @dataclass
# class Profile_Result:
#     """Complete profiling result for a transformation"""
#     html_size_bytes   : int
#     html_element_count: int
#     total_duration_ms : float
#     total_memory_kb   : float
#     phases            : List[Phase_Metrics]       = field(default_factory=list)
#     cprofile_stats    : Optional[str]             = None
#     bottlenecks       : List[str]                 = field(default_factory=list)
#
#
# # ═══════════════════════════════════════════════════════════════════════════════
# # Timing and Memory Context Managers
# # ═══════════════════════════════════════════════════════════════════════════════
#
# class Timer:
#     """High-precision timer for measuring execution time"""
#
#     def __init__(self):
#         self.start_time : float = 0.0
#         self.end_time   : float = 0.0
#         self.duration_ms: float = 0.0
#
#     def __enter__(self):
#         self.start_time = time.perf_counter()
#         return self
#
#     def __exit__(self, *args):
#         self.end_time    = time.perf_counter()
#         self.duration_ms = (self.end_time - self.start_time) * 1000
#
#
# class Memory_Tracker:
#     """Memory usage tracker using tracemalloc"""
#
#     def __init__(self):
#         self.start_memory  : int   = 0
#         self.end_memory    : int   = 0
#         self.peak_memory   : int   = 0
#         self.delta_kb      : float = 0.0
#         self.peak_kb       : float = 0.0
#
#     def __enter__(self):
#         tracemalloc.start()
#         self.start_memory = tracemalloc.get_traced_memory()[0]
#         return self
#
#     def __exit__(self, *args):
#         current, peak      = tracemalloc.get_traced_memory()
#         self.end_memory    = current
#         self.peak_memory   = peak
#         self.delta_kb      = (self.end_memory - self.start_memory) / 1024
#         self.peak_kb       = self.peak_memory / 1024
#         tracemalloc.stop()
#
#
# @contextmanager
# def phase_profiler(phase_name: str, metrics_list: List[Phase_Metrics]):
#     """Context manager to profile a single phase"""
#     with Timer() as timer:
#         with Memory_Tracker() as memory:
#             phase_metrics = Phase_Metrics(phase_name=phase_name)
#             yield phase_metrics
#
#     phase_metrics.duration_ms     = timer.duration_ms
#     phase_metrics.memory_delta_kb = memory.delta_kb
#     phase_metrics.peak_memory_kb  = memory.peak_kb
#     metrics_list.append(phase_metrics)
#
#
# # ═══════════════════════════════════════════════════════════════════════════════
# # Main Profiler Class
# # ═══════════════════════════════════════════════════════════════════════════════
#
# class Html_MGraph__Performance__Profiler(Type_Safe):
#     """
#     Performance profiler for Html_MGraph transformations.
#
#     Profiles each phase of the transformation pipeline:
#     1. HTML Parsing (BeautifulSoup)
#     2. Dict Creation (html_to_dict)
#     3. MGraph Document Creation (dict_to_mgraph)
#     4. Graph Index Building
#     5. Round-trip back to HTML
#     """
#
#     enable_cprofile: bool = False                                           # Enable cProfile for detailed stats
#
#     # ═══════════════════════════════════════════════════════════════════════
#     # Main Profiling Methods
#     # ═══════════════════════════════════════════════════════════════════════
#
#     def profile_html_to_document(self, html: str) -> Profile_Result:
#         """Profile the HTML → Html_MGraph__Document conversion"""
#         from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document import Html__To__Html_MGraph__Document
#
#         phases   = []
#         html_len = len(html)
#
#         # Count approximate elements
#         element_count = html.count('<') - html.count('</')
#
#         with Timer() as total_timer:
#             with Memory_Tracker() as total_memory:
#
#                 # Phase 1: HTML Parsing (via BeautifulSoup internally)
#                 with phase_profiler("1. HTML Parsing", phases) as p1:
#                     pass
#                     # from bs4 import BeautifulSoup
#                     # soup = BeautifulSoup(html, 'html.parser')
#                     # p1.extra_metrics['tag_count'] = len(soup.find_all())
#
#                 # Phase 2: Full conversion
#                 with phase_profiler("2. Html_MGraph__Document Creation", phases) as p2:
#                     with Html__To__Html_MGraph__Document() as converter:
#                         doc = converter.convert(html)
#
#                     # Collect metrics from the document
#                     if doc and doc.body_graph:
#                         p2.node_count = len(doc.body_graph.mgraph.data().nodes_ids())
#                         p2.edge_count = len(doc.body_graph.mgraph.data().edges_ids())
#                     if doc and doc.attrs_graph:
#                         p2.extra_metrics['attrs_node_count'] = len(doc.attrs_graph.mgraph.data().nodes_ids())
#                         p2.extra_metrics['attrs_edge_count'] = len(doc.attrs_graph.mgraph.data().edges_ids())
#
#         result = Profile_Result(
#             html_size_bytes    = html_len          ,
#             html_element_count = element_count     ,
#             total_duration_ms  = total_timer.duration_ms,
#             total_memory_kb    = total_memory.delta_kb  ,
#             phases             = phases            ,
#         )
#
#         self._identify_bottlenecks(result)
#         return result
#
#     def profile_round_trip(self, html: str) -> Profile_Result:
#         """Profile the complete HTML → MGraph → HTML round-trip"""
#         from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document import Html__To__Html_MGraph__Document
#         from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html_MGraph__Document__To__Html import Html_MGraph__Document__To__Html
#
#         phases        = []
#         html_len      = len(html)
#         element_count = html.count('<') - html.count('</')
#
#         with Timer() as total_timer:
#             with Memory_Tracker() as total_memory:
#
#                 # Phase 1: HTML → Document
#                 with phase_profiler("1. HTML → Html_MGraph__Document", phases) as p1:
#                     with Html__To__Html_MGraph__Document() as converter:
#                         doc = converter.convert(html)
#                     if doc and doc.body_graph:
#                         p1.node_count = len(doc.body_graph.mgraph.data().nodes_ids())
#                         p1.edge_count = len(doc.body_graph.mgraph.data().edges_ids())
#
#                 # Phase 2: Document → HTML
#                 with phase_profiler("2. Html_MGraph__Document → HTML", phases) as p2:
#                     with Html_MGraph__Document__To__Html() as converter:
#                         result_html = converter.convert(doc)
#                     p2.extra_metrics['output_size'] = len(result_html)
#
#         result = Profile_Result(
#             html_size_bytes    = html_len               ,
#             html_element_count = element_count          ,
#             total_duration_ms  = total_timer.duration_ms,
#             total_memory_kb    = total_memory.delta_kb  ,
#             phases             = phases                 ,
#         )
#
#         self._identify_bottlenecks(result)
#         return result
#
#     def profile_with_cprofile(self, html: str) -> Profile_Result:
#         """Profile with detailed cProfile statistics"""
#         from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document import Html__To__Html_MGraph__Document
#         from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html_MGraph__Document__To__Html import Html_MGraph__Document__To__Html
#
#         profiler = cProfile.Profile()
#         profiler.enable()
#
#         # Run the transformation
#         with Html__To__Html_MGraph__Document() as to_doc:
#             doc = to_doc.convert(html)
#         with Html_MGraph__Document__To__Html() as to_html:
#             result_html = to_html.convert(doc)
#
#         profiler.disable()
#
#         # Get stats
#         stream = io.StringIO()
#         stats  = pstats.Stats(profiler, stream=stream)
#         stats.sort_stats('cumulative')
#         stats.print_stats(50)                                               # Top 50 functions
#
#         result = Profile_Result(
#             html_size_bytes    = len(html)        ,
#             html_element_count = html.count('<')  ,
#             total_duration_ms  = 0                ,
#             total_memory_kb    = 0                ,
#             cprofile_stats     = stream.getvalue(),
#         )
#
#         return result
#
#     # ═══════════════════════════════════════════════════════════════════════
#     # Scalability Testing
#     # ═══════════════════════════════════════════════════════════════════════
#
#     def profile_scalability(self, base_html: str, multipliers: List[int] = None) -> Dict[str, List[Profile_Result]]:
#         """
#         Test scalability by running with different input sizes.
#
#         Args:
#             base_html: Base HTML snippet to multiply
#             multipliers: List of multipliers for the base HTML size
#
#         Returns:
#             Dict with 'results' list and 'analysis' dict
#         """
#         if multipliers is None:
#             multipliers = [1, 2, 5, 10, 20, 50]
#
#         results = []
#         for mult in multipliers:
#             # Create scaled HTML
#             scaled_html = self._scale_html(base_html, mult)
#             result      = self.profile_round_trip(scaled_html)
#             result.extra = {'multiplier': mult}                             # Store multiplier
#             results.append(result)
#
#         # Analyze O(n) characteristics
#         analysis = self._analyze_scalability(results, multipliers)
#
#         return {
#             'results' : results ,
#             'analysis': analysis,
#         }
#
#     def _scale_html(self, base_html: str, multiplier: int) -> str:
#         """Scale HTML content by repeating body content"""
#         # Simple scaling: wrap in html/body and repeat content
#         content = f"<div>Content block {'{}'}</div>\n"
#         body    = "\n".join(content.format(i) for i in range(multiplier))
#         return f"<html><head><title>Test</title></head><body>{body}</body></html>"
#
#     def _analyze_scalability(self, results: List[Profile_Result], multipliers: List[int]) -> Dict[str, Any]:
#         """Analyze scalability characteristics from results"""
#         if len(results) < 2:
#             return {'status': 'insufficient_data'}
#
#         # Calculate growth rates
#         times   = [r.total_duration_ms for r in results]
#         sizes   = [r.html_size_bytes for r in results]
#
#         # Linear regression approximation
#         growth_ratios = []
#         for i in range(1, len(times)):
#             size_ratio = sizes[i] / sizes[0]
#             time_ratio = times[i] / times[0] if times[0] > 0 else 0
#             growth_ratios.append(time_ratio / size_ratio if size_ratio > 0 else 0)
#
#         avg_growth = sum(growth_ratios) / len(growth_ratios) if growth_ratios else 0
#
#         complexity = "O(n)"
#         if avg_growth > 1.5:
#             complexity = "O(n²) or worse"
#         elif avg_growth > 1.1:
#             complexity = "O(n log n)"
#
#         return {
#             'estimated_complexity': complexity ,
#             'avg_growth_ratio'    : avg_growth ,
#             'times_ms'            : times      ,
#             'sizes_bytes'         : sizes      ,
#             'multipliers'         : multipliers,
#         }
#
#     # ═══════════════════════════════════════════════════════════════════════
#     # Bottleneck Identification
#     # ═══════════════════════════════════════════════════════════════════════
#
#     def _identify_bottlenecks(self, result: Profile_Result):
#         """Identify performance bottlenecks from phase metrics"""
#         bottlenecks = []
#
#         # Find slowest phase
#         if result.phases:
#             slowest = max(result.phases, key=lambda p: p.duration_ms)
#             if slowest.duration_ms > result.total_duration_ms * 0.5:
#                 bottlenecks.append(
#                     f"Phase '{slowest.phase_name}' takes {slowest.duration_ms:.1f}ms "
#                     f"({100 * slowest.duration_ms / result.total_duration_ms:.0f}% of total)"
#                 )
#
#         # Memory-intensive phases
#         for phase in result.phases:
#             if phase.memory_delta_kb > 1000:                                # More than 1MB
#                 bottlenecks.append(
#                     f"Phase '{phase.phase_name}' allocates {phase.memory_delta_kb:.0f}KB"
#                 )
#
#         # High node/edge count warning
#         for phase in result.phases:
#             if phase.node_count > 1000:
#                 ratio = phase.node_count / result.html_element_count if result.html_element_count > 0 else 0
#                 bottlenecks.append(
#                     f"Phase '{phase.phase_name}' creates {phase.node_count} nodes "
#                     f"({ratio:.1f}x HTML elements)"
#                 )
#
#         result.bottlenecks = bottlenecks
#
#     # ═══════════════════════════════════════════════════════════════════════
#     # Reporting
#     # ═══════════════════════════════════════════════════════════════════════
#
#     def format_report(self, result: Profile_Result) -> str:
#         """Format a profile result as a readable report"""
#         lines = []
#         lines.append("=" * 80)
#         lines.append("HTML MGraph Performance Profile Report")
#         lines.append("=" * 80)
#         lines.append("")
#
#         # Summary
#         lines.append("SUMMARY")
#         lines.append("-" * 40)
#         lines.append(f"  Input HTML Size    : {result.html_size_bytes:,} bytes")
#         lines.append(f"  HTML Element Count : {result.html_element_count:,}")
#         lines.append(f"  Total Duration     : {result.total_duration_ms:.2f} ms")
#         lines.append(f"  Total Memory Delta : {result.total_memory_kb:.2f} KB")
#         lines.append("")
#
#         # Phase breakdown
#         if result.phases:
#             lines.append("PHASE BREAKDOWN")
#             lines.append("-" * 40)
#             for phase in result.phases:
#                 pct = (phase.duration_ms / result.total_duration_ms * 100) if result.total_duration_ms > 0 else 0
#                 lines.append(f"  {phase.phase_name}")
#                 lines.append(f"    Time     : {phase.duration_ms:8.2f} ms ({pct:5.1f}%)")
#                 lines.append(f"    Memory   : {phase.memory_delta_kb:8.2f} KB")
#                 if phase.node_count > 0:
#                     lines.append(f"    Nodes    : {phase.node_count:8,}")
#                 if phase.edge_count > 0:
#                     lines.append(f"    Edges    : {phase.edge_count:8,}")
#                 for k, v in phase.extra_metrics.items():
#                     lines.append(f"    {k:9}: {v}")
#                 lines.append("")
#
#         # Bottlenecks
#         if result.bottlenecks:
#             lines.append("IDENTIFIED BOTTLENECKS")
#             lines.append("-" * 40)
#             for b in result.bottlenecks:
#                 lines.append(f"  ⚠ {b}")
#             lines.append("")
#
#         # cProfile stats
#         if result.cprofile_stats:
#             lines.append("CPROFILE TOP FUNCTIONS")
#             lines.append("-" * 40)
#             lines.append(result.cprofile_stats)
#
#         lines.append("=" * 80)
#         return "\n".join(lines)
#
#     def print_report(self, result: Profile_Result):
#         """Print the profile report to stdout"""
#         print(self.format_report(result))
#
#     def format_scalability_report(self, analysis: Dict[str, Any]) -> str:
#         """Format scalability analysis as a report"""
#         lines = []
#         lines.append("=" * 80)
#         lines.append("SCALABILITY ANALYSIS")
#         lines.append("=" * 80)
#         lines.append("")
#
#         if 'estimated_complexity' in analysis:
#             lines.append(f"  Estimated Complexity : {analysis['estimated_complexity']}")
#             lines.append(f"  Average Growth Ratio : {analysis['avg_growth_ratio']:.2f}")
#             lines.append("")
#
#             lines.append("  Size vs Time:")
#             lines.append("  " + "-" * 50)
#             for i, (mult, size, time) in enumerate(zip(
#                 analysis['multipliers'],
#                 analysis['sizes_bytes'],
#                 analysis['times_ms']
#             )):
#                 lines.append(f"    {mult:3}x : {size:8,} bytes → {time:8.2f} ms")
#
#         lines.append("")
#         lines.append("=" * 80)
#         return "\n".join(lines)
#
#
# # ═══════════════════════════════════════════════════════════════════════════════
# # Sample HTML Test Cases
# # ═══════════════════════════════════════════════════════════════════════════════
#
# SAMPLE_HTML = {
#     'minimal': '''<html><head></head><body></body></html>''',
#
#     'simple': '''<html lang="en">
#         <head><title>Test</title></head>
#         <body><div class="container"><p>Hello</p></div></body>
#     </html>''',
#
#     'with_attrs': '''<html lang="en" dir="ltr">
#         <head><meta charset="utf-8"><title>Test</title></head>
#         <body class="main" id="app">
#             <div class="container" data-id="123" data-type="widget">
#                 <input type="text" required disabled class="form-control">
#                 <button class="btn btn-primary" onclick="submit()">Submit</button>
#             </div>
#         </body>
#     </html>''',
#
#     'complex': '''<html lang="en">
#         <head>
#             <meta charset="utf-8">
#             <meta name="viewport" content="width=device-width">
#             <title>Complex Page</title>
#             <link rel="stylesheet" href="styles.css">
#             <style>.container { display: flex; }</style>
#         </head>
#         <body class="page">
#             <header id="top-nav">
#                 <nav class="navbar">
#                     <ul class="nav-list">
#                         <li><a href="/">Home</a></li>
#                         <li><a href="/about">About</a></li>
#                         <li><a href="/contact">Contact</a></li>
#                     </ul>
#                 </nav>
#             </header>
#             <main class="content">
#                 <article class="post" data-id="1">
#                     <h1>Title</h1>
#                     <p class="intro">Introduction paragraph.</p>
#                     <p>Second paragraph with <strong>bold</strong> and <em>italic</em>.</p>
#                 </article>
#                 <aside class="sidebar">
#                     <div class="widget">Widget content</div>
#                 </aside>
#             </main>
#             <footer>
#                 <small>&copy; 2024</small>
#             </footer>
#             <script src="app.js"></script>
#             <script>console.log('loaded');</script>
#         </body>
#     </html>''',
# }
#
#
# # ═══════════════════════════════════════════════════════════════════════════════
# # Main Entry Point
# # ═══════════════════════════════════════════════════════════════════════════════
#
# def main():
#     """Run performance profiling on sample HTML"""
#     profiler = Html_MGraph__Performance__Profiler()
#
#     print("\n" + "=" * 80)
#     print("HTML MGraph Performance Profiler")
#     print("=" * 80 + "\n")
#
#     # Profile each sample
#     for name, html in SAMPLE_HTML.items():
#         print(f"\n>>> Profiling: {name}")
#         print("-" * 40)
#
#         try:
#             result = profiler.profile_round_trip(html)
#             profiler.print_report(result)
#         except ImportError as e:
#             print(f"  ⚠ Import error: {e}")
#             print("  (Run this within the mgraph_ai_service_html_graph environment)")
#         except Exception as e:
#             print(f"  ⚠ Error: {e}")
#
#     # Scalability test
#     print("\n>>> Running Scalability Analysis...")
#     print("-" * 40)
#
#     try:
#         base_html = "<div class='item' data-id='X'><p>Content</p></div>"
#         scale_results = profiler.profile_scalability(base_html, [1, 5, 10, 25, 50, 100])
#         print(profiler.format_scalability_report(scale_results['analysis']))
#     except ImportError as e:
#         print(f"  ⚠ Import error: {e}")
#     except Exception as e:
#         print(f"  ⚠ Error: {e}")
#
#
# if __name__ == "__main__":
#     main()
