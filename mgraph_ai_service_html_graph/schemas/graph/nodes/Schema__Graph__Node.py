from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text        import Safe_Str__Text
from osbot_utils.type_safe.primitives.domains.identifiers.Edge_Id                   import Edge_Id
from mgraph_ai_service_html_graph.schemas.graph.nodes.Schema__Graph__Node__Style    import Schema__Graph__Node__Style
from osbot_utils.type_safe.primitives.core.Safe_UInt                                import Safe_UInt
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe

# todo: review this name so that It is not confusing with the other MGraph schemas
class Schema__Graph__Node(Type_Safe):                                                     # Base node schema for all export formats
    id           : Edge_Id                                                                # Unique node identifier
    label        : Safe_Str__Text             = ''                                        # Display label
    node_type    : str                        = 'element'                                 # todo: refactor to Type_Safe primitive or enum |  Type: element, tag, attr, text
    dom_path     : str                        = ''                                        # todo: refactor to Type_Safe primitive | DOM path (e.g., "html.body.div")
    value        : str                        = None                                      # todo: refactor to Type_Safe primitive | Value for value nodes
    depth        : Safe_UInt                  = Safe_UInt(0)                              # DOM depth
    category     : str                        = ''                                        # todo: refactor to Type_Safe primitive or enum |  Tag category (structural, text, form, etc.)
    style        : Schema__Graph__Node__Style = None