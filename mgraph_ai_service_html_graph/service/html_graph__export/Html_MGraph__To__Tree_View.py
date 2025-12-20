from osbot_utils.decorators.methods.cache_on_self                import cache_on_self
from mgraph_ai_service_html_graph.service.html_graph.Html_MGraph import Html_MGraph
from osbot_utils.type_safe.Type_Safe                             import Type_Safe


class Html_MGraph__To__Tree_View(Type_Safe):
    html_mgraph : Html_MGraph

    def export_tree(self):
        #return self.html_mgraph.mgraph.export().to__json()
        with self.export_tree_values() as _:
            trees = _.process_graph().get('trees')
            if len(trees) == 1:
                return trees[0]
            return {}

    def export_tree__as_text(self):
        tree = self.export_tree()
        return self.export_tree_values().format_as_text(tree=tree)

    @cache_on_self
    def export_tree_values(self):
        root_nodes_ids = [self.html_mgraph.root_id]

        with self.html_mgraph.mgraph.export() as _:
            return _.export_tree_values(root_nodes_ids=root_nodes_ids)