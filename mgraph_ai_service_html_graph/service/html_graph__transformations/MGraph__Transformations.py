from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base import Graph_Transformation__Base
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__D3     import MGraph__Engine__Config__D3
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__Dot    import MGraph__Engine__Config__Dot
from mgraph_ai_service_html_graph.service.mgraph__engines.schemas.MGraph__Engine__Config__Tree   import MGraph__Engine__Config__Tree
















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