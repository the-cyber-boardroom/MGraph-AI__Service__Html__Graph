from osbot_utils.type_safe.Type_Safe                                            import Type_Safe

class Schema__LETS__Save__Output(Type_Safe):                                     # Save phase output
    success : bool = False                                                       # Whether save succeeded
    cached  : bool = False                                                       # Whether stored in cache
    layer   : str  = None                                                        # Layer name if cached
    file_id : str  = None                                                        # File ID if cached
