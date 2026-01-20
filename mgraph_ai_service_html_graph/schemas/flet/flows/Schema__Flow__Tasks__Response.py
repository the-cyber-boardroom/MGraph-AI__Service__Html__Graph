# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Flow__Tasks__Response - Response containing flow tasks
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe import Type_Safe

# todo: add type_safe primitives and schemas to the attributes below (and fix the bug)
class Schema__Flow__Tasks__Response(Type_Safe):
    success         : bool = False                                                      # Whether retrieval succeeded
    flet_name       : str  = ''                                                         # Name of the FLeT
    tasks           : dict = None                                                       # Task list with details (indexed by task,name)
    tasks__as_list  : list                                                              # todo: fix the bug that cause this scenario where we get a list instead of a dictt
    count           : int  = 0                                                          # Number of tasks
