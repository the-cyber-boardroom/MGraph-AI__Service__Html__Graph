from osbot_utils.type_safe.primitives.core.Safe_UInt import Safe_UInt
from osbot_utils.type_safe.Type_Safe                 import Type_Safe


class Schema__Graph__Edge__Style(Type_Safe):                                    # Visual styling for an edge
    color        : str       = '#888888'                                        # todo: refactor to Type_Safe primitive | Line color
    width        : Safe_UInt = 1                                                # Line width
    dashed       : bool      = False                                            # Dashed line style
    arrow        : bool      = True                                             # Show arrow