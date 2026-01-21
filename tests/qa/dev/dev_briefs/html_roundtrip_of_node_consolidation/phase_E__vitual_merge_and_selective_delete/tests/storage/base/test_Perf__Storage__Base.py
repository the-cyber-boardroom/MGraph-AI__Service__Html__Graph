# ═══════════════════════════════════════════════════════════════════════════════
# test_Perf__Storage__Base - Tests for abstract storage base class
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                   import TestCase
from abc                                                                        import ABC
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.utils.Objects import base_classes
from phase_e.storage.base.Perf__Storage__Base                                   import Perf__Storage__Base
from phase_e.storage.safe_str.Safe_Str__Session_Name                            import Safe_Str__Session_Name
from phase_e.storage.safe_str.Safe_Str__Target_Name                             import Safe_Str__Target_Name
from tests.Phase_E__Fast_API__Test_Objs import client_cache_service


class test_Perf__Storage__Base(TestCase):

    def test__init__(self):                                                     # Test class structure
        assert Perf__Storage__Base.__bases__    == (Type_Safe,)                 # Inherits from Type_Safe
    
    def test__class_attributes(self):                                           # Test class has expected attributes
        annotations = Perf__Storage__Base.__annotations__
        assert 'session_name' in annotations
        assert 'target_name'  in annotations
        assert annotations['session_name'] == Safe_Str__Session_Name
        assert annotations['target_name']  == Safe_Str__Target_Name
