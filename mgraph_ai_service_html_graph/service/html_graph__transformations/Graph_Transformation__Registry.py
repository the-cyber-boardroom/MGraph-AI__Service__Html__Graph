# ═══════════════════════════════════════════════════════════════════════════════
# MGraph HTML Graph - Graph Transformation Registry
# v0.2.5 - Central registry for all transformations
# ═══════════════════════════════════════════════════════════════════════════════

from typing                          import Dict, List, Type
from enum                            import Enum
from osbot_utils.type_safe.Type_Safe import Type_Safe


class Graph_Transformation__Registry(Type_Safe):
    """Registry of available graph transformations.
    
    Maintains a mapping of transformation names to their classes.
    Provides lookup and enumeration of available transformations.
    """
    
    _transformations: Dict[str, Type]                                               # name → transformation class
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

        from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base            import Graph_Transformation__Base
        from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Collapse_Text   import Graph_Transformation__Collapse_Text
        from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Elements_Only   import Graph_Transformation__Elements_Only
        from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Body_Only       import Graph_Transformation__Body_Only

        self.register(Graph_Transformation__Base         )
        self.register(Graph_Transformation__Collapse_Text)
        self.register(Graph_Transformation__Elements_Only)
        self.register(Graph_Transformation__Body_Only    )
    
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
        return Enum('Transformation_Type', {name.upper(): name for name in self._transformations.keys()})


# ═══════════════════════════════════════════════════════════════════════════════
# Singleton instance
# ═══════════════════════════════════════════════════════════════════════════════

transformation_registry = Graph_Transformation__Registry()


# ═══════════════════════════════════════════════════════════════════════════════
# Static Enum for FastAPI routes (must be defined at module load time)
# ═══════════════════════════════════════════════════════════════════════════════

class Transformation_Type(str, Enum):
    """Available graph transformations."""
    default        = "default"
    collapse_text  = "collapse_text"
    elements_only  = "elements_only"
    body_only      = "body_only"
