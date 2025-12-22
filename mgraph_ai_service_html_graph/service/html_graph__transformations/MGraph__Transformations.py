from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base import Graph_Transformation__Base
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__D3     import MGraph__Engine__Config__D3
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__Dot    import MGraph__Engine__Config__Dot
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__Tree   import MGraph__Engine__Config__Tree


class Graph_Transform__Default(Graph_Transformation__Base):                              # Default: body graph
    name        : str = 'default'
    label       : str = 'Default'
    description : str = 'Standard body graph visualization'


class Graph_Transform__Body_Only(Graph_Transformation__Base):                            # Body graph only
    name        : str = 'body_only'
    label       : str = 'Body Only'
    description : str = 'Only the body graph, excludes head elements'


class Graph_Transform__Head_Only(Graph_Transformation__Base):                            # Head graph only
    name        : str = 'head_only'
    label       : str = 'Head Only'
    description : str = 'Only the head graph (meta, title, links, etc.)'

    def html_mgraph__to__mgraph(self, html_mgraph):                                      # Select head graph
        if hasattr(html_mgraph, 'graph__head'):
            head_graph = html_mgraph.graph__head
            if hasattr(head_graph, 'mgraph'):
                return head_graph.mgraph
            return head_graph
        return html_mgraph


class Graph_Transform__Document(Graph_Transformation__Base):                             # Full document graph
    name        : str = 'document'
    label       : str = 'Full Document'
    description : str = 'Complete document including head and body'

    def html_mgraph__to__mgraph(self, html_mgraph):                                      # Select document graph
        if hasattr(html_mgraph, 'graph__document'):
            doc_graph = html_mgraph.graph__document
            if hasattr(doc_graph, 'mgraph'):
                return doc_graph.mgraph
            return doc_graph
        return html_mgraph


class Graph_Transform__Attributes(Graph_Transformation__Base):                           # Attributes view
    name        : str = 'attributes'
    label       : str = 'Attributes View'
    description : str = 'Focus on element attributes'

    def html_mgraph__to__mgraph(self, html_mgraph):                                      # Select attributes graph
        if hasattr(html_mgraph, 'graph__attributes'):
            attr_graph = html_mgraph.graph__attributes
            if hasattr(attr_graph, 'mgraph'):
                return attr_graph.mgraph
            return attr_graph
        return html_mgraph

    def configure_dot(self, config: MGraph__Engine__Config__Dot                          # Horizontal layout for attrs
                     ) -> MGraph__Engine__Config__Dot:
        config.rankdir        = 'LR'
        config.node_shape     = 'ellipse'
        config.node_fillcolor = '#e8f0e8'
        return config


class Graph_Transform__Scripts(Graph_Transformation__Base):                              # Scripts graph
    name        : str = 'scripts'
    label       : str = 'Scripts'
    description : str = 'Script elements and their content'

    def html_mgraph__to__mgraph(self, html_mgraph):
        if hasattr(html_mgraph, 'graph__scripts'):
            scripts_graph = html_mgraph.graph__scripts
            if hasattr(scripts_graph, 'mgraph'):
                return scripts_graph.mgraph
            return scripts_graph
        return html_mgraph


class Graph_Transform__Styles(Graph_Transformation__Base):                               # Styles graph
    name        : str = 'styles'
    label       : str = 'Styles'
    description : str = 'Style elements and their content'

    def html_mgraph__to__mgraph(self, html_mgraph):
        if hasattr(html_mgraph, 'graph__styles'):
            styles_graph = html_mgraph.graph__styles
            if hasattr(styles_graph, 'mgraph'):
                return styles_graph.mgraph
            return styles_graph
        return html_mgraph


class Graph_Transform__Structure_Only(Graph_Transformation__Base):                       # Element structure only
    name        : str = 'structure_only'
    label       : str = 'Structure Only'
    description : str = 'Element structure without text nodes'

    def configure_dot(self, config: MGraph__Engine__Config__Dot
                     ) -> MGraph__Engine__Config__Dot:
        config.node_shape     = 'box'
        config.node_style     = 'rounded'
        config.node_fillcolor = '#f0f0f0'
        return config


class Graph_Transform__Clean(Graph_Transformation__Base):                                # Clean/minimal styling
    name        : str = 'clean'
    label       : str = 'Clean'
    description : str = 'Minimal styling for clean visualization'

    def configure_dot(self, config: MGraph__Engine__Config__Dot
                     ) -> MGraph__Engine__Config__Dot:
        config.node_style     = 'filled'
        config.node_fillcolor = '#ffffff'
        config.node_fontcolor = '#000000'
        config.edge_color     = '#000000'
        config.bgcolor        = 'transparent'
        return config

    def configure_d3(self, config: MGraph__Engine__Config__D3
                    ) -> MGraph__Engine__Config__D3:
        config.include_stats = False
        return config


class Graph_Transform__Compact(Graph_Transformation__Base):                              # Compact layout
    name        : str = 'compact'
    label       : str = 'Compact'
    description : str = 'Compact layout with short labels'

    def configure_dot(self, config: MGraph__Engine__Config__Dot
                     ) -> MGraph__Engine__Config__Dot:
        config.max_label_len = 20
        config.node_sep      = 0.25
        config.rank_sep      = 0.25
        config.font_size     = 8
        return config

    def configure_tree(self, config: MGraph__Engine__Config__Tree
                      ) -> MGraph__Engine__Config__Tree:
        config.max_label_len = 30
        config.indent_size   = 1
        return config


class Graph_Transform__Expanded(Graph_Transformation__Base):                             # Expanded layout
    name        : str = 'expanded'
    label       : str = 'Expanded'
    description : str = 'Expanded layout with full labels and IDs'

    def configure_dot(self, config: MGraph__Engine__Config__Dot
                     ) -> MGraph__Engine__Config__Dot:
        config.max_label_len = 100
        config.show_node_ids = True
        config.node_sep      = 1.0
        config.rank_sep      = 1.0
        config.font_size     = 12
        return config

    def configure_tree(self, config: MGraph__Engine__Config__Tree
                      ) -> MGraph__Engine__Config__Tree:
        config.max_label_len = 100
        config.show_node_ids = True
        config.indent_size   = 4
        return config