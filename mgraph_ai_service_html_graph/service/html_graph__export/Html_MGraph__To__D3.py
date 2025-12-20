# ═══════════════════════════════════════════════════════════════════════════════
# MGraph HTML Graph - D3.js Native Exporter
# Converts Html_MGraph to D3.js force-directed format
# https://d3js.org/
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                               import List, Dict, Any
from osbot_utils.type_safe.Type_Safe                                                      import Type_Safe
from mgraph_db.mgraph.MGraph                                                              import MGraph
from mgraph_ai_service_html_graph.service.html_render.Html_MGraph__Render__Config         import Html_MGraph__Render__Config
from mgraph_ai_service_html_graph.service.html_graph__export.Html_MGraph__Data__Extractor import Html_MGraph__Data__Extractor, Extracted__Node, Extracted__Edge


class Html_MGraph__To__D3(Type_Safe):                                                   # Converts Html_MGraph to D3.js format
    mgraph : MGraph
    config : Html_MGraph__Render__Config = None

    def export(self) -> Dict[str, Any]:                                                 # Export to D3.js format
        extractor = Html_MGraph__Data__Extractor(mgraph=self.mgraph, config=self.config)
        extractor.extract()

        return { 'nodes'  : self._convert_nodes(extractor.nodes)  ,
                 'links'  : self._convert_links(extractor.edges)  ,  # D3 uses 'links' not 'edges'
                 'rootId' : extractor.root_id                     }

    def _convert_nodes(self, nodes: List[Extracted__Node]) -> List[Dict]:               # Convert to D3 node format
        result = []
        for node in nodes:
            d3_node = {
                'id'        : node.id                             ,
                'label'     : node.label                          ,
                'color'     : node.fill_color                     ,
                'fontColor' : node.font_color                     ,
                'radius'    : self._calculate_radius(node)        ,
                # Semantic metadata
                'nodeType'  : node.node_type                      ,
                'domPath'   : node.dom_path                       ,
                'category'  : node.category                       ,
                'depth'     : node.depth
            }
            if node.value:
                d3_node['value'] = node.value
            result.append(d3_node)
        return result

    def _convert_links(self, edges: List[Extracted__Edge]) -> List[Dict]:               # Convert to D3 link format
        result = []
        for edge in edges:
            d3_link = {
                'source'    : edge.source                         ,
                'target'    : edge.target                         ,
                'color'     : edge.color                          ,
                'dashed'    : edge.dashed                         ,
                'width'     : 2 if edge.predicate == 'child' else 1,
                'predicate' : edge.predicate
            }
            if edge.position is not None:
                d3_link['position'] = edge.position
            result.append(d3_link)
        return result

    def _calculate_radius(self, node: Extracted__Node) -> int:                          # Calculate node radius
        base = {'element': 25, 'tag': 20, 'attr': 18, 'text': 22}.get(node.node_type, 20)
        return base + min(len(node.label) // 5, 10)
