"""
Html_MGraph Performance Tests with Timestamp Capture
=====================================================

Performance test suite using the @timestamp decorator system
to capture detailed timing breakdowns of the Html_MGraph pipeline.

These tests are designed to:
1. Identify performance bottlenecks via self-time analysis
2. Track performance regressions over time
3. Validate optimization improvements

"""

#from unittest                                                                                    import TestCase

# from mgraph_db.utils.testing.mgraph_test_ids import mgraph_test_ids
# from osbot_utils.helpers.timestamp_capture.Timestamp_Collector                                   import Timestamp_Collector
# from osbot_utils.helpers.timestamp_capture.actions.Timestamp_Collector__Report import Timestamp_Collector__Report
#
# from osbot_utils.helpers.timestamp_capture.context_managers.timestamp_block                      import timestamp_block
# from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document import Html__To__Html_MGraph__Document
# from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html_MGraph__Document__To__Html import Html_MGraph__Document__To__Html
# from osbot_utils.utils.Dev import pprint


#class test_perf__Html_MGraph__timestamps(TestCase):

    # def test_timestamp__minimal_html(self):                                             # Capture timing breakdown for minimal HTML (baseline)
    #
    #     _timestamp_collector_ = Timestamp_Collector(name="minimal_html_conversion")
    #     #html = HTML_MINIMAL
    #     html = HTML_MEDIUM
    #     #size = 500
    #     #html = generate_scaled_html(size)
    #     with mgraph_test_ids():
    #         with _timestamp_collector_:
    #             with timestamp_block("phase.html-to-document"):
    #                 with Html__To__Html_MGraph__Document() as converter:
    #                     doc = converter.convert(html)
    #
    #             with timestamp_block("phase.document-to-html"):
    #                 with Html_MGraph__Document__To__Html() as converter:
    #                     result = converter.convert(doc)
    #
    #     # Print reports
    #     print("\n")
    #     report = Timestamp_Collector__Report(collector=_timestamp_collector_)
    #     report.print_report()
    #     report.print_hotspots(top_n=30)
    #     report.print_timeline()
    #
    #     # Basic assertions
    #     assert doc is not None
    #     assert result is not None
    #     assert _timestamp_collector_.total_duration_ms() > 0
