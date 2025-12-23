from typing                                                                                         import Any, Dict, List
from time                                                                                           import perf_counter
import re
from mgraph_db.mgraph.MGraph                                                                        import MGraph
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base    import Graph_Transformation__Base
from mgraph_ai_service_html_graph.service.html_mgraph.Html_MGraph                                   import Html_MGraph
from mgraph_ai_service_html_graph.service.html_mgraph.graphs.Html_MGraph__Document                  import Html_MGraph__Document
from mgraph_db.mgraph.schemas.identifiers.Node_Path                                                 import Node_Path
from osbot_utils.helpers.html.transformers.Html__To__Html_Dict                                      import Html__To__Html_Dict
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id                                   import Node_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Obj_Id                                    import Obj_Id


# ═══════════════════════════════════════════════════════════════════════════
# Custom Value Types for Semantic Coloring
# ═══════════════════════════════════════════════════════════════════════════

class Metric__Time(str):          pass
class Metric__Count(str):         pass
class Metric__Graph_Name(str):    pass


# ═══════════════════════════════════════════════════════════════════════════
# Color Configuration
# ═══════════════════════════════════════════════════════════════════════════

COLOR_TIME          = '#C8E6C9'
COLOR_COUNT         = '#BBDEFB'
COLOR_GRAPH_NAME    = '#E1BEE7'
COLOR_EDGE          = '#78909C'

CLUSTER_COLORS = {
    'body'   : '#E3F2FD',
    'head'   : '#E8F5E9',
    'attrs'  : '#FFF3E0',
    'scripts': '#FCE4EC',
    'styles' : '#F3E5F5',
}

CLUSTER_LABELS = {
    'body'   : 'Body Graph',
    'head'   : 'Head Graph',
    'attrs'  : 'Attributes Graph',
    'scripts': 'Scripts Graph',
    'styles' : 'Styles Graph',
}

SCRIPT_TAGS = {'script'}
STYLE_TAGS  = {'style', 'link'}


