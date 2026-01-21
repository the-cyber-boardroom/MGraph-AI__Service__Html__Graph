from unittest                                                                            import TestCase
from mgraph_ai_service_html_graph.schemas.timestamps.enums.Schema__Trace__Response__Type import Schema__Trace__Response__Type
from mgraph_db.mgraph.schemas.Schema__MGraph__Node__Data import Schema__MGraph__Node__Data
from osbot_utils.helpers.timestamp_capture.Timestamp_Collector                           import Timestamp_Collector
from osbot_utils.helpers.timestamp_capture.actions.Timestamp_Collector__Export           import Timestamp_Collector__Export
from osbot_utils.helpers.timestamp_capture.decorators.timestamp import timestamp
from osbot_utils.type_safe.Type_Safe import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id import Node_Id
from osbot_utils.utils.Files                                                             import path_combine, file_create
from mgraph_db.mgraph.models.Model__MGraph__Graph                                        import Model__MGraph__Graph
from mgraph_db.mgraph.schemas.Schema__MGraph__Graph                                      import Schema__MGraph__Graph
from mgraph_db.mgraph.schemas.Schema__MGraph__Node                                       import Schema__MGraph__Node
from mgraph_db.mgraph.schemas.Schema__MGraph__Edge                                       import Schema__MGraph__Edge
from mgraph_db.mgraph.schemas.Schema__MGraph__Types                                      import Schema__MGraph__Types
from osbot_utils.utils.Json import json_save


class Simple_Node(Schema__MGraph__Node): pass
class Custom_Node(Schema__MGraph__Node): pass