#
#     # # ═══════════════════════════════════════════════════════════════════════
#     # # Test: Simple HTML
#     # # ═══════════════════════════════════════════════════════════════════════
#     #
#     # def test_timestamp__simple_html(self):
#     #     """Capture timing breakdown for simple HTML"""
#     #     from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document import Html__To__Html_MGraph__Document
#     #     from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html_MGraph__Document__To__Html import Html_MGraph__Document__To__Html
#     #
#     #     _timestamp_collector_ = Timestamp_Collector(name="simple_html_conversion")
#     #
#     #     with _timestamp_collector_:
#     #         with timestamp_block("phase.html_to_document"):
#     #             with Html__To__Html_MGraph__Document() as converter:
#     #                 doc = converter.convert(HTML_SIMPLE)
#     #
#     #         with timestamp_block("phase.document_to_html"):
#     #             with Html_MGraph__Document__To__Html() as converter:
#     #                 result = converter.convert(doc)
#     #
#     #     print("\n")
#     #     report = Timestamp_Collector__Report(collector=_timestamp_collector_)
#     #     report.print_report()
#     #     report.print_hotspots(top_n=10)
#     #
#     #     assert doc is not None
#     #
#     # # ═══════════════════════════════════════════════════════════════════════
#     # # Test: HTML with Attributes (suspected bottleneck)
#     # # ═══════════════════════════════════════════════════════════════════════
#     #
#     # def test_timestamp__html_with_attrs(self):
#     #     """Capture timing breakdown for attribute-heavy HTML"""
#     #     from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document import Html__To__Html_MGraph__Document
#     #     from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html_MGraph__Document__To__Html import Html_MGraph__Document__To__Html
#     #
#     #     _timestamp_collector_ = Timestamp_Collector(name="attrs_html_conversion")
#     #
#     #     with _timestamp_collector_:
#     #         with timestamp_block("phase.html_to_document"):
#     #             with Html__To__Html_MGraph__Document() as converter:
#     #                 doc = converter.convert(HTML_WITH_ATTRS)
#     #
#     #         with timestamp_block("phase.document_to_html"):
#     #             with Html_MGraph__Document__To__Html() as converter:
#     #                 result = converter.convert(doc)
#     #
#     #     print("\n")
#     #     report = Timestamp_Collector__Report(collector=_timestamp_collector_)
#     #     report.print_report()
#     #     report.print_hotspots(top_n=15)
#     #
#     #     # This test specifically targets the attrs bottleneck
#     #     # Check if attrs-related methods dominate self-time
#     #     timings = _timestamp_collector_.get_method_timings()
#     #
#     #     # Print attrs-specific breakdown if available
#     #     attrs_methods = {k: v for k, v in timings.items() if 'attrs' in k.lower()}
#     #     if attrs_methods:
#     #         print("\n  Attributes-related methods:")
#     #         for name, timing in sorted(attrs_methods.items(), key=lambda x: x[1].total_ns, reverse=True):
#     #             print(f"    {name}: {timing.total_ms():.2f}ms ({timing.call_count} calls)")
#     #
#     # # ═══════════════════════════════════════════════════════════════════════
#     # # Test: Medium HTML
#     # # ═══════════════════════════════════════════════════════════════════════
#     #
#     # def test_timestamp__medium_html(self):
#     #     """Capture timing breakdown for medium complexity HTML"""
#     #     from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document import Html__To__Html_MGraph__Document
#     #     from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html_MGraph__Document__To__Html import Html_MGraph__Document__To__Html
#     #
#     #     _timestamp_collector_ = Timestamp_Collector(name="medium_html_conversion")
#     #
#     #     with _timestamp_collector_:
#     #         with timestamp_block("phase.html_to_document"):
#     #             with Html__To__Html_MGraph__Document() as converter:
#     #                 doc = converter.convert(HTML_MEDIUM)
#     #
#     #         with timestamp_block("phase.document_to_html"):
#     #             with Html_MGraph__Document__To__Html() as converter:
#     #                 result = converter.convert(doc)
#     #
#     #     print("\n")
#     #     report = Timestamp_Collector__Report(collector=_timestamp_collector_)
#     #     report.print_report()
#     #     report.print_hotspots(top_n=15)
#     #     report.print_timeline(max_entries=50)
#     #
#     # # ═══════════════════════════════════════════════════════════════════════
#     # # Test: Scalability Analysis
#     # # ═══════════════════════════════════════════════════════════════════════
#     #
#     # def test_timestamp__scalability(self):
#     #     """Analyze how timing scales with element count"""
#     #     from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document import Html__To__Html_MGraph__Document
#     #
#     #     sizes = [5, 10, 20, 30]
#     #     results = []
#     #
#     #     print("\n  Scalability Analysis:")
#     #     print(f"  {'Elements':>10} | {'Total(ms)':>10} | {'Per-elem':>10}")
#     #     print(f"  {'-'*10} | {'-'*10} | {'-'*10}")
#     #
#     #     for size in sizes:
#     #         html = generate_scaled_html(size)
#     #
#     #         _timestamp_collector_ = Timestamp_Collector(name=f"scale_{size}")
#     #
#     #         with _timestamp_collector_:
#     #             with Html__To__Html_MGraph__Document() as converter:
#     #                 doc = converter.convert(html)
#     #
#     #         total_ms = _timestamp_collector_.total_duration_ms()
#     #         per_elem = total_ms / size
#     #
#     #         print(f"  {size:>10} | {total_ms:>10.2f} | {per_elem:>10.2f}")
#     #
#     #         results.append({
#     #             'size'    : size    ,
#     #             'total_ms': total_ms,
#     #             'per_elem': per_elem,
#     #         })
#     #
#     #     # Print detailed breakdown for largest size
#     #     print(f"\n  Detailed breakdown for {sizes[-1]} elements:")
#     #     report = Timestamp_Collector__Report(collector=_timestamp_collector_)
#     #     report.print_hotspots(top_n=10)
#     #
#     #     # Check for super-linear growth
#     #     if len(results) >= 2:
#     #         growth = results[-1]['per_elem'] / results[0]['per_elem']
#     #         print(f"\n  Growth factor (last/first per-elem): {growth:.2f}x")
#     #         if growth > 1.5:
#     #             print("  ⚠ Super-linear growth detected!")
#     #
#     # # ═══════════════════════════════════════════════════════════════════════
#     # # Test: MGraph-DB Layer Isolation
#     # # ═══════════════════════════════════════════════════════════════════════
#     #
#     # def test_timestamp__mgraph_operations(self):
#     #     """Isolate MGraph-DB operations timing"""
#     #     from mgraph_db.mgraph.MGraph import MGraph
#     #
#     #     _timestamp_collector_ = Timestamp_Collector(name="mgraph_operations")
#     #
#     #     with _timestamp_collector_:
#     #         with timestamp_block("mgraph.create"):
#     #             mgraph = MGraph()
#     #
#     #         with timestamp_block("mgraph.add_nodes"):
#     #             nodes = []
#     #             for i in range(20):
#     #                 node = mgraph.edit().new_node()
#     #                 nodes.append(node)
#     #
#     #         with timestamp_block("mgraph.add_edges"):
#     #             for i in range(len(nodes) - 1):
#     #                 mgraph.edit().new_edge(
#     #                     from_node_id=nodes[i].node_id,
#     #                     to_node_id=nodes[i + 1].node_id
#     #                 )
#     #
#     #         with timestamp_block("mgraph.add_values"):
#     #             for i in range(10):
#     #                 mgraph.edit().new_value(f"value_{i}")
#     #
#     #     print("\n")
#     #     report = Timestamp_Collector__Report(collector=_timestamp_collector_)
#     #     report.print_report()
#     #     report.print_hotspots(top_n=10)
#     #
#     #     # Analyze per-operation cost
#     #     timings = _timestamp_collector_.get_method_timings()
#     #
#     #     print("\n  Per-operation analysis:")
#     #     for name in ['mgraph.edit.new_node', 'mgraph.edit.new_edge', 'mgraph.edit.new_value']:
#     #         if name in timings:
#     #             t = timings[name]
#     #             print(f"    {name}: {t.avg_ms():.3f}ms avg ({t.call_count} calls)")
#     #
#     # # ═══════════════════════════════════════════════════════════════════════
#     # # Test: Document Setup Isolation
#     # # ═══════════════════════════════════════════════════════════════════════
#     #
#     # def test_timestamp__document_setup(self):
#     #     """Isolate Html_MGraph__Document setup timing"""
#     #     from mgraph_ai_service_html_graph.service.html_mgraph.graphs.Html_MGraph__Document import Html_MGraph__Document
#     #
#     #     _timestamp_collector_ = Timestamp_Collector(name="document_setup")
#     #
#     #     with _timestamp_collector_:
#     #         with timestamp_block("document.create_and_setup"):
#     #             doc = Html_MGraph__Document().setup()
#     #
#     #     print("\n")
#     #     report = Timestamp_Collector__Report(collector=_timestamp_collector_)
#     #     report.print_report()
#     #     report.print_hotspots(top_n=10)
#     #     report.print_timeline()
#     #
#     #     # This should reveal the 46.7ms breakdown
#     #     print(f"\n  Document setup total: {_timestamp_collector_.total_duration_ms():.2f}ms")
#     #
#     # # ═══════════════════════════════════════════════════════════════════════
#     # # Test: Index Operations Isolation
#     # # ═══════════════════════════════════════════════════════════════════════
#     #
#     # def test_timestamp__index_operations(self):
#     #     """Isolate MGraph index operation timing"""
#     #     from mgraph_db.mgraph.MGraph import MGraph
#     #
#     #     _timestamp_collector_ = Timestamp_Collector(name="index_operations")
#     #
#     #     with _timestamp_collector_:
#     #         mgraph = MGraph()
#     #
#     #         # Create nodes and observe index overhead
#     #         with timestamp_block("create_50_nodes"):
#     #             for i in range(50):
#     #                 mgraph.edit().new_node()
#     #
#     #         # Query index
#     #         with timestamp_block("index_queries"):
#     #             for _ in range(10):
#     #                 mgraph.index().nodes_by_type()
#     #                 mgraph.index().edges_by_type()
#     #
#     #     print("\n")
#     #     report = Timestamp_Collector__Report(collector=_timestamp_collector_)
#     #     report.print_report()
#     #     report.print_hotspots(top_n=10)
#     #
#     #     # Show index-related methods
#     #     timings = _timestamp_collector_.get_method_timings()
#     #     index_methods = {k: v for k, v in timings.items() if 'index' in k.lower()}
#     #     if index_methods:
#     #         print("\n  Index-related methods:")
#     #         for name, timing in sorted(index_methods.items(), key=lambda x: x[1].total_ns, reverse=True):
#     #             print(f"    {name}: {timing.total_ms():.2f}ms total, {timing.avg_ms():.3f}ms avg ({timing.call_count} calls)")
#     #
#     # # ═══════════════════════════════════════════════════════════════════════
#     # # Test: Value Node Uniqueness
#     # # ═══════════════════════════════════════════════════════════════════════
#     #
#     # def test_timestamp__value_uniqueness(self):
#     #     """Test value node uniqueness checking overhead"""
#     #     from mgraph_db.mgraph.MGraph import MGraph
#     #
#     #     _timestamp_collector_ = Timestamp_Collector(name="value_uniqueness")
#     #
#     #     with _timestamp_collector_:
#     #         mgraph = MGraph()
#     #
#     #         # Create unique values
#     #         with timestamp_block("unique_values"):
#     #             for i in range(30):
#     #                 mgraph.edit().new_value(f"unique_{i}")
#     #
#     #         # Create duplicate values (should be fast - reuse existing)
#     #         with timestamp_block("duplicate_values"):
#     #             for i in range(30):
#     #                 mgraph.edit().new_value(f"unique_{i % 10}")  # Reuse first 10
#     #
#     #     print("\n")
#     #     report = Timestamp_Collector__Report(collector=_timestamp_collector_)
#     #     report.print_report()
#     #     report.print_hotspots(top_n=10)
#     #
#     #     # Compare unique vs duplicate timing
#     #     timings = _timestamp_collector_.get_method_timings()
#     #     print("\n  Unique vs Duplicate value creation:")
#     #     if 'unique_values' in timings and 'duplicate_values' in timings:
#     #         unique_time = timings['unique_values'].total_ms()
#     #         dup_time    = timings['duplicate_values'].total_ms()
#     #         print(f"    Unique (30 new):     {unique_time:.2f}ms")
#     #         print(f"    Duplicate (30 reuse):{dup_time:.2f}ms")
#     #         print(f"    Ratio: {unique_time/dup_time:.2f}x")
#
#
# ═══════════════════════════════════════════════════════════════════════════════
# Test HTML Samples
# ═══════════════════════════════════════════════════════════════════════════════

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
#                 <p class="intro">Intro paragraph.</p>
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
#     """Generate HTML with N div elements, each with attributes"""
#     items = "\n".join(
#         f'        <div class="item item-{i}" data-id="{i}" data-type="widget">'
#         f'<span class="label">Item {i}</span></div>'
#         for i in range(element_count)
#     )
#     return f'''<html lang="en">
#     <head><title>Scaled Test ({element_count} elements)</title></head>
#     <body class="container">
#         <div class="items">{items}</div>
#     </body>
# </html>'''