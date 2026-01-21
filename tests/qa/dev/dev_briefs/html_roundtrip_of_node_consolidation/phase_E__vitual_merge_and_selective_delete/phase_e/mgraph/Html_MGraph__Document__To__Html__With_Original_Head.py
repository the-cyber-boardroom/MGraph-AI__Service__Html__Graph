# ═══════════════════════════════════════════════════════════════════════════════
# Html_MGraph__Document__To__Html__With_Original_Head
# ═══════════════════════════════════════════════════════════════════════════════
#
# Patched converter that reconstructs HTML from MGraph but preserves the original
# <head> section from the source html_dict.
#
# This works around a bug where MGraph→HTML reconstruction corrupts/duplicates
# elements in the <head> section.
#
# Usage:
#     converter = Html_MGraph__Document__To__Html__With_Original_Head(
#         original_html_dict=html_dict
#     )
#     html = converter.convert(document)
#
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                          import Optional

from osbot_utils.helpers.html.transformers.Html_Dict__To__Html import Html_Dict__To__Html
from osbot_utils.type_safe.Type_Safe                                                                 import Type_Safe
from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html_MGraph__Document__To__Html_Dict import Html_MGraph__Document__To__Html_Dict



class Html_MGraph__Document__To__Html__With_Original_Head(Type_Safe):
    """Convert MGraph to HTML, preserving original <head> from source html_dict."""

    original_html_dict: dict = None                                             # Original L2 html_dict with correct head

    def convert(self, document) -> str:                                         # Convert document to HTML with original head
        # Step 1: Convert MGraph to html_dict
        converted_dict = Html_MGraph__Document__To__Html_Dict().convert(document)

        # Step 2: Patch the head if we have original
        if self.original_html_dict:
            patched_dict = self.patch_head(converted_dict, self.original_html_dict)
        else:
            patched_dict = converted_dict

        # Step 3: Convert patched dict to HTML
        html = Html_Dict__To__Html(root=patched_dict).convert()

        return html

    def patch_head(self, converted_dict: dict, original_dict: dict) -> dict:    # Replace head in converted dict with original
        original_head  = self.find_head(original_dict)

        if original_head is None:
            return converted_dict                                               # No head to patch

        # Find and replace head in converted dict
        self.replace_head(converted_dict, original_head)

        return converted_dict

    def find_head(self, html_dict: dict) -> Optional[dict]:                     # Find <head> element in html_dict
        if not html_dict:
            return None

        tag = html_dict.get('tag', '')

        if tag == 'head':
            return html_dict

        # Search in child nodes
        nodes = html_dict.get('nodes', [])
        for node in nodes:
            if isinstance(node, dict):
                result = self.find_head(node)
                if result:
                    return result

        return None

    def replace_head(self, html_dict: dict, original_head: dict) -> bool:       # Replace head element in place
        if not html_dict:
            return False

        nodes = html_dict.get('nodes', [])

        for i, node in enumerate(nodes):
            if isinstance(node, dict):
                if node.get('tag') == 'head':
                    # Found it - replace with original
                    nodes[i] = original_head
                    return True

                # Recurse into children
                if self.replace_head(node, original_head):
                    return True

        return False


# ═══════════════════════════════════════════════════════════════════════════════
# Convenience function
# ═══════════════════════════════════════════════════════════════════════════════

def convert_mgraph_to_html_with_original_head(document, original_html_dict: dict) -> str:
    """Convenience function to convert MGraph to HTML preserving original head."""
    converter = Html_MGraph__Document__To__Html__With_Original_Head(
        original_html_dict=original_html_dict
    )
    return converter.convert(document)