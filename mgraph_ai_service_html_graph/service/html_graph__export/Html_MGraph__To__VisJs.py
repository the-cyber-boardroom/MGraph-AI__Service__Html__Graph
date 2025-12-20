# ═══════════════════════════════════════════════════════════════════════════════
# MGraph HTML Graph - vis.js Native Exporter
# Converts Html_MGraph to vis.js Network format
# https://visjs.github.io/vis-network/docs/network/
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                               import List, Dict, Any
from osbot_utils.type_safe.Type_Safe                                                      import Type_Safe
from mgraph_db.mgraph.MGraph                                                              import MGraph
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Config         import Html_MGraph__Render__Config
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__Data__Extractor import Html_MGraph__Data__Extractor, Extracted__Node, Extracted__Edge



class Html_MGraph__To__VisJs(Type_Safe):                                                # Converts Html_MGraph to vis.js format
    mgraph : MGraph
    config : Html_MGraph__Render__Config = None

    def export(self) -> Dict[str, Any]:                                                 # Export to vis.js format
        extractor = Html_MGraph__Data__Extractor(mgraph=self.mgraph, config=self.config)
        extractor.extract()

        return { 'nodes'  : self._convert_nodes(extractor.nodes)  ,
                 'edges'  : self._convert_edges(extractor.edges)  ,
                 'rootId' : extractor.root_id                     }

    def _convert_nodes(self, nodes: List[Extracted__Node]) -> List[Dict]:               # Convert to vis.js node format
        result = []
        for node in nodes:
            vis_node = {
                'id'       : node.id                              ,
                'label'    : node.label                           ,
                'title'    : node.value or node.label             ,  # Tooltip
                'shape'    : self._map_shape(node.shape)          ,
                'color'    : {
                    'background' : node.fill_color                ,
                    'border'     : node.border_color              ,
                    'highlight'  : {
                        'background' : self._lighten(node.fill_color),
                        'border'     : '#6366f1'
                    }
                },
                'font'     : {
                    'color' : node.font_color                     ,
                    'size'  : 11 if node.node_type == 'element' else 10
                },
                # Semantic metadata for client-side filtering/styling
                'nodeType' : node.node_type                       ,
                'domPath'  : node.dom_path                        ,
                'category' : node.category                        ,
                'depth'    : node.depth
            }
            result.append(vis_node)
        return result

    def _convert_edges(self, edges: List[Extracted__Edge]) -> List[Dict]:               # Convert to vis.js edge format
        result = []
        for edge in edges:
            vis_edge = {
                'id'        : edge.id                             ,
                'from'      : edge.source                         ,
                'to'        : edge.target                         ,
                'dashes'    : edge.dashed                         ,
                'color'     : {
                    'color'     : edge.color                      ,
                    'highlight' : '#6366f1'
                },
                'predicate' : edge.predicate
            }
            if edge.position is not None:
                vis_edge['position'] = edge.position
            result.append(vis_edge)
        return result

    def _map_shape(self, shape: str) -> str:                                            # Map shapes to vis.js shapes
        return {'box': 'box', 'ellipse': 'ellipse', 'note': 'box',
                'circle': 'circle', 'diamond': 'diamond'}.get(shape, 'box')

    def _lighten(self, hex_color: str) -> str:                                          # Lighten color for highlight
        if not hex_color or len(hex_color) != 7:
            return '#FFFFFF'
        try:
            r = min(255, int(hex_color[1:3], 16) + 30)
            g = min(255, int(hex_color[3:5], 16) + 30)
            b = min(255, int(hex_color[5:7], 16) + 30)
            return f'#{r:02x}{g:02x}{b:02x}'
        except ValueError:
            return '#FFFFFF'
