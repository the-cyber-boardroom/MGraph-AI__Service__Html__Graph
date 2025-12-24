from typing                                                                                         import Any, Dict, List, Set
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
    """Performance Statistics with accurate per-graph timing and clustered visualization."""

    name        : str  = "html-use-case-performance-stats"
    label       : str  = "Performance Stats"
    description : str  = "Detailed parsing performance with clustered graph breakdown"

    stats             : Dict = None
    dot_code          : str  = None
    node_to_cluster   : Dict = None
    cluster_to_node_id: Dict = None

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 1: Instrumented HTML parsing with NON-OVERLAPPING timing
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

        timing_accum = {
            'body'   : 0.0,
            'head'   : 0.0,
            'attrs'  : 0.0,
            'scripts': 0.0,
            'styles' : 0.0,
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
            t0 = perf_counter()
            document.attrs_graph.add_attribute(document.root_id, attr_name, attr_value, position)
            timing_accum['attrs'] += perf_counter() - t0
            stats['graphs']['attrs']['attributes'] += 1

        head_dict, body_dict = self._extract_head_body(html_dict)

        if head_dict:
            self._process_head_timed(document, head_dict, stats['graphs'], timing_accum)

        if body_dict:
            self._process_body_timed(document, body_dict, stats['graphs'], timing_accum)

        stats['graphs']['body']['time_ms']    = round(timing_accum['body'] * 1000, 2)
        stats['graphs']['head']['time_ms']    = round(timing_accum['head'] * 1000, 2)
        stats['graphs']['attrs']['time_ms']   = round(timing_accum['attrs'] * 1000, 2)
        stats['graphs']['scripts']['time_ms'] = round(timing_accum['scripts'] * 1000, 2)
        stats['graphs']['styles']['time_ms']  = round(timing_accum['styles'] * 1000, 2)

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

    def _process_head_timed(self, document, head_dict, graph_stats, timing_accum):
        t0 = perf_counter()
        head_node_id = Node_Id(Obj_Id())
        document.head_graph.create_element(node_path=Node_Path('head'), node_id=head_node_id)
        document.head_graph.set_root(head_node_id)
        timing_accum['head'] += perf_counter() - t0

        t0 = perf_counter()
        document.attrs_graph.register_element(head_node_id, 'head')
        timing_accum['attrs'] += perf_counter() - t0

        graph_stats['head']['elements'] += 1

        head_attrs = head_dict.get('attrs', {})
        for position, (attr_name, attr_value) in enumerate(head_attrs.items()):
            t0 = perf_counter()
            document.attrs_graph.add_attribute(head_node_id, attr_name, attr_value, position)
            timing_accum['attrs'] += perf_counter() - t0
            graph_stats['attrs']['attributes'] += 1

        self._process_children_timed(document, head_node_id, head_dict, 'head',
                                     document.head_graph, graph_stats, 'head', timing_accum)

    def _process_body_timed(self, document, body_dict, graph_stats, timing_accum):
        t0 = perf_counter()
        body_node_id = Node_Id(Obj_Id())
        document.body_graph.create_element(node_path=Node_Path('body'), node_id=body_node_id)
        document.body_graph.set_root(body_node_id)
        timing_accum['body'] += perf_counter() - t0

        t0 = perf_counter()
        document.attrs_graph.register_element(body_node_id, 'body')
        timing_accum['attrs'] += perf_counter() - t0

        graph_stats['body']['elements'] += 1

        body_attrs = body_dict.get('attrs', {})
        for position, (attr_name, attr_value) in enumerate(body_attrs.items()):
            t0 = perf_counter()
            document.attrs_graph.add_attribute(body_node_id, attr_name, attr_value, position)
            timing_accum['attrs'] += perf_counter() - t0
            graph_stats['attrs']['attributes'] += 1

        self._process_children_timed(document, body_node_id, body_dict, 'body',
                                     document.body_graph, graph_stats, 'body', timing_accum)

    def _process_children_timed(self, document, parent_id, parent_dict, parent_path,
                                 graph, graph_stats, graph_name, timing_accum):
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
                    t0 = perf_counter()
                    graph.create_text(text=text, parent_id=parent_id, position=position)
                    timing_accum[graph_name] += perf_counter() - t0
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

                t0 = perf_counter()
                graph.create_element(node_path=Node_Path(node_path), node_id=node_id)
                graph.add_child(parent_id, node_id, position)
                timing_accum[graph_name] += perf_counter() - t0
                graph_stats[graph_name]['elements'] += 1

                t0 = perf_counter()
                document.attrs_graph.register_element(node_id, tag)
                timing_accum['attrs'] += perf_counter() - t0

                attrs = node.get('attrs', {})
                for attr_pos, (attr_name, attr_value) in enumerate(attrs.items()):
                    t0 = perf_counter()
                    document.attrs_graph.add_attribute(node_id, attr_name, attr_value, attr_pos)
                    timing_accum['attrs'] += perf_counter() - t0
                    graph_stats['attrs']['attributes'] += 1

                if tag in SCRIPT_TAGS:
                    content = self._extract_text_content(node)
                    t0 = perf_counter()
                    document.scripts_graph.register_script(node_id, content)
                    timing_accum['scripts'] += perf_counter() - t0
                    graph_stats['scripts']['scripts'] += 1
                elif tag in STYLE_TAGS:
                    t0 = perf_counter()
                    if tag == 'link':
                        document.styles_graph.register_link(node_id)
                    else:
                        content = self._extract_text_content(node)
                        document.styles_graph.register_style(node_id, content)
                    timing_accum['styles'] += perf_counter() - t0
                    graph_stats['styles']['styles'] += 1
                else:
                    self._process_children_timed(document, node_id, node, node_path,
                                                  graph, graph_stats, graph_name, timing_accum)

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
    # Phase 2: Build stats graph
    # ═══════════════════════════════════════════════════════════════════════════

    def html_mgraph__to__mgraph(self, html_mgraph: Html_MGraph) -> MGraph:
        if not self.stats:
            return None

        self.node_to_cluster = {}
        self.cluster_to_node_id = {}
        mgraph = MGraph()

        with mgraph.builder() as builder:
            builder.add_node("Html_MGraph Performance")

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

            for graph_name, gs in self.stats['graphs'].items():
                builder.add_connected_node(Metric__Graph_Name(f"{graph_name.title()} Graph"))

                builder.add_predicate("time", Metric__Time(f"{gs['time_ms']} ms"), key=f"{graph_name}_time")
                builder.up()
                builder.add_predicate("nodes", Metric__Count(str(gs['nodes'])), key=f"{graph_name}_nodes")
                builder.up()
                builder.add_predicate("edges", Metric__Count(str(gs['edges'])), key=f"{graph_name}_edges")
                builder.up()

                if graph_name in ('body', 'head'):
                    builder.add_predicate("elements", Metric__Count(str(gs.get('elements', 0))), key=f"{graph_name}_elements")
                    builder.up()
                    builder.add_predicate("text_nodes", Metric__Count(str(gs.get('text_nodes', 0))), key=f"{graph_name}_text_nodes")
                    builder.up()
                elif graph_name == 'attrs':
                    builder.add_predicate("attributes", Metric__Count(str(gs.get('attributes', 0))), key=f"{graph_name}_attributes")
                    builder.up()
                elif graph_name == 'scripts':
                    builder.add_predicate("scripts", Metric__Count(str(gs.get('scripts', 0))), key=f"{graph_name}_scripts_count")
                    builder.up()
                elif graph_name == 'styles':
                    builder.add_predicate("styles", Metric__Count(str(gs.get('styles', 0))), key=f"{graph_name}_styles_count")
                    builder.up()

                builder.root()

        return mgraph

    # ═══════════════════════════════════════════════════════════════════════════
    # Phase 3: Generate DOT with nested row-wrapper clusters
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
            dot.set_graph__splines__polyline()
            dot.set_graph__node_sep(0.3)
            dot.set_graph__rank_sep(0.4)

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
        """Post-process DOT with nested row-wrapper clusters for proper layout."""

        lines = dot_code.split('\n')

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

        node_id_to_line = {}
        node_id_to_label = {}
        for line in node_lines:
            match = re.match(r'\s*"([^"]+)"\s*\[', line)
            if match:
                node_id = match.group(1)
                node_id_to_line[node_id] = line
                label_match = re.search(r'label="([^"]*)"', line)
                if label_match:
                    node_id_to_label[node_id] = label_match.group(1)

        edges = []
        for line in edge_lines:
            match = re.match(r'\s*"([^"]+)"\s*->\s*"([^"]+)"', line)
            if match:
                edges.append((match.group(1), match.group(2)))

        graph_node_to_cluster = {}
        for node_id, label in node_id_to_label.items():
            for cluster_name in CLUSTER_COLORS.keys():
                if f'{cluster_name.title()} Graph' in label:
                    graph_node_to_cluster[node_id] = cluster_name
                    break

        cluster_to_node_id = {v: k for k, v in graph_node_to_cluster.items()}

        cluster_nodes: Dict[str, Set[str]] = {name: set() for name in CLUSTER_COLORS.keys()}

        for graph_node_id, cluster_name in graph_node_to_cluster.items():
            cluster_nodes[cluster_name].add(graph_node_id)
            self._collect_descendants(graph_node_id, edges, cluster_nodes[cluster_name])

        all_clustered_nodes: Set[str] = set()
        for nodes in cluster_nodes.values():
            all_clustered_nodes.update(nodes)

        global_node_ids = set(node_id_to_line.keys()) - all_clustered_nodes

        # Build new DOT
        new_lines = []
        new_lines.extend(header_lines)
        new_lines.append('  newrank=true;')
        new_lines.append('  compound=true;')
        new_lines.append('')

        # Global nodes
        new_lines.append('  // Global nodes')
        for node_id in global_node_ids:
            if node_id in node_id_to_line:
                new_lines.append(f'  {node_id_to_line[node_id]}')
        new_lines.append('')

        body_id    = cluster_to_node_id.get('body', '')
        head_id    = cluster_to_node_id.get('head', '')
        attrs_id   = cluster_to_node_id.get('attrs', '')
        scripts_id = cluster_to_node_id.get('scripts', '')
        styles_id  = cluster_to_node_id.get('styles', '')

        # Row 1 wrapper: Body + Head
        new_lines.append('  // Row 1: Body + Head')
        new_lines.append('  subgraph cluster_row1 {')
        new_lines.append('    label="";')
        new_lines.append('    style=invis;')
        new_lines.append('    margin=0;')
        new_lines.append('')

        if cluster_nodes.get('body'):
            self._add_cluster_to_lines(new_lines, 'body', cluster_nodes['body'], node_id_to_line, indent=4)
        if cluster_nodes.get('head'):
            self._add_cluster_to_lines(new_lines, 'head', cluster_nodes['head'], node_id_to_line, indent=4)

        new_lines.append('  }')
        new_lines.append('')

        # Row 2 wrapper: Attrs + Styles
        new_lines.append('  // Row 2: Attrs + Styles')
        new_lines.append('  subgraph cluster_row2 {')
        new_lines.append('    label="";')
        new_lines.append('    style=invis;')
        new_lines.append('    margin=0;')
        new_lines.append('')

        if cluster_nodes.get('attrs'):
            self._add_cluster_to_lines(new_lines, 'attrs', cluster_nodes['attrs'], node_id_to_line, indent=4)
        if cluster_nodes.get('styles'):
            self._add_cluster_to_lines(new_lines, 'styles', cluster_nodes['styles'], node_id_to_line, indent=4)

        new_lines.append('  }')
        new_lines.append('')

        # Row 3: Scripts alone
        new_lines.append('  // Row 3: Scripts')
        if cluster_nodes.get('scripts'):
            self._add_cluster_to_lines(new_lines, 'scripts', cluster_nodes['scripts'], node_id_to_line, indent=2)

        # Edges with constraint=false for cluster edges
        new_lines.append('  // Edges')
        for line in edge_lines:
            modified_line = line
            for cluster_node_id in graph_node_to_cluster.keys():
                if f'-> "{cluster_node_id}"' in line:
                    if '[' in modified_line and '];' in modified_line:
                        modified_line = modified_line.replace('];', ', constraint=false];')
                    elif '];' in modified_line:
                        modified_line = modified_line.replace('];', ' [constraint=false];')
                    else:
                        modified_line = modified_line.rstrip(';') + ' [constraint=false];'
                    break
            new_lines.append(f'  {modified_line}')
        new_lines.append('')

        # Invisible edges between rows for vertical ordering
        new_lines.append('  // Row ordering (invisible edges)')

        # Row 1 -> Row 2
        if body_id and attrs_id:
            new_lines.append(f'  "{body_id}" -> "{attrs_id}" [style=invis, weight=100];')
        elif head_id and attrs_id:
            new_lines.append(f'  "{head_id}" -> "{attrs_id}" [style=invis, weight=100];')

        # Row 2 -> Row 3
        if attrs_id and scripts_id:
            new_lines.append(f'  "{attrs_id}" -> "{scripts_id}" [style=invis, weight=100];')
        elif styles_id and scripts_id:
            new_lines.append(f'  "{styles_id}" -> "{scripts_id}" [style=invis, weight=100];')

        new_lines.append('')
        new_lines.extend(footer_lines)

        return '\n'.join(new_lines)

    def _add_cluster_to_lines(self, lines: List[str], cluster_name: str,
                               nodes: Set[str], node_id_to_line: Dict[str, str], indent: int = 2):
        """Add a cluster subgraph with proper indentation."""
        color = CLUSTER_COLORS[cluster_name]
        label = CLUSTER_LABELS[cluster_name]
        pad = ' ' * indent

        lines.append(f'{pad}subgraph cluster_{cluster_name} {{')
        lines.append(f'{pad}  label="{label}";')
        lines.append(f'{pad}  style="filled,rounded";')
        lines.append(f'{pad}  fillcolor="{color}";')
        lines.append(f'{pad}  color="#666666";')
        lines.append(f'{pad}  fontname="Arial";')
        lines.append(f'{pad}  fontsize=12;')
        lines.append(f'{pad}  margin=16;')
        lines.append('')

        for node_id in nodes:
            if node_id in node_id_to_line:
                lines.append(f'{pad}  {node_id_to_line[node_id]}')

        lines.append(f'{pad}}}')
        lines.append('')

    def _collect_descendants(self, node_id: str, edges: List[tuple], collected: Set[str]):
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