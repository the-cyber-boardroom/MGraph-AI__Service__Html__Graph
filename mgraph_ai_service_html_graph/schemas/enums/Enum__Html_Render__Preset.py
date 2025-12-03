from enum import Enum


class Enum__Html_Render__Preset(str, Enum):                                                 # Rendering presets for different visualization needs
    FULL_DETAIL     = 'full_detail'                                                         # Show everything
    STRUCTURE_ONLY  = 'structure_only'                                                      # Only elements and child edges
    MINIMAL         = 'minimal'                                                             # Just element nodes with tags inline
