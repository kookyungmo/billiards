import unittest
from billiards.tests import wechat

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromModule(wechat))
    return suite