# Graph Transformation Registry
#
# Central registry for all available graph transformations.
# Provides lookup by name and listing functionality.

from typing                                                                                      import Dict, List, Type
from mgraph_ai_service_html_graph.service.html_graph__transformations.Graph_Transformation__Base import Graph_Transformation__Base
from mgraph_ai_service_html_graph.service.html_graph__transformations.MGraph__Transformations    import Graph_Transform__Default, Graph_Transform__Body_Only, Graph_Transform__Head_Only, \
                                                                                                        Graph_Transform__Document, Graph_Transform__Attributes, Graph_Transform__Scripts, Graph_Transform__Styles, Graph_Transform__Structure_Only, Graph_Transform__Clean, Graph_Transform__Compact, Graph_Transform__Expanded


# ═══════════════════════════════════════════════════════════════════════════════════════════
# Registry
# ═══════════════════════════════════════════════════════════════════════════════════════════

class Graph_Transformation__Registry:                                                    # Transformation registry

    _transformations: Dict[str, Type[Graph_Transformation__Base]] = {                   # Built-in transformations
        'default'        : Graph_Transform__Default        ,
        'body_only'      : Graph_Transform__Body_Only      ,
        'head_only'      : Graph_Transform__Head_Only      ,
        'document'       : Graph_Transform__Document       ,
        'attributes'     : Graph_Transform__Attributes     ,
        'scripts'        : Graph_Transform__Scripts        ,
        'styles'         : Graph_Transform__Styles         ,
        'structure_only' : Graph_Transform__Structure_Only ,
        'clean'          : Graph_Transform__Clean          ,
        'compact'        : Graph_Transform__Compact        ,
        'expanded'       : Graph_Transform__Expanded       ,
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
