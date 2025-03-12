import sys
import os
testdir = os.path.dirname(__file__)
libhome = os.path.dirname(testdir)
sys.path.insert(0, libhome)
import unittest

class TestLocalSettings(unittest.TestCase):
    def __init__(self, methodName='runTest'):  
        super().__init__(methodName)  

    def test_local_settings(self):
        from molass_pre.Local import get_local_settings
        local_settings = get_local_settings()
        self.assertEqual(type(local_settings), dict)

if __name__ == '__main__':
    unittest.main()