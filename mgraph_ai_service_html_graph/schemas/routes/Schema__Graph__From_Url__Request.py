from osbot_utils.type_safe.primitives.domains.numerical.safe_int.Safe_Int__Positive import Safe_Int__Positive
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url            import Safe_Str__Url
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Config   import Enum__Html_Render__Preset
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Colors   import Enum__Html_Render__Color_Scheme


class Schema__Graph__From_Url__Request(Type_Safe):                                                # Request schema for URL to graph conversion
    url             : Safe_Str__Url                   = ''                                        # URL to fetch HTML from
    timeout         : Safe_Int__Positive              = 30                                        # Request timeout in seconds
    preset          : Enum__Html_Render__Preset       = Enum__Html_Render__Preset.FULL_DETAIL     # Render preset
    show_tag_nodes  : bool                            = True                                      # Show tag value nodes
    show_attr_nodes : bool                            = True                                      # Show attribute value nodes
    show_text_nodes : bool                            = True                                      # Show text value nodes
    color_scheme    : Enum__Html_Render__Color_Scheme = Enum__Html_Render__Color_Scheme.DEFAULT   # Color scheme