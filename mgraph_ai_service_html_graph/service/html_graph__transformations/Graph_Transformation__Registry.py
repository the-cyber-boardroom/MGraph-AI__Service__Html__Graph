# Graph Transformation Registry
#
# Central registry for all available graph transformations.
# Provides lookup by name and listing functionality.

from typing                                                                                                                 import Dict, List, Type
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base                            import Graph_Transformation__Base
from mgraph_ai_service_html_graph.service.html_graph__transformations.core_transformations.Graph_Transform__Attributes      import Graph_Transform__Attributes
from mgraph_ai_service_html_graph.service.html_graph__transformations.core_transformations.Graph_Transform__Body_Only       import Graph_Transform__Body_Only
from mgraph_ai_service_html_graph.service.html_graph__transformations.core_transformations.Graph_Transform__Default         import Graph_Transform__Default
from mgraph_ai_service_html_graph.service.html_graph__transformations.core_transformations.Graph_Transform__Full_Document   import Graph_Transform__Full_Document
from mgraph_ai_service_html_graph.service.html_graph__transformations.core_transformations.Graph_Transform__Head_Only       import Graph_Transform__Head_Only
from mgraph_ai_service_html_graph.service.html_graph__transformations.core_transformations.Graph_Transform__Scripts         import Graph_Transform__Scripts
from mgraph_ai_service_html_graph.service.html_graph__transformations.core_transformations.Graph_Transform__Styles          import Graph_Transform__Styles
from mgraph_ai_service_html_graph.service.html_graph__transformations.html_use_cases.Html_Use_Case__1 import Html_Use_Case__1
from mgraph_ai_service_html_graph.service.html_graph__transformations.html_use_cases.Html_Use_Case__2 import Html_Use_Case__2


# ═══════════════════════════════════════════════════════════════════════════════════════════
# Registry
# ═══════════════════════════════════════════════════════════════════════════════════════════

class Graph_Transformation__Registry:                                                    # Transformation registry

    _transformations: Dict[str, Type[Graph_Transformation__Base]] = {
        'html-use-case-1': Html_Use_Case__1                ,
        'html-use-case-2': Html_Use_Case__2                ,
        'default'        : Graph_Transform__Default        ,                            # Built-in transformations
        'body_only'      : Graph_Transform__Body_Only      ,
        'head_only'      : Graph_Transform__Head_Only      ,
        'full-document'  : Graph_Transform__Full_Document  ,
        'attributes'     : Graph_Transform__Attributes     ,
        'scripts'        : Graph_Transform__Scripts        ,
        'styles'         : Graph_Transform__Styles         ,
    }

    def get(self, name: str) -> Graph_Transformation__Base:                              # Get transformation by name
        transform_class = self._transformations.get(name)
        if transform_class:
            return transform_class()
        return Graph_Transform__Default()                                                # Fallback to default

    def list_all(self) -> List[Dict[str, str]]:                                          # List all transformations
        result = []
        for name, transform_class in self._transformations.items():
            instance = transform_class()
            result.append({
                'name'       : instance.name       ,
                'label'      : instance.label      ,
                'description': instance.description,
            })
        return result

    def names(self) -> List[str]:                                                        # Get all transformation names
        return list(self._transformations.keys())

    def register(self, transform_class: Type[Graph_Transformation__Base]) -> None:      # Register custom transformation
        instance = transform_class()
        self._transformations[instance.name] = transform_class


# Global registry instance
transformation_registry = Graph_Transformation__Registry()