class Html_Use_Case__Performance_Stats(Graph_Transformation__Base):
    """Performance Statistics with per-graph timing and DOT cluster visualization."""

    name        : str  = "html-use-case-performance-stats"
    label       : str  = "Performance Stats"
    description : str  = "Detailed parsing performance with clustered graph breakdown"

    stats       : Dict = None
    dot_code    : str  = None
    node_to_cluster : Dict = None  # Maps node IDs to cluster names

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 1: Instrumented HTML parsing with per-graph timing
    # ═══════════════════════════════════════════════════════════════════════════

    def html__to__html_mgraph(self, html: str) -> Html_MGraph:
        self.stats = self._parse_with_detailed_timing(html)
        return None

    def _parse_with_detailed_timing(self, html: str) -> Dict:
        stats = {
            'total_time_ms'    : 0,
            'html_dict_time_ms': 0,
            'setup_time_ms'    : 0,
            'graphs'           : {
                'body'   : {'time_ms': 0, 'nodes': 0, 'edges': 0, 'elements': 0, 'text_nodes': 0},
                'head'   : {'time_ms': 0, 'nodes': 0, 'edges': 0, 'elements': 0, 'text_nodes': 0},
                'attrs'  : {'time_ms': 0, 'nodes': 0, 'edges': 0, 'attributes': 0},
                'scripts': {'time_ms': 0, 'nodes': 0, 'edges': 0, 'scripts': 0},
                'styles' : {'time_ms': 0, 'nodes': 0, 'edges': 0, 'styles': 0},
            }
        }

        total_start = perf_counter()

        t0 = perf_counter()
        html_dict = Html__To__Html_Dict(html=html).convert()
        stats['html_dict_time_ms'] = round((perf_counter() - t0) * 1000, 2)

        t0 = perf_counter()
        document = Html_MGraph__Document().setup()
        stats['setup_time_ms'] = round((perf_counter() - t0) * 1000, 2)

        html_attrs = html_dict.get('attrs', {})
        for position, (attr_name, attr_value) in enumerate(html_attrs.items()):
            document.attrs_graph.add_attribute(document.root_id, attr_name, attr_value, position)

        head_dict, body_dict = self._extract_head_body(html_dict)

        if head_dict:
            t0 = perf_counter()
            self._process_head_timed(document, head_dict, stats['graphs'])
            stats['graphs']['head']['time_ms'] = round((perf_counter() - t0) * 1000, 2)

        if body_dict:
            t0 = perf_counter()
            self._process_body_timed(document, body_dict, stats['graphs'])
            stats['graphs']['body']['time_ms'] = round((perf_counter() - t0) * 1000, 2)

        # Time attrs graph operations (already done inline, estimate from node count)
        # For more accurate timing, we'd need to wrap attrs_graph operations

        self._collect_final_counts(document, stats['graphs'])
        stats['total_time_ms'] = round((perf_counter() - total_start) * 1000, 2)

        return stats

    def _extract_head_body(self, html_dict):
        head_dict = None
        body_dict = None
        for node in html_dict.get('nodes', []):
            if isinstance(node, dict) and 'tag' in node:
                tag = node.get('tag', '').lower()
                if tag == 'head':
                    head_dict = node
                elif tag == 'body':
                    body_dict = node
        return head_dict, body_dict

    def _process_head_timed(self, document, head_dict, graph_stats):
        head_node_id = Node_Id(Obj_Id())
        document.head_graph.create_element(node_path=Node_Path('head'), node_id=head_node_id)
        document.head_graph.set_root(head_node_id)
        document.attrs_graph.register_element(head_node_id, 'head')
        graph_stats['head']['elements'] += 1

        head_attrs = head_dict.get('attrs', {})
        for position, (attr_name, attr_value) in enumerate(head_attrs.items()):
            document.attrs_graph.add_attribute(head_node_id, attr_name, attr_value, position)
            graph_stats['attrs']['attributes'] += 1

        self._process_children_timed(document, head_node_id, head_dict, 'head',
                                     document.head_graph, graph_stats, 'head')

    def _process_body_timed(self, document, body_dict, graph_stats):
        body_node_id = Node_Id(Obj_Id())
        document.body_graph.create_element(node_path=Node_Path('body'), node_id=body_node_id)
        document.body_graph.set_root(body_node_id)
        document.attrs_graph.register_element(body_node_id, 'body')
        graph_stats['body']['elements'] += 1

        body_attrs = body_dict.get('attrs', {})
        for position, (attr_name, attr_value) in enumerate(body_attrs.items()):
            document.attrs_graph.add_attribute(body_node_id, attr_name, attr_value, position)
            graph_stats['attrs']['attributes'] += 1

        self._process_children_timed(document, body_node_id, body_dict, 'body',
                                     document.body_graph, graph_stats, 'body')

    def _process_children_timed(self, document, parent_id, parent_dict, parent_path,
                                 graph, graph_stats, graph_name):
        nodes = parent_dict.get('nodes', [])
        tag_counts = {}
        tag_occurrence = {}

        for node in nodes:
            if isinstance(node, dict) and 'tag' in node:
                tag = node.get('tag', '').lower()
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        for position, node in enumerate(nodes):
            if not isinstance(node, dict):
                continue

            if self._is_text_node(node):
                text = node.get('data', '')
                if text.strip():
                    graph.create_text(text=text, parent_id=parent_id, position=position)
                    graph_stats[graph_name]['text_nodes'] += 1

            elif 'tag' in node:
                tag = node.get('tag', '').lower()
                tag_index = tag_occurrence.get(tag, 0)
                tag_occurrence[tag] = tag_index + 1

                if tag_counts.get(tag, 0) > 1:
                    node_path = f"{parent_path}.{tag}[{tag_index}]"
                else:
                    node_path = f"{parent_path}.{tag}"

                node_id = Node_Id(Obj_Id())
                graph.create_element(node_path=Node_Path(node_path), node_id=node_id)
                graph.add_child(parent_id, node_id, position)
                graph_stats[graph_name]['elements'] += 1

                document.attrs_graph.register_element(node_id, tag)
                attrs = node.get('attrs', {})
                for attr_pos, (attr_name, attr_value) in enumerate(attrs.items()):
                    document.attrs_graph.add_attribute(node_id, attr_name, attr_value, attr_pos)
                    graph_stats['attrs']['attributes'] += 1

                if tag in SCRIPT_TAGS:
                    content = self._extract_text_content(node)
                    document.scripts_graph.register_script(node_id, content)
                    graph_stats['scripts']['scripts'] += 1
                elif tag in STYLE_TAGS:
                    if tag == 'link':
                        document.styles_graph.register_link(node_id)
                    else:
                        content = self._extract_text_content(node)
                        document.styles_graph.register_style(node_id, content)
                    graph_stats['styles']['styles'] += 1
                else:
                    self._process_children_timed(document, node_id, node, node_path,
                                                  graph, graph_stats, graph_name)

    def _is_text_node(self, node):
        return node.get('type') == 'TEXT' or ('data' in node and 'tag' not in node)

    def _extract_text_content(self, node):
        texts = []
        for child in node.get('nodes', []):
            if isinstance(child, dict) and self._is_text_node(child):
                text = child.get('data', '')
                if text.strip():
                    texts.append(text)
        return ''.join(texts) if texts else None

    def _collect_final_counts(self, document, graph_stats):
        graph_sources = [
            ('body'   , document.body_graph   ),
            ('head'   , document.head_graph   ),
            ('attrs'  , document.attrs_graph  ),
            ('scripts', document.scripts_graph),
            ('styles' , document.styles_graph ),
        ]

        for name, graph in graph_sources:
            if graph and graph.mgraph:
                mg = graph.mgraph
                graph_stats[name]['nodes'] = len(mg.data().nodes_ids())
                graph_stats[name]['edges'] = len(mg.data().edges_ids())

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 2: Build stats graph with cluster tracking
    # ═══════════════════════════════════════════════════════════════════════════

    def html_mgraph__to__mgraph(self, html_mgraph: Html_MGraph) -> MGraph:
        if not self.stats:
            return None

        self.node_to_cluster = {}  # Track which nodes belong to which cluster
        mgraph = MGraph()

        with mgraph.builder() as builder:
            builder.add_node("Html_MGraph Performance")

            # Global timing (unique keys) - these stay outside clusters
            builder.add_predicate("total_time", Metric__Time(f"{self.stats['total_time_ms']} ms"), key="global_total_time")
            builder.root()
            builder.add_predicate("parse_html", Metric__Time(f"{self.stats['html_dict_time_ms']} ms"), key="global_parse_html")
            builder.root()
            builder.add_predicate("setup", Metric__Time(f"{self.stats['setup_time_ms']} ms"), key="global_setup")
            builder.root()

            total_nodes = sum(g.get('nodes', 0) for g in self.stats['graphs'].values())
            total_edges = sum(g.get('edges', 0) for g in self.stats['graphs'].values())

            builder.add_predicate("total_nodes", Metric__Count(str(total_nodes)), key="global_total_nodes")
            builder.root()
            builder.add_predicate("total_edges", Metric__Count(str(total_edges)), key="global_total_edges")
            builder.root()

            # Per-graph breakdown - track keys for clustering
            for graph_name, gs in self.stats['graphs'].items():
                # Graph name node
                graph_key = f"{graph_name}_graph"
                builder.add_connected_node(Metric__Graph_Name(f"{graph_name.title()} Graph"))
                self._track_key(graph_key, graph_name)

                # Time
                time_key = f"{graph_name}_time"
                builder.add_predicate("time", Metric__Time(f"{gs['time_ms']} ms"), key=time_key)
                self._track_key(time_key, graph_name)
                builder.up()

                # Nodes count
                nodes_key = f"{graph_name}_nodes"
                builder.add_predicate("nodes", Metric__Count(str(gs['nodes'])), key=nodes_key)
                self._track_key(nodes_key, graph_name)
                builder.up()

                # Edges count
                edges_key = f"{graph_name}_edges"
                builder.add_predicate("edges", Metric__Count(str(gs['edges'])), key=edges_key)
                self._track_key(edges_key, graph_name)
                builder.up()

                # Graph-specific metrics
                if graph_name in ('body', 'head'):
                    elements_key = f"{graph_name}_elements"
                    builder.add_predicate("elements", Metric__Count(str(gs.get('elements', 0))), key=elements_key)
                    self._track_key(elements_key, graph_name)
                    builder.up()

                    text_key = f"{graph_name}_text_nodes"
                    builder.add_predicate("text_nodes", Metric__Count(str(gs.get('text_nodes', 0))), key=text_key)
                    self._track_key(text_key, graph_name)
                    builder.up()

                elif graph_name == 'attrs':
                    attrs_key = f"{graph_name}_attributes"
                    builder.add_predicate("attributes", Metric__Count(str(gs.get('attributes', 0))), key=attrs_key)
                    self._track_key(attrs_key, graph_name)
                    builder.up()

                elif graph_name == 'scripts':
                    scripts_key = f"{graph_name}_scripts_count"
                    builder.add_predicate("scripts", Metric__Count(str(gs.get('scripts', 0))), key=scripts_key)
                    self._track_key(scripts_key, graph_name)
                    builder.up()

                elif graph_name == 'styles':
                    styles_key = f"{graph_name}_styles_count"
                    builder.add_predicate("styles", Metric__Count(str(gs.get('styles', 0))), key=styles_key)
                    self._track_key(styles_key, graph_name)
                    builder.up()

                builder.root()

        return mgraph

    def _track_key(self, key: str, cluster: str):
        """Track which keys belong to which cluster."""
        self.node_to_cluster[key] = cluster

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 3: Generate DOT and post-process with clusters
    # ═══════════════════════════════════════════════════════════════════════════

    def transform_mgraph(self, mgraph: MGraph) -> MGraph:
        if mgraph is None:
            return None

        base_dot = self._create_base_dot(mgraph)
        self.dot_code = self._add_clusters_to_dot(base_dot)
        return None

    def _create_base_dot(self, mgraph: MGraph) -> str:
        with mgraph.export().export_dot() as dot:
            dot.set_graph__rank_dir__tb()
            #dot.set_graph__splines__ortho()
            dot.set_graph__splines__polyline()
            dot.set_graph__node_sep(0.5)
            dot.set_graph__rank_sep(0.6)

            dot.show_node__value()
            dot.show_edge__predicate__str()

            dot.set_node__shape__type__box()
            dot.set_node__shape__rounded()
            dot.set_node__fill_color('#E0E0E0')

            dot.set_value_type_fill_color(Metric__Time      , COLOR_TIME      )
            dot.set_value_type_fill_color(Metric__Count     , COLOR_COUNT     )
            dot.set_value_type_fill_color(Metric__Graph_Name, COLOR_GRAPH_NAME)

            dot.set_edge__color(COLOR_EDGE)
            dot.set_edge__arrow_head__vee()

            return dot.process_graph()

    def _add_clusters_to_dot(self, dot_code: str) -> str:
        """Post-process DOT to wrap graph-related nodes in clusters."""

        lines = dot_code.split('\n')

        # Separate into components
        header_lines = []
        node_lines = []
        edge_lines = []
        footer_lines = []

        in_graph = False
        for line in lines:
            stripped = line.strip()

            if stripped.startswith('digraph') or stripped.startswith('graph ['):
                header_lines.append(line)
                in_graph = True
            elif stripped == '}':
                footer_lines.append(line)
            elif '->' in stripped:
                edge_lines.append(line)
            elif stripped and in_graph:
                if stripped.startswith('node [') or stripped.startswith('edge ['):
                    header_lines.append(line)
                else:
                    node_lines.append(line)

        # Build node_id -> line mapping
        node_id_to_line = {}
        node_id_to_label = {}
        for line in node_lines:
            # Extract node ID: "node_id" [label="..."]
            match = re.match(r'\s*"([^"]+)"\s*\[', line)
            if match:
                node_id = match.group(1)
                node_id_to_line[node_id] = line
                # Extract label
                label_match = re.search(r'label="([^"]*)"', line)
                if label_match:
                    node_id_to_label[node_id] = label_match.group(1)

        # Parse edges to build parent->children mapping
        edges = []  # List of (from_id, to_id)
        for line in edge_lines:
            match = re.match(r'\s*"([^"]+)"\s*->\s*"([^"]+)"', line)
            if match:
                edges.append((match.group(1), match.group(2)))

        # Find graph name nodes and their cluster
        graph_node_to_cluster = {}
        for node_id, label in node_id_to_label.items():
            for cluster_name in CLUSTER_COLORS.keys():
                if f'{cluster_name.title()} Graph' in label:
                    graph_node_to_cluster[node_id] = cluster_name
                    break

        # Find all children of each graph node (nodes connected via edges FROM the graph node)
        cluster_nodes = {name: set() for name in CLUSTER_COLORS.keys()}

        for graph_node_id, cluster_name in graph_node_to_cluster.items():
            # Add the graph node itself
            cluster_nodes[cluster_name].add(graph_node_id)

            # Find all nodes reachable from this graph node
            self._collect_descendants(graph_node_id, edges, cluster_nodes[cluster_name])

        # Identify global nodes (not in any cluster)
        all_clustered_nodes = set()
        for nodes in cluster_nodes.values():
            all_clustered_nodes.update(nodes)

        global_node_ids = set(node_id_to_line.keys()) - all_clustered_nodes

        # Rebuild DOT with clusters
        new_lines = []
        new_lines.extend(header_lines)
        new_lines.append('')

        # Add global nodes first
        new_lines.append('  // Global nodes')
        for node_id in global_node_ids:
            new_lines.append(f'  {node_id_to_line[node_id]}')
        new_lines.append('')

        # Add clusters
        for cluster_name in CLUSTER_COLORS.keys():
            nodes = cluster_nodes[cluster_name]
            if nodes:
                color = CLUSTER_COLORS[cluster_name]
                label = CLUSTER_LABELS[cluster_name]

                new_lines.append(f'  subgraph cluster_{cluster_name} {{')
                new_lines.append(f'    label="{label}";')
                new_lines.append(f'    style=filled;')
                new_lines.append(f'    fillcolor="{color}";')
                new_lines.append(f'    color="#666666";')
                new_lines.append(f'    fontname="Arial";')
                new_lines.append(f'    fontsize=12;')
                new_lines.append('')

                for node_id in nodes:
                    if node_id in node_id_to_line:
                        new_lines.append(f'    {node_id_to_line[node_id]}')

                new_lines.append('  }')
                new_lines.append('')

        # Add edges
        new_lines.append('  // Edges')
        new_lines.extend(edge_lines)
        new_lines.append('')

        new_lines.extend(footer_lines)

        return '\n'.join(new_lines)

    def _collect_descendants(self, node_id: str, edges: list, collected: set):
        """Recursively collect all descendants of a node via outgoing edges."""
        for from_id, to_id in edges:
            if from_id == node_id and to_id not in collected:
                collected.add(to_id)
                self._collect_descendants(to_id, edges, collected)

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 5: Return clustered DOT
    # ═══════════════════════════════════════════════════════════════════════════

    def transform_export(self, output: Any) -> Any:
        return self.dot_code