import os
import sys
import unittest

from test_target_configure import TestTargetConfigure
from test_target_backup import TestTargetBackup
from test_target_rollback import TestTargetRollback

os.chdir(os.path.abspath(os.path.join(os.getcwd(), "test")))


def RunModelCase():
    suite = unittest.TestSuite()
    suite.addTest(TestTargetConfigure('test_target_server_FUN_configure'))
    suite.addTest(TestTargetBackup('test_target_server_FUN_backup'))
    suite.addTest(TestTargetRollback('test_target_server_FUN_rollback'))
    return suite


if __name__ == '__main__':
    print("--------------- start to run test cases ---------------")
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(RunModelCase())
    print("--------------- run test cases end ---------------")
