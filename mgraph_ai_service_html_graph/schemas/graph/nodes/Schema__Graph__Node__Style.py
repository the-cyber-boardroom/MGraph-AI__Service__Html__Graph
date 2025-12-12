from osbot_utils.type_safe.Type_Safe                                 import Type_Safe

class Schema__Graph__Node__Style(Type_Safe):                                    # Visual styling for a node
    fill_color   : str = '#E8E8E8'                                              # todo: refactor to Type_Safe primitive |  Background color
    font_color   : str = '#333333'                                              # todo: refactor to Type_Safe primitive |  Text color
    border_color : str = '#CCCCCC'                                              # todo: refactor to Type_Safe primitive |  Border color
    shape        : str = 'box'                                                  # todo: refactor to Type_Safe primitive or enum |  Shape type
