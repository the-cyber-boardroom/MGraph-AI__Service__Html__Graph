# ═══════════════════════════════════════════════════════════════════════════════
# MGraph HTML Graph - Cytoscape.js Native Exporter
# Converts Html_MGraph to Cytoscape.js format
# https://js.cytoscape.org/
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                               import List, Dict, Any
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__Export__Base    import Html_MGraph__Export__Base
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__Data__Extractor import Extracted__Node, Extracted__Edge


class Html_MGraph__To__Cytoscape(Html_MGraph__Export__Base):                              # Converts Html_MGraph to Cytoscape format

    def export(self) -> Dict[str, Any]:                                                   # Export to Cytoscape format
        return { 'elements' : { 'nodes' : self._convert_nodes(self.nodes) ,
                                'edges' : self._convert_edges(self.edges) },
                 'rootId'   : self.root_id                                 }

    def _convert_nodes(self, nodes: List[Extracted__Node]) -> List[Dict]:                 # Convert to Cytoscape node format
        result = []
        for node in nodes:
            cy_node = {
                'data': {
                    'id'          : node.id                       ,
                    'label'       : node.label                    ,
                    'color'       : node.fill_color               ,
                    'fontColor'   : node.font_color               ,
                    'borderColor' : node.border_color             ,
                    'nodeType'    : node.node_type                ,
                    'domPath'     : node.dom_path                 ,
                    'category'    : node.category                 ,
                    'depth'       : node.depth                    ,
                    'graphSource' : node.graph_source
                },
                'group': 'nodes'
            }
            if node.value:
                cy_node['data']['value'] = node.value
            result.append(cy_node)
        return result

    def _convert_edges(self, edges: List[Extracted__Edge]) -> List[Dict]:                 # Convert to Cytoscape edge format
        result = []
        for edge in edges:
            cy_edge = {
                'data': {
                    'id'          : edge.id                       ,
                    'source'      : edge.source                   ,
                    'target'      : edge.target                   ,
                    'color'       : edge.color                    ,
                    'dashed'      : edge.dashed                   ,
                    'predicate'   : edge.predicate                ,
                    'graphSource' : edge.graph_source
                },
                'group': 'edges'
            }
            if edge.position is not None:
                cy_edge['data']['position'] = edge.position
            result.append(cy_edge)
        return result