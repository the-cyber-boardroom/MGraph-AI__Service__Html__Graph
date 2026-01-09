# ═══════════════════════════════════════════════════════════════════════════════
# Html__To__Html_Dict__With__Node_Ids - HTML parser with unique node_id assignment
# Extends Html__To__Html_Dict to add node_id to every element and text node
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.helpers.html.transformers.Html__To__Html_Dict  import Html__To__Html_Dict
from osbot_utils.helpers.html.transformers.Html__To__Html_Dict  import STRING__SCHEMA_NODES
from osbot_utils.type_safe.primitives.domains.identifiers.Obj_Id import Obj_Id

STRING__NODE_ID = 'node_id'

"""Parse HTML to dict with unique node_id on every node.

Part of "html_roundtrip_of_node_consolidation" Phased development.
See: PHASE_A__brief.md
"""
# todo: see best way to refactor this with main Html__To__Html_Dict


class Html__To__Html_Dict__With__Node_Ids(Html__To__Html_Dict):                 # HTML parser with node_id assignment

    def handle_starttag(self, tag, attrs):                                      # Add node_id to element nodes
        was_root = self.current is None                                         # Track if this will be root
        super().handle_starttag(tag, attrs)

        if tag.lower() not in self.void_elements:
            self.current[STRING__NODE_ID] = self.generate_node_id()             # Regular elements: self.current is the new tag
        elif was_root:
            self.current[STRING__NODE_ID] = self.generate_node_id()             # Root void element (rare): add to current
        else:
            nodes = self.current[STRING__SCHEMA_NODES]                          # Void elements: appended to parent's nodes
            if nodes:
                nodes[-1][STRING__NODE_ID] = self.generate_node_id()

    def handle_data(self, data):                                                # Add node_id to text nodes
        super().handle_data(data)

        if data.strip():                                                        # Same condition as parent
            nodes = self.current[STRING__SCHEMA_NODES]
            if nodes:
                nodes[-1][STRING__NODE_ID] = self.generate_node_id()

    def generate_node_id(self) -> str:                                          # Generate unique node ID
        return str(Obj_Id())