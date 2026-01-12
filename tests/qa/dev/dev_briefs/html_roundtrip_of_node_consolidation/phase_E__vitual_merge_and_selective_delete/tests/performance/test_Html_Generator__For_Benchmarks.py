# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Html_Generator__For_Benchmarks
# Part of Phase E_1: Performance Analysis
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                   import TestCase
from phase_e.performance.Html_Generator__For_Benchmarks                         import Html_Generator__For_Benchmarks


class test_Html_Generator__For_Benchmarks(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.generator = Html_Generator__For_Benchmarks()

    def test__init__(self):                                                     # Test auto-initialization
        with self.generator as _:
            assert type(_).__name__ == 'Html_Generator__For_Benchmarks'

    # ═══════════════════════════════════════════════════════════════════════════
    # Paragraph Generation
    # ═══════════════════════════════════════════════════════════════════════════

    def test_generate_with_paragraphs__default(self):                           # Default parameters
        with self.generator as _:
            html = _.generate_with_paragraphs()

            assert '<html>'  in html
            assert '<body>'  in html
            assert '<p>'     in html
            assert html.count('<p>') == 10                                      # Default 10 paragraphs


    def test_generate_with_paragraphs__custom(self):                            # Custom paragraph count
        with self.generator as _:
            html = _.generate_with_paragraphs(num_paragraphs=5, words_per_para=10)

            assert html.count('<p>') == 5

    # ═══════════════════════════════════════════════════════════════════════════
    # Target Node Generation
    # ═══════════════════════════════════════════════════════════════════════════

    def test_generate_with_target_nodes__small(self):                           # Target ~100 nodes
        with self.generator as _:
            html = _.generate_with_target_nodes(100)

            assert '<html>' in html
            assert '<body>' in html
            assert len(html) > 100                                              # Has content

    def test_generate_with_target_nodes__large(self):                           # Target ~1000 nodes
        with self.generator as _:
            html = _.generate_with_target_nodes(1000)

            assert len(html) > 1000                                             # Larger content

    # ═══════════════════════════════════════════════════════════════════════════
    # Preset Sizes
    # ═══════════════════════════════════════════════════════════════════════════

    def test_generate_tiny(self):                                               # Tiny preset
        with self.generator as _:
            html = _.generate__10()

            assert '<html>' in html
            assert len(html) < 1000                                             # Small

    def test_generate_small(self):                                              # Small preset
        with self.generator as _:
            html = _.generate__100()

            assert '<html>' in html

    def test_generate_medium(self):                                             # Medium preset
        with self.generator as _:
            html = _.generate__500()

            assert '<html>' in html


    # ═══════════════════════════════════════════════════════════════════════════
    # Special Structures
    # ═══════════════════════════════════════════════════════════════════════════

    def test_generate_with_nested_divs(self):                                   # Nested div structure
        with self.generator as _:
            html = _.generate_with_nested_divs(num_sections=3, items_per_sec=4)

            assert '<div class="section-0">' in html
            assert '<div class="section-2">' in html
            assert html.count('<p>') == 12                                      # 3 sections × 4 items

    def test_generate_deep_nesting(self):                                       # Deep nesting
        with self.generator as _:
            html = _.generate_deep_nesting(depth=5)

            assert '<div><div><div><div><div>' in html
            assert 'Deep content' in html

    def test_generate_wide_structure(self):                                     # Wide (many siblings)
        with self.generator as _:
            html = _.generate_wide_structure(num_siblings=20)

            assert html.count('<span>') == 20

    def test_generate_mixed_content(self):                                      # Mixed content types
        with self.generator as _:
            html = _.generate_mixed_content(num_paragraphs=9)

            assert '<h2>'  in html
            assert '<p>'   in html
            assert '<b>'   in html
            assert '<ul>'  in html
            assert '<li>'  in html


    # ═══════════════════════════════════════════════════════════════════════════
    # HTML Structure
    # ═══════════════════════════════════════════════════════════════════════════

    def test_wrap_in_html(self):                                                # HTML wrapper
        with self.generator as _:
            html = _.wrap_in_html("<p>Test</p>")

            assert html.startswith('<html>')
            assert '<head>'  in html
            assert '<title>' in html
            assert '<body>'  in html
            assert '<p>Test</p>' in html
            assert '</html>' in html

    def test_count_approximate_nodes(self):                                     # Node count estimation
        with self.generator as _:
            html  = "<html><body><p>Hello</p><p>World</p></body></html>"
            count = _.count_approximate_nodes(html)

            assert count > 0
            assert count < 20                                                   # Reasonable estimate
