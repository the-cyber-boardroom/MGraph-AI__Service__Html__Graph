from typing                                                                       import Dict, Any, Optional, Callable
from mgraph_ai_service_html_graph.schemas.enums.Enum__Html_Render__Preset         import Enum__Html_Render__Preset
from osbot_utils.type_safe.Type_Safe                                              import Type_Safe
from mgraph_db.mgraph.actions.exporters.dot.MGraph__Export__Dot                   import MGraph__Export__Dot
from mgraph_db.mgraph.domain.Domain__MGraph__Node                                 import Domain__MGraph__Node
from mgraph_db.mgraph.domain.Domain__MGraph__Edge                                 import Domain__MGraph__Edge
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Colors import Html_MGraph__Render__Colors, Enum__Html_Render__Color_Scheme
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Labels import Html_MGraph__Render__Labels


class Html_MGraph__Render__Config(Type_Safe):                                               # Configuration for HTML-aware MGraph visualization using path-based styling
    colors           : Html_MGraph__Render__Colors                                          # Color scheme manager
    labels           : Html_MGraph__Render__Labels                                          # Label generation utilities
    preset           : Enum__Html_Render__Preset = Enum__Html_Render__Preset.FULL_DETAIL

    # Filter settings
    show_tag_nodes   : bool = True                                                          # Show tag value nodes
    show_attr_nodes  : bool = True                                                          # Show attribute value nodes
    show_text_nodes  : bool = True                                                          # Show text value nodes

    # Edge filter settings
    show_tag_edges   : bool = True                                                          # Show edges to tag nodes
    show_attr_edges  : bool = True                                                          # Show edges to attr nodes
    show_text_edges  : bool = True                                                          # Show edges to text nodes
    show_child_edges : bool = True                                                          # Show child edges

    # Node shape settings
    element_shape    : str  = 'box'                                                         # Shape for element nodes
    tag_shape        : str  = 'ellipse'                                                     # Shape for tag value nodes
    attr_shape       : str  = 'box'                                                         # Shape for attribute value nodes (box for better text fit)
    text_shape       : str  = 'note'                                                        # Shape for text value nodes

    # Edge style settings
    child_edge_style : str  = 'solid'                                                       # Style for child edges
    tag_edge_style   : str  = 'dashed'                                                      # Style for tag edges
    attr_edge_style  : str  = 'dotted'                                                      # Style for attr edges
    text_edge_style  : str  = 'solid'                                                       # Style for text edges

    # Internal tracking
    _filtered_nodes  : Dict[str, bool]                                                     # Track which nodes to filter


    # ═══════════════════════════════════════════════════════════════════════════════
    # Preset Application
    # ═══════════════════════════════════════════════════════════════════════════════

    def apply_preset(self, preset: Enum__Html_Render__Preset) -> 'Html_MGraph__Render__Config':  # Apply a rendering preset
        self.preset = preset

        if preset == Enum__Html_Render__Preset.STRUCTURE_ONLY:
            self.show_tag_nodes  = False
            self.show_attr_nodes = False
            self.show_text_nodes = False
            self.show_tag_edges  = False
            self.show_attr_edges = False
            self.show_text_edges = False

        elif preset == Enum__Html_Render__Preset.MINIMAL:
            self.show_tag_nodes  = False
            self.show_attr_nodes = False
            self.show_text_nodes = False
            self.show_tag_edges  = False
            self.show_attr_edges = False
            self.show_text_edges = False

        elif preset == Enum__Html_Render__Preset.FULL_DETAIL:
            self.show_tag_nodes  = True
            self.show_attr_nodes = True
            self.show_text_nodes = True
            self.show_tag_edges  = True
            self.show_attr_edges = True
            self.show_text_edges = True

        return self

    def set_color_scheme(self, scheme: Enum__Html_Render__Color_Scheme) -> 'Html_MGraph__Render__Config':  # Set color scheme
        self.colors.scheme = scheme
        return self

    # ═══════════════════════════════════════════════════════════════════════════════
    # DOT Exporter Configuration
    # ═══════════════════════════════════════════════════════════════════════════════

    def configure_dot_export(self, dot: MGraph__Export__Dot) -> MGraph__Export__Dot:        # Configure MGraph__Export__Dot with HTML-aware settings
        self._apply_graph_settings(dot)                                                     # Apply graph-level settings
        self._apply_global_node_settings(dot)                                               # Apply global node settings
        self._apply_global_edge_settings(dot)                                               # Apply global edge settings

        dot.on_add_node = self._create_node_callback()                                      # Set up callbacks for path-based styling
        dot.on_add_edge = self._create_edge_callback()

        #dot.set_graph__rank_dir__lr()
        return dot

    def _apply_graph_settings(self, dot: MGraph__Export__Dot):                              # Apply graph-level DOT settings for HTML trees
        dot.set_graph__rank_dir__tb()                                                       # Top-to-bottom for DOM hierarchy
        dot.set_graph__splines__ortho()                                                     # Right-angle edges for tree structure
        dot.set_graph__node_sep(0.5)                                                        # Horizontal spacing
        dot.set_graph__rank_sep(0.75)                                                       # Vertical spacing

    def _apply_global_node_settings(self, dot: MGraph__Export__Dot):                        # Apply default node styling
        dot.set_node__shape__type__box()
        dot.set_node__shape__rounded()
        dot.set_node__font__size(10)

    def _apply_global_edge_settings(self, dot: MGraph__Export__Dot):                        # Apply default edge styling
        dot.set_edge__font__size(8)
        dot.set_edge__arrow_size(0.5)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Callback Factories
    # ═══════════════════════════════════════════════════════════════════════════════

    def _create_node_callback(self) -> Callable[[Domain__MGraph__Node, Dict[str, Any]], Dict[str, Any]]:  # Create callback for node styling based on node_path
        def on_add_node(node: Domain__MGraph__Node, node_data: Dict[str, Any]) -> Dict[str, Any]:
            node_path = self._get_node_path(node)
            attrs     = node_data.get('attrs', [])

            if not isinstance(attrs, list):                                                  # Ensure attrs is a list
                attrs = []

            if node_path.startswith('tag:'):                                                # Style based on path type
                if not self.show_tag_nodes:
                    self._filtered_nodes[str(node.node_id)] = True
                    return node_data
                self._apply_tag_node_styling(node, node_path, attrs)

            elif node_path.startswith('attr:'):
                if not self.show_attr_nodes:
                    self._filtered_nodes[str(node.node_id)] = True
                    return node_data
                self._apply_attr_node_styling(node, node_path, attrs)

            elif node_path == 'text':
                if not self.show_text_nodes:
                    self._filtered_nodes[str(node.node_id)] = True
                    return node_data
                self._apply_text_node_styling(node, attrs)

            else:                                                                            # Element node
                self._apply_element_node_styling(node, node_path, attrs)

            node_data['attrs'] = attrs
            return node_data

        return on_add_node

    def _create_edge_callback(self) -> Callable[[Domain__MGraph__Edge, Domain__MGraph__Node, Domain__MGraph__Node, Dict[str, Any]], None]:  # Create callback for edge styling based on predicate
        def on_add_edge(edge       : Domain__MGraph__Edge  ,
                        from_node  : Domain__MGraph__Node  ,
                        to_node    : Domain__MGraph__Node  ,
                        edge_data  : Dict[str, Any]        ) -> None:

            predicate = self._get_edge_predicate(edge)
            attrs     = edge_data.get('attrs', [])

            if not isinstance(attrs, list):
                attrs = []

            to_node_id = str(to_node.node_id) if to_node else None                          # Check if target node is filtered

            if to_node_id and to_node_id in self._filtered_nodes:                           # Don't style edges to filtered nodes
                edge_data['_filtered'] = True
                return

            if predicate == 'child':                                                        # Apply predicate-based styling
                if not self.show_child_edges:
                    edge_data['_filtered'] = True
                    return
                self._apply_child_edge_styling(attrs)

            elif predicate == 'tag':
                if not self.show_tag_edges:
                    edge_data['_filtered'] = True
                    return
                self._apply_tag_edge_styling(attrs)

            elif predicate == 'attr':
                if not self.show_attr_edges:
                    edge_data['_filtered'] = True
                    return
                self._apply_attr_edge_styling(attrs)

            elif predicate == 'text':
                if not self.show_text_edges:
                    edge_data['_filtered'] = True
                    return
                self._apply_text_edge_styling(attrs)

            edge_data['attrs'] = attrs

        return on_add_edge

    # ═══════════════════════════════════════════════════════════════════════════════
    # Node Styling Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def _apply_element_node_styling(self, node: Domain__MGraph__Node, node_path: str, attrs: list):  # Apply styling to element nodes
        depth      = self.labels.get_path_depth(node_path)
        fill_color = self.colors.get_element_color(depth)
        font_color = self.colors.get_font_color('element')
        label      = self.labels.label_for_element_node(node_path)

        attrs.append(f'shape="{self.element_shape}"')
        attrs.append(f'fillcolor="{fill_color}"')
        attrs.append(f'fontcolor="{font_color}"')
        attrs.append(f'label="{label}"')
        attrs.append('style="filled,rounded"')

    def _apply_tag_node_styling(self, node: Domain__MGraph__Node, node_path: str, attrs: list):  # Apply styling to tag value nodes
        tag_name   = node_path[4:] if node_path.startswith('tag:') else ''                  # Remove 'tag:' prefix
        fill_color = self.colors.get_tag_color(tag_name)
        font_color = self.colors.get_font_color('tag')

        value = self._get_node_value(node)
        label = self.labels.label_for_tag_node(node_path, value)

        attrs.append(f'shape="{self.tag_shape}"')
        attrs.append(f'fillcolor="{fill_color}"')
        attrs.append(f'fontcolor="{font_color}"')
        attrs.append(f'label="{label}"')
        attrs.append('style="filled"')

    def _apply_attr_node_styling(self, node: Domain__MGraph__Node, node_path: str, attrs: list):  # Apply styling to attribute value nodes
        fill_color = self.colors.get_attr_color()
        font_color = self.colors.get_font_color('attr')

        value = self._get_node_value(node)
        label = self.labels.label_for_attr_node(node_path, value)
        label = self._escape_dot_string(label)                                              # Escape for DOT

        attrs.append(f'shape="{self.attr_shape}"')
        attrs.append(f'fillcolor="{fill_color}"')
        attrs.append(f'fontcolor="{font_color}"')
        attrs.append(f'label="{label}"')
        attrs.append('style="filled,rounded"')                                              # Rounded box for attrs
        attrs.append('fontsize="9"')                                                        # Slightly smaller font for long values

    def _apply_text_node_styling(self, node: Domain__MGraph__Node, attrs: list):            # Apply styling to text value nodes
        fill_color = self.colors.get_text_color()
        font_color = self.colors.get_font_color('text')

        value = self._get_node_value(node)
        label = self.labels.label_for_text_node(value)
        label = self._escape_dot_string(label)                                              # Escape for DOT

        attrs.append(f'shape="{self.text_shape}"')
        attrs.append(f'fillcolor="{fill_color}"')
        attrs.append(f'fontcolor="{font_color}"')
        attrs.append(f'label="{label}"')
        attrs.append('style="filled"')

    # ═══════════════════════════════════════════════════════════════════════════════
    # Edge Styling Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def _apply_child_edge_styling(self, attrs: list):                                       # Apply styling to child edges
        color = self.colors.get_edge_color('child')
        attrs.append(f'color="{color}"')
        attrs.append(f'style="{self.child_edge_style}"')

    def _apply_tag_edge_styling(self, attrs: list):                                         # Apply styling to tag edges
        color = self.colors.get_edge_color('tag')
        attrs.append(f'color="{color}"')
        attrs.append(f'style="{self.tag_edge_style}"')

    def _apply_attr_edge_styling(self, attrs: list):                                        # Apply styling to attr edges
        color = self.colors.get_edge_color('attr')
        attrs.append(f'color="{color}"')
        attrs.append(f'style="{self.attr_edge_style}"')

    def _apply_text_edge_styling(self, attrs: list):                                        # Apply styling to text edges
        color = self.colors.get_edge_color('text')
        attrs.append(f'color="{color}"')
        attrs.append(f'style="{self.text_edge_style}"')

    # ═══════════════════════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def _get_node_path(self, node: Domain__MGraph__Node) -> str:                            # Extract node_path from node
        if node and node.node and node.node.data and node.node.data.node_path:
            return str(node.node.data.node_path)
        return ''

    def _get_node_value(self, node: Domain__MGraph__Node) -> Optional[str]:                 # Extract value from value node
        if hasattr(node, 'node_data') and hasattr(node.node_data, 'value'):
            return str(node.node_data.value)
        return None

    def _get_edge_predicate(self, edge: Domain__MGraph__Edge) -> str:                       # Extract predicate from edge label
        if edge and edge.edge and edge.edge.data:
            edge_label = edge.edge.data.edge_label
            if edge_label and hasattr(edge_label, 'predicate') and edge_label.predicate:
                return str(edge_label.predicate)
        return ''

    def _escape_dot_string(self, text: str) -> str:                                         # Escape special characters for DOT format
        if not text:
            return ''
        return text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')