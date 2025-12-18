from typing                                                                                      import Dict, Any
from mgraph_ai_service_html_graph.service.html_graph.Html_Dict__To__Html_MGraph                  import Schema__Config__Html_Dict__To__Html_MGraph
from mgraph_ai_service_html_graph.service.html_graph.Html_MGraph                                 import Html_MGraph
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base import Graph_Transformation__Base


class Html_Use_Case__1(Graph_Transformation__Base):
    name        : str = "html_use_case__1"
    label       : str = "Html Use Case 1"
    description : str = "This is the Html Use Case 1"

    # Phase 1: Raw HTML Manipulation
    def transform_html(self, html):
        return html

    # Phase 2: Html_Dict Manipulation
    def transform_dict(self, html_dict: Dict[str, Any]) -> Dict[str, Any]:          # Remove text_nodes from dict, appending text to element labels.
        return html_dict

    # Phase 3: MGraph Creation
    def create_mgraph(self, html_dict: Dict[str, Any], config: Any):                # Create Html_MGraph from dict
        #pprint(html_dict)
        with Schema__Config__Html_Dict__To__Html_MGraph() as config:
            config.add_tag_nodes       = False
            config.add_attribute_nodes = False

        return Html_MGraph.from_html_dict(html_dict=html_dict, config=config)

    # Phase 4: MGraph Transformation
    def transform_mgraph(self, html_mgraph):
        print()
        nodes = html_mgraph.mgraph.graph.model.data.nodes
        for node_id, node in nodes.items():
            if node.node_path == 'text':
                node.node_path = ""
            #print(node.node_path)
            #node.node.

        return html_mgraph

    #     #return  "<html><div>with one div<p>and a paragraph</p></html>"
    #     return  "<html><body><div>This is an <a href=''>link</a> with some <b>bold<b> in the mix</div><div>this is the <i>2nd div</i> in here</body></html>"