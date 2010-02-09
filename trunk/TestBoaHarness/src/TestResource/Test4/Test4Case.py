import unittest
import Test4Case
import TestCaseHelper
import os

def injectParam(param,tepar) :
    Test4Case.param = param
    Test4Case.tepar = tepar

class TestSuite(unittest.TestCase):

    def setUp(self):
       TestCaseHelper.prepareRunDir(Test4Case.param, Test4Case.tepar)
       self.d = TestCaseHelper.ChangeDir(Test4Case.param)

    def testCase1(self):
        res1 = os.path.exists("out/file1.txt")
        res2 = os.path.exists("out/file2.txt")
        self.assertTrue(res1 and res2)

    def tearDown(self) :
        self.d.restore()
