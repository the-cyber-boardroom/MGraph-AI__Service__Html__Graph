from typing                                                            import Dict, Any, Optional

from mgraph_db.mgraph.domain.Domain__MGraph__Edge import Domain__MGraph__Edge
from mgraph_db.mgraph.schemas.Schema__MGraph__Edge__Label import Schema__MGraph__Edge__Label
from mgraph_db.mgraph.schemas.identifiers.Edge_Path                    import Edge_Path
from mgraph_db.mgraph.schemas.identifiers.Node_Path                    import Node_Path
from osbot_utils.type_safe.Type_Safe                                   import Type_Safe
from mgraph_db.mgraph.MGraph                                           import MGraph
from mgraph_db.mgraph.schemas.Schema__MGraph__Node                     import Schema__MGraph__Node
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id import Node_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id import Safe_Id
from osbot_utils.type_safe.type_safe_core.decorators.type_safe import type_safe

from mgraph_ai_service_html_graph.service.html_graph.Html_MGraph__Path import Html_MGraph__Path


class Html_Dict__To__Html_MGraph(Type_Safe):                                    # Convert Html__Dict (from OSBot-Utils) to Html_MGraph
    mgraph      : MGraph            = None                                      # The MGraph being built
    path_utils  : Html_MGraph__Path = None                                      # Path computation utilities
    tag_cache   : Dict[str, str]    = None                                      # Cache for tag value nodes (tag_name -> node_id)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.path_utils is None:
            self.path_utils = Html_MGraph__Path()
        if self.tag_cache is None:
            self.tag_cache = {}

    def convert(self, html_dict: Dict[str, Any]) -> MGraph:                     # Convert Html__Dict to Html_MGraph
        self.mgraph    = MGraph()                                               # Initialize fresh graph and cache
        self.tag_cache = {}

        self.convert_element(html_dict       = html_dict        ,               # Convert root element (no parent path)
                             parent_path     = None             ,
                             position        = 0                ,
                             sibling_counts  = {'_root': 1}     )

        return self.mgraph

    def convert_element(self, html_dict      : Dict[str, Any]  ,                # Element dictionary
                              parent_path    : Optional[str]   ,                # DOM path of parent element
                              position       : int             ,                # Position among siblings (for child edge)
                              sibling_counts : Dict[str, int]  ) -> str:        # Count of each tag among siblings
        tag   = html_dict.get('tag'  , 'unknown')
        attrs = html_dict.get('attrs', {}       )

        tag_index    = self.count_preceding_siblings_with_tag(html_dict, sibling_counts)    # Compute DOM path for this element
        element_path = self.path_utils.compute_element_path(parent_path    = parent_path    ,
                                                            tag            = tag            ,
                                                            sibling_index  = tag_index      ,
                                                            sibling_counts = sibling_counts )

        element_node    = self.mgraph.edit().new_node(node_type = Schema__MGraph__Node     ,  # Create element node
                                                      node_path = Node_Path(element_path)  )
        element_node_id = element_node.node_id

        # todo: a) see the value of this extra 'tag' node (which at the moment is a unique node)
        #       b) see if we can't get the same with an edge
        #       c) find a good way to filter these nodes out from the rendered view
        # todo: add option to disable this
        tag_node_id = self.get_or_create_tag_node(tag)                                      # Link to tag value node
        self.new_edge_with_predicate(from_node_id = element_node_id,
                                     to_node_id   = tag_node_id    ,
                                     predicate    = 'tag'          )

        # todo: add option to disable this
        for attr_name, attr_value in attrs.items():                             # Process attributes
            self.add_attribute(element_node_id, attr_name, attr_value)

        child_nodes          = html_dict.get('child_nodes', [])                 # Process children (elements and text) in order
        text_nodes           = html_dict.get('text_nodes' , [])
        child_sibling_counts = self.compute_sibling_counts(child_nodes)         # Compute sibling counts for children (for path computation)
        tag_occurrence       = {}                                               # Track tag occurrence for index computation

        for child in child_nodes:                                               # Process child elements
            child_tag      = child.get('tag'     , 'unknown')
            child_position = child.get('position', 0       )

            occurrence                = tag_occurrence.get(child_tag, 0)        # Track occurrence of this tag
            tag_occurrence[child_tag] = occurrence + 1
            child['_tag_occurrence']  = occurrence                              # Store occurrence in element dict for path computation

            child_node_id = self.convert_element(html_dict      = child                ,
                                                 parent_path    = element_path         ,
                                                 position       = child_position       ,
                                                 sibling_counts = child_sibling_counts )

            # self.mgraph.edit().new_edge(from_node_id = element_node_id                 ,  # Add child edge with position
            #                             to_node_id   = child_node_id                   ,
            #                             predicate    = 'child'                         ,
            #                             edge_path    = Edge_Path(str(child_position))  )
            self.new_edge_with_predicate(from_node_id = element_node_id ,
                                         to_node_id   = child_node_id   ,
                                         predicate    = 'child'         ,
                                         edge_path    = Edge_Path(str(child_position)))

        for text_node in text_nodes:                                            # Process text nodes
            text_data     = text_node.get('data'    , '')
            text_position = text_node.get('position', 0 )

            if text_data:                                                       # Skip empty text
                text_node_id = self.create_text_node(text_data)

                # self.mgraph.edit().new_edge(from_node_id = element_node_id                ,  # Add text edge with position
                #                             to_node_id   = text_node_id                   ,
                #                             predicate    = 'text'                         ,
                #                             edge_path    = Edge_Path(str(text_position))  )
                self.new_edge_with_predicate(from_node_id = element_node_id ,
                                             to_node_id   = text_node_id    ,
                                             predicate    = 'text'          ,
                                             edge_path    = Edge_Path(str(text_position)))

        return element_node_id

    def get_or_create_tag_node(self, tag: str) -> str:                          # Get or create a value node for an HTML tag
        if tag in self.tag_cache:
            return self.tag_cache[tag]

        tag_path = self.path_utils.value_node_path('tag', tag)                  # Create tag value node with path "tag:{tag_name}"
        tag_node = self.mgraph.edit().new_value(value     = tag                 ,
                                                node_path = Node_Path(tag_path) )

        self.tag_cache[tag] = tag_node.node_id
        return tag_node.node_id

    def add_attribute(self, element_node_id : str,                              # Node ID of the element
                            attr_name       : str,                              # Attribute name
                            attr_value      : str) -> str:                      # Attribute value
        attr_path = self.path_utils.value_node_path('attr', attr_name)          # Path is "attr:{attr_name}" to enable queries
        attr_node = self.mgraph.edit().new_value(value     = attr_value              ,
                                                 node_path = Node_Path(attr_path)    )

        # self.mgraph.edit().new_edge(from_node_id = element_node_id     ,        # Link element to attribute value with attr_name in edge_path
        #                             to_node_id   = attr_node.node_id   ,
        #                             predicate    = 'attr'              ,
        #                             edge_path    = Edge_Path(attr_name))
        self.new_edge_with_predicate(from_node_id = element_node_id     ,        # Link element to attribute value with attr_name in edge_path
                                     to_node_id   = attr_node.node_id   ,
                                     predicate    = 'attr'              ,
                                     edge_path    = Edge_Path(attr_name))

        return attr_node.node_id

    def create_text_node(self, text: str) -> str:                               # Create a value node for text content
        text_path = self.path_utils.value_node_path('text')                     # Create text value node with path "text"
        text_node = self.mgraph.edit().new_value(value     = text                ,
                                                 node_path = Node_Path(text_path))
        return text_node.node_id

    def compute_sibling_counts(self, child_nodes: list) -> Dict[str, int]:      # Compute count of each tag among siblings
        counts = {}
        for child in child_nodes:
            tag         = child.get('tag', 'unknown')
            counts[tag] = counts.get(tag, 0) + 1
        return counts

    def count_preceding_siblings_with_tag(self, html_dict      : Dict[str, Any] ,   # Element dictionary (may have '_tag_occurrence' set)
                                                sibling_counts : Dict[str, int] ) -> int:  # Count of each tag among siblings
        return html_dict.get('_tag_occurrence', 0)                              # Get the index of this element among siblings with the same tag

    @type_safe
    def new_edge_with_predicate(self,
                                from_node_id: Node_Id        ,
                                to_node_id  : Node_Id        ,
                                predicate   : Safe_Id        ,
                                edge_path   : Edge_Path =None
                           ) -> Domain__MGraph__Edge:                           # Create edge with predicate label.
        edge = self.mgraph.edit().new_edge(from_node_id = from_node_id,
                                           to_node_id   = to_node_id  ,
                                           edge_path    = edge_path   )
        edge.edge.data.edge_label = Schema__MGraph__Edge__Label(predicate=predicate)
        return edge