# # ═══════════════════════════════════════════════════════════════════════════════
# # Perf_Report__Renderer__Base - Abstract base for report renderers
# # Provides common helpers for formatting
# # ═══════════════════════════════════════════════════════════════════════════════
#
# from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe
# from osbot_utils.type_safe.primitives.core.Safe_UInt                                                    import Safe_UInt
# from osbot_utils.type_safe.primitives.core.Safe_Int                                                     import Safe_Int
# from osbot_utils.type_safe.primitives.domains.numerical.safe_float.Safe_Float__Percentage_Change        import Safe_Float__Percentage_Change
# from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                          import type_safe
# from phase_e.report.schemas.Schema__Perf_Report                                                       import Schema__Perf_Report
#
#
# class Perf_Report__Renderer__Base(Type_Safe):                     # Abstract renderer base
#
#     @type_safe
#     def render(self, report: Schema__Perf_Report) -> str:         # Override in subclasses
#         raise NotImplementedError('Subclasses must implement render()')
#
#     # ═══════════════════════════════════════════════════════════════════════════
#     # Formatting Helpers
#     # ═══════════════════════════════════════════════════════════════════════════
#
#     @type_safe
#     def format_ns(self, ns: int) -> str:                          # Format nanoseconds for display
#         if ns >= 1_000_000_000:
#             return f"{ns / 1_000_000_000:.2f}s"
#         elif ns >= 1_000_000:
#             return f"{ns / 1_000_000:.2f}ms"
#         elif ns >= 1_000:
#             return f"{ns / 1_000:.2f}µs"
#         else:
#             return f"{ns}ns"
#
#     @type_safe
#     def format_ns_padded(self, ns: int, width: int = 10) -> str:  # Format with padding
#         formatted = self.format_ns(ns)
#         return f"{formatted:>{width}}"
#
#     @type_safe
#     def format_pct(self, pct: float, decimals: int = 1) -> str:   # Format percentage
#         if decimals == 0:
#             return f"{pct:.0f}%"
#         elif decimals == 1:
#             return f"{pct:.1f}%"
#         else:
#             return f"{pct:.2f}%"
#
#     @type_safe
#     def format_pct_padded(self                                ,   # Format with padding
#                           pct     : float                     ,
#                           width   : int = 6                   ,
#                           decimals: int = 1
#                      ) -> str:
#         formatted = self.format_pct(pct, decimals)
#         return f"{formatted:>{width}}"
#
#     @type_safe
#     def escape_markdown(self, text: str) -> str:                  # Escape HTML/Markdown chars
#         return (text.replace('&', '&amp;')
#                     .replace('<', '&lt;')
#                     .replace('>', '&gt;')
#                     .replace('|', '\\|'))