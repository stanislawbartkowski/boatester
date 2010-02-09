import unittest
import Test3Case
import TestCaseHelper
import os

def injectParam(param,tepar) :
    Test3Case.param = param
    Test3Case.tepar = tepar

class TestSuite(unittest.TestCase):

    def setUp(self):
       TestCaseHelper.prepareRunDir(Test3Case.param, Test3Case.tepar)
       self.d = TestCaseHelper.ChangeDir(Test3Case.param)

    def testCase1(self):
        res = os.path.exists("out/file1.txt")
        self.assertTrue(res)

    def tearDown(self) :
        self.d.restore()
