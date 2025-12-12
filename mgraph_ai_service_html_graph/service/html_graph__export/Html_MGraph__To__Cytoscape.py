# ═══════════════════════════════════════════════════════════════════════════════
# MGraph HTML Graph - Cytoscape.js Native Exporter
# Converts Html_MGraph to Cytoscape.js format
# https://js.cytoscape.org/
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                             import List, Dict, Any
from osbot_utils.type_safe.Type_Safe                                                    import Type_Safe
from mgraph_db.mgraph.MGraph                                                            import MGraph
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Config       import Html_MGraph__Render__Config
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__Data__Extractor import (
    Html_MGraph__Data__Extractor, Extracted__Node, Extracted__Edge
)


class Html_MGraph__To__Cytoscape(Type_Safe):                                            # Converts Html_MGraph to Cytoscape format
    mgraph : MGraph
    config : Html_MGraph__Render__Config = None

    def export(self) -> Dict[str, Any]:                                                 # Export to Cytoscape format
        extractor = Html_MGraph__Data__Extractor(mgraph=self.mgraph, config=self.config)
        extractor.extract()

        return { 'elements' : {
                     'nodes' : self._convert_nodes(extractor.nodes) ,
                     'edges' : self._convert_edges(extractor.edges)
                 },
                 'rootId' : extractor.root_id                       }

    def _convert_nodes(self, nodes: List[Extracted__Node]) -> List[Dict]:               # Convert to Cytoscape node format
        result = []
        for node in nodes:
            cy_node = {
                'data': {
                    'id'          : node.id                       ,
                    'label'       : node.label                    ,
                    'color'       : node.fill_color               ,
                    'fontColor'   : node.font_color               ,
                    'borderColor' : node.border_color             ,
                    # Semantic metadata
                    'nodeType'    : node.node_type                ,
                    'domPath'     : node.dom_path                 ,
                    'category'    : node.category                 ,
                    'depth'       : node.depth
                },
                'group': 'nodes'
            }
            if node.value:
                cy_node['data']['value'] = node.value
            result.append(cy_node)
        return result

    def _convert_edges(self, edges: List[Extracted__Edge]) -> List[Dict]:               # Convert to Cytoscape edge format
        result = []
        for edge in edges:
            cy_edge = {
                'data': {
                    'id'        : edge.id                         ,
                    'source'    : edge.source                     ,
                    'target'    : edge.target                     ,
                    'color'     : edge.color                      ,
                    'dashed'    : edge.dashed                     ,
                    'predicate' : edge.predicate
                },
                'group': 'edges'
            }
            if edge.position is not None:
                cy_edge['data']['position'] = edge.position
            result.append(cy_edge)
        return result
