# ═══════════════════════════════════════════════════════════════════════════════
# MGraph HTML Graph - Graph Transformation Registry
# v0.3.0 - Updated for multi-graph architecture
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                            import Dict, List, Type
from enum                                                                                              import Enum

#from mgraph_ai_service_html_graph.service.html_graph__transformations.html_use_cases.Html_Use_Case__1 import Html_Use_Case__1
from osbot_utils.type_safe.Type_Safe                                                                   import Type_Safe
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base       import Graph_Transformation__Base
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transform__Body_Only       import Graph_Transform__Body_Only
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transform__Structure_Only  import Graph_Transform__Structure_Only
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transform__Attributes_View import Graph_Transform__Attributes_View
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transform__Clean           import Graph_Transform__Clean
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transform__Semantic        import Graph_Transform__Semantic


class Graph_Transformation__Registry(Type_Safe):
    """Registry of available graph transformations.

    Maintains a mapping of transformation names to their classes.
    Provides lookup and enumeration of available transformations.
    """

    _transformations: Dict[str, Type]
    _initialized    : bool = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._transformations = {}
        if not self._initialized:
            self._register_all()
            self._initialized = True

    # ═══════════════════════════════════════════════════════════════════════════
    # Registration
    # ═══════════════════════════════════════════════════════════════════════════

    def register(self, transformation_class: Type) -> None:                         # Register a transformation class
        instance = transformation_class()
        self._transformations[instance.name] = transformation_class

    def _register_all(self) -> None:                                                # Register all built-in transformations
        #self.register(Html_Use_Case__1                )
        self.register(Graph_Transformation__Base      )                             # Default (pass-through)
        self.register(Graph_Transform__Body_Only      )                             # Body content only
        self.register(Graph_Transform__Structure_Only )                             # Page structure, no text
        self.register(Graph_Transform__Attributes_View)                             # Attributes focus
        self.register(Graph_Transform__Clean          )                             # Clean DOM view
        self.register(Graph_Transform__Semantic       )                             # Merged text, collapsed chains

    # ═══════════════════════════════════════════════════════════════════════════
    # Lookup
    # ═══════════════════════════════════════════════════════════════════════════

    def get(self, name: str):                                                       # Get transformation instance by name
        transformation_class = self._transformations.get(name)
        if not transformation_class:
            raise ValueError(f"Unknown transformation: {name}")
        return transformation_class()

    def exists(self, name: str) -> bool:                                            # Check if transformation exists
        return name in self._transformations

    def names(self) -> List[str]:                                                   # Get list of transformation names
        return list(self._transformations.keys())

    # ═══════════════════════════════════════════════════════════════════════════
    # Enumeration
    # ═══════════════════════════════════════════════════════════════════════════

    def list_all(self) -> List[Dict[str, str]]:                                     # Get metadata for all transformations
        result = []
        for transformation_class in self._transformations.values():
            instance = transformation_class()
            result.append(instance.to_dict())
        return result

    def create_enum(self) -> Type[Enum]:                                            # Create dynamic enum of transformation names
        return Enum('Transformation_Type',
                    {name.upper(): name for name in self._transformations.keys()})


# ═══════════════════════════════════════════════════════════════════════════════
# Singleton instance
# ═══════════════════════════════════════════════════════════════════════════════

transformation_registry = Graph_Transformation__Registry()


# ═══════════════════════════════════════════════════════════════════════════════
# Static Enum for FastAPI routes (must be defined at module load time)
# ═══════════════════════════════════════════════════════════════════════════════

class Transformation_Type(str, Enum):
    """Available graph transformations."""
    default         = "default"
    body_only       = "body_only"
    structure_only  = "structure_only"
    attributes_view = "attributes_view"
    clean           = "clean"
    semantic        = "semantic"