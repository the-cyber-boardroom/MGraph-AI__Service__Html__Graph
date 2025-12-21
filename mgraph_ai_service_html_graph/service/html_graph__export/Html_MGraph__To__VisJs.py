# ═══════════════════════════════════════════════════════════════════════════════
# MGraph HTML Graph - vis.js Native Exporter
# Converts Html_MGraph to vis.js Network format
# https://visjs.github.io/vis-network/docs/network/
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                               import List, Dict, Any
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__Export__Base    import Html_MGraph__Export__Base
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__Data__Extractor import Extracted__Node, Extracted__Edge


class Html_MGraph__To__VisJs(Html_MGraph__Export__Base):                                  # Converts Html_MGraph to vis.js format

    def export(self) -> Dict[str, Any]:                                                   # Export to vis.js format
        return { 'nodes'  : self._convert_nodes(self.nodes)  ,
                 'edges'  : self._convert_edges(self.edges)  ,
                 'rootId' : self.root_id                     }

    def _convert_nodes(self, nodes: List[Extracted__Node]) -> List[Dict]:                 # Convert to vis.js node format
        result = []
        for node in nodes:
            vis_node = {
                'id'          : node.id                              ,
                'label'       : node.label                           ,
                'title'       : node.value or node.label             ,   # Tooltip
                'shape'       : self._map_shape(node.shape)          ,
                'color'       : {
                    'background' : node.fill_color                   ,
                    'border'     : node.border_color                 ,
                    'highlight'  : {
                        'background' : self.lighten_color(node.fill_color),
                        'border'     : '#6366f1'
                    }
                },
                'font'        : {
                    'color' : node.font_color                        ,
                    'size'  : 11 if node.node_type == 'element' else 10
                },
                'nodeType'    : node.node_type                       ,
                'domPath'     : node.dom_path                        ,
                'category'    : node.category                        ,
                'depth'       : node.depth                           ,
                'graphSource' : node.graph_source
            }
            result.append(vis_node)
        return result

    def _convert_edges(self, edges: List[Extracted__Edge]) -> List[Dict]:                 # Convert to vis.js edge format
        result = []
        for edge in edges:
            vis_edge = {
                'id'          : edge.id                              ,
                'from'        : edge.source                          ,
                'to'          : edge.target                          ,
                'dashes'      : edge.dashed                          ,
                'color'       : {
                    'color'     : edge.color                         ,
                    'highlight' : '#6366f1'
                },
                'predicate'   : edge.predicate                       ,
                'graphSource' : edge.graph_source
            }
            if edge.position is not None:
                vis_edge['position'] = edge.position
            result.append(vis_edge)
        return result

    def _map_shape(self, shape: str) -> str:                                              # Map shapes to vis.js shapes
        return {'box': 'box', 'ellipse': 'ellipse', 'note': 'box',
                'circle': 'circle', 'diamond': 'diamond'}.get(shape, 'box')