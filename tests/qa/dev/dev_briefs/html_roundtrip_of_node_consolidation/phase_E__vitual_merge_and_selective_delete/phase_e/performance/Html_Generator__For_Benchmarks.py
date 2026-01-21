# # ═══════════════════════════════════════════════════════════════════════════════
# # Html_Generator__For_Benchmarks - Generate controlled test HTML for benchmarks
# # Part of Phase E_1: Performance Analysis
# # ═══════════════════════════════════════════════════════════════════════════════
#
# from typing                                                                     import List
# from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
# from osbot_utils.type_safe.type_safe_core.decorators.type_safe                  import type_safe
#
#
# class Html_Generator__For_Benchmarks(Type_Safe):                                # Generate controlled test HTML
#
#     # ═══════════════════════════════════════════════════════════════════════════
#     # Main Generation Methods
#     # ═══════════════════════════════════════════════════════════════════════════
#
#     @type_safe
#     def generate_with_paragraphs(self                      ,                    # Generate HTML with N paragraphs
#                                  num_paragraphs : int = 10 ,                    # Number of <p> elements
#                                  words_per_para : int = 20 ) -> str:            # Words per paragraph
#         paragraphs = []
#
#         for i in range(num_paragraphs):
#             words = [f"word{j}" for j in range(words_per_para)]
#             text  = ' '.join(words)
#             paragraphs.append(f"        <p>Paragraph {i}: {text}</p>")
#
#         body_content = '\n'.join(paragraphs)
#
#         return self.wrap_in_html(body_content)
#
#     @type_safe
#     def generate_with_target_nodes(self                    ,                    # Generate HTML targeting node count
#                                    target_nodes : int = 100) -> str:            # Approximate target node count
#         # Each <p>text</p> creates ~2-3 nodes (p element + text node)
#         # Each <div><p>text</p></div> creates ~4-5 nodes
#         # Aim for simple structure: paragraphs with text
#
#         num_paragraphs = max(1, target_nodes // 3)                              # ~3 nodes per paragraph
#
#         return self.generate_with_paragraphs(num_paragraphs=num_paragraphs,
#                                              words_per_para=5              )
#
#     @type_safe
#     def generate_with_nested_divs(self                    ,                     # Generate nested div structure
#                                   num_sections  : int = 5 ,                     # Number of sections
#                                   items_per_sec : int = 5 ) -> str:             # Items per section
#         sections = []
#
#         for s in range(num_sections):
#             items = []
#             for i in range(items_per_sec):
#                 items.append(f"            <p>Section {s} item {i}: content here</p>")
#
#             section_content = '\n'.join(items)
#             sections.append(f"        <div class=\"section-{s}\">\n{section_content}\n        </div>")
#
#         body_content = '\n'.join(sections)
#
#         return self.wrap_in_html(body_content)
#
#     @type_safe
#     def generate_deep_nesting(self                ,                             # Generate deeply nested structure
#                               depth : int = 10   ) -> str:                      # Nesting depth
#         indent  = "        "
#         content = f"{indent}{'<div>' * depth}Deep content{'</div>' * depth}"
#
#         return self.wrap_in_html(content)
#
#     @type_safe
#     def generate_wide_structure(self                   ,                        # Generate wide (many siblings) structure
#                                 num_siblings : int = 50) -> str:                # Number of sibling elements
#         siblings = []
#
#         for i in range(num_siblings):
#             siblings.append(f"        <span>Item {i}</span>")
#
#         body_content = '\n'.join(siblings)
#
#         return self.wrap_in_html(body_content)
#
#     @type_safe
#     def generate_mixed_content(self                      ,                      # Generate realistic mixed content
#                                num_paragraphs : int = 10 ) -> str:              # Number of paragraphs
#         elements = []
#
#         for i in range(num_paragraphs):
#             if i % 3 == 0:
#                 elements.append(f"        <h2>Heading {i}</h2>")
#             elif i % 3 == 1:
#                 elements.append(f"        <p>Paragraph with <b>bold</b> and <i>italic</i> text number {i}.</p>")
#             else:
#                 elements.append(f"        <ul><li>Item A</li><li>Item B</li><li>Item C</li></ul>")
#
#         body_content = '\n'.join(elements)
#
#         return self.wrap_in_html(body_content)
#
#     # ═══════════════════════════════════════════════════════════════════════════
#     # Preset Sizes
#     # ═══════════════════════════════════════════════════════════════════════════
#
#     def generate__1(self) -> str:                                             # ~10 nodes
#         return self.generate_with_paragraphs(num_paragraphs=1, words_per_para=5)
#
#     def generate__5(self) -> str:                                             # ~10 nodes
#         return self.generate_with_paragraphs(num_paragraphs=5, words_per_para=5)
#
#     def generate__10(self) -> str:                                             # ~10 nodes
#         return self.generate_with_paragraphs(num_paragraphs=10, words_per_para=5)
#
#     def generate__50(self) -> str:                                            # ~100 nodes
#         return self.generate_with_paragraphs(num_paragraphs=50, words_per_para=5)
#
#     def generate__100(self) -> str:                                            # ~100 nodes
#         return self.generate_with_paragraphs(num_paragraphs=100, words_per_para=5)
#
#     def generate__200(self) -> str:                                            # ~100 nodes
#         return self.generate_with_paragraphs(num_paragraphs=200, words_per_para=5)
#
#     def generate__300(self) -> str:                                             # 100 nodes
#         return self.generate_with_paragraphs(num_paragraphs=300, words_per_para=5)
#
#     def generate__500(self) -> str:                                             # 500 nodes
#         return self.generate_with_paragraphs(num_paragraphs=500, words_per_para=5)
#
#     def generate__1_000(self) -> str:                                            # 1,000 nodes
#         return self.generate_with_paragraphs(num_paragraphs=1_000, words_per_para=5)
#
#     def generate__10_000(self) -> str:                                           # 10,000 nodes
#         return self.generate_with_paragraphs(num_paragraphs=10_000, words_per_para=5)
#
#     def generate__100_000(self) -> str:                                          # 100,000 nodes
#         return self.generate_with_paragraphs(num_paragraphs=100_000, words_per_para=5)
#
#     # ═══════════════════════════════════════════════════════════════════════════
#     # Helper Methods
#     # ═══════════════════════════════════════════════════════════════════════════
#
#     def wrap_in_html(self, body_content: str) -> str:                           # Wrap content in HTML structure
#         return f"""<html>
#     <head>
#         <title>Benchmark Test Page</title>
#     </head>
#     <body>
# {body_content}
#     </body>
# </html>"""
#
#     @type_safe
#     def count_approximate_nodes(self, html: str) -> int:                        # Estimate node count from HTML
#         # Rough approximation: count tags + estimate text nodes
#         tag_count  = html.count('<') - html.count('</')                         # Opening tags
#         text_nodes = html.count('>') - html.count('><')                         # Text between tags
#
#         return tag_count + max(0, text_nodes // 2)
