import os
import sys
import unittest

from test_target_configure import TestTargetConfigure

os.chdir(os.path.abspath(os.path.join(os.getcwd(), "test")))


def RunModelCase():
    suite = unittest.TestSuite()
    suite.addTest(TestTargetConfigure('test_target_server_FUN_configure'))
    return suite


if __name__ == '__main__':
    print("--------------- start to run test cases ---------------")
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(RunModelCase())
    print("--------------- run test cases end ---------------")
