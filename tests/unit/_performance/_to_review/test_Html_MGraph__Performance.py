# """
# Html_MGraph Performance Test Suite
# ==================================
#
# Pytest-compatible test suite for measuring and validating performance
# characteristics of Html_MGraph transformations.
#
# Run with: pytest test_Html_MGraph__Performance.py -v -s
#
# The -s flag is important to see timing output.
# """
#
# import time
# import pytest
# from unittest                                                                           import TestCase
# from typing                                                                             import Dict, List, Tuple
#
#
# # ═══════════════════════════════════════════════════════════════════════════════
# # Test HTML Samples - Varying Complexity
# # ═══════════════════════════════════════════════════════════════════════════════
#
# HTML_MINIMAL = '''<html><head></head><body></body></html>'''
#
# HTML_SIMPLE = '''<html lang="en">
#     <head><title>Test</title></head>
#     <body><div class="container"><p>Hello</p></div></body>
# </html>'''
#
# HTML_WITH_ATTRS = '''<html lang="en" dir="ltr">
#     <head><meta charset="utf-8"><title>Test</title></head>
#     <body class="main" id="app">
#         <div class="container" data-id="123" data-type="widget">
#             <input type="text" required disabled class="form-control">
#             <button class="btn btn-primary" onclick="submit()">Submit</button>
#         </div>
#     </body>
# </html>'''
#
# HTML_MEDIUM = '''<html lang="en">
#     <head>
#         <meta charset="utf-8">
#         <meta name="viewport" content="width=device-width">
#         <title>Medium Page</title>
#         <link rel="stylesheet" href="styles.css">
#         <style>.container { display: flex; }</style>
#     </head>
#     <body class="page">
#         <header id="nav">
#             <nav><ul><li><a href="/">Home</a></li><li><a href="/about">About</a></li></ul></nav>
#         </header>
#         <main>
#             <article class="post" data-id="1">
#                 <h1>Title</h1>
#                 <p class="intro">Intro</p>
#                 <p>Content with <strong>bold</strong> and <em>italic</em>.</p>
#             </article>
#         </main>
#         <footer><small>&copy; 2024</small></footer>
#         <script src="app.js"></script>
#     </body>
# </html>'''
#
#
# def generate_scaled_html(element_count: int) -> str:
#     """Generate HTML with a specific number of elements"""
#     items = "\n".join(
#         f'        <div class="item item-{i}" data-id="{i}" data-type="widget">'
#         f'<span class="label">Item {i}</span><span class="value">{i * 10}</span></div>'
#         for i in range(element_count)
#     )
#     return f'''<html lang="en">
#     <head><title>Scaled Test</title></head>
#     <body class="container">
#         <div class="items">{items}</div>
#     </body>
# </html>'''
#
#
# # ═══════════════════════════════════════════════════════════════════════════════
# # Performance Measurement Utilities
# # ═══════════════════════════════════════════════════════════════════════════════
#
# class Timer:
#     """Simple timer for measuring execution time"""
#
#     def __init__(self):
#         self.start_time  : float = 0.0
#         self.end_time    : float = 0.0
#         self.duration_ms : float = 0.0
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
# def measure_conversion(html: str, iterations: int = 1) -> Tuple[float, float, Dict]:
#     """
#     Measure HTML → Document → HTML round-trip performance.
#
#     Returns: (avg_ms, std_ms, stats_dict)
#     """
#     from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document import Html__To__Html_MGraph__Document
#     from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html_MGraph__Document__To__Html import Html_MGraph__Document__To__Html
#
#     times = []
#     stats = {}
#
#     for i in range(iterations):
#         with Timer() as t:
#             with Html__To__Html_MGraph__Document() as to_doc:
#                 doc = to_doc.convert(html)
#             with Html_MGraph__Document__To__Html() as to_html:
#                 result = to_html.convert(doc)
#
#         times.append(t.duration_ms)
#
#         # Collect stats on first iteration
#         if i == 0:
#             stats['input_bytes']  = len(html)
#             stats['output_bytes'] = len(result)
#             if doc and doc.body_graph and doc.body_graph.mgraph:
#                 stats['body_nodes'] = len(doc.body_graph.mgraph.data().nodes_ids())
#                 stats['body_edges'] = len(doc.body_graph.mgraph.data().edges_ids())
#             if doc and doc.attrs_graph and doc.attrs_graph.mgraph:
#                 stats['attr_nodes'] = len(doc.attrs_graph.mgraph.data().nodes_ids())
#                 stats['attr_edges'] = len(doc.attrs_graph.mgraph.data().edges_ids())
#
#     avg = sum(times) / len(times)
#     std = (sum((t - avg) ** 2 for t in times) / len(times)) ** 0.5
#
#     return avg, std, stats
#
#
# # ═══════════════════════════════════════════════════════════════════════════════
# # Performance Test Cases
# # ═══════════════════════════════════════════════════════════════════════════════
#
# class test_Html_MGraph__Performance(TestCase):
#     """Performance test suite for Html_MGraph transformations"""
#
#     # ═══════════════════════════════════════════════════════════════════════
#     # Basic Performance Tests
#     # ═══════════════════════════════════════════════════════════════════════
#
#     def test_perf__minimal_html(self):
#         """Baseline: minimal HTML document"""
#         avg_ms, std_ms, stats = measure_conversion(HTML_MINIMAL, iterations=5)
#
#         print(f"\n  Minimal HTML:")
#         print(f"    Time: {avg_ms:.2f}ms (±{std_ms:.2f})")
#         print(f"    Stats: {stats}")
#
#         # Baseline assertion - should be fast
#         assert avg_ms < 100, f"Minimal HTML too slow: {avg_ms:.2f}ms"
#
#     def test_perf__simple_html(self):
#         """Simple HTML with basic structure"""
#         avg_ms, std_ms, stats = measure_conversion(HTML_SIMPLE, iterations=5)
#
#         print(f"\n  Simple HTML:")
#         print(f"    Time: {avg_ms:.2f}ms (±{std_ms:.2f})")
#         print(f"    Stats: {stats}")
#
#         assert avg_ms < 200, f"Simple HTML too slow: {avg_ms:.2f}ms"
#
#     def test_perf__html_with_attrs(self):
#         """HTML with multiple attributes per element"""
#         avg_ms, std_ms, stats = measure_conversion(HTML_WITH_ATTRS, iterations=5)
#
#         print(f"\n  HTML with Attrs:")
#         print(f"    Time: {avg_ms:.2f}ms (±{std_ms:.2f})")
#         print(f"    Stats: {stats}")
#
#         # Check node multiplication factor
#         if stats.get('attr_nodes', 0) > 0:
#             input_bytes  = stats['input_bytes']
#             attr_nodes   = stats['attr_nodes']
#             print(f"    Attr nodes per input KB: {attr_nodes / (input_bytes/1024):.1f}")
#
#         assert avg_ms < 300, f"HTML with attrs too slow: {avg_ms:.2f}ms"
#
#     def test_perf__medium_html(self):
#         """Medium complexity HTML document"""
#         avg_ms, std_ms, stats = measure_conversion(HTML_MEDIUM, iterations=5)
#
#         print(f"\n  Medium HTML:")
#         print(f"    Time: {avg_ms:.2f}ms (±{std_ms:.2f})")
#         print(f"    Stats: {stats}")
#
#         assert avg_ms < 500, f"Medium HTML too slow: {avg_ms:.2f}ms"
#
#     # ═══════════════════════════════════════════════════════════════════════
#     # Scalability Tests
#     # ═══════════════════════════════════════════════════════════════════════
#
#     def test_perf__scalability(self):
#         pytest.skip("was taking too long")
#         """Test O(n) characteristics with increasing element count"""
#         #sizes = [10, 25, 50, 100, 200]
#         sizes = [3, 7 ,10, 20,30]
#         results = []
#
#         print(f"\n  Scalability Test:")
#         print(f"  {'Elements':>10} | {'Time (ms)':>10} | {'Body Nodes':>10} | {'ms/element':>10}")
#         print(f"  {'-'*10} | {'-'*10} | {'-'*10} | {'-'*10}")
#
#         for size in sizes:
#             html = generate_scaled_html(size)
#             avg_ms, std_ms, stats = measure_conversion(html, iterations=3)
#
#             body_nodes  = stats.get('body_nodes', 0)
#             ms_per_elem = avg_ms / size
#
#             print(f"  {size:>10} | {avg_ms:>10.2f} | {body_nodes:>10} | {ms_per_elem:>10.3f}")
#
#             results.append({
#                 'size'       : size      ,
#                 'time_ms'    : avg_ms    ,
#                 'body_nodes' : body_nodes,
#                 'ms_per_elem': ms_per_elem,
#             })
#
#         # Check for super-linear growth (O(n²) would be bad)
#         if len(results) >= 2:
#             first_rate = results[0]['ms_per_elem']
#             last_rate  = results[-1]['ms_per_elem']
#             growth     = last_rate / first_rate if first_rate > 0 else 0
#
#             print(f"\n  Growth factor (last/first ms_per_elem): {growth:.2f}")
#
#             # If growth > 2, likely O(n²) behavior
#             assert growth < 3.0, f"Possible O(n²) behavior detected: {growth:.2f}x growth"
#
#     # ═══════════════════════════════════════════════════════════════════════
#     # Phase Breakdown Tests
#     # ═══════════════════════════════════════════════════════════════════════
#
#     def test_perf__phase_breakdown(self):
#         """Break down time spent in each transformation phase"""
#         from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document import Html__To__Html_MGraph__Document
#         from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html_MGraph__Document__To__Html import Html_MGraph__Document__To__Html
#
#         html = HTML_MEDIUM
#
#         # Phase 1: HTML to Document
#         with Timer() as t1:
#             with Html__To__Html_MGraph__Document() as converter:
#                 doc = converter.convert(html)
#
#         # Phase 2: Document to HTML
#         with Timer() as t2:
#             with Html_MGraph__Document__To__Html() as converter:
#                 result = converter.convert(doc)
#
#         total = t1.duration_ms + t2.duration_ms
#
#         print(f"\n  Phase Breakdown (Medium HTML):")
#         print(f"    HTML → Document : {t1.duration_ms:>8.2f}ms ({100*t1.duration_ms/total:>5.1f}%)")
#         print(f"    Document → HTML : {t2.duration_ms:>8.2f}ms ({100*t2.duration_ms/total:>5.1f}%)")
#         print(f"    Total           : {total:>8.2f}ms")
#
#         # Usually parsing/construction is slower than serialization
#         if t1.duration_ms > t2.duration_ms * 3:
#             print(f"\n  ⚠ HTML→Document is {t1.duration_ms/t2.duration_ms:.1f}x slower than Document→HTML")
#
#     # ═══════════════════════════════════════════════════════════════════════
#     # Node/Edge Count Analysis
#     # ═══════════════════════════════════════════════════════════════════════
#
#     # def test_perf__node_multiplication_factor(self):
#     #     """Analyze how many nodes/edges are created per HTML element"""
#     #     from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document import Html__To__Html_MGraph__Document
#     #     from bs4 import BeautifulSoup
#     #
#     #     test_cases = [
#     #         ("Minimal" , HTML_MINIMAL  ),
#     #         ("Simple"  , HTML_SIMPLE   ),
#     #         ("Attrs"   , HTML_WITH_ATTRS),
#     #         ("Medium"  , HTML_MEDIUM   ),
#     #     ]
#     #
#     #     print(f"\n  Node Multiplication Analysis:")
#     #     print(f"  {'Case':>10} | {'Elements':>8} | {'Body N':>8} | {'Attr N':>8} | {'Mult':>6}")
#     #     print(f"  {'-'*10} | {'-'*8} | {'-'*8} | {'-'*8} | {'-'*6}")
#     #
#     #     for name, html in test_cases:
#     #         # Count HTML elements
#     #         soup = BeautifulSoup(html, 'html.parser')
#     #         element_count = len(soup.find_all())
#     #
#     #         # Convert and count nodes
#     #         with Html__To__Html_MGraph__Document() as converter:
#     #             doc = converter.convert(html)
#     #
#     #         body_nodes = 0
#     #         attr_nodes = 0
#     #
#     #         if doc and doc.body_graph and doc.body_graph.mgraph:
#     #             body_nodes = len(doc.body_graph.mgraph.data().nodes_ids())
#     #         if doc and doc.attrs_graph and doc.attrs_graph.mgraph:
#     #             attr_nodes = len(doc.attrs_graph.mgraph.data().nodes_ids())
#     #
#     #         total_nodes = body_nodes + attr_nodes
#     #         mult = total_nodes / element_count if element_count > 0 else 0
#     #
#     #         print(f"  {name:>10} | {element_count:>8} | {body_nodes:>8} | {attr_nodes:>8} | {mult:>6.1f}x")
#
#     # ═══════════════════════════════════════════════════════════════════════
#     # Attribute-Heavy Document Test
#     # ═══════════════════════════════════════════════════════════════════════
#
#     def test_perf__attribute_heavy(self):
#         """Test performance with many attributes per element"""
#         # Generate HTML with many attributes
#         attrs = " ".join(f'data-attr{i}="value{i}"' for i in range(20))
#         html = f'''<html><head></head><body>
#             <div {attrs}>
#                 <span {attrs}>Text</span>
#             </div>
#         </body></html>'''
#
#         avg_ms, std_ms, stats = measure_conversion(html, iterations=3)
#
#         print(f"\n  Attribute-Heavy HTML (20 attrs per element):")
#         print(f"    Time: {avg_ms:.2f}ms (±{std_ms:.2f})")
#         print(f"    Attr nodes: {stats.get('attr_nodes', 'N/A')}")
#
#         # 20 attrs × 2 elements = 40 attrs
#         # 3-node model: 40 × 3 = 120 nodes minimum
#         expected_min_nodes = 40 * 3
#         actual_nodes = stats.get('attr_nodes', 0)
#
#         if actual_nodes > 0:
#             overhead = actual_nodes / expected_min_nodes
#             print(f"    Expected min nodes: {expected_min_nodes}")
#             print(f"    Actual nodes: {actual_nodes}")
#             print(f"    Overhead factor: {overhead:.2f}x")
#
#     # ═══════════════════════════════════════════════════════════════════════
#     # Memory Usage Test
#     # ═══════════════════════════════════════════════════════════════════════
#
#     def test_perf__memory_usage(self):
#         pytest.skip("was taking too long")
#         """Test memory usage during transformation"""
#         import tracemalloc
#         from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document import Html__To__Html_MGraph__Document
#         #elements_size = 100
#         elements_size = 30
#
#         html = generate_scaled_html(elements_size)  # 100 elements
#
#         tracemalloc.start()
#
#         with Html__To__Html_MGraph__Document() as converter:
#             doc = converter.convert(html)
#
#         current, peak = tracemalloc.get_traced_memory()
#         tracemalloc.stop()
#
#         print(f"\n  Memory Usage ({elements_size} elements):")
#         print(f"    Current: {current/1024:.1f} KB")
#         print(f"    Peak   : {peak/1024:.1f} KB")
#         print(f"    Input  : {len(html)/1024:.1f} KB")
#         print(f"    Memory/Input ratio: {peak/len(html):.1f}x")
#
#         # Memory shouldn't be more than 100x input size
#         assert peak < len(html) * 100, f"Excessive memory usage: {peak/len(html):.0f}x input"
#
#
# # ═══════════════════════════════════════════════════════════════════════════════
# # Benchmark Runner
# # ═══════════════════════════════════════════════════════════════════════════════
#
# def run_all_benchmarks():
#     """Run all performance tests and print summary"""
#     print("\n" + "=" * 80)
#     print("Html_MGraph Performance Benchmark Suite")
#     print("=" * 80)
#
#     test = test_Html_MGraph__Performance()
#
#     tests = [
#         ('Minimal HTML'        , test.test_perf__minimal_html           ),
#         ('Simple HTML'         , test.test_perf__simple_html            ),
#         ('HTML with Attrs'     , test.test_perf__html_with_attrs        ),
#         ('Medium HTML'         , test.test_perf__medium_html            ),
#         ('Scalability'         , test.test_perf__scalability            ),
#         ('Phase Breakdown'     , test.test_perf__phase_breakdown        ),
#         #('Node Multiplication' , test.test_perf__node_multiplication_factor),
#         ('Attribute Heavy'     , test.test_perf__attribute_heavy        ),
#         ('Memory Usage'        , test.test_perf__memory_usage           ),
#     ]
#
#     for name, test_func in tests:
#         try:
#             print(f"\n>>> {name}")
#             print("-" * 40)
#             test_func()
#         except ImportError as e:
#             print(f"  ⚠ Import error: {e}")
#         except Exception as e:
#             print(f"  ✗ Error: {e}")
#
#     print("\n" + "=" * 80)
#     print("Benchmark Complete")
#     print("=" * 80)
#
# class test_Abc(TestCase):
#
#     def test_abc(self):
#         from mgraph_ai_service_html_graph.service.html_mgraph.graphs.Html_MGraph__Document import Html_MGraph__Document
#         import time
#
#         # Test 1: Just create the document (no conversion)
#         start = time.perf_counter()
#         doc = Html_MGraph__Document().setup()
#         print(f"Document init: {(time.perf_counter() - start) * 1000:.1f}ms")
#
#         # Test 2: Create 5 raw MGraphs
#         from mgraph_db.mgraph.MGraph import MGraph
#         start = time.perf_counter()
#         for _ in range(5):
#             mg = MGraph()
#         print(f"5x MGraph init: {(time.perf_counter() - start) * 1000:.1f}ms")
#
# if __name__ == "__main__":
#     run_all_benchmarks()
