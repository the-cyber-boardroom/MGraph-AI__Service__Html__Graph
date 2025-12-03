from typing                                               import Optional, List, Tuple
from osbot_utils.type_safe.Type_Safe                      import Type_Safe


class Html_MGraph__Path(Type_Safe):                                             # Utilities for computing and manipulating DOM paths for Html_MGraph
    PATH_SEPARATOR : str = '.'                                                  # Separator between path segments

    def compute_element_path(self, parent_path    : Optional[str]       ,       # Path of the parent element (None for root)
                                   tag            : str                 ,       # HTML tag name
                                   sibling_index  : int                 ,       # Index among siblings with same tag (0-based)
                                   sibling_counts : dict                ) -> str:  # Dict mapping tag names to count
        same_tag_count = sibling_counts.get(tag, 1)                             # Determine if we need an index suffix
        if same_tag_count > 1:
            tag_with_index = f"{tag}[{sibling_index}]"
        else:
            tag_with_index = tag

        if parent_path:                                                         # Build full path
            return f"{parent_path}{self.PATH_SEPARATOR}{tag_with_index}"
        else:
            return tag_with_index

    def parse_path(self, path: str) -> List[Tuple[str, Optional[int]]]:         # Parse a DOM path into list of (tag, index) tuples
        if not path:
            return []

        result   = []
        segments = path.split(self.PATH_SEPARATOR)

        for segment in segments:
            if '[' in segment:                                                  # Has index: "div[2]"
                tag_part   = segment[:segment.index('[')]
                index_part = segment[segment.index('[')+1:segment.index(']')]
                result.append((tag_part, int(index_part)))
            else:                                                               # No index: "div"
                result.append((segment, None))

        return result

    def get_parent_path(self, path: str) -> Optional[str]:                      # Get the parent path from a DOM path
        if not path or self.PATH_SEPARATOR not in path:
            return None
        return path.rsplit(self.PATH_SEPARATOR, 1)[0]

    def get_depth(self, path: str) -> int:                                      # Get the depth of a path (number of segments)
        if not path:
            return 0
        return path.count(self.PATH_SEPARATOR) + 1

    def is_ancestor_of(self, ancestor_path   : str,                             # Potential ancestor path
                             descendant_path : str) -> bool:                    # Potential descendant path
        if not ancestor_path or not descendant_path:
            return False
        return descendant_path.startswith(ancestor_path + self.PATH_SEPARATOR)

    def value_node_path(self, category   : str                  ,               # Category type (tag, attr, text)
                              identifier : Optional[str] = None ) -> str:       # Optional identifier (tag name, attr name, etc.)
        if identifier:
            return f"{category}:{identifier}"
        return category