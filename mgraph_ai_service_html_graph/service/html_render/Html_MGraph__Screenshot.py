from typing                                                                       import Optional
from osbot_utils.type_safe.Type_Safe                                              import Type_Safe
from mgraph_db.mgraph.actions.MGraph__Screenshot                                  import MGraph__Screenshot
from mgraph_db.mgraph.MGraph                                                      import MGraph
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Config import Html_MGraph__Render__Config, Enum__Html_Render__Preset
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Colors import Enum__Html_Render__Color_Scheme


class Html_MGraph__Screenshot(Type_Safe):                                                   # Screenshot generation for HTML MGraph with semantic styling
    mgraph      : MGraph                                                                    # The MGraph to visualize
    config      : Html_MGraph__Render__Config                                               # Rendering configuration
    screenshot  : MGraph__Screenshot           = None                                       # The underlying screenshot instance
    target_file : str                          = None                                       # Target file path for saving
    png_bytes   : bytes                        = None                                       # Generated PNG bytes

    def setup(self) -> 'Html_MGraph__Screenshot':                                           # Initialize the screenshot with HTML-aware configuration
        if self.mgraph is None:
            raise ValueError("mgraph must be provided")

        self.screenshot = MGraph__Screenshot(graph=self.mgraph.graph)                       # Create base screenshot

        with self.screenshot.export().export_dot() as dot:                                  # Configure DOT exporter with HTML-aware settings
            self.config.configure_dot_export(dot)
            self.show_attrs(False)
            #self.show_text(False)
            dot.set_graph__layout_engine__fdp()
            dot.set_graph__splines__line()
            dot.set_graph__spring_constant(0.5)
            #dot.set_graph__overlap__scale()
            # self.structure_only()
            # dot.set_graph__node_sep(2.0)   # More horizontal space
            # dot.set_graph__rank_sep(2.5)   # More vertical space
            # dot.set_graph__overlap__ortho()

        return self

    # ═══════════════════════════════════════════════════════════════════════════════
    # Configuration Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def set_preset(self, preset: Enum__Html_Render__Preset) -> 'Html_MGraph__Screenshot':   # Set rendering preset
        self.config.apply_preset(preset)
        return self

    def set_color_scheme(self, scheme: Enum__Html_Render__Color_Scheme) -> 'Html_MGraph__Screenshot':  # Set color scheme
        self.config.set_color_scheme(scheme)
        return self

    def set_target_file(self, path: str) -> 'Html_MGraph__Screenshot':                      # Set target file path
        self.target_file = path
        return self

    # ═══════════════════════════════════════════════════════════════════════════════
    # Preset Shortcuts
    # ═══════════════════════════════════════════════════════════════════════════════

    def full_detail(self) -> 'Html_MGraph__Screenshot':                                     # Configure for full detail view
        return self.set_preset(Enum__Html_Render__Preset.FULL_DETAIL)

    def structure_only(self) -> 'Html_MGraph__Screenshot':                                  # Configure for structure-only view
        return self.set_preset(Enum__Html_Render__Preset.STRUCTURE_ONLY)

    def minimal(self) -> 'Html_MGraph__Screenshot':                                         # Configure for minimal view
        return self.set_preset(Enum__Html_Render__Preset.MINIMAL)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Color Scheme Shortcuts
    # ═══════════════════════════════════════════════════════════════════════════════

    def default_colors(self) -> 'Html_MGraph__Screenshot':                                  # Use default color scheme
        return self.set_color_scheme(Enum__Html_Render__Color_Scheme.DEFAULT)

    def monochrome(self) -> 'Html_MGraph__Screenshot':                                      # Use monochrome color scheme
        return self.set_color_scheme(Enum__Html_Render__Color_Scheme.MONOCHROME)

    def high_contrast(self) -> 'Html_MGraph__Screenshot':                                   # Use high contrast color scheme
        return self.set_color_scheme(Enum__Html_Render__Color_Scheme.HIGH_CONTRAST)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Rendering Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def render(self, print_dot_code: bool = False) -> bytes:                                # Render the graph and return PNG bytes
        self.setup()                                                                        # Ensure setup is done

        if self.target_file:
            self.screenshot.save_to(self.target_file)

        self.png_bytes = self.screenshot.dot(print_dot_code=print_dot_code)
        return self.png_bytes

    def save_to(self, path: str) -> 'Html_MGraph__Screenshot':                              # Set save path and return self for chaining
        self.target_file = path
        return self

    def dot(self, print_dot_code: bool = False) -> bytes:                                   # Generate PNG using Graphviz DOT
        return self.render(print_dot_code=print_dot_code)

    def dot_code(self) -> str:                                                              # Get the DOT code without rendering
        self.setup()
        return self.screenshot.export().export_dot().to_dict()

    # ═══════════════════════════════════════════════════════════════════════════════
    # Filtering Configuration
    # ═══════════════════════════════════════════════════════════════════════════════

    def show_tags(self, show: bool = True) -> 'Html_MGraph__Screenshot':                    # Configure tag node visibility
        self.config.show_tag_nodes = show
        self.config.show_tag_edges = show
        return self

    def show_attrs(self, show: bool = True) -> 'Html_MGraph__Screenshot':                   # Configure attribute node visibility
        self.config.show_attr_nodes = show
        self.config.show_attr_edges = show
        return self

    def show_text(self, show: bool = True) -> 'Html_MGraph__Screenshot':                    # Configure text node visibility
        self.config.show_text_nodes = show
        self.config.show_text_edges = show
        return self

    # ═══════════════════════════════════════════════════════════════════════════════
    # Style Configuration
    # ═══════════════════════════════════════════════════════════════════════════════

    def set_max_text_length(self, length: int) -> 'Html_MGraph__Screenshot':                # Set maximum text display length
        self.config.labels.max_text_length = length
        return self

    def set_element_shape(self, shape: str) -> 'Html_MGraph__Screenshot':                   # Set shape for element nodes
        self.config.element_shape = shape
        return self

    def set_tag_shape(self, shape: str) -> 'Html_MGraph__Screenshot':                       # Set shape for tag nodes
        self.config.tag_shape = shape
        return self

    def set_attr_shape(self, shape: str) -> 'Html_MGraph__Screenshot':                      # Set shape for attribute nodes
        self.config.attr_shape = shape
        return self

    def set_text_shape(self, shape: str) -> 'Html_MGraph__Screenshot':                      # Set shape for text nodes
        self.config.text_shape = shape
        return self

    # ═══════════════════════════════════════════════════════════════════════════════
    # Graph Settings
    # ═══════════════════════════════════════════════════════════════════════════════

    def set_title(self, title: str) -> 'Html_MGraph__Screenshot':                           # Set graph title
        if self.screenshot:
            with self.screenshot.export().export_dot() as dot:
                dot.set_graph__title(title)
        return self

    def set_background_color(self, color: str) -> 'Html_MGraph__Screenshot':                # Set background color
        if self.screenshot:
            with self.screenshot.export().export_dot() as dot:
                dot.set_graph__background__color(color)
        return self
