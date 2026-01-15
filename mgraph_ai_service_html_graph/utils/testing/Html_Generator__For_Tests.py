# ═══════════════════════════════════════════════════════════════════════════════
# Test__Helpers - Test data factories and helper utilities
# Provides in-memory cache service and sample HTML for testing
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                      import Tuple
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                   import type_safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html        import Safe_Str__Html


# ═══════════════════════════════════════════════════════════════════════════════
# HTML Generator for Tests (matches Html_Generator__For_Benchmarks pattern)
# ═══════════════════════════════════════════════════════════════════════════════

class Html_Generator__For_Tests(Type_Safe):                                      # Generate test HTML

    @type_safe
    def simple_html(self) -> Safe_Str__Html:                                     # Simple HTML document
        return Safe_Str__Html("""<html>
    <head><title>Test Page</title></head>
    <body>
        <h1>Test Heading</h1>
        <p>Test paragraph with <b>bold</b> text.</p>
    </body>
</html>""")

    @type_safe
    def minimal_html(self) -> Safe_Str__Html:                                    # Minimal HTML
        return Safe_Str__Html("<html><body><p>Hello</p></body></html>")

    @type_safe
    def nested_html(self) -> Safe_Str__Html:                                     # Nested structure
        return Safe_Str__Html("""<html>
    <body>
        <div class="container">
            <div class="section">
                <p>Paragraph 1</p>
                <p>Paragraph 2</p>
            </div>
        </div>
    </body>
</html>""")

    @type_safe
    def generate_with_paragraphs(self                      ,                     # Generate HTML with N paragraphs
                                 num_paragraphs : int = 10 ,
                                 words_per_para : int = 20 ) -> str:
        paragraphs = []
        for i in range(num_paragraphs):
            words = [f"word{j}" for j in range(words_per_para)]
            text  = ' '.join(words)
            paragraphs.append(f"        <p>Paragraph {i}: {text}</p>")
        body_content = '\n'.join(paragraphs)
        return self.wrap_in_html(body_content)

    @type_safe
    def generate_mixed_content(self, num_paragraphs: int = 10) -> str:           # Realistic mixed content
        elements = []
        for i in range(num_paragraphs):
            if i % 3 == 0:
                elements.append(f"        <h2>Heading {i}</h2>")
            elif i % 3 == 1:
                elements.append(f"        <p>Paragraph with <b>bold</b> and <i>italic</i> text {i}.</p>")
            else:
                elements.append(f"        <ul><li>Item A</li><li>Item B</li><li>Item C</li></ul>")
        body_content = '\n'.join(elements)
        return self.wrap_in_html(body_content)

    def wrap_in_html(self, body_content: str) -> str:                            # Wrap content in HTML
        return f"""<html>
    <head><title>Test Page</title></head>
    <body>
{body_content}
    </body>
</html>"""

    @type_safe
    def html_with_paragraphs(self, count: int = 5) -> Safe_Str__Html:            # HTML with N paragraphs
        paragraphs = '\n'.join([f'        <p>Paragraph {i}</p>' for i in range(count)])
        return Safe_Str__Html(f"""<html>
    <body>
{paragraphs}
    </body>
</html>""")