class test_QA__Model__MGraph__Node__Factory(TestCase):              # Focused performance tracing for node creation operations

    @classmethod
    def setUpClass(cls):
        cls.target_folder = path_combine(__file__, '../_traces/node_factory')
        cls.schema_types  = Schema__MGraph__Types(node_type=Simple_Node, edge_type=Schema__MGraph__Edge)

    def _create_fresh_graph(self):
        graph_data = Schema__MGraph__Graph(schema_types=self.schema_types, graph_type=Schema__MGraph__Graph)
        return Model__MGraph__Graph(data=graph_data)

    def _save_speedscope(self, export: Timestamp_Collector__Export, name: str):
        file_path = path_combine(self.target_folder, f'speedscope__{name}.json')
        file_create(file_path, export.to_speedscope_json())
        print(f"Saved: {file_path}")

    def _save_export_full(self, export: Timestamp_Collector__Export, name: str):
        file_path = path_combine(self.target_folder, f'export_full__{name}.json')
        traces    = export.to_export_full().json()
        json_data = dict(graph         = None, #Schema__Graph__Response__Base().json(),
                         response_type = Schema__Trace__Response__Type.FULL,
                         traces        = traces                            )
        json_save(json_data, file_path)
        print(f"Saved: {file_path}")

    # --- Single Node Creation Traces ---

    def test__trace__create__one_node(self):                                              # Trace a single node creation
        graph                  = self._create_fresh_graph()
        _timestamp_collector_  = Timestamp_Collector(name='create__one_node')


        with _timestamp_collector_:
            node = graph.new_node()

        export = Timestamp_Collector__Export(collector=_timestamp_collector_)
        self._save_speedscope(export, 'create__one_node')

    def test_create_30(self):
        self.test__trace__batch_30_nodes()

    def test__trace__create__one_node__warm(self):                                              # Trace a single node creation
        name                   = 'create__one_node__warm'
        graph                  = self._create_fresh_graph()
        _timestamp_collector_  = Timestamp_Collector(name=name)

        graph.new_node()
        with _timestamp_collector_:
            graph.new_node()

        export = Timestamp_Collector__Export(collector=_timestamp_collector_)
        self._save_speedscope(export, name)
        self._save_export_full(export, name)

    def test__trace__create__two_nodes(self):                                              # Trace a single node creation
        graph                  = self._create_fresh_graph()
        _timestamp_collector_  = Timestamp_Collector(name='create__two_nodes')

        with _timestamp_collector_:
            graph.new_node()
            graph.new_node()

        export = Timestamp_Collector__Export(collector=_timestamp_collector_)
        self._save_speedscope(export, 'create__two_nodes')

    def test__trace__create__three_nodes(self):                                              # Trace a single node creation
        graph                  = self._create_fresh_graph()
        _timestamp_collector_  = Timestamp_Collector(name='create__three_nodes')

        with _timestamp_collector_:
            graph.new_node()
            graph.new_node()
            graph.new_node()

        export = Timestamp_Collector__Export(collector=_timestamp_collector_)
        self._save_speedscope(export, 'create__three_nodes')

    def test__trace__create_node_with_type(self):                                           # Trace node creation with explicit type
        graph                  = self._create_fresh_graph()
        _timestamp_collector_  = Timestamp_Collector(name='create_node_with_type')

        with _timestamp_collector_:
            node = graph.new_node(node_type=Custom_Node)

        export = Timestamp_Collector__Export(collector=_timestamp_collector_)
        self._save_speedscope(export, 'create_node_with_type')

    # --- Batch Node Creation Traces ---

    def test__trace__batch_10_nodes(self):                                                  # Trace creating 10 nodes
        graph                  = self._create_fresh_graph()
        _timestamp_collector_  = Timestamp_Collector(name='batch_10_nodes')

        with _timestamp_collector_:
            for _ in range(10):
                graph.new_node()

        export = Timestamp_Collector__Export(collector=_timestamp_collector_)
        self._save_speedscope(export, 'batch_10_nodes')

    def test__trace__batch_30_nodes(self):                                                  # Trace creating 30 nodes - matches HTML size=30
        graph                  = self._create_fresh_graph()
        _timestamp_collector_  = Timestamp_Collector(name='batch_30_nodes')

        with _timestamp_collector_:
            for _ in range(30):
                graph.new_node()

        export = Timestamp_Collector__Export(collector=_timestamp_collector_)
        self._save_speedscope(export, 'batch_30_nodes')

    def test__trace__batch_100_nodes(self):                                                 # Trace creating 100 nodes
        graph                  = self._create_fresh_graph()
        _timestamp_collector_  = Timestamp_Collector(name='batch_100_nodes')

        with _timestamp_collector_:
            for _ in range(100):
                graph.new_node()

        export = Timestamp_Collector__Export(collector=_timestamp_collector_)
        self._save_speedscope(export, 'batch_100_nodes')

    # --- Mixed Operations Traces ---

    def test__trace__mixed_node_types(self):                                                # Trace mixed node type creation
        graph                  = self._create_fresh_graph()
        _timestamp_collector_  = Timestamp_Collector(name='mixed_node_types')

        with _timestamp_collector_:
            for i in range(30):
                if i % 2 == 0:
                    graph.new_node()                                                        # Default type
                else:
                    graph.new_node(node_type=Custom_Node)                                   # Explicit type

        export = Timestamp_Collector__Export(collector=_timestamp_collector_)
        self._save_speedscope(export, 'mixed_node_types')

    def test__trace__cold_vs_warm_cache(self):                                              # Trace cache warming effect
        graph                  = self._create_fresh_graph()
        _timestamp_collector_  = Timestamp_Collector(name='cold_vs_warm_cache')

        with _timestamp_collector_:
            # First call - cold cache
            graph.new_node(node_type=Custom_Node)

            # Clear and retry
            graph.node_factory().clear_caches()
            graph.new_node(node_type=Custom_Node)

            # Warm cache calls
            for _ in range(10):
                graph.new_node(node_type=Custom_Node)

        export = Timestamp_Collector__Export(collector=_timestamp_collector_)
        self._save_speedscope(export, 'cold_vs_warm_cache')

    # --- Full Pipeline Simulation ---

    def test__trace__simulate_html_element_creation(self):                                  # Simulate what happens per HTML element
        """Each HTML element typically creates: 1 element node + edges + attribute nodes"""
        graph                  = self._create_fresh_graph()
        _timestamp_collector_  = Timestamp_Collector(name='simulate_html_elements')

        with _timestamp_collector_:
            for element_idx in range(10):                                                   # 10 HTML elements
                # Element node
                element_node = graph.new_node()

                # 2 attribute value nodes per element (simulating class, id, etc.)
                for attr_idx in range(2):
                    attr_node = graph.new_node()

        export = Timestamp_Collector__Export(collector=_timestamp_collector_)
        self._save_speedscope(export, 'simulate_html_elements')

    # --- misc timestamps collectors ----

    def test__trace__debug_class_creation(self):
        name                   = 'debug_class_creation'
        _timestamp_collector_  = Timestamp_Collector(name=name)

        # --- Test Classes ---

        class An_Class__Python:
            """Pure Python class - baseline"""
            pass

        class An_Class__Type_Safe(Type_Safe):
            """Empty Type_Safe - measures Type_Safe overhead"""
            pass

        # Simple_Node is already defined (Schema__MGraph__Node subclass)
        # - has node_id, node_data, node_type attributes

        # --- Creation Functions ---

        @timestamp(name='1_python_class')
        def create_python_class():
            An_Class__Python()

        @timestamp(name='2_type_safe_empty')
        def create_type_safe_empty():
            An_Class__Type_Safe()

        @timestamp(name='3_simple_node_normal')
        def create_simple_node_normal():
            Simple_Node(node_data=None)

        @timestamp(name='4_simple_node_fast_factory')
        def create_simple_node_fast_factory():
            """Bypass Type_Safe __init__ entirely"""
            node = object.__new__(Simple_Node)
            node_dict = {
                'node_id'  : Node_Id(),
                'node_data': None,
                'node_type': Simple_Node,
            }
            object.__setattr__(node, '__dict__', node_dict)
            return node

        # --- Run Tests ---

        with _timestamp_collector_:
            # Run each 4 times to see cold vs warm
            for _ in range(4):
                create_python_class()
                create_type_safe_empty()
                create_simple_node_normal()
                create_simple_node_fast_factory()

        export = Timestamp_Collector__Export(collector=_timestamp_collector_)
        self._save_speedscope(export, name)
        self._save_export_full(export, name)